"""
通知服务单元测试

测试 NotificationService、TemplateRenderer 和 EmailService
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from uuid import uuid4

from app.services.notification import (
    NotificationService,
    TemplateRenderer,
    EmailService,
)
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationChannel,
    NotificationStatus,
    UserNotificationSetting,
    EventLog,
    EventLogStatus,
)


class TestTemplateRenderer:
    """模板渲染器测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock()
        return db

    @pytest.fixture
    def renderer(self, mock_db):
        """创建模板渲染器"""
        return TemplateRenderer(mock_db)

    def test_render_success(self, renderer, mock_db):
        """测试成功渲染模板"""
        # 准备测试数据
        template = NotificationTemplate(
            id=uuid4(),
            code="test_template",
            name="测试模板",
            title_template="你好，{{name}}！",
            content_template="欢迎使用{{product}}",
            is_active=True,
        )

        mock_db.query.return_value.filter.return_value.first.return_value = template

        # 执行渲染
        result = renderer.render(
            template_code="test_template",
            variables={"name": "Felix", "product": "FitMind"},
        )

        # 验证结果
        assert result is not None
        assert result["title"] == "你好，Felix！"
        assert "欢迎使用" in result["content"] and "FitMind" in result["content"]
        assert result["template_code"] == "test_template"

    def test_render_template_not_found(self, renderer, mock_db):
        """测试模板未找到"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = renderer.render(template_code="nonexistent", variables={})

        assert result is not None
        assert result["title"] == "FitMind 通知"
        assert result["content"] == "你有一条新的通知"

    def test_render_with_missing_variables(self, renderer, mock_db):
        """测试缺少变量的情况"""
        template = NotificationTemplate(
            id=uuid4(),
            code="test_template",
            name="测试模板",
            title_template="你好，{{name}}！",
            content_template="欢迎",
            is_active=True,
        )

        mock_db.query.return_value.filter.return_value.first.return_value = template

        # 不提供 name 变量
        result = renderer.render(template_code="test_template", variables={})

        # Jinja2 会渲染为空字符串或保持原样
        assert result is not None


class TestNotificationService:
    """通知服务测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock()
        db.flush = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def notification_service(self, mock_db):
        """创建通知服务"""
        return NotificationService(mock_db)

    @pytest.mark.asyncio
    async def test_send_notification_success(self, notification_service, mock_db):
        """测试成功发送通知"""
        # Mock user
        mock_user = Mock(id=1, email="test@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock settings
        mock_settings = Mock(
            enabled=True,
            email_enabled=False,
            is_in_do_not_disturb=Mock(return_value=False),
        )

        with patch.object(
            notification_service, "_get_user_settings", return_value=mock_settings
        ):
            with patch.object(
                notification_service, "_is_notification_type_enabled", return_value=True
            ):
                result = await notification_service.send_notification(
                    user_id=1,
                    notification_type="test",
                    title="测试通知",
                    content="测试内容",
                )

        assert result is not None
        assert result.notification_type == "test"
        assert result.title == "测试通知"
        assert result.status == NotificationStatus.SENT

    @pytest.mark.asyncio
    async def test_send_notification_disabled(self, notification_service, mock_db):
        """测试用户禁用通知"""
        mock_user = Mock(id=1)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_settings = Mock(enabled=False)

        with patch.object(
            notification_service, "_get_user_settings", return_value=mock_settings
        ):
            result = await notification_service.send_notification(
                user_id=1,
                notification_type="test",
                title="测试通知",
                content="测试内容",
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_send_with_template(self, notification_service, mock_db):
        """测试使用模板发送通知"""
        mock_user = Mock(id=1)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_settings = Mock(
            enabled=True,
            email_enabled=False,
            is_in_do_not_disturb=Mock(return_value=False),
        )

        mock_rendered = {
            "title": "渲染后的标题",
            "content": "渲染后的内容",
            "template_id": uuid4(),
        }

        with patch.object(
            notification_service, "_get_user_settings", return_value=mock_settings
        ):
            with patch.object(
                notification_service.template_renderer,
                "render",
                return_value=mock_rendered,
            ):
                result = await notification_service.send_with_template(
                    user_id=1,
                    notification_type="test",
                    template_code="test_template",
                    template_data={"key": "value"},
                )

        assert result is not None
        assert result.title == "渲染后的标题"

    def test_get_unread_count(self, notification_service, mock_db):
        """测试获取未读数量"""
        mock_db.query.return_value.filter.return_value.count.return_value = 5

        result = notification_service.get_unread_count(user_id=1)

        assert result == 5
        assert mock_db.query.call_count == 1

    def test_mark_all_as_read(self, notification_service, mock_db):
        """测试全部标记已读"""
        mock_db.query.return_value.filter.return_value.update.return_value = 10

        result = notification_service.mark_all_as_read(user_id=1)

        assert result == 10
        mock_db.commit.assert_called_once()

    def test_create_event_log(self, notification_service, mock_db):
        """测试创建事件日志"""
        event_data = {"key": "value"}

        result = notification_service.create_event_log(
            user_id=1,
            event_type="test.event",
            event_data=event_data,
            business_type="test",
            business_id="123",
        )

        assert result is not None
        assert result.event_type == "test.event"
        assert result.notification_status == EventLogStatus.PENDING

        # 验证添加到数据库
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestEmailService:
    """邮件服务测试"""

    @pytest.fixture
    def email_service(self):
        """创建邮件服务"""
        return EmailService()

    def test_email_service_initialization(self, email_service):
        """测试邮件服务初始化"""
        # 验证配置加载
        assert email_service.smtp_host is not None
        assert email_service.smtp_port is not None

    @pytest.mark.asyncio
    async def test_send_without_email(self, email_service):
        """测试没有邮箱地址"""
        result = await email_service.send(
            to="",
            subject="测试",
            html="<p>测试</p>",
        )

        assert result is False

    @pytest.mark.asyncio
    @patch(
        "aiosmtplib.send",
        new_callable=AsyncMock,
    )
    async def test_send_success(self, mock_send, email_service):
        """测试成功发送邮件"""
        # 设置邮件服务为启用状态
        email_service.enabled = True
        email_service.smtp_host = "smtp.test.com"
        email_service.smtp_port = 587

        result = await email_service.send(
            to="test@example.com",
            subject="测试邮件",
            html="<p>测试内容</p>",
        )

        # 验证发送方法被调用
        mock_send.assert_called_once()
        assert result is True


class TestEventLogProcessing:
    """事件日志处理测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock()
        db.query = Mock()
        db.commit = Mock()
        return db

    @pytest.fixture
    def notification_service(self, mock_db):
        """创建通知服务"""
        return NotificationService(mock_db)

    @pytest.mark.asyncio
    async def test_process_event_logs_empty(self, notification_service, mock_db):
        """测试处理空事件队列"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = await notification_service.process_event_logs()

        assert result == 0

    @pytest.mark.asyncio
    async def test_process_event_logs_with_handler(self, notification_service, mock_db):
        """测试处理有处理器的事件"""
        mock_event = Mock(
            id=uuid4(),
            event_type="habit.completed",
            event_data={"habit_name": "晨跑", "streak_days": 7},
            user_id=1,
            business_id="123",
        )
        mock_event.deduplication_hash = None

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_event
        ]

        # Mock handler
        with patch.object(
            notification_service, "_handle_habit_completed", new_callable=AsyncMock
        ) as mock_handler:
            result = await notification_service.process_event_logs()

            mock_handler.assert_called_once_with(mock_event)
            assert result >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
