from datetime import date, datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.habit import Habit, HabitCompletion
from app.schemas.habit import (
    HabitCompletionCreate,
    HabitCompletionInDB,
    HabitCreate,
    HabitInDB,
    HabitRecommendation,
    HabitStats,
    HabitUpdate,
    HabitWithCompletions,
    StreakInfo,
)
from app.services.habit_service import get_habit_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/", response_model=List[HabitInDB])
async def get_habits(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户的所有习惯"""
    logger.info("Getting all habits", user_id=current_user.id)
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return habits


# IMPORTANT: More specific routes must come BEFORE routes with path parameters
@router.get("/daily-checklist")
async def get_daily_checklist(
    target_date: Optional[date] = Query(None, description="目标日期（默认今天）"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日习惯检查清单"""
    logger.info(
        "Getting daily checklist", user_id=current_user.id, target_date=target_date
    )

    habit_service = get_habit_service(db)

    try:
        checklist = habit_service.get_daily_checklist(current_user, target_date)

        return checklist

    except Exception as e:
        logger.error(
            "Failed to get daily checklist", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get daily checklist",
        )


@router.get("/recommendations", response_model=List[HabitRecommendation])
async def get_habit_recommendations(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯推荐"""
    logger.info("Getting habit recommendations", user_id=current_user.id)
    habit_service = get_habit_service(db)
    recommendations = habit_service.get_habit_recommendations(current_user)
    return recommendations


@router.get("/{habit_id}", response_model=HabitWithCompletions)
async def get_habit(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定习惯"""
    logger.info("Getting habit", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        # 获取完成记录
        completions = habit_service.get_completions(habit)

        return HabitWithCompletions(
            **habit.__dict__,
            completions=completions,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get habit", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit",
        )


@router.put("/{habit_id}", response_model=HabitInDB)
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新习惯"""
    logger.info("Updating habit", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        updated_habit = habit_service.update_habit(habit, habit_data)

        return updated_habit

    except ValueError as e:
        logger.warning("Failed to update habit", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update habit", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update habit",
        )


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除习惯"""
    logger.info("Deleting habit", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        habit_service.delete_habit(habit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete habit", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete habit",
        )


@router.post(
    "/{habit_id}/completions",
    response_model=HabitCompletionInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_completion(
    habit_id: int,
    completion_data: HabitCompletionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """记录习惯完成"""
    logger.info(
        "Recording habit completion", user_id=current_user.id, habit_id=habit_id
    )

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        completion = habit_service.record_completion(habit, completion_data)

        return completion

    except ValueError as e:
        logger.warning(
            "Failed to record completion", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to record completion", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record completion",
        )


@router.get("/{habit_id}/completions", response_model=List[HabitCompletionInDB])
async def get_completions(
    habit_id: int,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯完成记录"""
    logger.info("Getting habit completions", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        completions = habit_service.get_completions(habit, start_date, end_date)

        return completions

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get completions", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completions",
        )


@router.get("/{habit_id}/streak", response_model=StreakInfo)
async def get_streak_info(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯连续天数信息"""
    logger.info("Getting streak info", user_id=current_user.id, habit_id=habit_id)

    habit_service = get_habit_service(db)

    try:
        habit = habit_service.get_habit_by_id(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        streak_info = habit_service.get_streak_info(habit)

        return streak_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get streak info", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve streak info",
        )


@router.get("/stats/overview", response_model=HabitStats)
async def get_habit_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯统计概览"""
    logger.info("Getting habit stats", user_id=current_user.id)

    habit_service = get_habit_service(db)

    try:
        stats = habit_service.get_habit_stats(current_user)

        return stats

    except Exception as e:
        logger.error("Failed to get habit stats", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit stats",
        )
