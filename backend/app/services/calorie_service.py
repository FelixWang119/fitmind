from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any

import structlog
from sqlalchemy.orm import Session

from app.models.calorie_goal import CalorieGoal
from app.models.nutrition import Meal
from app.models.user import User
from app.services.nutrition_service import NutritionService

logger = structlog.get_logger(__name__)


class CalorieService:
    """热量计算服务"""

    def __init__(self, db: Session):
        self.db = db
        self.nutrition_service = NutritionService(db)

    def get_calorie_goal(
        self, user_id: int, target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        获取用户指定日期的热量目标

        Args:
            user_id: 用户ID
            target_date: 目标日期，默认今天

        Returns:
            热量目标字典
        """
        if target_date is None:
            target_date = date.today()

        # 尝试从数据库获取自定义目标
        goal = (
            self.db.query(CalorieGoal)
            .filter(
                CalorieGoal.user_id == user_id,
                CalorieGoal.goal_date == target_date,
            )
            .first()
        )

        if goal:
            return {
                "calories": goal.target_calories,
                "protein": goal.target_protein,
                "carbs": goal.target_carbs,
                "fat": goal.target_fat,
                "is_auto_calculated": goal.is_auto_calculated,
                "source": "custom",
            }

        # 如果没有自定义目标，自动计算
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            auto_goals = self.nutrition_service.calculate_calorie_target(user)
            macros = self.nutrition_service.calculate_macronutrients(
                user, auto_goals["target"]
            )
            return {
                "calories": int(auto_goals["target"]),
                "protein": int(macros["protein_g"]),
                "carbs": int(macros["carb_g"]),
                "fat": int(macros["fat_g"]),
                "is_auto_calculated": True,
                "source": "auto",
            }

        # 默认值
        return {
            "calories": 2000,
            "protein": 50,
            "carbs": 250,
            "fat": 65,
            "is_auto_calculated": True,
            "source": "default",
        }

    def set_calorie_goal(
        self,
        user_id: int,
        goal_data: Dict[str, Any],
        target_date: Optional[date] = None,
    ) -> CalorieGoal:
        """
        设置用户热量目标

        Args:
            user_id: 用户ID
            goal_data: 目标数据
            target_date: 目标日期

        Returns:
            创建/更新的 CalorieGoal 对象
        """
        if target_date is None:
            target_date = date.today()

        # 查找是否已存在
        goal = (
            self.db.query(CalorieGoal)
            .filter(
                CalorieGoal.user_id == user_id,
                CalorieGoal.goal_date == target_date,
            )
            .first()
        )

        if goal:
            # 更新现有目标
            if "target_calories" in goal_data:
                goal.target_calories = goal_data["target_calories"]
            if "target_protein" in goal_data:
                goal.target_protein = goal_data["target_protein"]
            if "target_carbs" in goal_data:
                goal.target_carbs = goal_data["target_carbs"]
            if "target_fat" in goal_data:
                goal.target_fat = goal_data["target_fat"]
            goal.is_auto_calculated = False
        else:
            # 创建新目标
            goal = CalorieGoal(
                user_id=user_id,
                goal_date=target_date,
                target_calories=goal_data.get("target_calories", 2000),
                target_protein=goal_data.get("target_protein", 50),
                target_carbs=goal_data.get("target_carbs", 250),
                target_fat=goal_data.get("target_fat", 65),
                is_auto_calculated=False,
            )
            self.db.add(goal)

        self.db.commit()
        self.db.refresh(goal)

        logger.info("Calorie goal set", user_id=user_id, date=target_date)
        return goal

    def calculate_daily_balance(
        self, user_id: int, target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        计算当日热量余额

        Args:
            user_id: 用户ID
            target_date: 目标日期，默认今天

        Returns:
            热量余额字典
        """
        if target_date is None:
            target_date = date.today()

        # 获取目标
        goal = self.get_calorie_goal(user_id, target_date)

        # 获取当日实际摄入
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)

        meals = (
            self.db.query(Meal)
            .filter(
                Meal.user_id == user_id,
                Meal.meal_datetime >= start_datetime,
                Meal.meal_datetime < end_datetime,
            )
            .all()
        )

        actual_calories = sum(meal.calories or 0 for meal in meals)
        actual_protein = sum(meal.protein or 0 for meal in meals)
        actual_carbs = sum(meal.carbs or 0 for meal in meals)
        actual_fat = sum(meal.fat or 0 for meal in meals)

        # 计算余额
        balance_calories = goal["calories"] - actual_calories
        balance_protein = goal["protein"] - actual_protein
        balance_carbs = goal["carbs"] - actual_carbs
        balance_fat = goal["fat"] - actual_fat

        # 计算状态
        if actual_calories == 0:
            status = "green"
        else:
            ratio = actual_calories / goal["calories"]
            if ratio < 0.7:
                status = "green"
            elif ratio <= 1.0:
                status = "yellow"
            else:
                status = "red"

        return {
            "date": target_date.isoformat(),
            "goal": goal,
            "actual": {
                "calories": actual_calories,
                "protein": actual_protein,
                "carbs": actual_carbs,
                "fat": actual_fat,
            },
            "balance": {
                "calories": balance_calories,
                "protein": balance_protein,
                "carbs": balance_carbs,
                "fat": balance_fat,
            },
            "status": status,  # green/yellow/red
            "meal_count": len(meals),
        }

    def recalculate_from_items(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        根据食材列表重新计算营养总量

        Args:
            items: 食材列表，每个食材包含 grams, calories, protein, carbs, fat

        Returns:
            重新计算后的营养总量
        """
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for item in items:
            # 获取该食材的克数（默认为100g）
            grams = float(item.get("grams", 100))
            # 基础营养是按100g计算的，需要按实际克数调整
            ratio = grams / 100.0

            total_calories += float(item.get("calories", 0)) * ratio
            total_protein += float(item.get("protein", 0)) * ratio
            total_carbs += float(item.get("carbs", 0)) * ratio
            total_fat += float(item.get("fat", 0)) * ratio

        return {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
        }


def get_calorie_service(db: Session) -> CalorieService:
    """获取热量服务实例"""
    return CalorieService(db)
