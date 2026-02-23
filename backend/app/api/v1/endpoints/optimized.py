"""优化的API端点"""
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.cache import CacheManager, cached, get_cache, invalidate_cache
from app.core.database import get_db
from app.core.performance import get_performance_monitor, timer_decorator
from app.models.user import User as UserModel
from app.services.dashboard_service import get_dashboard_service
from app.services.gamification_service import get_gamification_service
from app.services.scientific_persona_service import get_scientific_persona_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/dashboard-quick")
@timer_decorator("dashboard_quick")
async def get_dashboard_quick(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """快速获取仪表板数据（优化版）"""
    logger.info("Getting quick dashboard", user_id=current_user.id)

    cache = get_cache()
    cache_key = f"dashboard_quick:{current_user.id}"

    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug("Dashboard cache hit", user_id=current_user.id)
        return cached_data

    # 使用性能监控
    monitor = get_performance_monitor()

    with monitor.monitor_db_query("dashboard_quick_query"):
        dashboard_service = get_dashboard_service(db)

        try:
            # 获取关键数据
            overview = dashboard_service.get_overview(current_user)

            # 简化响应，只返回关键信息
            quick_data = {
                "user_info": {
                    "name": overview["user_info"]["name"],
                    "weight_progress": overview["user_info"]["weight_progress"],
                },
                "today_summary": {
                    "completed": overview["today_todos"]["completed_count"],
                    "total": overview["today_todos"]["total_count"],
                    "percentage": overview["today_todos"]["completion_percentage"],
                },
                "motivational_message": overview["motivational_message"],
                "last_updated": overview["last_updated"],
            }

            # 缓存3分钟
            cache.set(cache_key, quick_data, 180)

            return quick_data

        except Exception as e:
            logger.error(
                "Failed to get quick dashboard", user_id=current_user.id, error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve dashboard",
            )


@router.get("/user-stats")
@cached("user_stats", ttl=300)
async def get_user_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户统计数据（缓存优化）"""
    logger.info("Getting user stats", user_id=current_user.id)

    # 使用批量查询优化
    monitor = get_performance_monitor()

    with monitor.monitor_db_query("user_stats_batch"):
        # 并行获取各项统计数据
        from app.services.emotional_support_service import get_emotional_support_service
        from app.services.habit_service import get_habit_service
        from app.services.nutrition_service import get_nutrition_service

        nutrition_service = get_nutrition_service(db)
        habit_service = get_habit_service(db)
        emotional_service = get_emotional_support_service(db)
        gamification_service = get_gamification_service(db)

        try:
            # 获取卡路里目标
            calorie_targets = nutrition_service.calculate_calorie_target(current_user)

            # 获取习惯统计
            habit_stats = habit_service.get_habit_stats(current_user)

            # 获取情感洞察
            emotional_insights = emotional_service.get_emotional_insights(
                current_user, 7
            )

            # 获取游戏化数据
            gamification_overview = gamification_service.get_gamification_overview(
                current_user
            )

            return {
                "nutrition": {
                    "calorie_target": calorie_targets.get("target", 0),
                    "maintenance": calorie_targets.get("maintenance", 0),
                },
                "habits": {
                    "total": habit_stats.total_habits,
                    "completion_rate": habit_stats.completion_rate,
                    "current_streak": habit_stats.current_streak,
                },
                "emotional": {
                    "dominant_emotion": emotional_insights.dominant_emotion.value,
                    "avg_stress": emotional_insights.avg_stress_level,
                },
                "gamification": {
                    "level": gamification_overview.user_level.current_level,
                    "points": gamification_overview.user_points.total_points,
                    "badges": len(gamification_overview.recent_badges),
                },
            }

        except Exception as e:
            logger.error(
                "Failed to get user stats", user_id=current_user.id, error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user stats",
            )


@router.get("/cached-report")
async def get_cached_scientific_report(
    days: int = Query(30, ge=7, le=90),
    use_cache: bool = Query(True, description="是否使用缓存"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取缓存的科学报告"""
    logger.info("Getting cached scientific report", user_id=current_user.id)

    if use_cache:
        cache = get_cache()
        cache_key = f"scientific_report:{current_user.id}:{days}"

        cached_report = cache.get(cache_key)
        if cached_report:
            logger.debug("Scientific report cache hit", user_id=current_user.id)
            return {
                **cached_report,
                "cached": True,
                "cached_at": cache._cache.get(cache_key, (None, 0))[1] - 1800,
            }

    # 生成新报告
    persona_service = get_scientific_persona_service(db)

    try:
        report = persona_service.generate_scientific_report(current_user, days)

        # 缓存30分钟
        if use_cache:
            cache = get_cache()
            cache_key = f"scientific_report:{current_user.id}:{days}"
            cache.set(cache_key, report, 1800)

        return {
            **report,
            "cached": False,
        }

    except Exception as e:
        logger.error("Failed to generate report", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        )


@router.post("/invalidate-cache")
async def invalidate_user_cache(
    cache_type: Optional[str] = Query(None, description="缓存类型"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """使用户缓存失效"""
    logger.info("Invalidating cache", user_id=current_user.id, cache_type=cache_type)

    cache_manager = CacheManager()
    cache_manager.invalidate_user_cache(current_user.id)

    return {
        "message": "Cache invalidated successfully",
        "user_id": current_user.id,
        "cache_type": cache_type or "all",
    }


@router.get("/cache-stats")
async def get_cache_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取缓存统计"""
    cache = get_cache()
    stats = cache.get_stats()

    return {
        "cache_stats": stats,
        "user_cache_keys": len(
            [k for k in cache._cache.keys() if str(current_user.id) in k]
        ),
    }


@router.get("/performance-stats")
async def get_performance_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取性能统计"""
    monitor = get_performance_monitor()
    stats = monitor.get_stats()

    return {
        "performance_stats": stats,
        "slow_query_threshold": 1.0,
    }


@router.get("/batch-data")
async def get_batch_data(
    data_types: str = Query(..., description="数据类型，逗号分隔: dashboard,stats,gamification"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """批量获取数据（减少API调用次数）"""
    logger.info("Getting batch data", user_id=current_user.id, types=data_types)

    types_list = [t.strip() for t in data_types.split(",")]
    result = {}

    try:
        if "dashboard" in types_list:
            dashboard_service = get_dashboard_service(db)
            result["dashboard"] = dashboard_service.get_quick_stats(current_user)

        if "stats" in types_list:
            nutrition_service = get_nutrition_service(db)
            habit_service = get_habit_service(db)

            result["stats"] = {
                "nutrition": nutrition_service.calculate_calorie_target(current_user),
                "habits": habit_service.get_habit_stats(current_user).__dict__,
            }

        if "gamification" in types_list:
            gamification_service = get_gamification_service(db)
            result["gamification"] = gamification_service.get_gamification_overview(
                current_user
            ).__dict__

        return result

    except Exception as e:
        logger.error("Failed to get batch data", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve batch data",
        )


@router.get("/lightweight-dashboard")
async def get_lightweight_dashboard(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """轻量级仪表板（移动端优化）"""
    logger.info("Getting lightweight dashboard", user_id=current_user.id)

    cache = get_cache()
    cache_key = f"lightweight_dashboard:{current_user.id}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        # 只获取最关键的数据
        dashboard_service = get_dashboard_service(db)
        quick_stats = dashboard_service.get_quick_stats(current_user)

        # 极度简化的响应
        lightweight_data = {
            "today_completion": quick_stats["today"]["completion_percentage"],
            "current_weight": quick_stats["weight"]["latest"],
            "weight_progress": quick_stats["weight"]["progress"].get("percentage", 0),
            "calorie_target": quick_stats["nutrition"]["calorie_target"],
            "current_streak": quick_stats["habits"]["current_streak"],
            "level": quick_stats["habits"]["current_streak"],  # 简化处理
        }

        # 缓存2分钟
        cache.set(cache_key, lightweight_data, 120)

        return lightweight_data

    except Exception as e:
        logger.error(
            "Failed to get lightweight dashboard", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard",
        )


from app.services.habit_service import get_habit_service

# 从其他服务导入
from app.services.nutrition_service import get_nutrition_service
