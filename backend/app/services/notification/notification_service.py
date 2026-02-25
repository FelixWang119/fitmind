"""通知服务"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import (
    EventLog,
    EventLogStatus,
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationTemplate,
    UserNotificationSetting,
)
from app.models.user import User
from app.services.notification.template_renderer import TemplateRenderer
from app.services.notification.email_service import email_service

logger = logging.getLogger(__name__)

# 重要通知类型（会发送邮件）
IMPORTANT_NOTIFICATION_TYPES = {
    "habit.streak_30days",
    "milestone.weight_goal",
    "milestone.streak_master",
    "report.weekly",
    "report.monthly",
}


class NotificationService:
    """通知服务"""

    def __init__(self, db: Session):
        self.db = db
        self.template_renderer = TemplateRenderer(db)

    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        content: str,
        template_code: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        channel: Optional[NotificationChannel] = None,
        is_important: bool = False,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Notification]:
        """
        发送通知

        Args:
            user_id: 用户 ID
            notification_type: 通知类型
            title: 标题
            content: 内容
            template_code: 模板代码（可选）
            template_data: 模板变量数据（可选）
            channel: 通知渠道（可选，默认根据配置决定）
            is_important: 是否重要通知（重要通知会发送邮件）
            source_type: 触发源类型
            source_id: 触发源 ID
            metadata: 元数据

        Returns:
            Notification: 通知对象，如果发送失败返回 None
        """
        # 1. 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found: {user_id}")
            return None

        # 2. 获取用户通知设置
        settings = self._get_user_settings(user_id)
        if not settings or not settings.enabled:
            logger.info(f"Notifications disabled for user {user_id}")
            return None

        # 3. 检查免打扰时间
        if settings.is_in_do_not_disturb():
            logger.info(f"User {user_id} is in do-not-disturb period")
            # 可以延迟发送，这里简单跳过
            return None

        # 4. 检查通知类型开关
        if not self._is_notification_type_enabled(settings, notification_type):
            logger.info(
                f"Notification type {notification_type} disabled for user {user_id}"
            )
            return None

        # 5. 创建通知记录
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            channel=channel or NotificationChannel.IN_APP,
            status=NotificationStatus.PENDING,
            template_data=template_data or {},
            source_type=source_type,
            source_id=source_id,
            metadata_=metadata or {},
        )

        if template_code:
            template = self._get_template_by_code(template_code)
            if template:
                notification.template_id = template.id

        self.db.add(notification)
        self.db.flush()  # 获取 notification.id

        # 6. 发送通知
        try:
            # 发送到 App 内
            notification.status = NotificationStatus.SENT
            logger.info(f"Notification sent to user {user_id}: {notification_type}")

            # 如果是重要通知，发送邮件
            if is_important or notification_type in IMPORTANT_NOTIFICATION_TYPES:
                if settings.email_enabled and user.email:
                    await self._send_email(
                        user=user,
                        subject=title,
                        content=content,
                        notification_type=notification_type,
                    )

            self.db.commit()
            return notification

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            self.db.rollback()
            notification.status = NotificationStatus.FAILED
            self.db.commit()
            return None

    async def send_with_template(
        self,
        user_id: int,
        notification_type: str,
        template_code: str,
        template_data: Dict[str, Any],
        is_important: bool = False,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> Optional[Notification]:
        """
        使用模板发送通知

        Args:
            user_id: 用户 ID
            notification_type: 通知类型
            template_code: 模板代码
            template_data: 模板变量
            is_important: 是否重要通知
            source_type: 触发源类型
            source_id: 触发源 ID

        Returns:
            Notification: 通知对象
        """
        # 渲染模板
        rendered = self.template_renderer.render(template_code, template_data)

        if not rendered:
            logger.error(f"Failed to render template: {template_code}")
            return None

        return await self.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=rendered["title"],
            content=rendered["content"],
            template_code=template_code,
            template_data=template_data,
            is_important=is_important,
            source_type=source_type,
            source_id=source_id,
        )

    def create_event_log(
        self,
        user_id: int,
        event_type: str,
        event_data: Dict[str, Any],
        occurred_at: Optional[datetime] = None,
        business_type: Optional[str] = None,
        business_id: Optional[str] = None,
        deduplication_key: Optional[str] = None,
    ) -> EventLog:
        """
        创建事件日志（用于解耦业务系统和通知系统）

        Args:
            user_id: 用户 ID
            event_type: 事件类型
            event_data: 事件数据
            occurred_at: 事件发生时间
            business_type: 业务类型
            business_id: 业务记录 ID
            deduplication_key: 去重键

        Returns:
            EventLog: 事件日志对象
        """
        # 计算去重 hash
        deduplication_hash = None
        if deduplication_key:
            deduplication_hash = hashlib.sha256(deduplication_key.encode()).hexdigest()

        event_log = EventLog(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            occurred_at=occurred_at or datetime.utcnow(),
            business_type=business_type,
            business_id=business_id,
            notification_status=EventLogStatus.PENDING,
            deduplication_key=deduplication_key,
            deduplication_hash=deduplication_hash,
        )

        self.db.add(event_log)
        self.db.commit()

        return event_log

    async def process_event_logs(self, batch_size: int = 100) -> int:
        """
        处理待发送的事件日志

        Args:
            batch_size: 每批处理的數量

        Returns:
            int: 处理的事件数量
        """
        # 查询待处理的事件
        events = (
            self.db.query(EventLog)
            .filter(
                EventLog.notification_status == EventLogStatus.PENDING,
            )
            .order_by(EventLog.occurred_at)
            .limit(batch_size)
            .all()
        )

        processed_count = 0
        for event in events:
            try:
                # 去重检查
                if event.deduplication_hash:
                    duplicate = (
                        self.db.query(EventLog)
                        .filter(
                            EventLog.deduplication_hash == event.deduplication_hash,
                            EventLog.id != event.id,
                            EventLog.notification_status == EventLogStatus.SENT,
                            EventLog.created_at > event.created_at - timedelta(hours=1),
                        )
                        .first()
                    )
                    if duplicate:
                        logger.info(f"Duplicate event skipped: {event.id}")
                        event.mark_as_skipped()
                        self.db.commit()
                        continue

                # 根据事件类型获取处理器
                handler = self._get_event_handler(event.event_type)
                if handler:
                    await handler(event)
                    processed_count += 1
                else:
                    logger.warning(f"No handler for event type: {event.event_type}")
                    event.mark_as_skipped()

                self.db.commit()

            except Exception as e:
                logger.error(f"Failed to process event {event.id}: {e}")
                event.mark_as_failed(str(e))
                self.db.commit()

        return processed_count

    def _get_event_handler(self, event_type: str):
        """获取事件处理器"""
        # 这里可以注册不同的事件处理器
        # Phase 1 先实现一个简单的路由
        handlers = {
            "habit.completed": self._handle_habit_completed,
            "milestone.achieved": self._handle_milestone_achieved,
        }
        return handlers.get(event_type)

    async def _handle_habit_completed(self, event: EventLog):
        """处理习惯完成事件"""
        habit_data = event.event_data
        streak_days = habit_data.get("streak_days", 1)

        # 根据连续天数选择模板
        if streak_days >= 30:
            template_code = "habit_streak_30"
            is_important = True
        elif streak_days >= 7:
            template_code = "habit_streak_7"
            is_important = False
        else:
            template_code = "habit_completed"
            is_important = False

        await self.send_with_template(
            user_id=event.user_id,
            notification_type="habit.completed",
            template_code=template_code,
            template_data=habit_data,
            is_important=is_important,
            source_type="habit",
            source_id=event.business_id,
        )

        event.mark_as_sent()

    async def _handle_milestone_achieved(self, event: EventLog):
        """处理里程碑达成事件"""
        milestone_data = event.event_data
        milestone_type = milestone_data.get("milestone_type", "unknown")

        # 使用通用里程碑模板
        template_code = "milestone_weight_goal"  # 可以根据 milestone_type 选择不同模板

        await self.send_with_template(
            user_id=event.user_id,
            notification_type="milestone.achieved",
            template_code=template_code,
            template_data=milestone_data,
            is_important=True,  # 里程碑总是重要通知
            source_type="milestone",
            source_id=event.business_id,
        )

        event.mark_as_sent()

    async def _send_email(
        self,
        user: User,
        subject: str,
        content: str,
        notification_type: str,
    ):
        """发送邮件通知"""
        try:
            await email_service.send_notification_email(
                user=user,
                subject=subject,
                content=content,
                notification_type=notification_type,
            )
        except Exception as e:
            logger.error(f"Failed to send email to user {user.id}: {e}")

    def _get_user_settings(self, user_id: int) -> Optional[UserNotificationSetting]:
        """获取用户通知设置"""
        return (
            self.db.query(UserNotificationSetting)
            .filter(UserNotificationSetting.user_id == user_id)
            .first()
        )

    def _is_notification_type_enabled(
        self, settings: UserNotificationSetting, notification_type: str
    ) -> bool:
        """检查通知类型是否启用"""
        type_mapping = {
            "habit.completed": settings.notify_habit_reminder,
            "habit.streak_7days": settings.notify_habit_reminder,
            "habit.streak_30days": settings.notify_habit_reminder,
            "milestone.achieved": settings.notify_milestone,
            "milestone.weight_goal": settings.notify_milestone,
            "care.morning": settings.notify_care,
            "care.inactive": settings.notify_care,
        }

        return type_mapping.get(notification_type, True)

    def _get_template_by_code(self, code: str) -> Optional[NotificationTemplate]:
        """根据代码获取模板"""
        return (
            self.db.query(NotificationTemplate)
            .filter(NotificationTemplate.code == code)
            .first()
        )

    def mark_notification_as_read(self, notification_id: UUID, user_id: int) -> bool:
        """标记通知为已读"""
        notification = (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            return False

        notification.mark_as_read()
        self.db.commit()
        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        updated = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .update(
                {
                    Notification.is_read: True,
                    Notification.read_at: datetime.utcnow(),
                    Notification.status: NotificationStatus.READ,
                }
            )
        )
        self.db.commit()
        return updated

    def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数量"""
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .count()
        )

    def get_notifications(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> List[Notification]:
        """获取通知列表"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )


# 全局通知服务实例（用于非依赖注入场景）
notification_service: Optional[NotificationService] = None
