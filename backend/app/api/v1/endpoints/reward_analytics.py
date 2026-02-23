from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.gamification import (
    UserPoints,
    PointsTransaction,
    UserLevel,
    Achievement,
    Challenge,
)
from app.schemas.reward_analytics import (
    RewardAnalyticsResponse,
    RewardTrendData,
    UserRewardSummary,
    RewardEffectivenessData,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/analytics/overview", response_model=RewardAnalyticsResponse)
async def get_reward_analytics_overview(
    days_back: int = Query(30, ge=1, le=365, description="回溯天数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励系统数据分析总览"""
    logger.info(
        "Getting reward analytics overview",
        user_id=current_user.id,
        days_back=days_back,
    )

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)

    # 1. Get point transactions analysis
    point_transactions = (
        db.query(PointsTransaction)
        .filter(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.created_at >= start_date,
        )
        .order_by(PointsTransaction.created_at.desc())
        .all()
    )

    # Calculate point statistics
    total_points_earned = 0
    total_points_spent = 0
    points_earned_by_type = {}
    points_spent_by_source = {}

    for tx in point_transactions:
        if tx.points_amount > 0:  # Earnings
            total_points_earned += tx.points_amount
            if tx.transaction_type not in points_earned_by_type:
                points_earned_by_type[tx.transaction_type] = 0
            points_earned_by_type[tx.transaction_type] += tx.points_amount
        else:  # Spending
            total_points_spent += abs(tx.points_amount)
            if tx.reference_type not in points_spent_by_source:
                points_spent_by_source[tx.reference_type] = 0
            points_spent_by_source[tx.reference_type] += abs(tx.points_amount)

    # 2. Get user's achievements progress
    achievements = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == current_user.id, Achievement.created_at >= start_date
        )
        .all()
    )

    unlocked_achievements = [a for a in achievements if a.is_completed]

    # 3. Get user's challenges progress
    challenges = (
        db.query(Challenge)
        .filter(
            Challenge.user_id == current_user.id, Challenge.created_at >= start_date
        )
        .all()
    )

    completed_challenges = [c for c in challenges if c.status == "completed"]

    # 4. Get user's current level and experience
    user_level = (
        db.query(UserLevel).filter(UserLevel.user_id == current_user.id).first()
    )

    # Create analytics response
    analytics_response = RewardAnalyticsResponse(
        period_days=days_back,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        user_summary=UserRewardSummary(
            current_level=user_level.current_level if user_level else 1,
            current_xp=user_level.experience_points if user_level else 0,
            points_to_next_level=user_level.points_to_next_level if user_level else 100,
            unlocked_achievements_count=len(unlocked_achievements),
            completed_challenges_count=len(completed_challenges),
            total_points_earned=total_points_earned,
            total_points_spent=total_points_spent,
            net_points_balance=total_points_earned - total_points_spent,
        ),
        trends=RewardTrendData(
            daily_points_earned={},  # Populated below with daily aggregation
            daily_points_spent={},  # Populated below
            achievement_completion_rate=len(unlocked_achievements) / len(achievements)
            if achievements
            else 0,
            challenge_completion_rate=len(completed_challenges) / len(challenges)
            if challenges
            else 0,
        ),
        effectiveness=RewardEffectivenessData(
            top_earning_activities=sorted(
                points_earned_by_type.items(), key=lambda x: x[1], reverse=True
            )[:5],
            top_spending_sources=sorted(
                points_spent_by_source.items(), key=lambda x: x[1], reverse=True
            )[:5],
            achievement_unlock_frequency=len(unlocked_achievements),
            engagement_score=len(point_transactions) / days_back
            if days_back > 0
            else 0,
        ),
    )

    # Calculate daily aggregation for trends
    daily_earnings = {}
    daily_spending = {}

    for tx in point_transactions:
        date_str = tx.created_at.strftime("%Y-%m-%d")
        if tx.points_amount > 0:
            daily_earnings[date_str] = (
                daily_earnings.get(date_str, 0) + tx.points_amount
            )
        else:
            daily_spending[date_str] = daily_spending.get(date_str, 0) + abs(
                tx.points_amount
            )

    # Fill in missing dates with 0
    for i in range(days_back):
        date = end_date - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in daily_earnings:
            daily_earnings[date_str] = 0
        if date_str not in daily_spending:
            daily_spending[date_str] = 0

    analytics_response.trends.daily_points_earned = daily_earnings
    analytics_response.trends.daily_points_spent = daily_spending

    logger.info(
        "Reward analytics overview generated",
        user_id=current_user.id,
        days_back=days_back,
        total_points_earned=total_points_earned,
        total_points_spent=total_points_spent,
    )

    return analytics_response


