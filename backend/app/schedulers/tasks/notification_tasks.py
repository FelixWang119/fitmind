"""通知相关定时任务"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.notification import NotificationService
from app.models.notification import (
    EventLog,
    EventLogStatus,
    UserNotificationSetting,
    Notification,
    NotificationStatus,
)
from app.models.user import User
from app.models.habit import Habit, HabitCompletion

logger = logging.getLogger(__name__)

# 习惯类型对应的提醒内容模板
HABIT_REMINDER_TEMPLATES = {
    # 饮水 (HYDRATION)
    "HYDRATION": {
        "title": "💧 饮水提醒",
        "content": "距离目标还差{remaining}杯水，今天加油！",
    },
    # 运动 (EXERCISE)
    "EXERCISE": {
        "title": "🏃 运动提醒",
        "content": "今日{habit_name}还未完成，现在开始吧！",
    },
    # 睡眠 (SLEEP)
    "SLEEP": {
        "title": "😴 睡眠提醒",
        "content": "夜深了，该休息了～",
    },
    # 冥想/心理健康 (MENTAL_HEALTH)
    "MENTAL_HEALTH": {
        "title": "🧘 冥想提醒",
        "content": "放松时刻到了，花几分钟冥想吧",
    },
    # 饮食 (DIET)
    "DIET": {
        "title": "🍽️ 饮食提醒",
        "content": "今日饮食还未记录，记得打卡哦",
    },
    # 其他
    "OTHER": {
        "title": "⏰ 打卡提醒",
        "content": "别忘了今天的{habit_name}",
    },
}


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_today_completion_count(db: Session, habit_id: int) -> int:
    """获取习惯今日完成次数"""
    today = date.today()
    return (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date >= today,
        )
        .count()
    )


def _check_do_not_disturb(db: Session, user_id: int) -> bool:
    """检查用户是否在免打扰时段"""
    settings = (
        db.query(UserNotificationSetting)
        .filter(UserNotificationSetting.user_id == user_id)
        .first()
    )
    if not settings:
        return False
    return settings.is_in_do_not_disturb()


def _check_daily_limit(db: Session, user_id: int) -> bool:
    """检查用户今日通知数量是否已达上限"""
    settings = (
        db.query(UserNotificationSetting)
        .filter(UserNotificationSetting.user_id == user_id)
        .first()
    )
    if not settings:
        return True  # 没有设置则不限制

    max_per_day = settings.max_notifications_per_day or 20

    # 查询今日已发送的通知数量
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.created_at >= today_start,
            or_(
                Notification.status == NotificationStatus.SENT,
                Notification.status == NotificationStatus.DELIVERED,
                Notification.status == NotificationStatus.READ,
            ),
        )
        .count()
    )

    return today_count < max_per_day


def _generate_reminder_content(habit: Habit, completed_today: bool) -> dict:
    """生成提醒内容"""
    category = habit.category.upper() if habit.category else "OTHER"
    template = HABIT_REMINDER_TEMPLATES.get(category, HABIT_REMINDER_TEMPLATES["OTHER"])

    title = template["title"]

    # 根据完成状态生成内容
    if completed_today:
        # 已完成，给出鼓励
        if category == "HYDRATION":
            content = f"太棒了！{habit.name}已完成，继续保持！"
        elif category == "EXERCISE":
            content = f"太厉害了！今日{habit.name}已完成！"
        elif category == "SLEEP":
            content = "祝你有个好梦！🌙"
        elif category == "MENTAL_HEALTH":
            content = "继续保持平静的心态～"
        else:
            content = f"太棒了！{habit.name}已完成！"
    else:
        # 未完成，生成提醒
        content = template["content"].format(
            habit_name=habit.name,
            remaining=habit.target_value or 1,
        )

    return {"title": title, "content": content}


async def habit_reminder_task():
    """习惯提醒轮询任务 - 每分钟执行"""
    logger.info("Running habit reminder task")

    db = SessionLocal()
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 查询当前时间需要提醒的习惯
        # 只查询本分钟内应该提醒的习惯（考虑定时任务可能有轻微延迟）
        habits_to_remind = (
            db.query(Habit)
            .filter(
                Habit.reminder_enabled == True,
                Habit.reminder_time == current_time,
                Habit.is_active == True,
            )
            .all()
        )

        if not habits_to_remind:
            logger.debug(f"No habits to remind at {current_time}")
            return

        logger.info(f"Found {len(habits_to_remind)} habits to remind at {current_time}")

        notification_service = NotificationService(db)
        sent_count = 0
        skipped_dnd_count = 0
        skipped_limit_count = 0
        skipped_completed_count = 0

        for habit in habits_to_remind:
            try:
                # 1. 检查用户通知设置是否存在
                user = db.query(User).filter(User.id == habit.user_id).first()
                if not user or not user.is_active:
                    continue

                # 2. 检查是否在免打扰时段
                if _check_do_not_disturb(db, habit.user_id):
                    logger.debug(f"Skipping reminder for habit {habit.id}: DND enabled")
                    skipped_dnd_count += 1
                    continue

                # 3. 检查每日通知上限
                if not _check_daily_limit(db, habit.user_id):
                    logger.debug(
                        f"Skipping reminder for habit {habit.id}: daily limit reached"
                    )
                    skipped_limit_count += 1
                    continue

                # 4. 检查今日是否已完成
                completed_today = _get_today_completion_count(db, habit.id) > 0
                if completed_today:
                    logger.debug(
                        f"Skipping reminder for habit {habit.id}: already completed today"
                    )
                    skipped_completed_count += 1
                    continue

                # 5. 生成提醒内容
                reminder_content = _generate_reminder_content(habit, completed_today)

                # 6. 发送通知
                await notification_service.send_notification(
                    user_id=habit.user_id,
                    notification_type="habit.reminder",
                    title=reminder_content["title"],
                    content=reminder_content["content"],
                    is_important=False,
                    source_type="habit",
                    source_id=str(habit.id),
                    metadata={"habit_id": habit.id, "habit_name": habit.name},
                )
                sent_count += 1
                logger.info(f"Sent reminder for habit {habit.id}: {habit.name}")

            except Exception as e:
                logger.error(f"Failed to send reminder for habit {habit.id}: {e}")

        logger.info(
            f"Habit reminder task completed. Sent: {sent_count}, "
            f"Skipped DND: {skipped_dnd_count}, "
            f"Skipped limit: {skipped_limit_count}, "
            f"Skipped completed: {skipped_completed_count}"
        )

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
