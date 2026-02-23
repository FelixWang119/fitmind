from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.nutrition import Meal, MealItem
from app.models.emotional_support import EmotionalSupport, EmotionalState
from app.models.gamification import UserPoints, Achievement
from app.models.health_assessment import HealthAssessment
from app.schemas.health_assessment import (
    HealthAssessmentRequest,
    HealthAssessmentResponse,
    ComprehensiveHealthScore,
    HealthDimensionAssessment,
    HealthRecommendation,
    WellnessTrendAnalysis,
    RiskFactorAssessment,
    # New schemas
    HealthAssessmentCreateRequest,
    HealthAssessmentCreateResponse,
    HealthAssessmentRecord,
    HealthAssessmentHistoryItem,
    HealthAssessmentHistoryResponse,
    HealthAssessmentComparison,
    NutritionDetail,
    BehaviorDetail,
    EmotionDetail,
    DataCompleteness,
    AssessmentSuggestion,
)

logger = structlog.get_logger()

router = APIRouter()


@router.post("/assessment", response_model=HealthAssessmentResponse)
async def generate_health_assessment(
    assessment_req: HealthAssessmentRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成综合健康评估"""
    logger.info(
        "Generating health assessment",
        user_id=current_user.id,
        start_date=assessment_req.start_date,
        end_date=assessment_req.end_date,
    )

    # 确定评估周期
    start_date = assessment_req.start_date
    end_date = assessment_req.end_date or datetime.utcnow().date()

    # 1. 获取健康记录数据
    health_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
        )
        .order_by(HealthRecord.record_date.desc())
        .all()
    )

    # 2. 获取饮食记录
    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            func.date(Meal.meal_datetime) >= start_date,
            func.date(Meal.meal_datetime) <= end_date,
        )
        .all()
    )

    # 3. 获取运动记录
    exercise_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            (HealthRecord.exercise_minutes != None)
            | (HealthRecord.steps_count != None),
        )
        .all()
    )

    # 4. 获取习惯完成情况
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()

    # 获取习惯完成记录
    habit_completions = (
        db.query(HabitCompletion)
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(
            Habit.user_id == current_user.id,
            func.date(HabitCompletion.completion_date) >= start_date,
            func.date(HabitCompletion.completion_date) <= end_date,
        )
        .all()
    )

    # 5. 获取情感数据
    emotional_records = (
        db.query(EmotionalSupport)
        .join(EmotionalState)
        .filter(
            EmotionalSupport.user_id == current_user.id,
            EmotionalSupport.created_at
            >= datetime.combine(start_date, datetime.min.time()),
            EmotionalSupport.created_at
            <= datetime.combine(end_date, datetime.max.time()),
        )
        .order_by(EmotionalSupport.created_at.desc())
        .all()
    )

    # 6. 获取游戏化数据
    user_points = (
        db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
    )

    user_achievements = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == current_user.id,
            Achievement.achieved_at >= start_date,
            Achievement.achieved_at <= end_date,
        )
        .all()
    )

    # 数据分析和评估计算
    # Weight trend analysis
    weight_records = [hr for hr in health_records if hr.weight is not None]
    weight_trend = None
    weight_change = None
    if len(weight_records) >= 2:
        first_weight = weight_records[-1].weight / 1000.0  # Convert to kg
        last_weight = weight_records[0].weight / 1000.0  # Latest weight
        weight_change = last_weight - first_weight

        if weight_change < -0.5:  # Lost significant weight
            weight_trend = (
                "significantly_decreasing" if weight_change < -2.0 else "decreasing"
            )
        elif weight_change > 0.5:  # Gained significant weight
            weight_trend = (
                "significantly_increasing" if weight_change > 2.0 else "increasing"
            )
        else:
            weight_trend = "stable"

    # Nutrition analysis
    nutrition_data = {
        "total_calories": sum(m.calories or 0 for m in meals),
        "total_protien": sum(m.food_item.protein_per_serving for m in meals)
        if meals
        else 0,
        "total_carbs": sum(m.food_item.carbs_per_serving for m in meals)
        if meals
        else 0,
        "total_fat": sum(m.food_item.fat_per_serving for m in meals) if meals else 0,
    }

    avg_daily_calories = (
        nutrition_data["total_calories"] / (end_date - start_date).days
        if (end_date - start_date).days > 0
        else 0
    )

    # Exercise analysis
    total_exercise_minutes = sum(er.exercise_minutes or 0 for er in exercise_records)
    avg_exercise_minutes_daily = (
        total_exercise_minutes / (end_date - start_date).days
        if (end_date - start_date).days > 0
        else 0
    )

    total_steps = sum(er.steps_count or 0 for er in exercise_records)
    avg_daily_steps = (
        total_steps / (end_date - start_date).days
        if (end_date - start_date).days > 0
        else 0
    )

    # Habit completion analysis
    total_active_habits = len([h for h in habits if h.is_active])
    completed_habits = len(habit_completions)
    avg_daily_habits = (
        completed_habits / (end_date - start_date).days
        if (end_date - start_date).days > 0
        else 0
    )

    # Emotional patterns
    emotional_data = {}
    if emotional_records:
        emotional_types = [
            er.emotional_state.state_name
            for er in emotional_records
            if er.emotional_state
        ]
        if emotional_types:
            from collections import Counter

            emotional_counts = Counter(emotional_types)
            primary_emotion = (
                emotional_counts.most_common(1)[0][0] if emotional_counts else None
            )

            emotional_data = {
                "primary_emotion": primary_emotion,
                "emotional_diversity_index": len(emotional_counts)
                / len(
                    emotional_records
                ),  # Ratio of different emotions to total check-ins
                "mood_variety": len(
                    set(emotional_types)
                ),  # Number of different emotions experienced
            }

    # Calculate a composite health score based on various dimensions
    # Each dimension contributes to the overall health score based on normalized values
    weight_score = 20  # Max 20 points based on healthy weight tracking

    calorie_balance_score = 20  # Max 20 points based on balanced caloric intake
    exercise_score = (
        min(20, (avg_exercise_minutes_daily / 30) * 10)
        if avg_exercise_minutes_daily > 0
        else 0
    )  # Max points for 30+ mins daily exercise

    habit_adherence_score = (
        min(20, (avg_daily_habits / max(1, total_active_habits)) * 10)
        if total_active_habits > 0
        else 0
    )  # Max points if completing all active habits

    emotional_balance_score = (
        20 if emotional_data.get("emotional_diversity_index", 0) > 0.7 else 10
    )

    # Aggregate composite scores
    overall_health_score = (
        weight_score
        + calorie_balance_score
        + exercise_score
        + habit_adherence_score
        + emotional_balance_score
    )
    max_possible_score = 100  # Max points

    # Identify risk factors
    risk_factors = []
    if weight_trend == "significantly_increasing":
        risk_factors.append(
            RiskFactorAssessment(
                type="weight_increase",
                severity="medium",
                description="体重显著上升趋势，可能与健康目标不符",
                timeframe="short_term",
            )
        )

    if avg_exercise_minutes_daily < 15:
        risk_factors.append(
            RiskFactorAssessment(
                type="low_activity",
                severity="medium",
                description="每日运动量偏低（低于15分钟）",
                timeframe="ongoing",
            )
        )

    if avg_daily_calories < 1200:  # Generally too low for adults
        risk_factors.append(
            RiskFactorAssessment(
                type="low_calorie_intake",
                severity="high",
                description="热量摄入过低（低于1200卡/日）",
                timeframe="ongoing",
            )
        )

    # Generate personalized recommendations
    recommendations = []

    if weight_trend in ["increasing", "significantly_increasing"]:
        recommendations.append(
            HealthRecommendation(
                category="weight_management",
                title="体重管理指导",
                content="监测到体重上升趋势。建议检查饮食热量控制和运动频率，与营养师讨论调整方案。",
                priority="medium",
                action_needed=True,
            )
        )

    if avg_exercise_minutes_daily < 30:
        recommendations.append(
            HealthRecommendation(
                category="physical_activity",
                title="运动量增加计划",
                content=f"当前平均每日运动{avg_exercise_minutes_daily:.0f}分钟，建议增加到30-60分钟以促进健康。",
                priority="medium",
                action_needed=True,
            )
        )

    if avg_daily_steps < 6000:
        recommendations.append(
            HealthRecommendation(
                category="daily_mobility",
                title="增加日常步数",
                content=f"当前平均每日步数{avg_daily_steps:.0f}，建议逐步增加到每日6000-10000步。",
                priority="low",
                action_needed=True,
            )
        )

    # If habit adherence is low
    if avg_daily_habits < 1 and total_active_habits > 0:
        recommendations.append(
            HealthRecommendation(
                category="habit_formation",
                title="提高习惯坚持性",
                content=f"当前习惯坚持性较低。建议选择1-2个容易完成的小习惯，逐步形成规律。",
                priority="medium",
                action_needed=True,
            )
        )

    # Create the assessment response with multiple dimensions
    assessment = HealthAssessmentResponse(
        user_id=current_user.id,
        assessment_period_start=start_date.isoformat(),
        assessment_period_end=end_date.isoformat(),
        timestamp=datetime.utcnow().isoformat(),
        overall_health_score=ComprehensiveHealthScore(
            score=overall_health_score,
            max_score=max_possible_score,
            category="normal"
            if 60 <= overall_health_score <= 80
            else "good"
            if overall_health_score > 80
            else "needs_improvement"
            if overall_health_score >= 40
            else "concerning",
            interpretation=(
                "您的健康状况目前处于正常水平。继续保持现有健康习惯以维持健康状态。"
                if 60 <= overall_health_score <= 80
                else "您的健康状况良好！保持积极的健康行为会带来长期益处。"
                if overall_health_score > 80
                else "您的健康状况有待改进。建议关注以下建议以实现更好健康状况。"
                if overall_health_score >= 40
                else "健康状况令人担忧。强烈建议咨询医疗专业人员并采取积极措施。"
            ),
        ),
        health_dimensions={
            "weight_and_body_composition": HealthDimensionAssessment(
                score=weight_score,
                max_score=20,
                status=weight_trend or "no_data",
                metrics={
                    "starting_weight_kg": weight_records[-1].weight / 1000.0
                    if weight_records
                    else None,
                    "current_weight_kg": weight_records[0].weight / 1000.0
                    if weight_records
                    else None,
                    "weight_change_kg": weight_change
                    if weight_records and len(weight_records) > 1
                    else 0,
                    "weight_check_frequency_per_week": (
                        len(weight_records) / max((end_date - start_date).days, 1)
                    )
                    * 7,
                },
                interpretation=(
                    f"体重{('下降' if weight_change < 0 else '增加' if weight_change > 0 else '稳定')}了{abs(weight_change) if weight_change is not None else 0:.2f}kg"
                )
                if weight_records and len(weight_records) > 1
                else "暂无体重变化数据",
            ),
            "nutrition_and_diet": HealthDimensionAssessment(
                score=min(20, avg_daily_calories / 100)
                if avg_daily_calories > 0
                else 5,  # Normalize against 2000 cal target
                max_score=20,
                status="balanced"
                if 1500 <= avg_daily_calories <= 2500
                else "high"
                if avg_daily_calories > 2500
                else "low",
                metrics={
                    "avg_daily_calories": avg_daily_calories,
                    "total_calories": nutrition_data["total_calories"],
                    "avg_daily_protein_g": nutrition_data["total_protein"]
                    / (end_date - start_date).days
                    if (end_date - start_date).days > 0
                    else 0,
                    "avg_daily_carbs_g": nutrition_data["total_carbs"]
                    / (end_date - start_date).days
                    if (end_date - start_date).days > 0
                    else 0,
                    "avg_daily_fat_g": nutrition_data["total_fat"]
                    / (end_date - start_date).days
                    if (end_date - start_date).days > 0
                    else 0,
                },
                interpretation=f"平均每日摄入{avg_daily_calories:.0f}卡路里，饮食结构合理度需关注营养均衡性",
            ),
            "physical_activity": HealthDimensionAssessment(
                score=exercise_score,
                max_score=20,
                status="active"
                if avg_exercise_minutes_daily >= 30
                else "moderate"
                if avg_exercise_minutes_daily >= 15
                else "inactive",
                metrics={
                    "avg_daily_exercise_minutes": avg_exercise_minutes_daily,
                    "total_exercise_minutes": total_exercise_minutes,
                    "avg_daily_steps": int(avg_daily_steps),
                    "total_steps": total_steps,
                    "active_days": len(exercise_records),
                },
                interpretation=f"平均每日运动{avg_exercise_minutes_daily:.0f}分钟，共{int(avg_daily_steps)}步",
            ),
            "behavior_and_habits": HealthDimensionAssessment(
                score=habit_adherence_score,
                max_score=20,
                status="great"
                if avg_daily_habits >= 2
                else "good"
                if avg_daily_habits >= 1
                else "improvable",
                metrics={
                    "total_active_habits": total_active_habits,
                    "completed_habits_in_period": completed_habits,
                    "avg_daily_habit_completion": avg_daily_habits,
                    "streak_days_current": 0,  # Placeholder - would need streak tracking
                },
                interpretation=f"正在进行{total_active_habits}个习惯，平均每日完成{avg_daily_habits:.2f}个习惯",
            ),
            "emotional_wellbeing": HealthDimensionAssessment(
                score=emotional_balance_score,
                max_score=20,
                status="balanced"
                if emotional_data.get("emotional_diversity_index", 0) > 0.5
                else "need_attention",
                metrics={
                    "emotional_check_ins_count": len(emotional_records),
                    "primary_emotion_type": emotional_data.get(
                        "primary_emotion", "no_records"
                    ),
                    "emotional_diversity": emotional_data.get(
                        "emotional_diversity_index", 0
                    ),
                    "emotional_range_variety": emotional_data.get("mood_variety", 0),
                },
                interpretation=f"记录了{len(emotional_records)}次情绪检查，主要情绪为{emotional_data.get('primary_emotion', '无')}",
            ),
        },
        wellness_trends=WellnessTrendAnalysis(
            period_days=(end_date - start_date).days,
            trends_identified=[
                f"体重变化: {weight_change:+.2f}kg"
                if len(weight_records) > 1
                else "无足够体重记录",
                f"饮食规律: 平均每日{avg_daily_calories:.0f}卡路里摄入"
                if avg_daily_calories > 0
                else "无饮食记录",
                f"运动持续: 平均每日{avg_exercise_minutes_daily:.0f}分钟"
                if avg_exercise_minutes_daily > 0
                else "无运动记录",
                f"习惯维持: 平均每日完成{avg_daily_habits:.2f}个习惯"
                if avg_daily_habits > 0
                else "无习惯记录",
            ],
            patterns=[
                "情绪多样性适中",
                "持续性较好",
            ],  # Inference patterns based on data diversity
            predictive_insights=[
                f"如保持当前趋势，预计体重在未来{abs(weight_change) * 10 if weight_change is not None else 0:+.2f}kg变化"
            ]
            if weight_change != 0
            else [],
        ),
        risk_assessment=risk_factors,
        personalized_recommendations=recommendations,
        data_quality_score=min(
            100,
            (
                len(health_records)
                + len(meals)
                + len(habit_completions)
                + len(exercise_records)
                + len(emotional_records)
            )
            * 2,
        )
        if health_records
        or meals
        or habit_completions
        or exercise_records
        or emotional_records
        else 0,
    )

    logger.info(
        "Health assessment generated",
        user_id=current_user.id,
        overall_score=overall_health_score,
    )

    return assessment


@router.get("/assessment-summary", response_model=dict)
async def get_health_assessment_summary(
    days_back: int = Query(30, description="回溯评估天数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康评估摘要"""
    logger.info("Getting health assessment summary", user_id=current_user.id)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)

    # 获取核心健康指标
    recent_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
        )
        .order_by(HealthRecord.record_date.desc())
        .all()
    )

    # Calculate summary data
    weights = [r.weight / 1000.0 for r in recent_records if r.weight is not None]
    avg_weight = sum(weights) / len(weights) if weights else 0
    current_weight = weights[0] if weights else 0
    initial_weight = weights[-1] if len(weights) > 1 else (weights[0] if weights else 0)

    weight_change = current_weight - initial_weight if len(weights) > 1 else 0

    # Exercise summary
    exercise_records = [
        r for r in recent_records if r.exercise_minutes or r.steps_count
    ]

    avg_exercise = (
        sum(r.exercise_minutes or 0 for r in exercise_records) / len(exercise_records)
        if exercise_records
        else 0
    )
    total_steps = sum(r.steps_count or 0 for r in exercise_records)

    # Habit data
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
    active_habits = (
        [h for h in habits if h.is_active] if isinstance(habits, list) else habits
    )  # This may need adjustment

    summary = {
        "period_days": days_back,
        "weight_summary": {
            "current_weight_kg": round(current_weight, 2),
            "initial_weight_kg": round(initial_weight, 2),
            "weight_change_kg": round(weight_change, 2),
            "weight_tracking_days": len(weights),
        },
        "activity_summary": {
            "avg_daily_exercise_min": round(avg_exercise, 2),
            "total_steps": total_steps,
            "tracked_days": len(exercise_records),
        },
        "habits_summary": {
            "total_habits": 0,  # This needs to be calculated differently
        },
        "overall_interpretation": (
            f"体重{('减少' if weight_change < -0.5 else '增加' if weight_change > 0.5 else '稳定')}，运动量{'适量' if avg_exercise >= 30 else '偏低'}"
            if len(weights) and len(exercise_records)
            else "继续追踪以获得全面评估"
        ),
        "last_updated": datetime.utcnow().isoformat(),
    }

    return summary


