from datetime import date, datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.emotional_support import (
    CopingStrategy,
    DailyEmotionalSummary,
    EmotionalCheckIn,
    EmotionalInsight,
    EmotionalStateCreate,
    EmotionalStateInDB,
    EmotionalSupportCreate,
    EmotionalSupportInDB,
    EmotionalWellnessPlan,
    EmotionType,
    GratitudeJournalCreate,
    GratitudeJournalInDB,
    MindfulnessExerciseCreate,
    MindfulnessExerciseInDB,
    PositiveAffirmationCreate,
    PositiveAffirmationInDB,
    StressLevelCreate,
    StressLevelInDB,
    SupportRecommendation,
    SupportType,
)
from app.services.emotional_support_service import get_emotional_support_service

logger = structlog.get_logger()

router = APIRouter()


# ========== 情感状态管理 ==========


@router.post(
    "/emotional-states",
    response_model=EmotionalStateInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_emotional_state(
    state_data: EmotionalStateCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """记录情感状态"""
    logger.info("Creating emotional state", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        emotional_state = emotional_service.record_emotional_state(
            current_user, state_data
        )

        return emotional_state

    except Exception as e:
        logger.error(
            "Failed to create emotional state", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record emotional state",
        )


@router.get("/emotional-states", response_model=List[EmotionalStateInDB])
async def get_emotional_states(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    emotion_type: Optional[EmotionType] = Query(None, description="情感类型"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取情感状态记录"""
    logger.info("Getting emotional states", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        states = emotional_service.get_emotional_states(
            current_user, start_date, end_date, emotion_type
        )

        return states

    except Exception as e:
        logger.error(
            "Failed to get emotional states", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emotional states",
        )


# ========== 情感支持 ==========


@router.post("/support", response_model=SupportRecommendation)
async def get_emotional_support(
    emotion_type: EmotionType,
    intensity: int = Query(..., ge=1, le=10, description="情感强度 1-10"),
    context: Optional[str] = Query(None, description="上下文"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取情感支持建议"""
    logger.info(
        "Getting emotional support",
        user_id=current_user.id,
        emotion=emotion_type.value,
        intensity=intensity,
    )

    emotional_service = get_emotional_support_service(db)

    try:
        recommendation = emotional_service.provide_emotional_support(
            current_user, emotion_type, intensity, context
        )

        return recommendation

    except Exception as e:
        logger.error(
            "Failed to get emotional support", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate emotional support",
        )


@router.get("/support-history", response_model=List[EmotionalSupportInDB])
async def get_support_history(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    support_type: Optional[SupportType] = Query(None, description="支持类型"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取支持历史"""
    logger.info("Getting support history", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        query = emotional_service.db.query(EmotionalSupport).filter(
            EmotionalSupport.user_id == current_user.id
        )

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(EmotionalSupport.provided_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(EmotionalSupport.provided_at <= end_datetime)

        if support_type:
            query = query.filter(EmotionalSupport.support_type == support_type)

        supports = query.order_by(EmotionalSupport.provided_at.desc()).all()

        return supports

    except Exception as e:
        logger.error(
            "Failed to get support history", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve support history",
        )


# ========== 压力管理 ==========


@router.post(
    "/stress-levels",
    response_model=StressLevelInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_stress_level(
    stress_data: StressLevelCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """记录压力水平"""
    logger.info("Creating stress level", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        stress_level = emotional_service.record_stress_level(current_user, stress_data)

        return stress_level

    except Exception as e:
        logger.error(
            "Failed to create stress level", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record stress level",
        )


@router.get("/stress-trend")
async def get_stress_trend(
    days: int = Query(7, ge=1, le=30, description="天数 (1-30)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取压力趋势"""
    logger.info("Getting stress trend", user_id=current_user.id, days=days)

    emotional_service = get_emotional_support_service(db)

    try:
        trend = emotional_service.get_stress_trend(current_user, days)

        return {
            "trend": trend,
            "days": days,
            "avg_stress_level": (
                sum(day["stress_level"] for day in trend if day["stress_level"])
                / len([day for day in trend if day["stress_level"]])
                if any(day["stress_level"] for day in trend)
                else 0
            ),
        }

    except Exception as e:
        logger.error(
            "Failed to get stress trend", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stress trend",
        )


@router.get("/coping-strategies", response_model=List[CopingStrategy])
async def get_coping_strategies(
    stress_level: int = Query(..., ge=1, le=10, description="当前压力水平 1-10"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取应对策略"""
    logger.info(
        "Getting coping strategies", user_id=current_user.id, stress_level=stress_level
    )

    emotional_service = get_emotional_support_service(db)

    try:
        strategies = emotional_service.get_coping_strategies(stress_level)

        return strategies

    except Exception as e:
        logger.error(
            "Failed to get coping strategies", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coping strategies",
        )


# ========== 感恩日记 ==========


@router.post(
    "/gratitude",
    response_model=GratitudeJournalInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_gratitude_entry(
    gratitude_data: GratitudeJournalCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """记录感恩日记"""
    logger.info("Creating gratitude entry", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        gratitude_entry = emotional_service.record_gratitude(
            current_user, gratitude_data
        )

        return gratitude_entry

    except Exception as e:
        logger.error(
            "Failed to create gratitude entry", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record gratitude entry",
        )


@router.get("/gratitude-prompts")
async def get_gratitude_prompts(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取感恩提示"""
    logger.info("Getting gratitude prompts", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        prompts = emotional_service.get_gratitude_prompts()

        return {
            "prompts": prompts,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(
            "Failed to get gratitude prompts", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gratitude prompts",
        )


@router.get("/gratitude-history", response_model=List[GratitudeJournalInDB])
async def get_gratitude_history(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取感恩历史"""
    logger.info("Getting gratitude history", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        query = emotional_service.db.query(GratitudeJournal).filter(
            GratitudeJournal.user_id == current_user.id
        )

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(GratitudeJournal.recorded_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(GratitudeJournal.recorded_at <= end_datetime)

        entries = query.order_by(GratitudeJournal.recorded_at.desc()).all()

        return entries

    except Exception as e:
        logger.error(
            "Failed to get gratitude history", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gratitude history",
        )


# ========== 积极肯定语 ==========


@router.get("/affirmations", response_model=List[PositiveAffirmationInDB])
async def get_affirmations(
    category: Optional[str] = Query(None, description="类别"),
    count: int = Query(3, ge=1, le=10, description="数量 (1-10)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取积极肯定语"""
    logger.info(
        "Getting affirmations", user_id=current_user.id, category=category, count=count
    )

    emotional_service = get_emotional_support_service(db)

    try:
        affirmations = emotional_service.get_positive_affirmations(
            current_user, category, count
        )

        return affirmations

    except Exception as e:
        logger.error(
            "Failed to get affirmations", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve affirmations",
        )


@router.post(
    "/affirmations",
    response_model=PositiveAffirmationInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_affirmation(
    affirmation_data: PositiveAffirmationCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建个性化积极肯定语"""
    logger.info("Creating affirmation", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        # 创建新的肯定语记录
        affirmation = PositiveAffirmation(
            user_id=current_user.id,
            affirmation=affirmation_data.affirmation,
            category=affirmation_data.category,
            personalized=affirmation_data.personalized,
            times_used=0,
            created_at=datetime.utcnow(),
        )

        emotional_service.db.add(affirmation)
        emotional_service.db.commit()
        emotional_service.db.refresh(affirmation)

        return affirmation

    except Exception as e:
        logger.error(
            "Failed to create affirmation", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create affirmation",
        )


# ========== 正念练习 ==========


@router.post(
    "/mindfulness",
    response_model=MindfulnessExerciseInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_mindfulness_exercise(
    exercise_data: MindfulnessExerciseCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """记录正念练习"""
    logger.info("Creating mindfulness exercise", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        exercise = emotional_service.record_mindfulness_exercise(
            current_user, exercise_data
        )

        return exercise

    except Exception as e:
        logger.error(
            "Failed to create mindfulness exercise",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record mindfulness exercise",
        )


@router.get("/mindfulness-exercises")
async def get_mindfulness_exercises(
    duration: Optional[int] = Query(None, ge=1, description="最大持续时间(分钟)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取正念练习建议"""
    logger.info("Getting mindfulness exercises", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        exercises = emotional_service.get_mindfulness_exercises(duration)

        return {
            "exercises": exercises,
            "recommended_duration": duration or 10,
        }

    except Exception as e:
        logger.error(
            "Failed to get mindfulness exercises", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mindfulness exercises",
        )


# ========== 情感洞察和分析 ==========


@router.get("/insights", response_model=EmotionalInsight)
async def get_emotional_insights(
    days: int = Query(30, ge=1, le=90, description="天数 (1-90)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取情感洞察"""
    logger.info("Getting emotional insights", user_id=current_user.id, days=days)

    emotional_service = get_emotional_support_service(db)

    try:
        insights = emotional_service.get_emotional_insights(current_user, days)

        return insights

    except Exception as e:
        logger.error(
            "Failed to get emotional insights", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emotional insights",
        )


@router.get("/daily-summary", response_model=DailyEmotionalSummary)
async def get_daily_emotional_summary(
    target_date: Optional[date] = Query(None, description="目标日期 (默认今天)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日情感总结"""
    if target_date is None:
        target_date = date.today()

    logger.info(
        "Getting daily emotional summary", user_id=current_user.id, date=target_date
    )

    emotional_service = get_emotional_support_service(db)

    try:
        summary = emotional_service.get_daily_emotional_summary(
            current_user, target_date
        )

        return summary

    except Exception as e:
        logger.error(
            "Failed to get daily emotional summary",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily emotional summary",
        )


@router.get("/check-in", response_model=EmotionalCheckIn)
async def emotional_check_in(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """情感签到"""
    logger.info("Emotional check-in", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        check_in = emotional_service.create_emotional_check_in(current_user)

        return check_in

    except Exception as e:
        logger.error(
            "Failed to create emotional check-in", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create emotional check-in",
        )


@router.get("/wellness-plan", response_model=EmotionalWellnessPlan)
async def get_emotional_wellness_plan(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取情感健康计划"""
    logger.info("Getting emotional wellness plan", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        plan = emotional_service.create_emotional_wellness_plan(current_user)

        return plan

    except Exception as e:
        logger.error(
            "Failed to get emotional wellness plan",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create emotional wellness plan",
        )


# ========== 快速工具 ==========


@router.get("/quick-support")
async def get_quick_support(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """快速获取情感支持"""
    logger.info("Getting quick support", user_id=current_user.id)

    emotional_service = get_emotional_support_service(db)

    try:
        # 获取最近的情感状态
        recent_states = emotional_service.get_emotional_states(current_user, None, None)

        if recent_states:
            latest_state = recent_states[0]
            support = emotional_service.provide_emotional_support(
                current_user, latest_state.emotion_type, latest_state.intensity
            )
        else:
            # 默认支持
            support = emotional_service.provide_emotional_support(
                current_user, EmotionType.NEUTRAL, 5
            )

        # 获取今日感恩提示
        gratitude_prompts = emotional_service.get_gratitude_prompts()

        # 获取肯定语
        affirmations = emotional_service.get_positive_affirmations(
            current_user, None, 2
        )

        # 获取快速正念练习
        mindfulness_exercises = emotional_service.get_mindfulness_exercises(5)

        return {
            "support": support,
            "gratitude_prompts": gratitude_prompts,
            "affirmations": [a.affirmation for a in affirmations],
            "quick_mindfulness": mindfulness_exercises[0]
            if mindfulness_exercises
            else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(
            "Failed to get quick support", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quick support",
        )
