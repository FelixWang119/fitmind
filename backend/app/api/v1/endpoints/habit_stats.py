from datetime import date, datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.habit import (
    BehaviorPatterns,
    CompletionRateStats,
    HabitDetailedStats,
    HabitGoalCreate,
    HabitGoalInDB,
    HabitGoalUpdate,
    HabitGoalWithProgress,
    HabitStatsOverview,
)
from app.services.habit_service import get_habit_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/stats/overview", response_model=HabitStatsOverview)
async def get_stats_overview(
    period: str = Query("weekly", description="时间周期: weekly/monthly/quarterly"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯统计概览"""
    logger.info("Getting habit stats overview", user_id=current_user.id, period=period)

    habit_service = get_habit_service(db)

    try:
        stats = habit_service.get_stats_overview(current_user, period)
        return stats
    except Exception as e:
        logger.error(
            "Failed to get stats overview", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit stats overview",
        )


@router.get("/stats/completion", response_model=CompletionRateStats)
async def get_completion_rate_stats(
    period: str = Query("weekly", description="时间周期: weekly/monthly/quarterly"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取完成率统计"""
    logger.info("Getting completion rate stats", user_id=current_user.id, period=period)

    habit_service = get_habit_service(db)

    try:
        stats = habit_service.get_completion_rate_stats(current_user, period)
        return stats
    except Exception as e:
        logger.error(
            "Failed to get completion rate stats", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completion rate stats",
        )


@router.get("/{habit_id}/detailed-stats", response_model=HabitDetailedStats)
async def get_detailed_stats(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取单个习惯详细统计"""
    logger.info("Getting detailed stats", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        # Verify habit belongs to user
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        stats = habit_service.get_detailed_stats(habit)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get detailed stats", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve detailed stats",
        )


@router.get("/stats/patterns", response_model=BehaviorPatterns)
async def get_behavior_patterns(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取行为模式分析"""
    logger.info("Getting behavior patterns", user_id=current_user.id)

    habit_service = get_habit_service(db)

    try:
        patterns = habit_service.get_behavior_patterns(current_user)
        return patterns
    except Exception as e:
        logger.error(
            "Failed to get behavior patterns", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve behavior patterns",
        )


# ============== Goal Management Endpoints ==============


@router.get("/goals", response_model=List[HabitGoalInDB])
async def get_goals(
    habit_id: Optional[int] = Query(None, description="按习惯过滤"),
    active_only: bool = Query(False, description="只返回活跃目标"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯目标列表"""
    logger.info("Getting habit goals", user_id=current_user.id)

    habit_service = get_habit_service(db)

    try:
        goals = habit_service.get_user_goals(
            current_user, habit_id=habit_id, active_only=active_only
        )

        # Convert to response model
        return [
            HabitGoalInDB(
                id=goal.id,
                user_id=goal.user_id,
                habit_id=goal.habit_id,
                goal_type=goal.goal_type,
                target_value=goal.target_value,
                period=goal.period,
                start_date=goal.start_date.date()
                if isinstance(goal.start_date, datetime)
                else goal.start_date,
                end_date=goal.end_date.date()
                if isinstance(goal.end_date, datetime)
                else goal.end_date,
                is_active=goal.is_active,
                is_achieved=goal.is_achieved,
                current_progress=goal.current_progress,
                created_at=goal.created_at,
            )
            for goal in goals
        ]
    except Exception as e:
        logger.error("Failed to get goals", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goals",
        )


@router.get("/goals/{goal_id}", response_model=HabitGoalWithProgress)
async def get_goal(
    goal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取目标详情（带进度）"""
    logger.info("Getting goal with progress", user_id=current_user.id, goal_id=goal_id)

    habit_service = get_habit_service(db)

    try:
        goal_with_progress = habit_service.get_goal_with_progress(current_user, goal_id)

        if not goal_with_progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )

        return goal_with_progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get goal", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goal",
        )


@router.post(
    "/goals", response_model=HabitGoalInDB, status_code=status.HTTP_201_CREATED
)
async def create_goal(
    goal_data: HabitGoalCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建习惯目标"""
    logger.info("Creating habit goal", user_id=current_user.id)

    habit_service = get_habit_service(db)

    try:
        goal = habit_service.create_goal(current_user, goal_data)

        return HabitGoalInDB(
            id=goal.id,
            user_id=goal.user_id,
            habit_id=goal.habit_id,
            goal_type=goal.goal_type,
            target_value=goal.target_value,
            period=goal.period,
            start_date=goal.start_date.date()
            if isinstance(goal.start_date, datetime)
            else goal.start_date,
            end_date=goal.end_date.date()
            if isinstance(goal.end_date, datetime)
            else goal.end_date,
            is_active=goal.is_active,
            is_achieved=goal.is_achieved,
            current_progress=goal.current_progress,
            created_at=goal.created_at,
        )
    except ValueError as e:
        logger.warning("Failed to create goal", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Failed to create goal", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goal",
        )


@router.put("/goals/{goal_id}", response_model=HabitGoalInDB)
async def update_goal(
    goal_id: int,
    goal_data: HabitGoalUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新习惯目标"""
    logger.info("Updating habit goal", user_id=current_user.id, goal_id=goal_id)

    habit_service = get_habit_service(db)

    try:
        goal = habit_service.get_goal_by_id(current_user, goal_id)

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )

        updated_goal = habit_service.update_goal(goal, goal_data)

        return HabitGoalInDB(
            id=updated_goal.id,
            user_id=updated_goal.user_id,
            habit_id=updated_goal.habit_id,
            goal_type=updated_goal.goal_type,
            target_value=updated_goal.target_value,
            period=updated_goal.period,
            start_date=updated_goal.start_date.date()
            if isinstance(updated_goal.start_date, datetime)
            else updated_goal.start_date,
            end_date=updated_goal.end_date.date()
            if isinstance(updated_goal.end_date, datetime)
            else updated_goal.end_date,
            is_active=updated_goal.is_active,
            is_achieved=updated_goal.is_achieved,
            current_progress=updated_goal.current_progress,
            created_at=updated_goal.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update goal", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal",
        )


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除习惯目标"""
    logger.info("Deleting habit goal", user_id=current_user.id, goal_id=goal_id)

    habit_service = get_habit_service(db)

    try:
        goal = habit_service.get_goal_by_id(current_user, goal_id)

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )

        habit_service.delete_goal(goal)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete goal", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goal",
        )
