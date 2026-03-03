"""
科普内容 API 端点
Story 9.1: 科普内容生成服务

AC #5: 内容存储到数据库，支持历史查看
AC #6: 支持手动触发重新生成
"""

from datetime import datetime, date, timedelta
from typing import Optional, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.daily_tip import DailyTip
from app.schemas.daily_tip import (
    DailyTipResponse,
    DailyTipListResponse,
)
from app.schedulers.tasks.daily_tip_task import regenerate_daily_tip

logger = structlog.get_logger()

router = APIRouter()


@router.get("/today", response_model=DailyTipResponse)
async def get_today_tip(
    db: Session = Depends(get_db),
):
    """
    获取当日科普内容
    AC #3: GET /daily-tips/today 获取当日科普
    """
    logger.info("Getting today's daily tip")

    today = date.today()

    # 查询今天的科普内容
    tip = (
        db.query(DailyTip)
        .filter(func.date(DailyTip.date) == today)
        .filter(DailyTip.is_active == True)
        .first()
    )

    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="今日暂无科普内容",
        )

    return tip


@router.get("", response_model=DailyTipListResponse)
async def get_tips(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(10, ge=1, le=100, description="返回条数"),
    topic: Optional[str] = Query(None, description="按主题筛选"),
    db: Session = Depends(get_db),
):
    """
    获取科普内容列表
    AC #4: GET /daily-tips 获取历史科普列表
    """
    logger.info("Getting daily tips list", skip=skip, limit=limit, topic=topic)

    query = db.query(DailyTip).filter(DailyTip.is_active == True)

    if topic:
        query = query.filter(DailyTip.topic == topic)

    # 获取总数
    total = query.count()

    # 获取分页数据
    tips = query.order_by(DailyTip.date.desc()).offset(skip).limit(limit).all()

    return DailyTipListResponse(total=total, items=tips)


@router.post("/regenerate", response_model=DailyTipResponse)
async def regenerate_tip(
    target_date: Optional[date] = Query(None, description="目标日期，默认今天"),
    db: Session = Depends(get_db),
):
    """
    手动触发重新生成科普内容
    AC #6: POST /daily-tips/regenerate 手动触发重新生成
    """
    logger.info("Regenerating daily tip", target_date=target_date)

    try:
        # 如果没有指定日期，使用今天
        if target_date is None:
            target_date = date.today()

        # 调用重新生成任务
        new_tip = await regenerate_daily_tip(target_date)

        return new_tip

    except Exception as e:
        logger.error("Failed to regenerate tip", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新生成失败: {str(e)}",
        )


@router.get("/{tip_id}", response_model=DailyTipResponse)
async def get_tip(
    tip_id: int,
    db: Session = Depends(get_db),
):
    """
    获取特定科普内容
    """
    logger.info("Getting daily tip", tip_id=tip_id)

    tip = db.query(DailyTip).filter(DailyTip.id == tip_id).first()

    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科普内容不存在",
        )

    return tip