# =====================================================
# 新增端点：健康评估记录管理 (Story 6.1)
# =====================================================


def _get_grade(score: int) -> str:
    """根据评分获取等级"""
    if score >= 80:
        return "优秀"
    elif score >= 60:
        return "良好"
    elif score >= 40:
        return "一般"
    else:
        return "需改善"


def _calculate_nutrition_score_v2(
    meals: List[Meal], user: UserModel, days: int
) -> tuple[int, Dict, List[Dict]]:
    """计算营养评分 v2（Story 6.1）"""

    # 1. 热量均衡度 (30分)
    total_calories = sum(m.calories or 0 for m in meals)
    avg_daily_calories = total_calories / days if days > 0 else 0

    # 估算TDEE
    tdee = 2000  # 默认值
    if user.initial_weight and user.height and user.age:
        # 基础代谢率计算
        weight_kg = user.initial_weight / 1000
        if user.gender == "male":
            bmr = 10 * weight_kg + 6.25 * user.height - 5 * user.age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * user.height - 5 * user.age - 161

        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        tdee = bmr * activity_multipliers.get(user.activity_level, 1.2)

    calorie_deviation = abs(avg_daily_calories - tdee) / tdee if tdee > 0 else 1
    if calorie_deviation < 0.1:
        calorie_score = 30
    elif calorie_deviation < 0.2:
        calorie_score = 25
    elif calorie_deviation < 0.3:
        calorie_score = 20
    else:
        calorie_score = 15

    # 2. 宏量营养素平衡 (25分)
    total_protein = sum(
        m.food_item.protein_per_serving if m.food_item else 0 for m in meals
    )
    total_carbs = sum(
        m.food_item.carbs_per_serving if m.food_item else 0 for m in meals
    )
    total_fat = sum(m.food_item.fat_per_serving if m.food_item else 0 for m in meals)

    total_macro = total_protein + total_carbs + total_fat
    if total_macro > 0:
        protein_ratio = total_protein / total_macro
        carbs_ratio = total_carbs / total_macro
        fat_ratio = total_fat / total_macro

        # 理想比例：蛋白质 20-30%, 碳水 40-50%, 脂肪 20-30%
        protein_score = (
            25
            if 0.2 <= protein_ratio <= 0.3
            else 20
            if 0.15 <= protein_ratio <= 0.35
            else 15
        )
        carbs_score = (
            25 if 0.4 <= carbs_ratio <= 0.5 else 20 if 0.3 <= carbs_ratio <= 0.6 else 15
        )
        fat_score = (
            25 if 0.2 <= fat_ratio <= 0.3 else 20 if 0.15 <= fat_ratio <= 0.35 else 15
        )
        macro_balance = (protein_score + carbs_score + fat_score) / 3
    else:
        macro_balance = 15

    # 3. 饮食规律性 (20分)
    # 检查是否有规律的三餐
    meal_times = {}
    for meal in meals:
        if meal.meal_datetime:
            day = meal.meal_datetime.date()
            meal_type = meal.meal_type or "other"
            if day not in meal_times:
                meal_times[day] = set()
            meal_times[day].add(meal_type)

    regular_days = sum(1 for day_meals in meal_times.values() if len(day_meals) >= 3)
    regularity_score = (
        20 if regular_days >= days * 0.7 else 15 if regular_days >= days * 0.5 else 10
    )

    # 4. 营养多样性 (15分)
    food_items = set()
    for meal in meals:
        if meal.food_item:
            food_items.add(meal.food_item.id)
    diversity_score = min(15, len(food_items))

    # 5. 健康饮食习惯 (10分)
    # 简化的健康饮食评分
    healthy_score = 8

    # 计算总分
    nutrition_score = int(
        calorie_score
        + macro_balance
        + regularity_score
        + diversity_score
        + healthy_score
    )
    nutrition_score = min(100, max(0, nutrition_score))

    # 构建详情
    details = {
        "calorie_balance": calorie_score,
        "macro_balance": macro_balance,
        "diet_regularity": regularity_score,
        "nutrition_diversity": diversity_score,
        "healthy_habits": healthy_score,
        "avg_daily_calories": round(avg_daily_calories, 1),
        "target_calories": round(tdee, 1),
        "protein_ratio": round(protein_ratio * 100, 1) if total_macro > 0 else 0,
        "carbs_ratio": round(carbs_ratio * 100, 1) if total_macro > 0 else 0,
        "fat_ratio": round(fat_ratio * 100, 1) if total_macro > 0 else 0,
        "meal_regularity_score": regularity_score,
    }

    # 生成建议
    suggestions = []
    if calorie_score < 25:
        suggestions.append(
            {
                "category": "nutrition",
                "content": f"当前每日平均热量摄入{avg_daily_calories:.0f}千卡，建议根据TDEE({tdee:.0f}千卡)调整",
                "priority": "high",
            }
        )
    if macro_balance < 20:
        suggestions.append(
            {
                "category": "nutrition",
                "content": "建议优化宏量营养素比例，增加蛋白质摄入",
                "priority": "medium",
            }
        )
    if regularity_score < 15:
        suggestions.append(
            {
                "category": "nutrition",
                "content": "建议保持规律的三餐时间，避免暴饮暴食",
                "priority": "medium",
            }
        )
    if len(food_items) < 10:
        suggestions.append(
            {
                "category": "nutrition",
                "content": "建议增加食物多样性，每天摄入至少10种不同食物",
                "priority": "low",
            }
        )

    return nutrition_score, details, suggestions


