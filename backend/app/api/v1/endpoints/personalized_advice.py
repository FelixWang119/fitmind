from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.nutrition import Meal
from app.models.emotional_support import EmotionalSupport, EmotionalState
from app.models.gamification import UserPoints, Achievement
from app.schemas.health_advice import (
    PersonalizedHealthAdviceRequest,
    PersonalizedHealthAdviceResponse,
    PersonalizedRecommendation,
    UserHealthProfile,
)
from app.services.ai_service import get_ai_response

logger = structlog.getLogger()

router = APIRouter()


@router.post("/personalized-advice", response_model=PersonalizedHealthAdviceResponse)
async def get_personalized_health_advice(
    advice_request: PersonalizedHealthAdviceRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取个性化健康建议"""
    logger.info(
        "Personalized health advice request",
        user_id=current_user.id,
        context_type=advice_request.context_type,
        target_metric=advice_request.target_metric,
    )

    try:
        # Get comprehensive user health profile
        # Get health records for profile analysis
        from datetime import datetime, timedelta

        # Fetch recent health records
        start_date = datetime.utcnow() - timedelta(days=advice_request.days_back or 30)

        # Get health records
        health_records = (
            db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == current_user.id,
                HealthRecord.created_at >= start_date,
            )
            .order_by(HealthRecord.created_at.desc())
            .all()
        )

        # Extract and organize health data
        weights = [
            (hr.created_at.date(), hr.weight / 1000.0)  # Convert grams to kg
            for hr in health_records
            if hr.weight and hr.weight > 0
        ]

        # Calculate trends and statistics if we have meaningful data
        trends_data = {}
        if weights:
            # Determine weight trend using the first and last values
            initial_weight = weights[-1][1] if weights else None
            current_weight = weights[0][1] if weights else None
            weight_change = 0

            if len(weights) > 1 and initial_weight and current_weight:
                weight_change = current_weight - initial_weight

            avg_weight = sum(w[1] for w in weights) / len(weights) if weights else 0
            latest_weight = weights[0][1] if weights else 0

            trends_data["weight"] = {
                "initial_weight_kg": round(initial_weight, 2)
                if initial_weight
                else None,
                "current_weight_kg": round(latest_weight, 2) if latest_weight else None,
                "weight_change_kg": round(weight_change, 2),
                "average_weight_kg": round(avg_weight, 2),
                "trend_direction": "decreasing"
                if weight_change < -0.5
                else "increasing"
                if weight_change > 0.5
                else "stable",
                "data_points_count": len(weights),
            }

        # Get habit completion data
        habit_completions = (
            db.query(HabitCompletion)
            .join(Habit, Habitat.id == HabitCompletion.habit_id)
            .filter(
                Habit.user_id == current_user.id,
                HabitCompletion.completion_date >= start_date.date(),
            )
            .order_by(HabitCompletion.completion_date.desc())
            .all()
        )

        # Group completions by habit and calculate consistency scores
        habit_stats = {}
        if habit_completions:
            # Create a structure for habit completions
            from collections import defaultdict, Counter

            habit_completions_dict = defaultdict(list)

            for comp in habit_completions:
                habit_completions_dict[comp.habit.name].append(comp)

            for habit_name, completions in habit_completions_dict.items():
                total_days = (datetime.utcnow().date() - start_date.date()).days + 1

                # Calculate consistency percentage
                completion_count = len(completions)
                consistency_rate = (
                    (completion_count / float(total_days)) * 100
                    if total_days > 0
                    else 0
                )

                habit_stats[habit_name] = {
                    "total_completions": completion_count,
                    "total_days": total_days,
                    "consistency_rate": consistency_rate,
                    "completion_frequency": "daily"
                    if consistency_rate > 80
                    else "frequent"
                    if consistency_rate > 60
                    else "occasional"
                    if consistency_rate > 30
                    else "infrequent",
                }

        # Get nutrition data
        meal_records = (
            db.query(Meal)
            .filter(Meal.user_id == current_user.id, Meal.meal_datetime >= start_date)
            .order_by(Meal.meal_datetime.desc())
            .all()
        )

        nutrition_data = {}
        if meal_records:
            total_calories = sum(m.calories or 0 for m in meal_records)
            nutrition_data["calories"] = {
                "total": total_calories,
                "average_daily": round(
                    total_calories
                    / max(1, (datetime.utcnow().date() - start_date.date()).days),
                    1,
                ),
            }

        # Get emotional check-ins
        emotional_records = (
            db.query(EmotionalSupport, EmotionalState)
            .join(
                EmotionalState, EmotionalSupport.emotional_state_id == EmotionalState.id
            )
            .filter(
                EmotionalSupport.user_id == current_user.id,
                EmotionalSupport.created_at >= start_date,
            )
            .order_by(EmotionalSupport.created_at.desc())
            .all()
        )

        emotional_data = {}
        if emotional_records:
            mood_values = [
                ec.intensity_level for ec, _ in emotional_records if ec.intensity_level
            ]
            emotional_data["mood_trends"] = {
                "average_mood": round(sum(mood_values) / len(mood_values), 1)
                if mood_values
                else 0,
                "mood_consistency": len(mood_values)
                >= 5,  # Check if user records mood regularly enough for analysis
                "emotional_entries_count": len(emotional_records),
            }

        # Create user profile for personalized AI
        user_profile = UserHealthProfile(
            user_id=current_user.id,
            days_analyzed=advice_request.days_back or 30,
            health_trends=trends_data,
            habit_compliance=habit_stats,
            nutrition_summary=nutrition_data,
            emotional_summary=emotional_data,
            personal_factors={
                "age": current_user.age,
                "gender": current_user.gender,
                "height_cm": current_user.height,
                "baseline_weight": (current_user.initial_weight / 1000.0)
                if current_user.initial_weight
                else None,  # Convert to kg
                "target_weight": (current_user.target_weight / 1000.0)
                if current_user.target_weight
                else None,  # Convert to kg
                "activity_level": current_user.activity_level,
                "dietary_preferences": current_user.dietary_preferences,
            },
        )

        # Enhance the AI request with personalized context
        ai_context = {
            "user_profile": user_profile.dict(),
            "health_trends": trends_data,
            "habit_insights": habit_stats,
            "context": advice_request.context,
            "target_metric": advice_request.target_metric,
        }

        # Get AI response using the existing service
        ai_response = await get_ai_response(
            message=advice_request.request_message,
            user_id=current_user.id,
            context=ai_context,
            db=db,
        )

        # Create the personalized advice response
        personalized_advice = PersonalizedHealthAdviceResponse(
            message="Personalized health advice generated",
            user_profile=user_profile,
            recommendations=[
                PersonalizedRecommendation(
                    title="个性化建议",
                    content=ai_response.response,
                    priority="medium",
                    category="general",
                    relevance_score=0.85,  # Would be calculated based on profile matching
                )
            ],
            generated_at=datetime.utcnow().isoformat(),
            context_used=advice_request.context,
        )

        logger.info(
            "Personalized advice generated",
            user_id=current_user.id,
            recommendations_count=len(personalized_advice.recommendations),
        )

        return personalized_advice

    except Exception as e:
        logger.error(
            "Personalized advice generation failed",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Personalized health advice generation failed",
        )


@router.get("/user-profile", response_model=UserHealthProfile)
async def get_comprehensive_user_profile(
    days_back: int = Query(30, ge=1, le=365, description="回溯天数 (1-365)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取综合健康档案"""
    logger.info("Getting comprehensive user profile", user_id=current_user.id)

    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Build comprehensive profile
    profile_data = {
        "user_id": current_user.id,
        "days_analyzed": days_back,
        "personal_factors": {
            "age": current_user.age,
            "gender": current_user.gender,
            "height_cm": current_user.height,
            "baseline_weight_kg": (current_user.initial_weight / 1000.0)
            if current_user.initial_weight
            else None,
            "target_weight_kg": (current_user.target_weight / 1000.0)
            if current_user.target_weight
            else None,
            "activity_level": current_user.activity_level,
            "dietary_preferences": current_user.dietary_preferences or [],
        },
        "health_trends": {},
        "habit_compliance": {},
        "nutrition_summary": {},
        "emotional_summary": {},
    }

    # Fetch health records for trend data
    health_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.created_at >= start_date,
        )
        .order_by(HealthRecord.created_at.desc())
        .all()
    )

    weights = [
        (hr.created_at.date(), hr.weight / 1000.0)  # Convert grams to kg
        for hr in health_records
        if hr.weight and hr.weight > 0
    ]

    if weights:
        initial_weight = weights[-1][1] if weights else None
        current_weight = weights[0][1] if weights else None
        weight_change = 0

        if len(weights) > 1 and initial_weight and current_weight:
            weight_change = current_weight - initial_weight

        profile_data["health_trends"]["weight"] = {
            "initial_weight_kg": round(initial_weight, 2) if initial_weight else None,
            "current_weight_kg": round(current_weight, 2) if current_weight else None,
            "weight_change_kg": round(weight_change, 2),
            "average_weight_kg": round(sum(w[1] for w in weights) / len(weights), 2)
            if weights
            else 0,
            "trend_direction": "decreasing"
            if weight_change < -0.5
            else "increasing"
            if weight_change > 0.5
            else "stable",
            "data_points_count": len(weights),
        }

    # Get habit compliance data
    from app.models.habit import Habit, HabitCompletion

    habit_completions = (
        db.query(HabitCompletion)
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(
            Habit.user_id == current_user.id,
            HabitCompletion.completion_date >= start_date.date(),
        )
        .all()
    )

    # Group by habits and calculate compliance
    from collections import defaultdict

    habit_data = defaultdict(list)
    for comp in habit_completions:
        habit_data[comp.habit.name if comp.habit else "unnamed"].append(comp)

    # Calculate consistency scores
    for habit_name, completions in habit_data.items():
        total_days = (datetime.utcnow().date() - start_date.date()).days + 1
        completion_count = len(completions)
        compliance_rate = (
            (completion_count / float(total_days)) * 100 if total_days > 0 else 0
        )

        profile_data["habit_compliance"][habit_name] = {
            "total_completions": completion_count,
            "total_days": total_days,
            "compliance_rate": compliance_rate,
            "frequency": "daily"
            if compliance_rate > 80
            else "frequent"
            if compliance_rate > 60
            else "occasional"
            if compliance_rate > 30
            else "infrequent",
        }

    # Get nutrition summary
    from app.models.nutrition import Meal

    meal_records = (
        db.query(Meal)
        .filter(Meal.user_id == current_user.id, Meal.meal_datetime >= start_date)
        .order_by(Meal.meal_datetime.desc())
        .all()
    )

    if meal_records:
        total_calories = sum(m.calories or 0 for m in meal_records)
        profile_data["nutrition_summary"] = {
            "calories": {
                "total": total_calories,
                "average_daily": round(
                    total_calories
                    / max(1, (datetime.utcnow().date() - start_date.date()).days),
                    1,
                ),
            }
        }

    # Get emotional data
    emotional_records = (
        db.query(EmotionalSupport, EmotionalState)
        .join(EmotionalState, EmotionalSupport.emotional_state_id == EmotionalState.id)
        .filter(
            EmotionalSupport.user_id == current_user.id,
            EmotionalSupport.created_at >= start_date,
        )
        .all()
    )

    if emotional_records:
        mood_values = [
            ec.intensity_level for ec, _ in emotional_records if ec.intensity_level
        ]
        profile_data["emotional_summary"] = {
            "mood_trends": {
                "average_mood": round(sum(mood_values) / len(mood_values), 1)
                if mood_values
                else 0,
                "mood_consistency": len(mood_values) >= 5,
                "emotional_entries_count": len(emotional_records),
            }
        }

    logger.info("Comprehensive user profile generated", user_id=current_user.id)

    return UserHealthProfile(**profile_data)