@router.get("/analytics/reward-trends", response_model=List[Dict])
async def get_reward_trends(
    metric: str = Query(
        "points", description="指标类型: points, achievements, challenges, levels"
    ),
    period: str = Query("weekly", description="周期类型: daily, weekly, monthly"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励趋势数据"""
    logger.info(
        "Getting reward trends", user_id=current_user.id, metric=metric, period=period
    )

    if metric == "points":
        # Query daily point earnings over time
        transactions = (
            db.query(
                func.date(PointsTransaction.created_at).label("date"),
                func.sum(PointsTransaction.points_amount).label("total_points"),
            )
            .filter(PointsTransaction.user_id == current_user.id)
            .group_by(func.date(PointsTransaction.created_at))
            .order_by(desc("date"))
            .limit(30)  # Last 30 days
            .all()
        )

        trend_data = [
            {"date": row[0].strftime("%Y-%m-%d"), "points": row[1]}
            for row in transactions
        ]

    elif metric == "achievements":
        # Get achievement unlocks over time
        achievements = (
            db.query(
                func.date(Achievement.created_at).label("date"),
                func.count(Achievement.id).label("unlocks"),
            )
            .filter(Achievement.user_id == current_user.id)
            .group_by(func.date(Achievement.created_at))
            .order_by(desc("date"))
            .limit(30)
            .all()
        )

        trend_data = [
            {"date": row[0].strftime("%Y-%m-%d"), "unlocks": row[1]}
            for row in achievements
        ]

    elif metric == "challenges":
        # Get challenge completions over time
        challenges = (
            db.query(
                func.date(Challenge.updated_at).label(
                    "date"
                ),  # Assuming updated_at is when status changes
                func.count(Challenge.id).label("completions"),
            )
            .filter(
                Challenge.user_id == current_user.id,
                # Only completed challenges
            )
            .group_by(
                func.date(Challenge.completion_date)
            )  # Using completion_date if it exists
            .order_by(desc("completion_date"))
            .limit(30)
            .all()
        )

        # Actually use the completion date if tracked, otherwise use updated_at
        # For implementation: we might store completion timestamps
        from app.models.gamification import (
            Challenge as ChallengeModel,
        )  # Import again to confirm structure

        challenge_completions = (
            db.query(
                func.date(Challenge.completed_at).label("date"),
                func.count(Challenge.id).label("completions"),
            )
            .filter(
                Challenge.user_id == current_user.id, Challenge.completed_at.isnot(None)
            )
            .group_by(func.date(Challenge.completion_date))
            .order_by(desc("date"))
            .limit(30)
            .all()
        )

        trend_data = [
            {"date": str(row[0]), "completions": row[1]}
            for row in challenge_completions
        ]

    else:  # levels, other metrics
        # For other metrics return empty or implement as needed
        trend_data = []

    logger.info(
        "Reward trends retrieved",
        user_id=current_user.id,
        metric=metric,
        total_records=len(trend_data),
    )

    return trend_data


@router.get("/analytics/effectiveness", response_model=Dict)
async def get_reward_effectiveness(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励系统有效性分析"""
    logger.info("Getting reward effectiveness analysis", user_id=current_user.id)

    # Use today's date if no dates provided
    end_date = end_date or datetime.utcnow()
    start_date = start_date or (end_date - timedelta(days=30))

    # Get data for the analysis
    transactions = (
        db.query(PointsTransaction)
        .filter(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.created_at >= start_date,
            PointsTransaction.created_at <= end_date,
        )
        .all()
    )

    achievements = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == current_user.id,
            Achievement.created_at >= start_date,
            Achievement.created_at <= end_date,
        )
        .all()
    )

    challenges = (
        db.query(Challenge)
        .filter(
            Challenge.user_id == current_user.id,
            Challenge.created_at >= start_date,
            Challenge.created_at <= end_date,
        )
        .all()
    )

    # Calculate effectiveness metrics
    total_points_earned = sum(
        tx.points_amount for tx in transactions if tx.points_amount > 0
    )
    total_points_spent = sum(
        abs(tx.points_amount) for tx in transactions if tx.points_amount < 0
    )

    active_perfect = sum(
        1 for a in achievements if a.progress_percentage == 100 and a.is_completed
    )
    avg_achievement_progress = (
        sum(a.progress_percentage for a in achievements) / len(achievements)
        if achievements
        else 0
    )

    completed_challenges = sum(1 for c in challenges if c.completed_at is not None)
    avg_challenge_completion_rate = (
        (completed_challenges / len(challenges) * 100) if challenges else 0
    )

    effectiveness_analysis = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "activity_metrics": {
            "total_points_earned": total_points_earned,
            "total_points_spent": total_points_spent,
            "net_points_gained": total_points_earned - total_points_spent,
            "transactions_count": len(transactions),
        },
        "achievement_effectiveness": {
            "total_achievements": len(achievements),
            "perfect_achievements": active_perfect,
            "average_progress": round(avg_achievement_progress, 2),
            "completion_rate": round(
                avg_achievement_progress, 2
            ),  # Same as progress if measuring completion
        },
        "challenge_effectiveness": {
            "total_challenges": len(challenges),
            "completed_challenges": completed_challenges,
            "completion_rate": round(avg_challenge_completion_rate, 2),
        },
        "engagement_score": round(
            (len(transactions) + len(achievements) + len(challenges)) / 10, 2
        ),  # Simplified engagement measurement
        "recommended_improvements": generate_improvement_recommendations(
            total_points_earned,
            total_points_spent,
            avg_achievement_progress,
            avg_challenge_completion_rate,
        ),
    }

    logger.info(
        "Reward effectiveness analysis generated",
        user_id=current_user.id,
        activity_score=effectiveness_analysis["engagement_score"],
        achievement_completion=avg_achievement_progress,
    )

    return effectiveness_analysis