def _calculate_behavior_score_v2(
    habits: List[Habit],
    habit_completions: List[HabitCompletion],
    exercise_records: List[HealthRecord],
    sleep_records: List[HealthRecord],
    days: int,
) -> tuple[int, Dict, List[Dict]]:
    """计算行为评分 v2（Story 6.1）"""

    active_habits = [h for h in habits if h.is_active]

    # 1. 习惯完成率 (30分)
    if active_habits and days > 0:
        total_expected = len(active_habits) * days
        completion_rate = (
            len(habit_completions) / total_expected if total_expected > 0 else 0
        )
        habit_score = int(min(30, completion_rate * 30))
    else:
        habit_score = 15

    # 2. 运动频率 (25分)
    if exercise_records:
        exercise_days = len(
            set(r.record_date for r in exercise_records if r.record_date)
        )
        weekly_days = exercise_days / (days / 7) if days > 0 else 0
        if weekly_days >= 5:
            exercise_score = 25
        elif weekly_days >= 3:
            exercise_score = 20
        elif weekly_days >= 1:
            exercise_score = 15
        else:
            exercise_score = 10
    else:
        exercise_score = 10

    # 3. 睡眠质量 (25分)
    if sleep_records:
        sleep_hours = [r.sleep_hours for r in sleep_records if r.sleep_hours]
        if sleep_hours:
            avg_sleep = sum(sleep_hours) / len(sleep_hours)
            if 7 <= avg_sleep <= 9:
                sleep_quality = 25
            elif 6 <= avg_sleep < 7 or 9 < avg_sleep <= 10:
                sleep_quality = 20
            elif 5 <= avg_sleep < 6 or 10 < avg_sleep <= 11:
                sleep_quality = 15
            else:
                sleep_quality = 10
        else:
            sleep_quality = 15
    else:
        sleep_quality = 15

    # 4. 作息规律性 (20分)
    # 简化版：检查记录时间的一致性
    routine_score = 15

    # 计算总分
    behavior_score = habit_score + exercise_score + sleep_quality + routine_score
    behavior_score = min(100, max(0, behavior_score))

    # 计算详细指标
    avg_exercise_minutes = (
        sum(r.exercise_minutes or 0 for r in exercise_records) / days
        if days > 0 and exercise_records
        else 0
    )
    avg_steps = (
        sum(r.steps_count or 0 for r in exercise_records) / days
        if days > 0 and exercise_records
        else 0
    )
    avg_sleep_hours = (
        sum(r.sleep_hours or 0 for r in sleep_records) / len(sleep_records)
        if sleep_records
        else 0
    )

    details = {
        "habit_completion_rate": habit_score,
        "exercise_frequency": exercise_score,
        "sleep_quality": sleep_quality,
        "routine_regularity": routine_score,
        "total_active_habits": len(active_habits),
        "completed_habits": len(habit_completions),
        "avg_daily_exercise_minutes": round(avg_exercise_minutes, 1),
        "weekly_exercise_days": round(exercise_days / (days / 7) if days > 0 else 0, 1),
        "avg_daily_steps": round(avg_steps, 1),
        "avg_sleep_hours": round(avg_sleep_hours, 1),
        "sleep_quality_score": sleep_quality,
    }

    # 生成建议
    suggestions = []
    if habit_score < 25:
        suggestions.append(
            {
                "category": "behavior",
                "content": "建议提高习惯完成率，可以从每天完成1-2个核心习惯开始",
                "priority": "high",
            }
        )
    if exercise_score < 20:
        suggestions.append(
            {
                "category": "behavior",
                "content": f"当前每周运动{exercise_days / (days / 7) if days > 0 else 0:.1f}天，建议每周至少运动3-5天",
                "priority": "high",
            }
        )
    if sleep_quality < 20:
        suggestions.append(
            {
                "category": "behavior",
                "content": f"当前平均睡眠{avg_sleep_hours:.1f}小时，建议保持7-9小时的充足睡眠",
                "priority": "medium",
            }
        )

    return behavior_score, details, suggestions