@router.post("/generate-personalized-plan", response_model=dict)
async def generate_personalized_health_plan(
    plan_request: dict,  # Specific schema would be defined
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成个性化健康计划"""
    logger.info("Generating personalized health plan", user_id=current_user.id)

    # Get user health profile to inform the plan
    profile_response = await get_comprehensive_user_profile(
        days_back=plan_request.get("days_back", 30), current_user=current_user, db=db
    )

    # Use AI to generate personalized plan based on user profile
    health_profile = profile_response.dict()

    # Construct prompt for AI
    plan_prompt = (
        f"根据用户健康档案生成个性化健康计划:\n"
        f"年龄: {health_profile.get('personal_factors', {}).get('age')}\n"
        f"性别: {health_profile.get('personal_factors', {}).get('gender')}\n"
        f"身高: {health_profile.get('personal_factors', {}).get('height_cm')}cm\n"
        f"体重趋势: {health_profile.get('health_trends', {}).get('weight', {}).get('trend_direction', 'unknown')}\n"
        f"习惯遵守率: {health_profile.get('habit_compliance')}\n"
        f"饮食概要: {health_profile.get('nutrition_summary')}\n"
        f"情绪概况: {health_profile.get('emotional_summary')}\n"
        f"请提供为期4周的个性化健康计划，包含每日小步骤、每周目标和健康贴士。"
    )

    try:
        # Get AI to generate personalized plan
        ai_response = await get_ai_response(
            message=plan_prompt, user_id=current_user.id, context=health_profile, db=db
        )

        plan_response = {
            "message": "个性化健康计划生成成功",
            "plan_summary": ai_response.response,  # Actual AI-generated plan
            "based_on_profile": health_profile,
            "personalization_score": 0.92,  # Would be based on profile match
            "focus_areas": [],
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Infer focus areas from profile analysis
        if (
            health_profile.get("health_trends", {})
            .get("weight", {})
            .get("trend_direction")
            == "increasing"
        ):
            plan_response["focus_areas"].append("体重管理")
        if len(health_profile.get("habit_compliance", {})) > 0:
            low_compliance_habits = [
                name
                for name, data in health_profile.get("habit_compliance", {}).items()
                if data.get("compliance_rate", 0) < 60  # Below 60% adherence
            ]
            if low_compliance_habits:
                plan_response["focus_areas"].extend(
                    ["习惯建设", f"特别关注习惯: {', '.join(low_compliance_habits)}"]
                )

        return plan_response
    except Exception as e:
        logger.error(
            "Personalized plan generation failed", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Personalized plan generation failed",
        )
