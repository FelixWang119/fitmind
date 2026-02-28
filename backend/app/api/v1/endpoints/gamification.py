from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.gamification import (
    AchievementInDB,
    BadgeUnlocked,
    ChallengeCreate,
    ChallengeInDB,
    GamificationOverview,
    LevelProgress,
    PointsEarned,
    PointsTransactionInDB,
    StreakRecordInDB,
    UserBadgeInDB,
    UserPointsInDB,
)
from app.services.gamification_service import get_gamification_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/overview", response_model=GamificationOverview)
async def get_gamification_overview(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取游戏化概览"""
    logger.info("Getting gamification overview", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        overview = gamification_service.get_gamification_overview(current_user)
        return overview

    except Exception as e:
        logger.error(
            "Failed to get gamification overview", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gamification overview",
        )


@router.get("/points", response_model=UserPointsInDB)
async def get_user_points(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户积分"""
    logger.info("Getting user points", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        points = gamification_service.get_user_points(current_user)
        return points

    except Exception as e:
        logger.error("Failed to get user points", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user points",
        )


@router.get("/points-history", response_model=List[PointsTransactionInDB])
async def get_points_history(
    limit: int = Query(50, ge=1, le=100, description="记录数量限制"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取积分历史"""
    logger.info("Getting points history", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        history = gamification_service.get_points_history(current_user, limit)
        return history

    except Exception as e:
        logger.error(
            "Failed to get points history", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve points history",
        )


@router.get("/level", response_model=LevelProgress)
async def get_level_progress(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取等级进度"""
    logger.info("Getting level progress", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        progress = gamification_service.get_level_progress(current_user)
        return progress

    except Exception as e:
        logger.error(
            "Failed to get level progress", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve level progress",
        )


@router.get("/badges", response_model=List[UserBadgeInDB])
async def get_user_badges(
    category: Optional[str] = Query(None, description="徽章类别过滤"),
    limit: int = Query(50, ge=1, le=100, description="数量限制"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户徽章"""
    logger.info("Getting user badges", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        badges = gamification_service.get_user_badges(current_user, category, limit)
        return badges

    except Exception as e:
        logger.error("Failed to get user badges", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user badges",
        )


@router.post("/check-badges", response_model=List[BadgeUnlocked])
async def check_and_award_badges(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """检查并授予徽章"""
    logger.info("Checking badges", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        awarded_badges = gamification_service.check_and_award_badges(current_user)
        return awarded_badges

    except Exception as e:
        logger.error("Failed to check badges", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check and award badges",
        )


@router.post("/badges/{badge_id}/showcase")
async def showcase_badge(
    badge_id: str,
    order: int = Query(0, description="展示顺序"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """展示徽章"""
    logger.info("Showcasing badge", user_id=current_user.id, badge_id=badge_id)

    gamification_service = get_gamification_service(db)

    try:
        success = gamification_service.showcase_badge(current_user, badge_id, order)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Badge not found",
            )

        return {
            "message": "Badge showcased successfully",
            "badge_id": badge_id,
            "order": order,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to showcase badge", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to showcase badge",
        )


@router.get("/achievements", response_model=List[AchievementInDB])
async def get_user_achievements(
    completed_only: bool = Query(False, description="仅显示已完成成就"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户成就"""
    logger.info("Getting user achievements", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        achievements = gamification_service.get_user_achievements(
            current_user, completed_only
        )
        return achievements

    except Exception as e:
        logger.error(
            "Failed to get user achievements", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user achievements",
        )


@router.get("/achievements/nutrition", response_model=List[AchievementInDB])
async def get_nutrition_achievements(
    completed_only: bool = Query(False, description="仅显示已完成成就"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户营养成就 (Story 4.1)"""
    logger.info("Getting nutrition achievements", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        achievements = gamification_service.get_nutrition_achievements(
            current_user, completed_only
        )
        return achievements

    except Exception as e:
        logger.error(
            "Failed to get nutrition achievements",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve nutrition achievements",
        )


@router.post("/achievements/nutrition/{achievement_id}/progress")
async def update_nutrition_achievement_progress(
    achievement_id: str,
    increment: int = Query(1, description="进度增量"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新营养成就进度 (Story 4.1)"""
    logger.info(
        "Updating nutrition achievement progress",
        user_id=current_user.id,
        achievement_id=achievement_id,
        increment=increment,
    )

    gamification_service = get_gamification_service(db)

    try:
        achievement = gamification_service.update_nutrition_achievement(
            current_user, achievement_id, increment
        )

        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Achievement not found: {achievement_id}",
            )

        return {
            "achievement": achievement,
            "message": "进度已更新" if not achievement.is_completed else "成就已完成！",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update nutrition achievement",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update achievement progress",
        )


# ========== Story 4.2: 运动成就端点 ==========


@router.get("/achievements/exercise", response_model=List[AchievementInDB])
async def get_exercise_achievements(
    completed_only: bool = Query(False, description="仅显示已完成成就"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户运动成就 (Story 4.2)"""
    logger.info("Getting exercise achievements", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        achievements = gamification_service.get_exercise_achievements(
            current_user, completed_only
        )
        return achievements

    except Exception as e:
        logger.error(
            "Failed to get exercise achievements", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise achievements",
        )


@router.post("/achievements/exercise/{achievement_id}/progress")
async def update_exercise_achievement_progress(
    achievement_id: str,
    increment: int = Query(1, description="进度增量"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新运动成就进度 (Story 4.2)"""
    logger.info(
        "Updating exercise achievement progress",
        user_id=current_user.id,
        achievement_id=achievement_id,
        increment=increment,
    )

    gamification_service = get_gamification_service(db)

    try:
        achievement = gamification_service.update_exercise_achievement(
            current_user, achievement_id, increment
        )

        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Achievement not found: {achievement_id}",
            )

        return {
            "achievement": achievement,
            "message": "进度已更新" if not achievement.is_completed else "成就已完成！",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update exercise achievement",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update achievement progress",
        )


@router.get("/challenges", response_model=List[ChallengeInDB])
async def get_user_challenges(
    status: Optional[str] = Query(
        None, description="状态过滤: active, completed, failed"
    ),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户挑战"""
    logger.info("Getting user challenges", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        challenges = gamification_service.get_user_challenges(current_user, status)
        return challenges

    except Exception as e:
        logger.error(
            "Failed to get user challenges", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user challenges",
        )


@router.post(
    "/challenges", response_model=ChallengeInDB, status_code=status.HTTP_201_CREATED
)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建挑战"""
    logger.info("Creating challenge", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        challenge = gamification_service.create_challenge(current_user, challenge_data)
        return challenge

    except Exception as e:
        logger.error(
            "Failed to create challenge", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create challenge",
        )


@router.get("/streaks", response_model=List[StreakRecordInDB])
async def get_user_streaks(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户连续记录"""
    logger.info("Getting user streaks", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        streaks = gamification_service.get_user_streaks(current_user)
        return streaks

    except Exception as e:
        logger.error(
            "Failed to get user streaks", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user streaks",
        )


@router.get("/daily-reward")
async def get_daily_reward(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日奖励"""
    logger.info("Getting daily reward", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        reward = gamification_service.get_daily_reward(current_user)
        return reward

    except Exception as e:
        logger.error(
            "Failed to get daily reward", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily reward",
        )


@router.post("/claim-daily-reward", response_model=PointsEarned)
async def claim_daily_reward(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """领取每日奖励"""
    logger.info("Claiming daily reward", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        reward = gamification_service.claim_daily_reward(current_user)
        return reward

    except Exception as e:
        logger.error(
            "Failed to claim daily reward", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to claim daily reward",
        )


@router.get("/leaderboard")
async def get_leaderboard(
    type: str = Query(
        "points", description="排行榜类型: points, achievements, streaks"
    ),
    period: str = Query("weekly", description="周期: weekly, monthly, all_time"),
    limit: int = Query(20, ge=1, le=100, description="数量限制"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取排行榜"""
    logger.info(
        "Getting leaderboard", user_id=current_user.id, type=type, period=period
    )

    # 简化版排行榜
    gamification_service = get_gamification_service(db)

    try:
        # 这里可以实现更复杂的排行榜逻辑
        # 暂时返回演示数据
        return {
            "leaderboard_type": type,
            "period": period,
            "entries": [],
            "user_rank": None,
            "total_users": 0,
        }

    except Exception as e:
        logger.error("Failed to get leaderboard", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard",
        )


@router.get("/stats")
async def get_gamification_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取游戏化统计"""
    logger.info("Getting gamification stats", user_id=current_user.id)

    gamification_service = get_gamification_service(db)

    try:
        overview = gamification_service.get_gamification_overview(current_user)
        return overview.gamification_stats

    except Exception as e:
        logger.error(
            "Failed to get gamification stats", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gamification stats",
        )
