from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.nutrition import Meal
from app.models.exercise_checkin import ExerciseCheckIn
from app.services.nutrition_service import NutritionService

router = APIRouter()


class CalorieBalanceResponse(BaseModel):
    """热量平衡响应模型"""

    date: str
    intake: float  # 摄入热量
    bmr: float  # 基础代谢
    burn: float  # 运动消耗
    surplus: float  # 盈余 (摄入 - BMR - 运动)
    net: float  # 净消耗 (BMR + 运动 - 摄入)
    progress: float  # 进度百分比
    target: float  # 目标摄入 (BMR)


def get_daily_calorie_intake(db: Session, user_id: int, target_date: date) -> float:
    """
    获取指定日期的每日摄入热量

    Args:
        db: 数据库会话
        user_id: 用户ID
        target_date: 目标日期

    Returns:
        当日摄入热量总和
    """
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == user_id,
            Meal.meal_datetime >= start_datetime,
            Meal.meal_datetime < end_datetime,
        )
        .all()
    )

    return round(sum(meal.calories or 0 for meal in meals), 1)


def get_daily_exercise_burn(db: Session, user_id: int, target_date: date) -> float:
    """
    获取指定日期的运动消耗热量

    Args:
        db: 数据库会话
        user_id: 用户ID
        target_date: 目标日期

    Returns:
        当日运动消耗热量总和
    """
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    exercises = (
        db.query(ExerciseCheckIn)
        .filter(
            ExerciseCheckIn.user_id == user_id,
            ExerciseCheckIn.started_at >= start_datetime,
            ExerciseCheckIn.started_at < end_datetime,
        )
        .all()
    )

    return round(sum(exercise.calories_burned or 0 for exercise in exercises), 1)


@router.get("/calorie-balance", response_model=CalorieBalanceResponse)
def get_calorie_balance(
    date_str: Optional[str] = Query(
        None, description="日期 (YYYY-MM-DD格式，默认今天)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalorieBalanceResponse:
    """
    获取热量平衡数据

    返回三栏热量数据:
    - intake: 今日摄入热量 (from meals)
    - bmr: 基础代谢 BMR (calculated from profile)
    - burn: 运动消耗 (from exercise_checkins)
    - surplus: 热量盈余 = 摄入 - 基础代谢 - 运动消耗
    - net: 净消耗 = 基础代谢 + 运动消耗 - 摄入
    - progress: 进度百分比 (摄入/BMR * 100)
    - target: 目标摄入 (= BMR)

    热量平衡说明:
    - surplus > 0: 热量盈余 (摄入 > 消耗)
    - surplus < 0: 热量缺口 (消耗 > 摄入)
    """
    # 解析日期
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    # 1. 获取摄入热量
    intake = get_daily_calorie_intake(db, current_user.id, target_date)

    # 2. 计算基础代谢 BMR
    nutrition_service = NutritionService(db)
    bmr = nutrition_service.calculate_bmr(current_user)

    # 3. 获取运动消耗
    burn = get_daily_exercise_burn(db, current_user.id, target_date)

    # 4. 计算热量盈余
    # surplus = 摄入 - 基础代谢 - 运动消耗
    # 正值表示盈余(摄入过多), 负值表示缺口(有利于减脂)
    surplus = round(intake - bmr - burn, 1)

    # 5. 计算净消耗
    # net = 基础代谢 + 运动消耗 - 摄入
    # 正值表示净消耗, 负值表示净存储
    net = round(bmr + burn - intake, 1)

    # 6. 计算进度百分比
    # 相对于BMR的进度
    if bmr > 0:
        progress = round((intake / bmr) * 100, 1)
    else:
        progress = 0.0

    # 限制进度最大为200%
    progress = min(200.0, progress)

    return CalorieBalanceResponse(
        date=target_date.isoformat(),
        intake=intake,
        bmr=round(bmr, 1),
        burn=burn,
        surplus=surplus,
        net=net,
        progress=progress,
        target=round(bmr, 1),
    )


@router.get("/calorie-balance/history")
def get_calorie_balance_history(
    days: int = Query(7, ge=1, le=30, description="历史天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    获取热量平衡历史数据

    返回指定天数的热量平衡历史记录,用于趋势图展示
    """
    today = date.today()
    history = []

    for i in range(days):
        target_date = today - timedelta(days=i)

        # 获取各数据
        intake = get_daily_calorie_intake(db, current_user.id, target_date)

        nutrition_service = NutritionService(db)
        bmr = nutrition_service.calculate_bmr(current_user)

        burn = get_daily_exercise_burn(db, current_user.id, target_date)

        surplus = round(intake - bmr - burn, 1)

        history.append(
            {
                "date": target_date.isoformat(),
                "intake": intake,
                "bmr": round(bmr, 1),
                "burn": burn,
                "surplus": surplus,
            }
        )

    # 反转列表,让最早的在前面
    history.reverse()

    return {
        "history": history,
        "days": days,
    }
