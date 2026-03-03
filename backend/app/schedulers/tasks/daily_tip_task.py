"""
科普内容定时生成任务
Story 9.1: 科普内容生成服务

AC #1: 每日凌晨生成当日科普内容
"""

import logging
from datetime import datetime, date
from typing import Optional

import structlog
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.daily_tip import DailyTip, TipTopic
from app.services.daily_tip_service import get_daily_tip_service

logger = structlog.get_logger()


async def daily_tip_generation_task():
    """
    每日科普内容生成任务
    AC #1: 每日凌晨生成当日科普内容

    每天凌晨 00:00 执行，检查当天是否有科普内容，
    如果没有则生成新的科普内容。
    """
    logger.info("Starting daily tip generation task")

    db = SessionLocal()
    try:
        today = datetime.now()
        today_date = today.date()

        # 检查今天是否已有科普内容
        existing_tip = (
            db.query(DailyTip).filter(func.date(DailyTip.date) == today_date).first()
        )

        if existing_tip:
            logger.info(
                "Daily tip already exists for today",
                date=today_date,
                tip_id=existing_tip.id,
            )
            return

        # 获取当天主题
        service = get_daily_tip_service()
        topic = service.get_current_topic(today_date)

        # 生成科普内容
        logger.info("Generating daily tip", topic=topic, date=today_date)
        content = await service.generate_tip_content(topic)

        # 保存到数据库
        tip = DailyTip(
            date=today,
            topic=topic,
            title=content["title"],
            summary=content["summary"],
            content=content["content"],
            disclaimer=content.get("disclaimer", ""),
            is_active=True,
        )

        db.add(tip)
        db.commit()
        db.refresh(tip)

        logger.info(
            "Daily tip generated successfully",
            tip_id=tip.id,
            date=today_date,
            topic=topic,
            title=content["title"],
        )

    except Exception as e:
        logger.error("Failed to generate daily tip", error=str(e))
        db.rollback()
    finally:
        db.close()


async def regenerate_daily_tip(target_date: Optional[date] = None) -> DailyTip:
    """
    手动重新生成科普内容
    AC #6: 支持手动触发重新生成

    Args:
        target_date: 目标日期，默认今天

    Returns:
        生成的 DailyTip 对象
    """
    logger.info("Regenerating daily tip", target_date=target_date)

    db = SessionLocal()
    try:
        if target_date is None:
            target_date = datetime.now().date()

        # 查找现有的科普内容
        existing_tip = (
            db.query(DailyTip).filter(func.date(DailyTip.date) == target_date).first()
        )

        if existing_tip:
            # 标记旧的为 inactive
            existing_tip.is_active = False
            db.commit()

        # 获取主题
        service = get_daily_tip_service()
        topic = service.get_current_topic(target_date)

        # 生成新内容
        content = await service.generate_tip_content(topic)

        # 创建新的科普内容
        tip = DailyTip(
            date=datetime.combine(target_date, datetime.min.time()),
            topic=topic,
            title=content["title"],
            summary=content["summary"],
            content=content["content"],
            disclaimer=content.get("disclaimer", ""),
            is_active=True,
        )

        db.add(tip)
        db.commit()
        db.refresh(tip)

        logger.info(
            "Daily tip regenerated successfully",
            tip_id=tip.id,
            date=target_date,
            topic=topic,
        )

        return tip

    except Exception as e:
        logger.error("Failed to regenerate daily tip", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


async def regenerate_daily_tip(target_date: Optional[date] = None) -> DailyTip:
    """
    手动重新生成科普内容
    AC #6: 支持手动触发重新生成

    Args:
        target_date: 目标日期，默认今天

    Returns:
        生成的 DailyTip 对象
    """
    logger.info("Regenerating daily tip", target_date=target_date)

    db = SessionLocal()
    try:
        if target_date is None:
            target_date = datetime.now().date()

        # 查找现有的科普内容
        existing_tip = (
            db.query(DailyTip).filter(func.date(DailyTip.date) == target_date).first()
        )

        if existing_tip:
            # 标记旧的为 inactive
            existing_tip.is_active = False
            db.commit()

        # 获取主题
        service = get_daily_tip_service()
        topic = service.get_current_topic(target_date)

        # 生成新内容
        content = await service.generate_tip_content(topic)

        # 创建新的科普内容
        tip = DailyTip(
            date=datetime.combine(target_date, datetime.min.time()),
            topic=topic,
            title=content["title"],
            summary=content["summary"],
            content=content["content"],
            disclaimer=content.get("disclaimer", ""),
            is_active=True,
        )

        db.add(tip)
        db.commit()
        db.refresh(tip)

        logger.info(
            "Daily tip regenerated successfully",
            tip_id=tip.id,
            date=target_date,
            topic=topic,
        )

        return tip

    except Exception as e:
        logger.error("Failed to regenerate daily tip", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()
