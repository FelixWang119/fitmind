"""通知系统 Schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== 通知相关 Schemas ====================


class NotificationBase(BaseModel):
    """通知基础 Schema"""

    notification_type: str
    title: str
    content: str


class NotificationCreate(NotificationBase):
    """创建通知请求"""

    user_id: int
    channel: str = "in_app"
    is_important: bool = False
    template_code: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    """通知响应 Schema"""

    id: UUID
    user_id: int
    channel: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    template_code: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """通知列表响应"""

    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """未读数量响应"""

    unread_count: int


# ==================== 通知设置 Schemas ====================


class UserNotificationSettingBase(BaseModel):
    """用户通知设置基础 Schema"""

    enabled: bool = True
    do_not_disturb_enabled: bool = True
    do_not_disturb_start: str = "22:00"
    do_not_disturb_end: str = "08:00"
    notify_habit_reminder: bool = True
    notify_milestone: bool = True
    notify_care: bool = True
    notify_system: bool = True
    in_app_enabled: bool = True
    email_enabled: bool = False
    max_notifications_per_day: int = 20
    min_notification_interval: int = 300


class UserNotificationSettingCreate(UserNotificationSettingBase):
    """创建用户通知设置"""

    user_id: int


class UserNotificationSettingUpdate(BaseModel):
    """更新用户通知设置"""

    enabled: Optional[bool] = None
    do_not_disturb_enabled: Optional[bool] = None
    do_not_disturb_start: Optional[str] = None
    do_not_disturb_end: Optional[str] = None
    notify_habit_reminder: Optional[bool] = None
    notify_milestone: Optional[bool] = None
    notify_care: Optional[bool] = None
    notify_system: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    max_notifications_per_day: Optional[int] = None
    min_notification_interval: Optional[int] = None


class UserNotificationSettingResponse(UserNotificationSettingBase):
    """用户通知设置响应"""

    id: UUID
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 通用 Schemas ====================


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应"""

    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