def _calculate_emotion_score_v2(
    emotional_states: List[EmotionalState],
) -> tuple[int, Dict, List[Dict]]:
    """计算情感评分 v2（Story 6.1）"""

    if not emotional_states:
        return (
            50,
            {
                "emotional_stability": 15,
                "positive_emotion_ratio": 15,
                "stress_level": 10,
                "psychological_resilience": 10,
                "emotional_check_ins": 0,
                "primary_emotion": "无记录",
                "positive_ratio": 0,
                "emotional_variety": 0,
                "stress_indicators": [],
            },
            [
                {
                    "category": "emotion",
                    "content": "建议开始记录情绪状态，了解自己的情绪变化",
                    "priority": "medium",
                }
            ],
        )

    # 1. 情绪稳定性 (30分)
    intensities = [e.intensity for e in emotional_states if e.intensity]
    if len(intensities) >= 7:
        avg_intensity = sum(intensities) / len(intensities)
        variance = sum((i - avg_intensity) ** 2 for i in intensities) / len(intensities)
        std_dev = variance**0.5
        cv = (std_dev / avg_intensity) * 100 if avg_intensity > 0 else 100

        if cv < 20:
            stability_score = 30
        elif cv < 40:
            stability_score = 25
        elif cv < 60:
            stability_score = 20
        else:
            stability_score = 15
    else:
        stability_score = 20

    # 2. 积极情绪占比 (25分)
    positive_emotions = {
        "happy",
        "excited",
        "calm",
        "content",
        "grateful",
        "joy",
        "love",
    }
    positive_count = sum(
        1 for e in emotional_states if e.emotion_type in positive_emotions
    )
    positive_ratio = positive_count / len(emotional_states)

    if positive_ratio >= 0.7:
        positive_score = 25
    elif positive_ratio >= 0.5:
        positive_score = 20
    elif positive_ratio >= 0.3:
        positive_score = 15
    else:
        positive_score = 10

    # 3. 压力水平 (25分) - 反向评分
    negative_emotions = {"sad", "angry", "anxious", "stressed", "fear", "frustrated"}
    stress_count = sum(
        1 for e in emotional_states if e.emotion_type in negative_emotions
    )
    stress_ratio = stress_count / len(emotional_states)

    if stress_ratio < 0.2:
        stress_score = 25
    elif stress_ratio < 0.4:
        stress_score = 20
    elif stress_ratio < 0.6:
        stress_score = 15
    else:
        stress_score = 10

    # 4. 心理韧性 (20分)
    # 基于情绪记录的多样性和稳定性综合评估
    unique_emotions = len(set(e.emotion_type for e in emotional_states))
    if unique_emotions >= 5 and stability_score >= 20:
        resilience_score = 20
    elif unique_emotions >= 3:
        resilience_score = 15
    else:
        resilience_score = 10

    # 计算总分
    emotion_score = stability_score + positive_score + stress_score + resilience_score
    emotion_score = min(100, max(0, emotion_score))

    # 统计主要情绪
    from collections import Counter

    emotion_types = [e.emotion_type for e in emotional_states]
    emotion_counts = Counter(emotion_types)
    primary_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "未知"

    details = {
        "emotional_stability": stability_score,
        "positive_emotion_ratio": positive_score,
        "stress_level": stress_score,
        "psychological_resilience": resilience_score,
        "emotional_check_ins": len(emotional_states),
        "primary_emotion": primary_emotion,
        "positive_ratio": round(positive_ratio * 100, 1),
        "emotional_variety": unique_emotions,
        "stress_indicators": [
            e.emotion_type
            for e in emotional_states
            if e.emotion_type in negative_emotions
        ][:3],
    }

    # 生成建议
    suggestions = []
    if positive_score < 20:
        suggestions.append(
            {
                "category": "emotion",
                "content": "积极情绪占比偏低，建议多参与让自己感到快乐的活动",
                "priority": "high",
            }
        )
    if stress_score < 20:
        suggestions.append(
            {
                "category": "emotion",
                "content": "检测到一定的压力水平，建议尝试冥想或深呼吸放松",
                "priority": "high",
            }
        )
    if stability_score < 25:
        suggestions.append(
            {
                "category": "emotion",
                "content": "情绪波动较大，建议记录情绪触发因素并学习情绪管理技巧",
                "priority": "medium",
            }
        )

    return emotion_score, details, suggestions


