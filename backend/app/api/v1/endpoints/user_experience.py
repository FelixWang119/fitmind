"""用户体验端点"""
from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.services.user_experience_service import get_user_experience_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/greeting")
async def get_personalized_greeting(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取个性化问候"""
    logger.info("Getting personalized greeting", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    greeting = ux_service.get_personalized_greeting(current_user)

    return {
        "greeting": greeting,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/daily-tip")
async def get_daily_tip(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日提示"""
    logger.info("Getting daily tip", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    tip = ux_service.get_daily_tip(current_user)

    return tip


@router.get("/quick-actions")
async def get_quick_actions(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取快速操作"""
    logger.info("Getting quick actions", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    actions = ux_service.get_quick_actions(current_user)

    return {
        "actions": actions,
    }


@router.get("/progress-summary")
async def get_progress_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取进度摘要"""
    logger.info("Getting progress summary", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    summary = ux_service.get_progress_summary(current_user)

    return summary


@router.get("/recommended-next-steps")
async def get_recommended_next_steps(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取推荐的下一步行动"""
    logger.info("Getting recommended next steps", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    recommendations = ux_service.get_recommended_next_steps(current_user)

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
    }


@router.get("/achievements-preview")
async def get_achievements_preview(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取成就预览"""
    logger.info("Getting achievements preview", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    achievements = ux_service.get_achievements_preview(current_user)

    return {
        "achievements": achievements,
        "message": "完成这些成就可以获得奖励积分！",
    }


@router.get("/onboarding-flow")
async def get_onboarding_flow(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取新手引导流程"""
    logger.info("Getting onboarding flow", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    steps = ux_service.generate_onboarding_flow(current_user)

    # 计算完成进度
    completed = sum(1 for step in steps if step["is_completed"])
    total = len(steps)

    return {
        "steps": steps,
        "completed": completed,
        "total": total,
        "progress_percentage": round((completed / total) * 100, 1) if total > 0 else 0,
    }


@router.get("/notification-preferences")
async def get_notification_preferences(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取通知偏好"""
    logger.info("Getting notification preferences", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    preferences = ux_service.get_notification_preferences(current_user)

    return preferences


@router.get("/app-tour")
async def get_app_tour_steps(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取应用导览步骤"""
    logger.info("Getting app tour steps", user_id=current_user.id)

    ux_service = get_user_experience_service(db)
    steps = ux_service.get_app_tour_steps()

    return {
        "steps": steps,
        "total_steps": len(steps),
    }


@router.get("/home-screen-data")
async def get_home_screen_data(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取首页完整数据（聚合端点）"""
    logger.info("Getting home screen data", user_id=current_user.id)

    ux_service = get_user_experience_service(db)

    try:
        # 聚合所有首页需要的数据
        data = {
            "greeting": ux_service.get_personalized_greeting(current_user),
            "daily_tip": ux_service.get_daily_tip(current_user),
            "quick_actions": ux_service.get_quick_actions(current_user),
            "progress_summary": ux_service.get_progress_summary(current_user),
            "next_steps": ux_service.get_recommended_next_steps(current_user)[:3],
            "achievements_preview": ux_service.get_achievements_preview(current_user)[
                :2
            ],
        }

        return data

    except Exception as e:
        logger.error(
            "Failed to get home screen data", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve home screen data",
        )


from datetime import datetime
