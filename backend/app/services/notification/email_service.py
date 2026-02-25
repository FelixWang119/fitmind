"""邮件通知服务"""

import logging
import os
from typing import Optional

from app.models.user import User

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务

    Phase 1 使用 SMTP 或第三方服务（SendGrid/阿里云邮件推送）
    Phase 2 可以扩展更多功能
    """

    def __init__(self):
        # 邮件服务配置
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "apikey")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@fitmind.app")
        self.from_name = os.getenv("FROM_NAME", "FitMind")

        # 是否启用邮件服务
        self.enabled = bool(self.smtp_password)

        if not self.enabled:
            logger.warning("Email service is not configured. Emails will not be sent.")

    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
    ) -> bool:
        """
        发送邮件

        Args:
            to: 收件人邮箱
            subject: 邮件主题
            html: HTML 内容
            text: 纯文本内容（可选，如果没有则从 HTML 提取）

        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.info(f"Email service disabled, skipping send to {to}")
            return False

        if not to:
            logger.warning("No recipient email address provided")
            return False

        try:
            # Phase 1: 使用 aiosmtplib 发送
            # 这里先实现一个简化版本，实际使用时需要配置 SMTP
            await self._send_via_smtp(to, subject, html, text)
            logger.info(f"Email sent successfully to {to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    async def _send_via_smtp(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
    ):
        """通过 SMTP 发送邮件"""
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # 创建邮件
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to

        # 添加纯文本版本（如果没有提供，则简单提取）
        if not text:
            # 简单去除 HTML 标签
            import re

            text = re.sub(r"<[^>]+>", "", html)

        # 添加内容
        message.attach(MIMEText(text, "plain", "utf-8"))
        message.attach(MIMEText(html, "html", "utf-8"))

        # 发送邮件
        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_username,
            password=self.smtp_password,
            start_tls=True,
        )

    async def send_notification_email(
        self,
        user: User,
        subject: str,
        content: str,
        notification_type: Optional[str] = None,
    ) -> bool:
        """
        发送通知邮件

        Args:
            user: 用户对象
            subject: 邮件主题
            content: 邮件内容
            notification_type: 通知类型（用于邮件模板选择）

        Returns:
            bool: 是否发送成功
        """
        if not user.email:
            logger.warning(f"User {user.id} has no email address")
            return False

        # 检查用户是否启用邮件通知
        if user.notification_settings and not user.notification_settings.email_enabled:
            logger.info(f"User {user.id} has email notifications disabled")
            return False

        # 渲染邮件模板
        html = self._render_email_template(
            username=user.username or user.email,
            subject=subject,
            content=content,
        )

        # 发送邮件
        return await self.send(
            to=user.email,
            subject=subject,
            html=html,
        )

    def _render_email_template(self, username: str, subject: str, content: str) -> str:
        """渲染邮件 HTML 模板"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 FitMind</h1>
        </div>
    </div>

    <div class="content">
        <p>亲爱的 {username}，</p>
        <p>{content}</p>
        <a href="https://fitmind.app" class="button">打开 App 查看</a>
    </div>

    <div class="footer">
        <p>此邮件由 FitMind 自动发送，请勿回复。</p>
        <p>© 2026 FitMind. All rights reserved.</p>
        <p>
            <a href="https://fitmind.app/settings/notifications" style="color: #999;">
                管理通知设置
            </a>
        </p>
    </div>
</body>
</html>
"""

    def test_connection(self) -> bool:
        """测试邮件服务连接"""
        if not self.enabled:
            logger.warning("Email service is not configured")
            return False

        # 这里可以实现一个连接测试
        logger.info("Email service is configured and ready")
        return True


# 全局邮件服务实例
email_service = EmailService()
