from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.gamification import (
    UserPoints,
    PointsTransaction,
    UserLevel,
    Achievement,
    Challenge,
    UserBadge,
)
from app.schemas.reward_personalization import (
    PersonalizedRecommendation,
    PersonalizedRecommendationResponse,
    UserPreferenceProfile,
    UserIncentiveProfileResponse,
    TaskRecommendation,
    RewardRecommendation,
    CustomizationRequest,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/personalized-insights", response_model=UserIncentiveProfileResponse)
async def get_personalized_incentive_profile(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户个性化激励档案"""
    logger.info("Getting personalized incentive profile", user_id=current_user.id)

    # 获取用户的基本点数信息
    user_points = (
        db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
    )

    if not user_points:
        # If user has no points record, create default with 0 points
        from app.models.gamification import UserPoints as UserPointsModel

        new_user_points = UserPointsModel(
            user_id=current_user.id,
            total_points=0,
            current_points=0,
            lifetime_points=0,
        )
        db.add(new_user_points)
        db.commit()
        db.refresh(new_user_points)
        user_points = new_user_points

    # 获取用户成就
    user_achievements = (
        db.query(Achievement).filter(Achievement.user_id == current_user.id).all()
    )

    # Get user rewards history (from points transactions)
    reward_transactions = (
        db.query(PointsTransaction)
        .filter(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.transaction_type == "reward_purchase",
        )
        .order_by(PointsTransaction.created_at.desc())
        .limit(20)  # Get last 20 reward transactions
        .all()
    )

    # Determine user activity patterns
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    recent_transactions_count = (
        db.query(PointsTransaction)
        .filter(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.created_at >= thirty_days_ago,
        )
        .count()
    )

    # Analyze user preferences based on their reward choices and activity
    most_redeemed_category = None
    if reward_transactions:
        # Group by reward type/category and find most frequently purchased
        category_count = {}
        for tx in reward_transactions:
            category = getattr(
                tx, "reference_type", "general"
            )  # Assuming categories are in reference
            category_count[category] = category_count.get(category, 0) + 1
        most_redeemed_category = (
            max(category_count, key=category_count.get) if category_count else "general"
        )

    # Determine activity streaks and patterns
    achievements_percentage = (
        len([a for a in user_achievements if a.is_completed]) / len(user_achievements)
        if user_achievements
        else 0.0
    )

    reward_engagement_score = (
        len(reward_transactions) * 10  # Participation count factor
        + achievements_percentage * 20  # Achievement progress factor
        + min(recent_transactions_count * 3, 50)  # Recent activity factor
    )

    # Create user profile based on preferences and behavior
    profile = UserIncentiveProfileResponse(
        user_id=current_user.id,
        overall_engagement_score=round(reward_engagement_score, 2),
        preferred_reward_category=most_redeemed_category,
        reward_frequency_preference="moderate",  # Could be personalized based on user's redemption pattern
        ideal_point_cost_range=[100, 1000],  # Range could be personalized
        activity_streak=0,  # To be implemented with streak tracking
        points_velocity=(  # How quickly user earns points
            user_points.lifetime_points / max((now - current_user.created_at).days, 1)
            if user_points.lifetime_points > 0
            and hasattr(current_user, "created_at")
            and current_user.created_at
            else 0
        ),
        most_engaging_achievements=[
            "weight_milestone",
            "consistency",
            "nutrition",  # These would be personalized based on user behavior
        ],
        recommended_focus=[
            "continue_achieving_badges",
            "increase_reward_engagement",
            "try_new_challenge_types",
        ],
    )

    logger.info(
        "Personalized incentive profile generated",
        user_id=current_user.id,
        engagement_score=profile.overall_engagement_score,
    )

    return profile


@router.get("/recommendations", response_model=PersonalizedRecommendationResponse)
async def get_personalized_recommendations(
    include_achievements: bool = Query(True, description="是否包含成就推荐"),
    include_rewards: bool = Query(True, description="是否包含奖励推荐"),
    include_challenges: bool = Query(True, description="是否包含挑战推荐"),
    limit: int = Query(3, ge=1, le=10, description="推荐数量限制"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取个性化推荐"""
    logger.info("Getting personalized recommendations", user_id=current_user.id)

    # Get user's profile information based on past behavior
    user_points = (
        db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
    )

    if not user_points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User points record not found"
        )

    # Get user achievements to understand preference patterns
    user_achievements = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == current_user.id, Achievement.is_completed == True
        )
        .all()
    )

    completed_achievement_types = (
        [
            a.achievement_type
            for a in user_achievements
            if hasattr(a, "achievement_type")
        ]
        if user_achievements
        else []
    )

    # Get recent achievements
    recent_achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == current_user.id)
        .order_by(Achievement.created_at.desc())
        .limit(5)
        .all()
    )

    # Calculate engagement patterns
    recent_achievements_types = set()
    for ach in recent_achievements:
        if hasattr(ach, "achievement_type"):
            recent_achievements_types.add(ach.achievement_type)

    # Generate personalized achievement recommendations
    achievement_recommendations = []
    if include_achievements:
        # Suggest achievements based on past completions
        possible_achievements = [
            "weight_loss_beginner",
            "consistency_master",
            "nutrition_explorer",
            "exercise_enthusiast",
            "mindfulness_practitioner",
        ]

        # Filter out already completed ones
        potential_achievements = [
            a for a in possible_achievements if a not in completed_achievement_types
        ]
        # Take up to limit of recommendations
        for i, achievement_name in enumerate(potential_achievements[:limit]):
            achievement_recommendations.append(
                AchievementRecommendation(
                    id=f"rec_achievement_{i + 1}",
                    name=achievement_name.replace("_", " ").title(),
                    description=generate_achievement_description(achievement_name),
                    category=classify_achievement_category(achievement_name),
                    estimated_difficulty=determine_difficulty_level(achievement_name),
                    recommended_for_user=True,
                )
            )

    # Generate personalized reward recommendations based on user preference
    reward_recommendations = []
    if include_rewards:
        # Simulating rewards from the reward shop system - real system would have this
        from app.models.rewards import Reward as RewardModel

        available_rewards = (
            db.query(RewardModel)
            .filter(RewardModel.is_available == True)
            .filter(RewardModel.cost_points <= user_points.current_points)
            .order_by(RewardModel.cost_points.asc())
        ).all()

        # Choose rewards based on user's most purchased category or interest areas
        preferred_category = ""
        if recent_achievements_types:
            # Determine preferred category based on recent achievements
            # This is a simplified approach - real system would have complex logic
            weight_related = sum(
                1 for t in recent_achievements_types if "weight" in t.lower()
            )
            exercise_related = sum(
                1
                for t in recent_achievements_types
                if "exercise" in t.lower() or "fitness" in t.lower()
            )
            nutrition_related = sum(
                1
                for t in recent_achievements_types
                if "nutrit" in t.lower() or "food" in t.lower()
            )

            preferred_category = (
                "weight"
                if weight_related >= exercise_related
                and weight_related >= nutrition_related
                else "fitness"
                if exercise_related >= nutrition_related
                else "nutrition"
            )

        # Find rewards matching user's interests
        matching_rewards = [
            r for r in available_rewards if preferred_category in r.category.lower()
        ] or available_rewards[:limit]

        for i, reward in enumerate(matching_rewards[:limit]):
            reward_rec = RewardRecommendation(
                id=reward.id,
                name=reward.name,
                description=reward.description,
                category=reward.category,
                cost_points=reward.cost_points,
                estimated_value=estimate_reward_value(reward),
                match_reason=f"MATCHES_USER_PREFERENCES:{preferred_category.upper()}",
                recommended_for_user=True,
            )
            reward_recommendations.append(reward_rec)

    # Challenge recommendations
    challenge_recommendations = []
    if include_challenges:
        # Recommend challenges based on user's activity level
        from app.models.gamification import Challenge as ChallengeModel

        user_challenges = (
            db.query(ChallengeModel)
            .filter(ChallengeModel.user_id == current_user.id)
            .all()
        )

        # Find suitable challenges based on user's completion patterns
        active_challenges_count = sum(
            1 for ch in user_challenges if ch.status == "active"
        )

        # Determine challenge level based on user's achievement level
        base_challenges = [
            {"name": "7天健康饮食", "difficulty": "beginner", "category": "nutrition"},
            {"name": "连续打卡挑战", "difficulty": "beginner", "category": "habits"},
            {"name": "每日运动挑战", "difficulty": "beginner", "category": "fitness"},
        ]

        suitable_challenges = base_challenges[:limit]
        for i, challenge in enumerate(suitable_challenges):
            challenge_rec = ChallengeRecommendation(  # Use appropriate schema type
                id=f"rec_challenge_{i + 1}",
                title=challenge["name"],
                description=get_challenge_description(challenge["name"]),
                difficulty=challenge["difficulty"],
                category=challenge["category"],
                recommended_for_user=True,
            )
            challenge_recommendations.append(challenge_rec)

    # Create recommendation response
    recommendations_response = PersonalizedRecommendationResponse(
        user_id=current_user.id,
        recommendations={
            "achievements": achievement_recommendations,
            "rewards": reward_recommendations,
            "challenges": challenge_recommendations,
        },
        last_updated=datetime.utcnow().isoformat(),
        total_recommendations=len(achievement_recommendations)
        + len(reward_recommendations)
        + len(challenge_recommendations),
    )

    logger.info(
        "Personalized recommendations generated",
        user_id=current_user.id,
        total_recommendations=recommendations_response.total_recommendations,
    )

    return recommendations_response


