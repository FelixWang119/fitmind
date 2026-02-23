"""电子邮件服务

提供邮件发送功能，支持：
- 密码重置邮件
- 验证邮件
- 通知邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        self.smtp_server = getattr(settings, "SMTP_SERVER", "smtp.example.com")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_username = getattr(settings, "SMTP_USERNAME", "")
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", "")
        self.from_email = getattr(settings, "FROM_EMAIL", "noreply@example.com")
        self.use_tls = getattr(settings, "SMTP_USE_TLS", True)

    async def send_password_reset_email(self, to_email: str, token: str) -> bool:
        """发送密码重置邮件

        Args:
            to_email: 收件人邮箱
            token: 密码重置令牌

        Returns:
            bool: 是否发送成功
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        subject = "重置您的密码 - AI 体重管理助手"

        # HTML 邮件内容
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90D9;">密码重置请求</h2>
                <p>您好，</p>
                <p>我们收到您的密码重置请求。点击以下按钮重置您的密码：</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #4A90D9; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        重置密码
                    </a>
                </div>
                
                <p>或者复制以下链接到浏览器：</p>
                <p style="word-break: break-all; color: #4A90D9;">{reset_url}</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 14px;">
                    <strong>重要提示：</strong>
                </p>
                <ul style="color: #999; font-size: 14px;">
                    <li>此链接有效期为 24 小时</li>
                    <li>如果您没有请求重置密码，请忽略此邮件</li>
                    <li>不要向任何人分享此链接</li>
                </ul>
                
                <p style="margin-top: 30px; color: #999; font-size: 12px;">
                    此邮件由 AI 体重管理助手自动发送，请勿回复。
                </p>
            </div>
        </body>
        </html>
        """

        # 纯文本内容（备用）
        text_content = f"""
        密码重置请求
        
        您好，
        
        我们收到您的密码重置请求。点击以下链接重置您的密码：
        {reset_url}
        
        重要提示：
        - 此链接有效期为 24 小时
        - 如果您没有请求重置密码，请忽略此邮件
        - 不要向任何人分享此链接
        
        此邮件由 AI 体重管理助手自动发送，请勿回复。
        """

        return await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """通用邮件发送方法

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML 内容
            text_content: 纯文本内容（可选）

        Returns:
            bool: 是否发送成功
        """
        return await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """内部邮件发送实现"""
        try:
            # 检查 SMTP 配置
            if not self.smtp_username or not self.smtp_password:
                logger.warning(
                    "SMTP not configured, email would be sent in production",
                    to_email=to_email,
                    subject=subject,
                )
                # 开发模式：记录邮件内容但不发送
                logger.info(
                    "Email content (development mode)",
                    to=to_email,
                    subject=subject,
                    # html=html_content  # 不记录完整 HTML 避免日志过大
                )
                return True

            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # 添加纯文本和 HTML 版本
            if text_content:
                part1 = MIMEText(text_content, "plain", "utf-8")
                msg.attach(part1)

            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part2)

            # 发送邮件
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()

            logger.info("Email sent successfully", to_email=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error(
                "Failed to send email", to_email=to_email, subject=subject, error=str(e)
            )
            return False


# 全局邮件服务实例
email_service = EmailService()
