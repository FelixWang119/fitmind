"""通知相关定时任务"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.notification import NotificationService
from app.models.notification import EventLog, EventLogStatus
from app.models.user import User
from app.models.habit import Habit, HabitCompletion

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def habit_reminder_task():
    """习惯提醒轮询任务 - 每分钟执行"""
    logger.info("Running habit reminder task")

    db = SessionLocal()
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 查询当前时间需要提醒的习惯
        # 这里简化处理，实际应该查询用户的习惯提醒设置
        logger.info(f"Habit reminder task completed. Current time: {current_time}")

    except Exception as e:
        logger.error(f"Habit reminder task failed: {e}")
    finally:
        db.close()


async def milestone_detection_task():
    """里程碑检测轮询任务 - 每 5 分钟执行"""
    logger.info("Running milestone detection task")

    db = SessionLocal()
    try:
        # 这里实现里程碑检测逻辑
        # 简化版本：查询事件日志中的 pending 事件
        pending_events = (
            db.query(EventLog)
            .filter(
                EventLog.notification_status == EventLogStatus.PENDING,
                EventLog.event_type.like("milestone.%"),
            )
            .limit(100)
            .all()
        )

        logger.info(f"Found {len(pending_events)} pending milestone events")

    except Exception as e:
        logger.error(f"Milestone detection task failed: {e}")
    finally:
        db.close()


async def process_event_logs_task():
    """事件日志处理任务 - 每 30 秒执行"""
    logger.info("Running event logs processing task")

    db = SessionLocal()
    try:
        notification_service = NotificationService(db)

        # 处理待发送的事件
        processed_count = await notification_service.process_event_logs(batch_size=50)

        if processed_count > 0:
            logger.info(f"Processed {processed_count} event logs")

    except Exception as e:
        logger.error(f"Event logs processing task failed: {e}")
    finally:
        db.close()


async def morning_care_task():
    """早安关怀任务 - 每天早上 8:00 执行"""
    logger.info("Running morning care task")

    db = SessionLocal()
    try:
        notification_service = NotificationService(db)

        # 获取所有活跃用户
        users = db.query(User).filter(User.is_active == True).all()

        sent_count = 0
        for user in users:
            try:
                # 发送早安通知
                await notification_service.send_notification(
                    user_id=user.id,
                    notification_type="care.morning",
                    title="☀️ 早安！",
                    content="新的一天开始了，今天也要加油哦～",
                    is_important=False,
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send morning care to user {user.id}: {e}")

        logger.info(f"Morning care task completed. Sent {sent_count} notifications")

    except Exception as e:
        logger.error(f"Morning care task failed: {e}")
    finally:
        db.close()


async def inactive_user_care_task():
    """未登录关怀任务 - 每天下午 2 点执行"""
    logger.info("Running inactive user care task")

    db = SessionLocal()
    try:
        notification_service = NotificationService(db)

        # 查询 2 天未登录的用户
        two_days_ago = datetime.now() - timedelta(days=2)
        inactive_users = (
            db.query(User)
            .filter(
                User.is_active == True,
                User.last_login < two_days_ago,
            )
            .limit(100)
            .all()
        )

        sent_count = 0
        for user in inactive_users:
            try:
                # 计算未登录天数
                days = (
                    (datetime.now() - user.last_login).days if user.last_login else 999
                )

                # 发送关怀通知
                await notification_service.send_notification(
                    user_id=user.id,
                    notification_type="care.inactive",
                    title="💙 想你啦！",
                    content=f"{days}天没见到你了，一切还好吗？",
                    is_important=False,
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send inactive care to user {user.id}: {e}")

        logger.info(
            f"Inactive user care task completed. Sent {sent_count} notifications"
        )

    except Exception as e:
        logger.error(f"Inactive user care task failed: {e}")
    finally:
        db.close()
