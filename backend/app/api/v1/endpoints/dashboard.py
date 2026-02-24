from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOverview, QuickStats
from app.services.ai_health_advisor import get_daily_tip

# Also import needed schemas for the new endpoints
from app.schemas.ai import AIHealthAdviceRequest, AIHealthAdviceResponse
from app.models.health_record import HealthRecord
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# F15: 导入运动打卡模型和 Schema
from app.models.exercise_checkin import ExerciseCheckIn
from app.schemas.exercise_checkin import DailySummaryResponse

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取仪表板概览数据
    """
    from app.services.dashboard_service import get_dashboard_overview

    return get_dashboard_overview(db, current_user)


@router.get("/quick-stats", response_model=QuickStats)
def get_quick_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取快速统计数据
    """
    from app.services.dashboard_service import get_quick_stats

    return get_quick_stats(db, current_user)


@router.get("/ai-suggestions")
def get_dashboard_ai_suggestions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    仪表板AI建议（重定向到主要AI健康建议端点）
    """
    # Reuse the daily tip functionality
    daily_tip = get_daily_tip()

    # Or get comprehensive health advice
    from app.services.ai_health_advisor import get_health_advice_from_ai

    try:
        advice_data = get_health_advice_from_ai(
            db=db,
            user_id=int(current_user.id),  # Convert SQLAlchemy column to int
            context={},
        )
        return {
            "suggestions": [advice_data] if advice_data else [],
            "tip_of_the_day": daily_tip,
        }
    except Exception:
        # Fallback if the main health advice fails
        return {"suggestions": [], "tip_of_the_day": daily_tip}


@router.get("/trends")
def get_dashboard_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取仪表板趋势数据
    """
    # From recent health records, extract weight trends and other metrics
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_weight_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.weight.isnot(None),
            HealthRecord.created_at >= seven_days_ago,
        )
        .order_by(HealthRecord.created_at)
        .all()
    )

    weight_trend_data = []
    if recent_weight_records:
        for record in recent_weight_records:
            weight_trend_data.append(
                {
                    "date": record.created_at.strftime("%Y-%m-%d")
                    if record.created_at
                    else "N/A",
                    "weight_kg": float(record.weight) / 1000.0
                    if record.weight
                    else 0.0,  # Convert grams to kg
                }
            )

    # Get habit completion rates
    from app.models.habit import Habit, HabitCompletion
    from sqlalchemy import and_

    active_habits = (
        db.query(Habit)
        .filter(and_(Habit.user_id == current_user.id, Habit.is_active == True))
        .count()
    )

    habit_completions_last_week = (
        db.query(HabitCompletion)
        .join(Habit, Habit.id == HabitCompletion.habit_id)
        .filter(
            Habit.user_id == current_user.id,
            HabitCompletion.completion_date >= seven_days_ago,
        )
        .count()
    )

    # Calculate expected completions
    expected_completions = active_habits * 7 if active_habits else 1  # 7 days
    completion_rate = (
        (habit_completions_last_week / expected_completions * 100)
        if expected_completions
        else 0
    )

    return {
        "period": "last_7_days",
        "weight_trend": {"data": weight_trend_data},
        "habit_trend": {
            "completion_rate": min(completion_rate, 100),  # Cap at 100%
            "actual_completions": habit_completions_last_week,
            "expected_completions": expected_completions,
            "active_habits": active_habits,
        },
    }


@router.get("/exercise-summary", response_model=DailySummaryResponse)
def get_exercise_summary(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    F15: 获取 Dashboard 运动摘要卡片数据

    返回当日运动数据用于 Dashboard 显示
    """
    from datetime import date as date_type

    # 解析日期
    if date:
        target_date = datetime.fromisoformat(date).date()
    else:
        target_date = datetime.utcnow().date()

    # 日期范围
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    # 聚合查询
    result = (
        db.query(
            func.sum(ExerciseCheckIn.duration_minutes).label("total_duration"),
            func.sum(ExerciseCheckIn.calories_burned).label("total_calories"),
            func.count(ExerciseCheckIn.id).label("sessions_count"),
            func.avg(ExerciseCheckIn.heart_rate_avg).label("avg_heart_rate"),
        )
        .filter(
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.started_at >= start_datetime,
            ExerciseCheckIn.started_at < end_datetime,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .first()
    )

    # 获取运动类型列表
    types_result = (
        db.query(ExerciseCheckIn.exercise_type)
        .filter(
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.started_at >= start_datetime,
            ExerciseCheckIn.started_at < end_datetime,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    exercise_types = [t[0] for t in types_result]

    # Dashboard 特定字段：目标值 (可从用户设置获取，这里使用默认值)
    goal_duration = 60  # 默认目标：每天 60 分钟
    goal_calories = 500  # 默认目标：每天燃烧 500kcal

    # 计算进度百分比
    total_duration = result.total_duration or 0
    total_calories = result.total_calories or 0
    progress_percentage = max(
        (total_duration / goal_duration * 100) if goal_duration else 0,
        (total_calories / goal_calories * 100) if goal_calories else 0,
    )

    return DailySummaryResponse(
        date=target_date.isoformat(),
        total_duration_minutes=total_duration,
        total_calories_burned=total_calories,
        sessions_count=result.sessions_count or 0,
        exercise_types=exercise_types,
        average_heart_rate=int(result.avg_heart_rate)
        if result.avg_heart_rate
        else None,
        goal_duration=goal_duration,
        goal_calories=goal_calories,
        progress_percentage=min(progress_percentage, 100),  #  capped at 100%
    )
