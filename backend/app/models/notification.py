"""通知系统数据库模型"""

import uuid
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Index,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class NotificationStatus(str, PyEnum):
    """通知状态枚举"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class NotificationChannel(str, PyEnum):
    """通知渠道枚举"""

    IN_APP = "in_app"
    EMAIL = "email"


class Notification(Base):
    """通知记录表"""

    __tablename__ = "notifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 通知内容
    notification_type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    template_id = Column(
        PGUUID(as_uuid=True), ForeignKey("notification_templates.id"), nullable=True
    )
    template_data = Column(JSON, default=dict)

    # 通知渠道
    channel = Column(
        SQLEnum(NotificationChannel), nullable=False, default=NotificationChannel.IN_APP
    )

    # 通知状态
    status = Column(
        SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True
    )
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # 元数据
    metadata_ = Column("metadata", JSON, default=dict)
    source_type = Column(String(50), nullable=True)  # 触发源类型
    source_id = Column(String(100), nullable=True)  # 触发源 ID

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate", back_populates="notifications")

    # 索引
    __table_args__ = (
        Index("idx_notifications_user_status", "user_id", "status"),
        Index("idx_notifications_user_created", "user_id", "created_at"),
    )

    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.status = NotificationStatus.READ


class NotificationTemplate(Base):
    """通知模板表"""

    __tablename__ = "notification_templates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True, index=True)  # 模板代码
    name = Column(String(100), nullable=False)  # 模板名称
    description = Column(Text, nullable=True)

    # 模板内容
    title_template = Column(String(200), nullable=False)  # 标题模板
    content_template = Column(Text, nullable=False)  # 内容模板

    # 适用场景
    event_type = Column(String(50), nullable=True, index=True)  # 关联事件类型

    # 模板变量定义
    variables = Column(JSON, default=list)  # [{"name": "weight", "type": "number"}]

    # 状态
    is_active = Column(Boolean, default=True, index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    notifications = relationship("Notification", back_populates="template")

    def render(self, variables: dict) -> dict:
        """渲染模板"""
        from jinja2 import Template

        title = Template(self.title_template).render(**variables)
        content = Template(self.content_template).render(**variables)

        return {"title": title, "content": content}


class UserNotificationSetting(Base):
    """用户通知设置表"""

    __tablename__ = "user_notification_settings"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # 全局设置
    enabled = Column(Boolean, default=True)  # 是否启用通知
    do_not_disturb_enabled = Column(Boolean, default=True)  # 是否启用免打扰
    do_not_disturb_start = Column(String(5), default="22:00")  # 免打扰开始时间
    do_not_disturb_end = Column(String(5), default="08:00")  # 免打扰结束时间

    # 通知类型开关
    notify_habit_reminder = Column(Boolean, default=True)
    notify_milestone = Column(Boolean, default=True)
    notify_care = Column(Boolean, default=True)
    notify_system = Column(Boolean, default=True)

    # 渠道设置
    in_app_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=False)

    # 频率限制
    max_notifications_per_day = Column(Integer, default=20)
    min_notification_interval = Column(Integer, default=300)  # 最小间隔（秒）

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="notification_settings")

    def is_in_do_not_disturb(self, current_time: datetime = None) -> bool:
        """检查当前时间是否在免打扰时段"""
        if not self.do_not_disturb_enabled:
            return False

        from datetime import datetime as dt

        if current_time is None:
            current_time = dt.utcnow()

        current_time_str = current_time.strftime("%H:%M")
        return self.do_not_disturb_start <= current_time_str <= self.do_not_disturb_end


class EventLogStatus(str, PyEnum):
    """事件日志状态枚举"""

    PENDING = "pending"
    SENT = "sent"
    SKIPPED = "skipped"
    FAILED = "failed"


class EventLog(Base):
    """事件日志表（解耦业务系统和通知系统）"""

    __tablename__ = "event_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 事件基本信息
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # 业务信息
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_type = Column(String(50), nullable=True)  # 业务类型
    business_id = Column(String(100), nullable=True)  # 业务记录 ID

    # 通知处理状态
    notification_status = Column(
        SQLEnum(EventLogStatus), default=EventLogStatus.PENDING, index=True
    )
    notification_sent_at = Column(DateTime, nullable=True)
    notification_error = Column(Text, nullable=True)

    # 去重控制
    deduplication_key = Column(String(100), nullable=True, index=True)
    deduplication_hash = Column(String(64), nullable=True)  # SHA256 hash

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    # 索引：用于轮询 pending 状态事件
    __table_args__ = (
        Index(
            "idx_event_logs_pending",
            "notification_status",
            "occurred_at",
            postgresql_where=func.lower(notification_status) == "pending",
        ),
    )

    def mark_as_sent(self):
        """标记为已发送"""
        self.notification_status = EventLogStatus.SENT
        self.notification_sent_at = datetime.utcnow()

    def mark_as_failed(self, error: str):
        """标记为失败"""
        self.notification_status = EventLogStatus.FAILED
        self.notification_error = error
