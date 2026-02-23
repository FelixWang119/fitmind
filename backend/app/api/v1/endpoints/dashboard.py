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
from typing import List, Dict, Any

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