@router.post("/assessments", response_model=HealthAssessmentCreateResponse)
async def create_health_assessment(
    request: HealthAssessmentCreateRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    创建并保存健康评估 (Story 6.1 - AC 6.1.1, AC 6.1.2, AC 6.1.7)

    - 执行三维度健康评估（营养、行为、情感）
    - 计算综合健康评分
    - 保存评估记录到数据库
    """
    logger.info(
        "Creating health assessment",
        user_id=current_user.id,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # 确定评估周期
    end_date = request.end_date or datetime.utcnow().date()
    start_date = request.start_date or (end_date - timedelta(days=7))
    days = (end_date - start_date).days + 1

    # 1. 获取饮食记录
    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            func.date(Meal.meal_datetime) >= start_date,
            func.date(Meal.meal_datetime) <= end_date,
        )
        .all()
    )

    # 2. 获取健康记录（运动和睡眠）
    health_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
        )
        .all()
    )

    exercise_records = [
        r for r in health_records if r.exercise_minutes or r.steps_count
    ]
    sleep_records = [r for r in health_records if r.sleep_hours]

    # 3. 获取习惯数据
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    habit_completions = (
        db.query(HabitCompletion)
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(
            Habit.user_id == current_user.id,
            func.date(HabitCompletion.completion_date) >= start_date,
            func.date(HabitCompletion.completion_date) <= end_date,
        )
        .all()
    )

    # 4. 获取情感数据
    emotional_states = (
        db.query(EmotionalState)
        .filter(
            EmotionalState.user_id == current_user.id,
            EmotionalState.recorded_at
            >= datetime.combine(start_date, datetime.min.time()),
            EmotionalState.recorded_at
            <= datetime.combine(end_date, datetime.max.time()),
        )
        .all()
    )

    # 计算各维度评分
    nutrition_score, nutrition_details, nutrition_suggestions = (
        _calculate_nutrition_score_v2(meals, current_user, days)
    )
    behavior_score, behavior_details, behavior_suggestions = (
        _calculate_behavior_score_v2(
            habits, habit_completions, exercise_records, sleep_records, days
        )
    )
    emotion_score, emotion_details, emotion_suggestions = _calculate_emotion_score_v2(
        emotional_states
    )

    # 计算综合评分 (权重: 营养35%, 行为35%, 情感30%)
    overall_score = int(
        nutrition_score * 0.35 + behavior_score * 0.35 + emotion_score * 0.30
    )
    overall_grade = _get_grade(overall_score)

    # 检查数据完整性 (AC 6.1.5)
    food_logs_complete = len(meals) >= days * 0.5  # 至少50%的天数有记录
    habit_logs_complete = len(habit_completions) >= days * 0.3  # 至少30%的天数有记录
    sleep_logs_complete = len(sleep_records) >= days * 0.5  # 至少50%的天数有记录

    completeness_score = 0
    if food_logs_complete:
        completeness_score += 33
    if habit_logs_complete:
        completeness_score += 33
    if sleep_logs_complete:
        completeness_score += 34

    data_completeness = {
        "food_logs_complete": food_logs_complete,
        "food_logs_days": len(
            set(m.meal_datetime.date() for m in meals if m.meal_datetime)
        ),
        "habit_logs_complete": habit_logs_complete,
        "habit_logs_days": len(set(c.completion_date for c in habit_completions)),
        "sleep_logs_complete": sleep_logs_complete,
        "sleep_logs_days": len(sleep_records),
        "overall_completeness": completeness_score,
    }

    # 生成综合建议
    overall_suggestions = []
    weak_dimensions = []
    if nutrition_score < 60:
        weak_dimensions.append("营养")
    if behavior_score < 60:
        weak_dimensions.append("行为")
    if emotion_score < 60:
        weak_dimensions.append("情感")

    if weak_dimensions:
        overall_suggestions.append(
            {
                "category": "overall",
                "content": f"您的{', '.join(weak_dimensions)}维度需要重点关注，建议优先改善",
                "priority": "high",
            }
        )
    else:
        overall_suggestions.append(
            {
                "category": "overall",
                "content": "您的整体健康状况良好，请继续保持良好的生活习惯",
                "priority": "low",
            }
        )

    # 保存评估记录
    assessment = HealthAssessment(
        user_id=current_user.id,
        assessment_date=datetime.utcnow(),
        overall_score=overall_score,
        overall_grade=overall_grade,
        nutrition_score=nutrition_score,
        nutrition_details=nutrition_details,
        nutrition_suggestions=nutrition_suggestions,
        behavior_score=behavior_score,
        behavior_details=behavior_details,
        behavior_suggestions=behavior_suggestions,
        emotion_score=emotion_score,
        emotion_details=emotion_details,
        emotion_suggestions=emotion_suggestions,
        overall_suggestions=overall_suggestions,
        data_completeness=data_completeness,
        assessment_period_start=datetime.combine(start_date, datetime.min.time()),
        assessment_period_end=datetime.combine(end_date, datetime.max.time()),
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    logger.info(
        "Health assessment created",
        user_id=current_user.id,
        assessment_id=assessment.id,
        overall_score=overall_score,
    )

    # 构建响应
    assessment_record = HealthAssessmentRecord(
        id=assessment.id,
        user_id=assessment.user_id,
        assessment_date=assessment.assessment_date.isoformat(),
        overall_score=assessment.overall_score,
        overall_grade=assessment.overall_grade,
        nutrition_score=assessment.nutrition_score,
        nutrition_details=NutritionDetail(**assessment.nutrition_details),
        nutrition_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.nutrition_suggestions
        ],
        behavior_score=assessment.behavior_score,
        behavior_details=BehaviorDetail(**assessment.behavior_details),
        behavior_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.behavior_suggestions
        ],
        emotion_score=assessment.emotion_score,
        emotion_details=EmotionDetail(**assessment.emotion_details),
        emotion_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.emotion_suggestions
        ],
        overall_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.overall_suggestions
        ],
        data_completeness=DataCompleteness(**assessment.data_completeness),
        assessment_period_start=assessment.assessment_period_start.isoformat()
        if assessment.assessment_period_start
        else None,
        assessment_period_end=assessment.assessment_period_end.isoformat()
        if assessment.assessment_period_end
        else None,
        created_at=assessment.created_at.isoformat(),
    )

    return HealthAssessmentCreateResponse(
        success=True,
        message="健康评估已生成并保存",
        assessment=assessment_record,
    )


@router.get("/assessments/latest", response_model=HealthAssessmentRecord)
async def get_latest_assessment(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取最新健康评估 (Story 6.1 - AC 6.1.7)
    """
    logger.info("Getting latest health assessment", user_id=current_user.id)

    assessment = (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == current_user.id)
        .order_by(HealthAssessment.assessment_date.desc())
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="暂无健康评估记录，请先生成评估",
        )

    return HealthAssessmentRecord(
        id=assessment.id,
        user_id=assessment.user_id,
        assessment_date=assessment.assessment_date.isoformat(),
        overall_score=assessment.overall_score,
        overall_grade=assessment.overall_grade,
        nutrition_score=assessment.nutrition_score,
        nutrition_details=NutritionDetail(**assessment.nutrition_details),
        nutrition_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.nutrition_suggestions
        ],
        behavior_score=assessment.behavior_score,
        behavior_details=BehaviorDetail(**assessment.behavior_details),
        behavior_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.behavior_suggestions
        ],
        emotion_score=assessment.emotion_score,
        emotion_details=EmotionDetail(**assessment.emotion_details),
        emotion_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.emotion_suggestions
        ],
        overall_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.overall_suggestions
        ],
        data_completeness=DataCompleteness(**assessment.data_completeness),
        assessment_period_start=assessment.assessment_period_start.isoformat()
        if assessment.assessment_period_start
        else None,
        assessment_period_end=assessment.assessment_period_end.isoformat()
        if assessment.assessment_period_end
        else None,
        created_at=assessment.created_at.isoformat(),
    )