def generate_improvement_recommendations(
    total_points_earned: int,
    total_points_spent: int,
    avg_achievement_progress: float,
    avg_challenge_completion_rate: float,
) -> List[str]:
    """Generate improvement recommendations based on efficacy data"""
    recommendations = []

    # Points earning vs spending balance
    if total_points_earned > total_points_spent * 1.5:
        recommendations.append("您的积分赚取能力强于消费能力，可以考虑兑换更多奖励！")
    elif total_points_spent > total_points_earned * 1.2:
        recommendations.append("您正在大量消费积分，注意保持健康行为以继续赚取积分")

    # Achievement progress
    if avg_achievement_progress < 30:
        recommendations.append("尝试完成一些更容易的成就以提升自信和获得奖励")
    elif 30 <= avg_achievement_progress < 60:
        recommendations.append("您在成就方面表现平稳，可以挑战一些中等难度的目标")
    else:
        recommendations.append("您的成就完成度很高！可以尝试更具挑战的目标")

    # Challenge completion rate
    if avg_challenge_completion_rate < 40:
        recommendations.append("挑战完成率较低，可以从小挑战开始，逐步提升")
    elif 40 <= avg_challenge_completion_rate < 70:
        recommendations.append("挑战完成率达到平均水平，继续保持")
    else:
        recommendations.append("您在挑战方面表现优异，继续坚持高水准")

    if not recommendations:  # If no specific issues, give general encouragement
        recommendations.append("您在积分系统上的表现均衡且持续！继续保持您的健康行为。")

    return recommendations
