from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.health_record import HealthRecord
from app.models.user import User

logger = structlog.get_logger()


class NutritionService:
    """营养建议服务"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_bmr(self, user: User) -> float:
        """计算基础代谢率 (BMR)"""
        # 使用 Mifflin-St Jeor 公式
        # 数据库存储的体重单位是克，需要除以1000转换为千克

        # 安全处理用户参数，并确保使用可计算值
        user_initial_weight = getattr(user, "initial_weight", 70000)
        user_height = getattr(user, "height", 170)
        user_age = getattr(user, "age", 30)
        user_gender = getattr(user, "gender", "male")

        try:
            # 确保数值为数字类型而不是数据库查询对象
            weight_in_grams = (
                float(user_initial_weight) if user_initial_weight is not None else 70000
            )
        except (ValueError, TypeError):
            weight_in_grams = 70000

        try:
            height_cm = float(user_height) if user_height is not None else 170
        except (ValueError, TypeError):
            height_cm = 170

        try:
            age_years = float(user_age) if user_age is not None else 30
        except (ValueError, TypeError):
            age_years = 30

        weight_kg = weight_in_grams / 1000.0  # 从克转换为千克

        if user_gender == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
        elif user_gender == "female":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
        else:
            # 中性计算
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 78

        return round(bmr, 2)

    def calculate_tdee(self, user: User) -> float:
        """计算每日总能量消耗 (TDEE)"""
        bmr = self.calculate_bmr(user)

        # 活动水平系数
        activity_factors = {
            "sedentary": 1.2,  # 久坐
            "light": 1.375,  # 轻度活动
            "moderate": 1.55,  # 中度活动
            "active": 1.725,  # 活跃
            "very_active": 1.9,  # 非常活跃
        }

        # 安全地处理 activity_level 属性
        user_activity_level = getattr(user, "activity_level", None)
        if user_activity_level is None or str(user_activity_level).strip() == "":
            user_activity_level = "sedentary"

        activity_factor = activity_factors.get(str(user_activity_level), 1.2)
        tdee = bmr * activity_factor

        return round(tdee, 2)

    def calculate_calorie_target(self, user: User) -> Dict[str, float]:
        """计算每日卡路里目标"""
        tdee = self.calculate_tdee(user)

        # 从数据库安全检索和转换体重数据并处理null值
        try:
            initial_weight_value = user.initial_weight
            target_weight_value = user.target_weight

            current_weight = (
                float(initial_weight_value)
                if initial_weight_value is not None and initial_weight_value != ""
                else 70000.0
            )
            target_weight = (
                float(target_weight_value)
                if target_weight_value is not None and target_weight_value != ""
                else 65000.0
            )
        except (TypeError, ValueError, AttributeError):
            # 如果数值不合法使用默认值
            current_weight = 70000.0
            target_weight = 65000.0

        weight_difference_in_kg = (
            current_weight - target_weight
        ) / 1000.0  # 转换为公斤

        if weight_difference_in_kg > 0:
            # 需要减重
            calorie_deficit = min(
                500, weight_difference_in_kg * 7700
            )  # 每公斤差值约7700卡路里（近似）
            target_calories = max(tdee - calorie_deficit, tdee * 0.8)  # 最少减少20%
        elif weight_difference_in_kg < 0:
            # 需要增重
            calorie_surplus = min(
                300, abs(weight_difference_in_kg) * 7700
            )  # 最大300卡盈余
            target_calories = tdee + calorie_surplus
        else:
            # 维持体重
            target_calories = tdee

        return {
            "maintenance": round(tdee, 2),
            "target": round(target_calories, 2),
            "weight_loss": round(tdee * 0.85, 2),  # 15% 赤字
            "weight_gain": round(tdee * 1.15, 2),  # 15% 盈余
            "weight_difference_kg": round(weight_difference_in_kg, 2),
        }

    def calculate_macronutrients(
        self, user: User, target_calories: float
    ) -> Dict[str, float]:
        """计算宏量营养素目标"""
        # 从数据库安全获取体重数据并处理None和空值
        try:
            initial_weight_value = user.initial_weight
            target_wt_value = (
                user.target_weight if hasattr(user, "target_weight") else None
            )

            weight_in_grams = (
                float(initial_weight_value)
                if initial_weight_value is not None and initial_weight_value != ""
                else 70000
            )
            weight_kg = weight_in_grams / 1000.0

            # 获取目标体重以确定蛋白质比例
            target_wt = (
                float(target_wt_value)
                if target_wt_value is not None and target_wt_value != ""
                else 65000
            )
            current_wt = (
                float(initial_weight_value)
                if initial_weight_value is not None and initial_weight_value != ""
                else 70000
            )
        except (TypeError, ValueError, AttributeError):
            weight_kg = 70.0
            target_wt = 65000.0
            current_wt = 70000.0

        if target_wt < current_wt:
            # 减重时期取更高蛋白质比例
            protein_per_kg = 2.2
        else:
            # 维持或增重时期蛋白质比例
            protein_per_kg = 1.8

        protein_g = weight_kg * protein_per_kg
        protein_calories = protein_g * 4

        # 脂肪: 20-35% 总热量
        fat_percentage = 0.25  # 25%
        fat_calories = target_calories * fat_percentage
        fat_g = fat_calories / 9

        # 碳水化合物: 剩余热量
        carb_calories = target_calories - protein_calories - fat_calories
        carb_g = carb_calories / 4

        return {
            "protein_g": round(protein_g, 1),
            "fat_g": round(fat_g, 1),
            "carb_g": round(carb_g, 1),
            "protein_percentage": round((protein_calories / target_calories) * 100, 1),
            "fat_percentage": round((fat_calories / target_calories) * 100, 1),
            "carb_percentage": round((carb_calories / target_calories) * 100, 1),
        }

    def get_dietary_recommendations(self, user: User) -> Dict[str, any]:
        """获取饮食建议"""
        try:
            calorie_targets = self.calculate_calorie_target(user)
            target_calories = calorie_targets.get(
                "target", calorie_targets["maintenance"]
            )
            macros = self.calculate_macronutrients(user, target_calories)

            # 安全获取饮食偏好，处理None值
            dietary_preferences_raw = getattr(user, "dietary_preferences", "")
            dietary_prefs = (
                dietary_preferences_raw.split(",") if dietary_preferences_raw else []
            )

            meal_suggestions = self._generate_meal_suggestions(
                target_calories, macros, dietary_prefs
            )

            return {
                "calorie_targets": calorie_targets,
                "macronutrients": macros,
                "meal_suggestions": meal_suggestions,
                "hydration_goal": self._calculate_hydration_goal(user),
                "supplement_recommendations": self._get_supplement_recommendations(
                    user
                ),
            }
        except Exception as e:
            logger.error(f"Error getting dietary recommendations: {str(e)}")
            # 返回安全默认值以防止整个功能崩溃
            return {
                "calorie_targets": {
                    "maintenance": 2000.0,
                    "target": 1800.0,
                    "weight_loss": 1700.0,
                    "weight_gain": 2300.0,
                    "weight_difference_kg": 0.0,
                },
                "macronutrients": {
                    "protein_g": 150.0,
                    "fat_g": 50.0,
                    "carb_g": 200.0,
                    "protein_percentage": 25.0,
                    "fat_percentage": 25.0,
                    "carb_percentage": 50.0,
                },
                "meal_suggestions": {
                    "breakfast": [
                        {
                            "name": "默认早餐",
                            "description": "燕麦片配牛奶和水果",
                            "calories": 350,
                            "protein": 15,
                            "fat": 10,
                            "carb": 45,
                        }
                    ],
                    "lunch": [
                        {
                            "name": "默认午餐",
                            "description": "三明治配沙拉",
                            "calories": 450,
                            "protein": 25,
                            "fat": 15,
                            "carb": 50,
                        }
                    ],
                    "dinner": [
                        {
                            "name": "默认晚餐",
                            "description": "烤鸡胸肉配蔬菜",
                            "calories": 400,
                            "protein": 30,
                            "fat": 12,
                            "carb": 35,
                        }
                    ],
                    "snack": [
                        {
                            "name": "默认加餐",
                            "description": "希腊酸奶配坚果",
                            "calories": 200,
                            "protein": 15,
                            "fat": 12,
                            "carb": 15,
                        }
                    ],
                },
                "hydration_goal": 2450.0,
                "supplement_recommendations": ["维生素D: 1000-2000 IU/天"],
            }

    def _generate_meal_suggestions(
        self, target_calories: float, macros: Dict[str, float], dietary_prefs: List[str]
    ) -> Dict[str, List[Dict]]:
        """生成餐食建议"""
        try:
            # 分配每餐热量 (早餐25%, 午餐35%, 晚餐30%, 加餐10%)
            meal_distribution = {
                "breakfast": 0.25,
                "lunch": 0.35,
                "dinner": 0.30,
                "snack": 0.10,
            }

            suggestions = {}
            for meal, percentage in meal_distribution.items():
                meal_calories = target_calories * percentage
                meal_protein = macros["protein_g"] * percentage
                meal_fat = macros["fat_g"] * percentage
                meal_carb = macros["carb_g"] * percentage

                suggestions[meal] = self._get_meal_options(
                    meal,
                    meal_calories,
                    meal_protein,
                    meal_fat,
                    meal_carb,
                    dietary_prefs,
                )

            return suggestions
        except Exception as e:
            logger.error(f"Error generating meal suggestions: {str(e)}")
            # 返回默认餐食建议
            return {
                "breakfast": [
                    {
                        "name": "默认早餐",
                        "description": "燕麦片配牛奶和水果",
                        "calories": 350,
                        "protein": 15,
                        "fat": 10,
                        "carb": 45,
                    }
                ],
                "lunch": [
                    {
                        "name": "默认午餐",
                        "description": "三明治配沙拉",
                        "calories": 450,
                        "protein": 25,
                        "fat": 15,
                        "carb": 50,
                    }
                ],
                "dinner": [
                    {
                        "name": "默认晚餐",
                        "description": "烤鸡胸肉配蔬菜",
                        "calories": 400,
                        "protein": 30,
                        "fat": 12,
                        "carb": 35,
                    }
                ],
                "snack": [
                    {
                        "name": "默认加餐",
                        "description": "希腊酸奶配坚果",
                        "calories": 200,
                        "protein": 15,
                        "fat": 12,
                        "carb": 15,
                    }
                ],
            }

    def _get_meal_options(
        self,
        meal_type: str,
        calories: float,
        protein: float,
        fat: float,
        carb: float,
        dietary_prefs: List[str],
    ) -> List[Dict]:
        """获取餐食选项"""
        # 简化版餐食建议
        options = []

        if meal_type == "breakfast":
            options = [
                {
                    "name": "燕麦粥配坚果和水果",
                    "description": "50g燕麦片，20g坚果，100g水果",
                    "calories": 350,
                    "protein": 12,
                    "fat": 15,
                    "carb": 45,
                },
                {
                    "name": "鸡蛋蔬菜卷",
                    "description": "2个鸡蛋，全麦饼，蔬菜",
                    "calories": 300,
                    "protein": 20,
                    "fat": 12,
                    "carb": 25,
                },
            ]
        elif meal_type == "lunch":
            options = [
                {
                    "name": "鸡胸肉沙拉",
                    "description": "150g鸡胸肉，混合蔬菜，橄榄油酱",
                    "calories": 450,
                    "protein": 35,
                    "fat": 20,
                    "carb": 25,
                },
                {
                    "name": "三文鱼糙米饭",
                    "description": "120g三文鱼，100g糙米，蔬菜",
                    "calories": 500,
                    "protein": 30,
                    "fat": 22,
                    "carb": 45,
                },
            ]
        elif meal_type == "dinner":
            options = [
                {
                    "name": "烤蔬菜配豆腐",
                    "description": "200g豆腐，混合烤蔬菜",
                    "calories": 400,
                    "protein": 25,
                    "fat": 15,
                    "carb": 35,
                },
                {
                    "name": "瘦牛肉配红薯",
                    "description": "120g瘦牛肉，150g红薯，西兰花",
                    "calories": 450,
                    "protein": 30,
                    "fat": 18,
                    "carb": 40,
                },
            ]
        else:  # snack
            options = [
                {
                    "name": "希腊酸奶配莓果",
                    "description": "150g希腊酸奶，50g混合莓果",
                    "calories": 150,
                    "protein": 15,
                    "fat": 5,
                    "carb": 15,
                },
                {
                    "name": "坚果和水果",
                    "description": "30g混合坚果，1个苹果",
                    "calories": 200,
                    "protein": 6,
                    "fat": 15,
                    "carb": 20,
                },
            ]

        # 根据饮食偏好过滤
        filtered_options = []
        for option in options:
            if self._is_option_compatible(option, dietary_prefs):
                filtered_options.append(option)

        return filtered_options[:2]  # 返回前2个选项

    def _is_option_compatible(self, option: Dict, dietary_prefs: List[str]) -> bool:
        """检查餐食选项是否与饮食偏好兼容"""
        if not dietary_prefs:
            return True

        # 简化兼容性检查
        incompatible_map = {
            "vegetarian": ["鸡胸肉", "三文鱼", "瘦牛肉"],
            "vegan": ["鸡蛋", "鸡胸肉", "三文鱼", "瘦牛肉", "希腊酸奶", "豆腐"],
            "gluten_free": ["燕麦片", "全麦饼"],
            "dairy_free": ["希腊酸奶"],
        }

        for pref in dietary_prefs:
            incompatible_items = incompatible_map.get(pref, [])
            for item in incompatible_items:
                if item in option["description"]:
                    return False

        return True

    def _calculate_hydration_goal(self, user: User) -> float:
        """计算每日饮水目标 (毫升)"""
        # 先获取并验证用户的体重数据
        try:
            initial_weight = user.initial_weight
            weight_kg = (
                float(initial_weight) / 1000.0
                if initial_weight is not None and initial_weight != ""
                else 70.0
            )
            # 30-35 ml/kg 体重
            hydration_ml = weight_kg * 35
            return round(hydration_ml, 0)
        except (TypeError, ValueError, AttributeError):
            # 如果数值有问题使用默认值
            return 2450.0  # 70kg * 35ml/kg

    def _get_supplement_recommendations(self, user: User) -> List[str]:
        """获取补充剂建议"""
        try:
            recommendations = []

            # 基础补充剂
            recommendations.append("维生素D: 1000-2000 IU/天 (尤其日照不足时)")

            # 安全地访问用户属性
            user_gender = getattr(user, "gender", None)
            user_age = getattr(user, "age", None)
            dietary_prefs = getattr(user, "dietary_preferences", "")

            if user_gender == "female" and user_age and user_age > 50:
                recommendations.append("钙: 1200 mg/天 (预防骨质疏松)")

            if "vegetarian" in dietary_prefs or "vegan" in dietary_prefs:
                recommendations.append("维生素B12: 2.4 mcg/天")
                recommendations.append("铁: 注意补充植物性铁源")

            return recommendations
        except Exception as e:
            logger.error(f"Error getting supplement recommendation: {str(e)}")
            # 返回安全的默认推荐
            return ["维生素D: 1000-2000 IU/天 (尤其日照不足时)"]

    def analyze_food_log(self, food_items: List[Dict]) -> Dict[str, any]:
        """分析食物日志"""
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carb = 0

        for item in food_items:
            total_calories += item.get("calories", 0)
            total_protein += item.get("protein", 0)
            total_fat += item.get("fat", 0)
            total_carb += item.get("carb", 0)

        return {
            "total": {
                "calories": round(total_calories, 1),
                "protein_g": round(total_protein, 1),
                "fat_g": round(total_fat, 1),
                "carb_g": round(total_carb, 1),
            },
            "meal_distribution": self._analyze_meal_distribution(food_items),
            "nutrition_score": self._calculate_nutrition_score(
                total_calories, total_protein, total_fat, total_carb
            ),
        }

    def _analyze_meal_distribution(self, food_items: List[Dict]) -> Dict[str, float]:
        """分析餐食分布"""
        meal_totals = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}
        total_calories = sum(item.get("calories", 0) for item in food_items)

        if total_calories == 0:
            return {meal: 0 for meal in meal_totals}

        for item in food_items:
            meal_type = item.get("meal_type", "unknown")
            if meal_type in meal_totals:
                meal_totals[meal_type] += item.get("calories", 0)

        return {
            meal: round((calories / total_calories) * 100, 1)
            for meal, calories in meal_totals.items()
        }

    def _calculate_nutrition_score(
        self, calories: float, protein: float, fat: float, carb: float
    ) -> int:
        """计算营养评分 (0-100)"""
        score = 70  # 基础分

        # 蛋白质评分 (目标: 至少50g)
        if protein >= 50:
            score += 10
        elif protein >= 30:
            score += 5

        # 脂肪评分 (目标: 20-80g)
        if 20 <= fat <= 80:
            score += 10
        elif 10 <= fat <= 100:
            score += 5

        # 碳水化合物评分 (目标: 150-300g)
        if 150 <= carb <= 300:
            score += 10
        elif 100 <= carb <= 350:
            score += 5

        return min(100, score)


def get_nutrition_service(db: Session) -> NutritionService:
    """获取营养服务实例"""
    return NutritionService(db)
