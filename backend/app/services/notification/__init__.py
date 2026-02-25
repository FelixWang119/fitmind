"""通知系统服务模块

通知系统服务层包含：
- NotificationService: 核心通知服务
- TemplateRenderer: 模板渲染器
- EmailService: 邮件服务
"""

from app.services.notification.notification_service import (
    NotificationService,
    notification_service,
)
from app.services.notification.template_renderer import TemplateRenderer
from app.services.notification.email_service import EmailService, email_service

__all__ = [
    "NotificationService",
    "notification_service",
    "TemplateRenderer",
    "EmailService",
    "email_service",
]