@router.get("/assessments/history", response_model=HealthAssessmentHistoryResponse)
async def get_assessment_history(
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取健康评估历史 (Story 6.1 - AC 6.1.4)
    """
    logger.info(
        "Getting health assessment history", user_id=current_user.id, limit=limit
    )

    assessments = (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == current_user.id)
        .order_by(HealthAssessment.assessment_date.desc())
        .limit(limit)
        .all()
    )

    total_count = (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == current_user.id)
        .count()
    )

    history_items = [
        HealthAssessmentHistoryItem(
            id=a.id,
            assessment_date=a.assessment_date.isoformat(),
            overall_score=a.overall_score,
            overall_grade=a.overall_grade,
            nutrition_score=a.nutrition_score,
            behavior_score=a.behavior_score,
            emotion_score=a.emotion_score,
        )
        for a in assessments
    ]

    return HealthAssessmentHistoryResponse(
        assessments=history_items,
        total_count=total_count,
    )


@router.get("/assessments/{assessment_id}", response_model=HealthAssessmentRecord)
async def get_assessment_by_id(
    assessment_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取指定健康评估详情 (Story 6.1 - AC 6.1.3)
    """
    logger.info(
        "Getting health assessment by id",
        user_id=current_user.id,
        assessment_id=assessment_id,
    )

    assessment = (
        db.query(HealthAssessment)
        .filter(
            HealthAssessment.id == assessment_id,
            HealthAssessment.user_id == current_user.id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在",
        )

    return HealthAssessmentRecord(
        id=assessment.id,
        user_id=assessment.user_id,
        assessment_date=assessment.assessment_date.isoformat(),
        overall_score=assessment.overall_score,
        overall_grade=assessment.overall_grade,
        nutrition_score=assessment.nutrition_score,
        nutrition_details=NutritionDetail(**assessment.nutrition_details),
        nutrition_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.nutrition_suggestions
        ],
        behavior_score=assessment.behavior_score,
        behavior_details=BehaviorDetail(**assessment.behavior_details),
        behavior_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.behavior_suggestions
        ],
        emotion_score=assessment.emotion_score,
        emotion_details=EmotionDetail(**assessment.emotion_details),
        emotion_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.emotion_suggestions
        ],
        overall_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.overall_suggestions
        ],
        data_completeness=DataCompleteness(**assessment.data_completeness),
        assessment_period_start=assessment.assessment_period_start.isoformat()
        if assessment.assessment_period_start
        else None,
        assessment_period_end=assessment.assessment_period_end.isoformat()
        if assessment.assessment_period_end
        else None,
        created_at=assessment.created_at.isoformat(),
    )


