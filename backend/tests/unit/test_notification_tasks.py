"""
通知任务单元测试

测试通知相关的定时任务，包括 morning_care_task
Story 9.3: 通知引导
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from uuid import uuid4

from app.models.daily_tip import DailyTip, TipTopic
from app.models.user import User
from app.models.notification import Notification, NotificationStatus


class TestMorningCareTask:
    """早安关怀任务测试"""

    def _create_query_mock(self, return_value):
        """创建查询模拟"""
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.all.return_value = return_value
        mock_filter.first.return_value = return_value[0] if return_value else None
        mock_query.filter.return_value = mock_filter
        return mock_query

    @pytest.mark.asyncio
    async def test_morning_care_with_tip_enabled(self):
        """测试功能开关启用且有科普内容的情况"""
        # 创建模拟数据
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.is_active = True

        mock_tip = Mock(spec=DailyTip)
        mock_tip.id = 1
        mock_tip.title = "健康饮水指南"
        mock_tip.summary = "每日适量饮水对健康至关重要"

        # Mock SessionLocal
        mock_db = Mock()

        # 使用 side_effect 函数根据模型类返回不同的结果
        def query_side_effect(model):
            if model == User:
                m = Mock()
                f = Mock()
                f.all.return_value = [mock_user]
                m.filter.return_value = f
                return m
            elif model == DailyTip:
                # 返回当天的科普
                m = Mock()
                f = Mock()
                f.first.return_value = mock_tip
                m.filter.return_value = f
                return m
            return Mock()

        mock_db.query.side_effect = query_side_effect
        mock_db.close = Mock()

        # Mock 服务
        mock_notification_service = Mock()
        mock_notification_service.send_notification = AsyncMock()

        mock_config_service = Mock()
        mock_config_service.is_feature_enabled.return_value = True

        # Patch 所有依赖
        with patch(
            "app.schedulers.tasks.notification_tasks.SessionLocal", return_value=mock_db
        ):
            with patch(
                "app.schedulers.tasks.notification_tasks.NotificationService",
                return_value=mock_notification_service,
            ):
                with patch(
                    "app.schedulers.tasks.notification_tasks.SystemConfigService",
                    return_value=mock_config_service,
                ):
                    # 导入并执行任务
                    from app.schedulers.tasks.notification_tasks import (
                        morning_care_task,
                    )

                    await morning_care_task()

        # 验证
        mock_notification_service.send_notification.assert_called_once()
        call_kwargs = mock_notification_service.send_notification.call_args.kwargs

        assert "今日科普" in call_kwargs["title"]
        assert "健康饮水指南" in call_kwargs["title"]
        assert "deep_link" in call_kwargs["metadata"]
        assert call_kwargs["metadata"]["deep_link"] == "bmad://dashboard?tab=tip"
        assert call_kwargs["metadata"]["has_tip"] is True

    @pytest.mark.asyncio
    async def test_morning_care_with_tip_disabled(self):
        """测试功能开关关闭的情况"""
        # 创建模拟数据
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.is_active = True

        # Mock SessionLocal
        mock_db = Mock()

        def query_side_effect(model):
            if model == User:
                m = Mock()
                f = Mock()
                f.all.return_value = [mock_user]
                m.filter.return_value = f
                return m
            return Mock()

        mock_db.query.side_effect = query_side_effect
        mock_db.close = Mock()

        # Mock 服务
        mock_notification_service = Mock()
        mock_notification_service.send_notification = AsyncMock()

        mock_config_service = Mock()
        mock_config_service.is_feature_enabled.return_value = False

        # Patch 所有依赖
        with patch(
            "app.schedulers.tasks.notification_tasks.SessionLocal", return_value=mock_db
        ):
            with patch(
                "app.schedulers.tasks.notification_tasks.NotificationService",
                return_value=mock_notification_service,
            ):
                with patch(
                    "app.schedulers.tasks.notification_tasks.SystemConfigService",
                    return_value=mock_config_service,
                ):
                    from app.schedulers.tasks.notification_tasks import (
                        morning_care_task,
                    )

                    await morning_care_task()

        # 验证
        mock_notification_service.send_notification.assert_called_once()
        call_kwargs = mock_notification_service.send_notification.call_args.kwargs

        assert call_kwargs["title"] == "☀️ 早安！"
        assert call_kwargs["content"] == "新的一天开始了，今天也要加油哦～"
        assert call_kwargs["metadata"]["has_tip"] is False

    @pytest.mark.asyncio
    async def test_morning_care_no_tip(self):
        """测试功能开关启用但没有科普内容的情况"""
        # 创建模拟数据
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.is_active = True

        # Mock SessionLocal
        mock_db = Mock()

        daily_tip_query_count = [0]

        def query_side_effect(model):
            if model == User:
                m = Mock()
                f = Mock()
                f.all.return_value = [mock_user]
                m.filter.return_value = f
                return m
            elif model == DailyTip:
                daily_tip_query_count[0] += 1
                m = Mock()
                f = Mock()
                f.first.return_value = None  # 所有 first() 查询都返回 None

                # 第二次查询需要 order_by
                if daily_tip_query_count[0] > 1:
                    ob = Mock()
                    ob.first.return_value = None
                    f.order_by.return_value = ob

                m.filter.return_value = f
                return m
            return Mock()

        mock_db.query.side_effect = query_side_effect
        mock_db.close = Mock()

        # Mock 服务
        mock_notification_service = Mock()
        mock_notification_service.send_notification = AsyncMock()

        mock_config_service = Mock()
        mock_config_service.is_feature_enabled.return_value = True

        # Patch 所有依赖
        with patch(
            "app.schedulers.tasks.notification_tasks.SessionLocal", return_value=mock_db
        ):
            with patch(
                "app.schedulers.tasks.notification_tasks.NotificationService",
                return_value=mock_notification_service,
            ):
                with patch(
                    "app.schedulers.tasks.notification_tasks.SystemConfigService",
                    return_value=mock_config_service,
                ):
                    from app.schedulers.tasks.notification_tasks import (
                        morning_care_task,
                    )

                    await morning_care_task()

        # 验证 - 应该使用默认内容
        mock_notification_service.send_notification.assert_called_once()
        call_kwargs = mock_notification_service.send_notification.call_args.kwargs

        assert call_kwargs["title"] == "☀️ 早安！"
        assert call_kwargs["content"] == "新的一天开始了，今天也要加油哦～"
        assert call_kwargs["metadata"]["has_tip"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
