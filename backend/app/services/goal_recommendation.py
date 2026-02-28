"""
目标推荐服务
Story 2.1: 目标数据模型设计 - AI 推荐逻辑
提供基于用户健康数据的智能目标推荐
"""

from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
from enum import Enum


class ActivityLevel(str, Enum):
    """活动水平枚举"""

    SEDENTARY = "sedentary"  # 久坐
    LIGHT = "light"  # 轻度活动
    MODERATE = "moderate"  # 中度活动
    ACTIVE = "active"  # 高度活动


class GoalType(str, Enum):
    """目标类型枚举"""

    WEIGHT = "weight"  # 体重目标
    EXERCISE = "exercise"  # 运动目标
    DIET = "diet"  # 饮食目标
    HABIT = "habit"  # 习惯目标


class DietGoalType(str, Enum):
    """饮食目标类型"""

    LOSE = "lose"  # 减重
    MAINTAIN = "maintain"  # 维持
    GAIN = "gain"  # 增重


class GoalRecommendationService:
    """
    AI 驱动的目标推荐服务
    基于用户的健康数据计算科学合理的个性化目标建议
    """

    # 步数目标配置
    STEP_TARGETS = {
        ActivityLevel.SEDENTARY: 5000,
        ActivityLevel.LIGHT: 7000,
        ActivityLevel.MODERATE: 10000,
        ActivityLevel.ACTIVE: 12000,
    }

    # 每周运动分钟数配置
    WEEKLY_EXERCISE_MINUTES = {
        ActivityLevel.SEDENTARY: 90,
        ActivityLevel.LIGHT: 150,
        ActivityLevel.MODERATE: 225,
        ActivityLevel.ACTIVE: 300,
    }

    # 活动系数 (用于 TDEE 计算)
    ACTIVITY_MULTIPLIERS = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.ACTIVE: 1.725,
    }

    # 热量调整配置
    CALORIE_ADJUSTMENTS = {
        DietGoalType.LOSE: -400,  # 减重: 每天减少 400 kcal
        DietGoalType.MAINTAIN: 0,  # 维持
        DietGoalType.GAIN: 300,  # 增重: 每天增加 300 kcal
    }

    # 宏量营养素比例 (蛋白质/碳水/脂肪)
    MACRO_RATIOS = {
        "protein": 0.30,  # 30% 热量来自蛋白质
        "carbs": 0.40,  # 40% 热量来自碳水
        "fat": 0.30,  # 30% 热量来自脂肪
    }

    def calculate_weight_goal(
        self,
        height_cm: float,
        current_weight_g: float,
        target_weight_g: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        计算体重目标推荐

        基于健康 BMI (18.5-24) 计算推荐范围

        Args:
            height_cm: 身高 (厘米)
            current_weight_g: 当前体重 (克)
            target_weight_g: 目标体重 (克, 可选)

        Returns:
            包含推荐范围、当前 BMI、安全减重速度等信息的字典
        """
        height_m = height_cm / 100
        current_weight_kg = current_weight_g / 1000

        # 计算当前 BMI
        current_bmi = current_weight_kg / (height_m**2)

        # 计算健康体重范围 (BMI 18.5-24)
        min_weight_kg = 18.5 * height_m**2
        max_weight_kg = 24 * height_m**2
        ideal_weight_kg = 22 * height_m**2  # 最优 BMI

        # 转换为克
        min_weight_g = min_weight_kg * 1000
        max_weight_g = max_weight_kg * 1000
        ideal_weight_g = ideal_weight_kg * 1000

        # 每周安全减重范围 (0.5-1kg)
        weekly_safe_loss_min_g = 500
        weekly_safe_loss_max_g = 1000

        # 计算推荐的目标体重 (如果没有提供)
        if target_weight_g is None:
            if current_bmi > 24:
                # 当前超重，建议达到健康范围
                recommended_target_g = min_weight_g
            elif current_bmi < 18.5:
                # 当前偏瘦，建议达到健康范围
                recommended_target_g = min_weight_g
            else:
                # 当前在健康范围，建议维持或轻微调整
                recommended_target_g = ideal_weight_g
        else:
            recommended_target_g = target_weight_g

        # 计算预计达成时间 (假设每周减重 0.5kg)
        days_to_goal = None
        if recommended_target_g and recommended_target_g != current_weight_g:
            weight_diff_g = abs(current_weight_g - recommended_target_g)
            weeks_needed = weight_diff_g / 600000  # 假设每周减重 600g
            days_to_goal = int(weeks_needed * 7)

        # 生成推荐理由
        reasoning = self._generate_weight_reasoning(
            current_bmi, current_weight_kg, ideal_weight_kg
        )

        return {
            "recommended_range": {
                "min_g": min_weight_g,
                "max_g": max_weight_g,
                "min_kg": min_weight_kg,
                "max_kg": max_weight_kg,
            },
            "recommended_target_g": recommended_target_g,
            "ideal_g": ideal_weight_g,
            "ideal_kg": ideal_weight_kg,
            "current_bmi": round(current_bmi, 1),
            "bmi_category": self._get_bmi_category(current_bmi),
            "weekly_safe_loss_g": {
                "min": weekly_safe_loss_min_g,
                "max": weekly_safe_loss_max_g,
            },
            "estimated_days_to_goal": days_to_goal,
            "reasoning": reasoning,
        }

    def calculate_exercise_goal(
        self,
        activity_level: str,
        current_steps: Optional[int] = None,
        goal_type: str = "steps",  # steps / exercise_minutes
    ) -> Dict[str, Any]:
        """
        计算运动目标推荐

        基于用户的活动水平推荐合适的运动目标

        Args:
            activity_level: 活动水平 (sedentary/light/moderate/active)
            current_steps: 当前步数 (可选)
            goal_type: 目标类型 (steps / exercise_minutes)

        Returns:
            包含步数目标、每周运动时间等信息的字典
        """
        level = ActivityLevel(activity_level.lower())

        # 获取步数目标
        daily_steps = self.STEP_TARGETS.get(level, 7000)
        weekly_exercise_minutes = self.WEEKLY_EXERCISE_MINUTES.get(level, 150)
        daily_exercise_minutes = weekly_exercise_minutes / 5  # 假设每周运动 5 天

        # 计算推荐理由
        reasoning = self._generate_exercise_reasoning(level, daily_steps)

        result = {
            "daily_steps": daily_steps,
            "weekly_steps": daily_steps * 7,
            "daily_exercise_minutes": daily_exercise_minutes,
            "weekly_exercise_minutes": weekly_exercise_minutes,
            "activity_level": level.value,
            "reasoning": reasoning,
        }

        # 如果提供了当前步数，计算进度
        if current_steps is not None:
            progress_percentage = min(100, (current_steps / daily_steps) * 100)
            result["current_steps"] = current_steps
            result["progress_percentage"] = round(progress_percentage, 1)

            if current_steps < daily_steps:
                steps_remaining = daily_steps - current_steps
                result["steps_remaining"] = steps_remaining
                result["encouragement"] = (
                    f"再走 {steps_remaining} 步就能达成今日目标啦！"
                )
            else:
                result["encouragement"] = "太棒了！今日步数目标已达成！"

        return result

    def calculate_diet_goal(
        self,
        weight_g: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str,
        diet_goal_type: str = "lose",  # lose/maintain/gain
    ) -> Dict[str, Any]:
        """
        计算饮食目标推荐

        基于 BMR (基础代谢率) 和活动水平计算每日热量目标

        Args:
            weight_g: 体重 (克)
            height_cm: 身高 (厘米)
            age: 年龄
            gender: 性别 (male/female)
            activity_level: 活动水平
            diet_goal_type: 饮食目标类型 (lose/maintain/gain)

        Returns:
            包含 BMR、TDEE、目标热量、宏量营养素等信息的字典
        """
        weight_kg = weight_g / 1000
        level = ActivityLevel(activity_level.lower())

        # 计算基础代谢率 (BMR)
        # Mifflin-St Jeor 公式
        if gender.lower() == "male":
            bmr = weight_kg * 10 + height_cm * 6.25 - age * 5 + 5
        else:
            bmr = weight_kg * 10 + height_cm * 6.25 - age * 5 - 161

        # 计算总日常能量消耗 (TDEE)
        multiplier = self.ACTIVITY_MULTIPLIERS.get(level, 1.2)
        tdee = bmr * multiplier

        # 计算目标热量
        adjustment = self.CALORIE_ADJUSTMENTS.get(
            DietGoalType(diet_goal_type.lower()), 0
        )
        target_calories = tdee + adjustment

        # 计算宏量营养素 (克)
        protein_g = (
            target_calories * self.MACRO_RATIOS["protein"]
        ) / 4  # 1g 蛋白质 = 4 kcal
        carbs_g = (target_calories * self.MACRO_RATIOS["carbs"]) / 4  # 1g 碳水 = 4 kcal
        fat_g = (target_calories * self.MACRO_RATIOS["fat"]) / 9  # 1g 脂肪 = 9 kcal

        # 生成推荐理由
        reasoning = self._generate_diet_reasoning(
            bmr, tdee, target_calories, diet_goal_type
        )

        return {
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "target_calories": round(target_calories, 0),
            "calorie_adjustment": adjustment,
            "diet_goal_type": diet_goal_type,
            "activity_level": level.value,
            "macros": {
                "protein_g": round(protein_g, 0),
                "carbs_g": round(carbs_g, 0),
                "fat_g": round(fat_g, 0),
            },
            "meal_breakdown": {
                "breakfast": round(target_calories * 0.25, 0),
                "lunch": round(target_calories * 0.35, 0),
                "dinner": round(target_calories * 0.30, 0),
                "snacks": round(target_calories * 0.10, 0),
            },
            "reasoning": reasoning,
        }

    def calculate_habit_goals(
        self,
        weight_g: float,
        current_water_ml: Optional[int] = None,
        current_sleep_hours: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        计算习惯目标推荐

        基于体重计算每日饮水、睡眠等习惯目标

        Args:
            weight_g: 体重 (克)
            current_water_ml: 当前每日饮水量 (毫升, 可选)
            current_sleep_hours: 当前每日睡眠时长 (小时, 可选)

        Returns:
            包含饮水、睡眠、如厕等习惯目标的字典
        """
        weight_kg = weight_g / 1000

        # 饮水目标: 体重(kg) × 30-35 ml
        water_per_kg = 33
        daily_water_ml = int(weight_kg * water_per_kg)

        # 睡眠目标: 7-8 小时
        daily_sleep_hours = 7.5

        # 如厕目标: 1-2 次/天
        daily_defecation = 1

        # 生成推荐理由
        reasoning = self._generate_habit_reasoning(weight_kg)

        result = {
            "water_ml": daily_water_ml,
            "water_glasses": round(daily_water_ml / 250, 1),  # 假设每杯 250ml
            "sleep_hours": daily_sleep_hours,
            "defecation_per_day": daily_defecation,
            "reasoning": reasoning,
        }

        # 如果提供了当前数据，计算进度
        if current_water_ml is not None:
            water_progress = min(100, (current_water_ml / daily_water_ml) * 100)
            result["current_water_ml"] = current_water_ml
            result["water_progress_percentage"] = round(water_progress, 1)

        if current_sleep_hours is not None:
            sleep_progress = min(100, (current_sleep_hours / daily_sleep_hours) * 100)
            result["current_sleep_hours"] = current_sleep_hours
            result["sleep_progress_percentage"] = round(sleep_progress, 1)

        return result

    def predict_completion_date(
        self,
        current_value: float,
        target_value: float,
        goal_type: str,
        daily_progress: Optional[float] = None,
        recent_progress_list: Optional[list] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        预测目标完成日期

        Args:
            current_value: 当前值
            target_value: 目标值
            goal_type: 目标类型 (weight/exercise/diet/habit)
            daily_progress: 每日进步量 (可选)
            recent_progress_list: 最近进度列表，用于计算平均进步 (可选)

        Returns:
            包含预测日期、预计天数等信息的字典
        """
        # 计算需要达成的差值
        if goal_type in ["weight", "diet"]:
            # 减重/减脂目标: current > target
            remaining = current_value - target_value
            is_decreasing = True
        else:
            # 增肌/运动目标: current < target
            remaining = target_value - current_value
            is_decreasing = False

        if remaining <= 0:
            # 目标已达成
            return {
                "predicted_date": datetime.now().isoformat(),
                "days_remaining": 0,
                "is_achieved": True,
                "reasoning": "目标已达成！",
            }

        # 计算每日平均进步量
        if daily_progress is not None and daily_progress > 0:
            avg_daily_progress = daily_progress
        elif recent_progress_list and len(recent_progress_list) > 0:
            # 计算最近进度的平均值
            avg_daily_progress = sum(recent_progress_list) / len(recent_progress_list)
        else:
            # 使用默认值
            avg_daily_progress = self._get_default_daily_progress(goal_type)

        if avg_daily_progress <= 0:
            return None

        # 计算需要的天数
        days_needed = remaining / avg_daily_progress

        # 考虑平台期调整 (每 2 周休息 1 天)
        platform_buffer = days_needed / 14

        total_days = int(days_needed + platform_buffer)

        predicted_date = datetime.now() + timedelta(days=total_days)

        return {
            "predicted_date": predicted_date.isoformat(),
            "days_remaining": total_days,
            "is_achieved": False,
            "avg_daily_progress": avg_daily_progress,
            "reasoning": f"按当前进度，预计 {total_days} 天后达成目标",
        }

    def get_all_recommendations(
        self,
        user_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        获取用户的所有目标推荐

        Args:
            user_profile: 用户资料字典，需包含:
                - height: 身高 (厘米)
                - current_weight: 当前体重 (克)
                - age: 年龄
                - gender: 性别
                - activity_level: 活动水平

        Returns:
            包含所有类型目标推荐的字典
        """
        recommendations = {}

        # 基础数据
        height = user_profile.get("height")
        weight = user_profile.get("current_weight")
        age = user_profile.get("age")
        gender = user_profile.get("gender", "male")
        activity_level = user_profile.get("activity_level", "moderate")

        if height and weight:
            # 体重目标
            recommendations["weight"] = self.calculate_weight_goal(
                height_cm=height,
                current_weight_g=weight,
            )

        if activity_level:
            # 运动目标
            current_steps = user_profile.get("current_steps")
            recommendations["exercise"] = self.calculate_exercise_goal(
                activity_level=activity_level,
                current_steps=current_steps,
            )

        if height and weight and age and gender:
            # 饮食目标
            diet_goal = user_profile.get("diet_goal", "lose")
            recommendations["diet"] = self.calculate_diet_goal(
                weight_g=weight,
                height_cm=height,
                age=age,
                gender=gender,
                activity_level=activity_level,
                diet_goal_type=diet_goal,
            )

        if weight:
            # 习惯目标
            current_water = user_profile.get("current_water_ml")
            current_sleep = user_profile.get("current_sleep_hours")
            recommendations["habit"] = self.calculate_habit_goals(
                weight_g=weight,
                current_water_ml=current_water,
                current_sleep_hours=current_sleep,
            )

        return recommendations

    # ==================== 私有方法 ====================

    def _get_bmi_category(self, bmi: float) -> str:
        """获取 BMI 分类"""
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"

    def _generate_weight_reasoning(
        self,
        current_bmi: float,
        current_weight_kg: float,
        ideal_weight_kg: float,
    ) -> str:
        """生成体重目标推荐理由"""
        if current_bmi < 18.5:
            return f"当前 BMI {current_bmi:.1f} 偏瘦，建议增重到 {ideal_weight_kg:.1f}kg 以达到健康范围"
        elif current_bmi > 24:
            diff = current_weight_kg - ideal_weight_kg
            return (
                f"当前 BMI {current_bmi:.1f} 超重，建议减重 {diff:.1f}kg 以达到健康范围"
            )
        else:
            return f"当前 BMI {current_bmi:.1f} 在正常范围，建议维持体重在 {ideal_weight_kg:.1f}kg 左右"

    def _generate_exercise_reasoning(
        self,
        activity_level: ActivityLevel,
        daily_steps: int,
    ) -> str:
        """生成运动目标推荐理由"""
        level_descriptions = {
            ActivityLevel.SEDENTARY: "久坐",
            ActivityLevel.LIGHT: "轻度活动",
            ActivityLevel.MODERATE: "中度活动",
            ActivityLevel.ACTIVE: "高度活动",
        }

        desc = level_descriptions.get(activity_level, "普通")
        return (
            f"根据您的活动水平 ({desc})，建议每天 {daily_steps:,} 步，保持健康生活方式"
        )

    def _generate_diet_reasoning(
        self,
        bmr: float,
        tdee: float,
        target_calories: float,
        diet_goal_type: str,
    ) -> str:
        """生成饮食目标推荐理由"""
        if diet_goal_type == "lose":
            return f"您的 BMR 是 {bmr:.0f} kcal，TDEE 是 {tdee:.0f} kcal。建议每日摄入 {target_calories:.0f} kcal 以健康减重"
        elif diet_goal_type == "gain":
            return f"您的 BMR 是 {bmr:.0f} kcal，TDEE 是 {tdee:.0f} kcal。建议每日摄入 {target_calories:.0f} kcal 以健康增重"
        else:
            return f"您的 BMR 是 {bmr:.0f} kcal，TDEE 是 {tdee:.0f} kcal。建议每日摄入 {target_calories:.0f} kcal 以维持当前体重"

    def _generate_habit_reasoning(self, weight_kg: float) -> str:
        """生成习惯目标推荐理由"""
        water_ml = int(weight_kg * 33)
        return f"根据您的体重 {weight_kg:.1f}kg，建议每天饮水 {water_ml}ml，保持 7-8 小时睡眠"

    def _get_default_daily_progress(self, goal_type: str) -> float:
        """获取默认每日进步量"""
        defaults = {
            "weight": 500,  # 500g/天 (假设减重)
            "exercise": 1000,  # 1000 步/天
            "diet": 100,  # 100 kcal/天
            "habit": 250,  # 250ml/天 (饮水)
        }
        return defaults.get(goal_type, 100)