@router.get(
    "/assessments/{assessment_id}/comparison", response_model=HealthAssessmentComparison
)
async def get_assessment_comparison(
    assessment_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取健康评估对比（与上次评估）(Story 6.1 - AC 6.1.4)
    """
    logger.info(
        "Getting health assessment comparison",
        user_id=current_user.id,
        assessment_id=assessment_id,
    )

    # 获取当前评估
    assessment = (
        db.query(HealthAssessment)
        .filter(
            HealthAssessment.id == assessment_id,
            HealthAssessment.user_id == current_user.id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在",
        )

    # 获取上次评估
    previous_assessment = (
        db.query(HealthAssessment)
        .filter(
            HealthAssessment.user_id == current_user.id,
            HealthAssessment.assessment_date < assessment.assessment_date,
        )
        .order_by(HealthAssessment.assessment_date.desc())
        .first()
    )

    # 计算变化
    trends = {}
    if previous_assessment:
        overall_change = assessment.overall_score - previous_assessment.overall_score
        overall_change_percent = (
            (overall_change / previous_assessment.overall_score * 100)
            if previous_assessment.overall_score > 0
            else 0
        )

        nutrition_change = (
            assessment.nutrition_score - previous_assessment.nutrition_score
        )
        behavior_change = assessment.behavior_score - previous_assessment.behavior_score
        emotion_change = assessment.emotion_score - previous_assessment.emotion_score

        trends["nutrition"] = (
            "improving"
            if nutrition_change > 0
            else ("stable" if nutrition_change == 0 else "declining")
        )
        trends["behavior"] = (
            "improving"
            if behavior_change > 0
            else ("stable" if behavior_change == 0 else "declining")
        )
        trends["emotion"] = (
            "improving"
            if emotion_change > 0
            else ("stable" if emotion_change == 0 else "declining")
        )
    else:
        overall_change = None
        overall_change_percent = None
        nutrition_change = None
        behavior_change = None
        emotion_change = None
        trends = {"nutrition": "stable", "behavior": "stable", "emotion": "stable"}

    # 构建当前评估记录
    current_record = HealthAssessmentRecord(
        id=assessment.id,
        user_id=assessment.user_id,
        assessment_date=assessment.assessment_date.isoformat(),
        overall_score=assessment.overall_score,
        overall_grade=assessment.overall_grade,
        nutrition_score=assessment.nutrition_score,
        nutrition_details=NutritionDetail(**assessment.nutrition_details),
        nutrition_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.nutrition_suggestions
        ],
        behavior_score=assessment.behavior_score,
        behavior_details=BehaviorDetail(**assessment.behavior_details),
        behavior_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.behavior_suggestions
        ],
        emotion_score=assessment.emotion_score,
        emotion_details=EmotionDetail(**assessment.emotion_details),
        emotion_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.emotion_suggestions
        ],
        overall_suggestions=[
            AssessmentSuggestion(**s) for s in assessment.overall_suggestions
        ],
        data_completeness=DataCompleteness(**assessment.data_completeness),
        assessment_period_start=assessment.assessment_period_start.isoformat()
        if assessment.assessment_period_start
        else None,
        assessment_period_end=assessment.assessment_period_end.isoformat()
        if assessment.assessment_period_end
        else None,
        created_at=assessment.created_at.isoformat(),
    )

    # 构建上次评估记录（如果存在）
    previous_record = None
    if previous_assessment:
        previous_record = HealthAssessmentRecord(
            id=previous_assessment.id,
            user_id=previous_assessment.user_id,
            assessment_date=previous_assessment.assessment_date.isoformat(),
            overall_score=previous_assessment.overall_score,
            overall_grade=previous_assessment.overall_grade,
            nutrition_score=previous_assessment.nutrition_score,
            nutrition_details=NutritionDetail(**previous_assessment.nutrition_details),
            nutrition_suggestions=[
                AssessmentSuggestion(**s)
                for s in previous_assessment.nutrition_suggestions
            ],
            behavior_score=previous_assessment.behavior_score,
            behavior_details=BehaviorDetail(**previous_assessment.behavior_details),
            behavior_suggestions=[
                AssessmentSuggestion(**s)
                for s in previous_assessment.behavior_suggestions
            ],
            emotion_score=previous_assessment.emotion_score,
            emotion_details=EmotionDetail(**previous_assessment.emotion_details),
            emotion_suggestions=[
                AssessmentSuggestion(**s)
                for s in previous_assessment.emotion_suggestions
            ],
            overall_suggestions=[
                AssessmentSuggestion(**s)
                for s in previous_assessment.overall_suggestions
            ],
            data_completeness=DataCompleteness(**previous_assessment.data_completeness),
            assessment_period_start=previous_assessment.assessment_period_start.isoformat()
            if previous_assessment.assessment_period_start
            else None,
            assessment_period_end=previous_assessment.assessment_period_end.isoformat()
            if previous_assessment.assessment_period_end
            else None,
            created_at=previous_assessment.created_at.isoformat(),
        )

    return HealthAssessmentComparison(
        current=current_record,
        previous=previous_record,
        overall_change=overall_change,
        overall_change_percent=round(overall_change_percent, 1)
        if overall_change_percent is not None
        else None,
        nutrition_change=nutrition_change,
        behavior_change=behavior_change,
        emotion_change=emotion_change,
        trends=trends,
    )
