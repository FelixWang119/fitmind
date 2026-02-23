from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.professional_fusion import (
    IntegratedGuidance,
    IntegratedIntervention,
    ProgressTracking,
    RoleSwitchRequest,
    RoleTransition,
    UserNeedsAssessment,
)
from app.services.professional_fusion_service import get_professional_fusion_service

logger = structlog.get_logger()

router = APIRouter()


@router.post("/assess-needs", response_model=UserNeedsAssessment)
async def assess_user_needs(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """评估用户需求（营养师+行为教练综合评估）"""
    logger.info("Assessing user needs", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        assessment = fusion_service.assess_user_needs(current_user)

        return UserNeedsAssessment(
            nutrition_assessment=assessment["nutrition_assessment"],
            behavior_assessment=assessment["behavior_assessment"],
            emotional_assessment=assessment["emotional_assessment"],
            integrated_assessment=assessment["integrated_assessment"],
            recommended_role=assessment["recommended_role"],
            assessment_date=assessment["assessment_date"],
        )

    except Exception as e:
        logger.error(
            "Failed to assess user needs", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess user needs",
        )


@router.post("/create-intervention", response_model=IntegratedIntervention)
async def create_intervention_plan(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建综合干预计划"""
    logger.info("Creating intervention plan", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        # 首先进行需求评估
        assessment = fusion_service.assess_user_needs(current_user)

        # 基于评估创建干预计划
        intervention = fusion_service.create_integrated_intervention(
            current_user, assessment
        )

        return IntegratedIntervention(
            primary_role=intervention["primary_role"],
            focus_areas=intervention["focus_areas"],
            duration_weeks=intervention["duration_weeks"],
            weekly_sessions=intervention["weekly_sessions"],
            intervention_components=intervention["intervention_components"],
        )

    except Exception as e:
        logger.error(
            "Failed to create intervention plan", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create intervention plan",
        )


@router.post("/guidance", response_model=IntegratedGuidance)
async def get_integrated_guidance(
    context: str = Query(..., description="当前情境或问题描述"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取综合指导"""
    logger.info("Getting integrated guidance", user_id=current_user.id, context=context)

    fusion_service = get_professional_fusion_service(db)

    try:
        guidance = fusion_service.provide_integrated_guidance(current_user, context)

        return IntegratedGuidance(
            context=guidance["context"],
            assessment_summary=guidance["assessment_summary"],
            immediate_actions=guidance["immediate_actions"],
            short_term_goals=guidance["short_term_goals"],
            integrated_advice=guidance["integrated_advice"],
            follow_up_plan=guidance["follow_up_plan"],
        )

    except Exception as e:
        logger.error(
            "Failed to get integrated guidance", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate integrated guidance",
        )


@router.get("/progress-tracking", response_model=ProgressTracking)
async def track_progress(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """跟踪综合进展"""
    logger.info("Tracking progress", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        # 获取最新的干预计划（简化版）
        assessment = fusion_service.assess_user_needs(current_user)
        intervention_plan = fusion_service.create_integrated_intervention(
            current_user, assessment
        )

        # 跟踪进展
        progress = fusion_service.track_integrated_progress(
            current_user, intervention_plan
        )

        return ProgressTracking(
            nutrition_progress=progress["nutrition_progress"],
            behavior_progress=progress["behavior_progress"],
            emotional_progress=progress["emotional_progress"],
            integrated_progress=progress["integrated_progress"],
            overall_status=progress["overall_status"],
            recommendations=progress["recommendations"],
            tracking_date=progress["tracking_date"],
        )

    except Exception as e:
        logger.error("Failed to track progress", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track progress",
        )


@router.get("/role-status")
async def get_current_role(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前专业角色状态"""
    logger.info("Getting current role", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        assessment = fusion_service.assess_user_needs(current_user)

        return {
            "current_role": assessment["recommended_role"],
            "assessment": {
                "overall_priority": assessment["integrated_assessment"][
                    "overall_priority"
                ],
                "focus_areas": assessment["integrated_assessment"][
                    "integrated_focus_areas"
                ],
                "cross_cutting_issues": assessment["integrated_assessment"][
                    "cross_cutting_issues"
                ],
            },
            "last_updated": assessment["assessment_date"],
        }

    except Exception as e:
        logger.error("Failed to get role status", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role status",
        )


@router.post("/switch-role", response_model=RoleTransition)
async def switch_role(
    request: RoleSwitchRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """切换专业角色"""
    logger.info(
        "Switching role",
        user_id=current_user.id,
        from_role=request.current_role,
        to_role=request.target_role,
    )

    fusion_service = get_professional_fusion_service(db)

    try:
        # 验证角色切换
        assessment = fusion_service.assess_user_needs(current_user)
        recommended_role = assessment["recommended_role"]

        # 如果用户要求的角色与推荐角色不同，提供建议
        if request.target_role != recommended_role:
            transition_reason = f"用户要求切换到{request.target_role}，但系统推荐{recommended_role}"
            recommended_approach = f"建议考虑使用{recommended_role}角色以获得更好的效果"
        else:
            transition_reason = f"切换到{request.target_role}角色"
            recommended_approach = "按照推荐的综合方法进行"

        return RoleTransition(
            from_role=request.current_role,
            to_role=request.target_role,
            transition_reason=transition_reason,
            recommended_approach=recommended_approach,
            expected_outcomes=[
                "获得更专业的指导",
                "针对性的干预策略",
                "更好的目标达成",
            ],
        )

    except Exception as e:
        logger.error("Failed to switch role", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch role",
        )


@router.get("/focus-areas")
async def get_focus_areas(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前关注领域"""
    logger.info("Getting focus areas", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        assessment = fusion_service.assess_user_needs(current_user)

        return {
            "focus_areas": assessment["integrated_assessment"][
                "integrated_focus_areas"
            ],
            "priority_distribution": assessment["integrated_assessment"][
                "priority_distribution"
            ],
            "cross_cutting_issues": assessment["integrated_assessment"][
                "cross_cutting_issues"
            ],
        }

    except Exception as e:
        logger.error("Failed to get focus areas", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve focus areas",
        )


@router.get("/recommendations")
async def get_integrated_recommendations(
    context: Optional[str] = Query(None, description="当前情境"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取综合推荐"""
    logger.info("Getting integrated recommendations", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        # 获取评估和指导
        assessment = fusion_service.assess_user_needs(current_user)

        if context:
            guidance = fusion_service.provide_integrated_guidance(current_user, context)
        else:
            guidance = fusion_service.provide_integrated_guidance(
                current_user, "综合健康管理"
            )

        return {
            "primary_role": assessment["recommended_role"],
            "focus_areas": assessment["integrated_assessment"][
                "integrated_focus_areas"
            ],
            "immediate_actions": guidance["immediate_actions"],
            "short_term_goals": guidance["short_term_goals"],
            "integrated_advice": guidance["integrated_advice"],
            "next_steps": [
                "开始实施立即行动",
                "设定短期目标",
                "定期跟踪进展",
                "调整干预策略",
            ],
        }

    except Exception as e:
        logger.error(
            "Failed to get recommendations", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations",
        )


@router.get("/quick-check")
async def quick_check(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """快速检查用户状态"""
    logger.info("Quick check", user_id=current_user.id)

    fusion_service = get_professional_fusion_service(db)

    try:
        assessment = fusion_service.assess_user_needs(current_user)

        # 生成快速总结
        summary = {
            "overall_status": assessment["integrated_assessment"]["overall_priority"],
            "primary_role": assessment["recommended_role"],
            "top_focus_area": (
                assessment["integrated_assessment"]["integrated_focus_areas"][0]
                if assessment["integrated_assessment"]["integrated_focus_areas"]
                else "综合管理"
            ),
            "key_issues": assessment["integrated_assessment"]["cross_cutting_issues"][
                :2
            ],
            "recommendation": (
                "建议优先关注营养和行为改变"
                if assessment["integrated_assessment"]["overall_priority"] == "高"
                else "继续保持良好进展"
            ),
        }

        return summary

    except Exception as e:
        logger.error("Failed quick check", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform quick check",
        )