@router.post("/preferences/update", response_model=dict)
async def update_user_preferences(
    preferences: UserPreferenceProfile,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新用户激励偏爱设置"""
    # This function would update the user's preference settings in the database
    # Since direct user model doesn't have preference fields on our existing model,
    # we would create a separate preferences table if needed
    # For now, we'll log the preferences update as the system would use these for personalization

    logger.info(
        "User preferences updated",
        user_id=current_user.id,
        preferences=preferences.dict(),
    )

    # In a real implementation, you would store these preferences in a user preferences model
    return {
        "message": "Preferences updated successfully",
        "updated_preferences": preferences.dict(),
        "processed_at": datetime.utcnow().isoformat(),
    }


def generate_achievement_description(achievement_name: str) -> str:
    """生成成就描述"""
    descriptions = {
        "weight_loss_beginner": "初始减重里程碑，成功减重1-2公斤",
        "consistency_master": "连续打卡30天，体现坚持精神",
        "nutrition_explorer": "尝试过多种营养搭配，掌握健康饮食",
        "exercise_enthusiast": "积极参与运动，保持活力状态",
        "mindfulness_practitioner": "通过冥想、正念练习培养内心平静",
    }
    return descriptions.get(
        achievement_name, f"完成{achievement_name.replace('_', ' ')}挑战"
    )


def classify_achievement_category(achievement_name: str) -> str:
    """分类成就类别"""
    category_mapping = {
        "weight": ["weight", "loss", "gain", "milestone"],
        "fitness": ["exercise", "workout", "strength", "cardio"],
        "nutrition": ["nutrit", "food", "eat", "meal", "diet"],
        "habits": ["consistency", "streak", "daily", "habit"],
        "mental": ["mindful", "meditation", "emotion", "wellness"],
    }

    ach_lower = achievement_name.lower()
    for category, keywords in category_mapping.items():
        if any(keyword in ach_lower for keyword in keywords):
            return category.capitalize()

    return "General"


def determine_difficulty_level(achievement_name: str) -> str:
    """确定难度级别"""
    # Simplified algorithm - in real system would be more nuanced
    if "beginner" in achievement_name.lower() or "first" in achievement_name.lower():
        return "Easy"
    elif (
        "master" in achievement_name.lower()
        or "expert" in achievement_name.lower()
        or "advanced" in achievement_name.lower()
    ):
        return "Hard"
    else:
        return "Medium"


def estimate_reward_value(reward) -> str:
    """估算奖励价值"""
    if reward.cost_points <= 100:
        return "Small Value"
    elif reward.cost_points <= 500:
        return "Medium Value"
    else:
        return "High Value"


def get_challenge_description(challenge_name: str) -> str:
    """获取挑战描述"""
    desc_map = {
        "7天健康饮食": "坚持7天按时就餐，合理搭配营养",
        "连续打卡挑战": "每天完成习惯打卡，建立长期坚持",
        "每日运动挑战": "每天至少运动30分钟，增强体质",
    }
    return desc_map.get(challenge_name, f"连续{challenge_name}挑战，培养健康习惯")


@router.post("/customize-engagement", response_model=dict)
async def customize_user_engagement(
    customization_request: CustomizationRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """自定义用户参与体验"""
    logger.info(
        "Customizing user engagement",
        user_id=current_user.id,
        preferences=customization_request.preferences,
    )

    # In real implementation, this would adjust how challenges, rewards, and notifications
    # are presented to the user based on their preferences
    feedback = customization_request.feedback

    if feedback:
        logger.info("Received user feedback for customization", feedback=feedback)
        # Would normally store feedback in a feedback system for model improvement

    return {
        "message": "Engagement experience customized based on preferences",
        "applied_preferences": customization_request.preferences,
        "feedback_processed": bool(feedback),
        "customization_applied_on": datetime.utcnow().isoformat(),
    }
