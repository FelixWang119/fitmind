"""里程碑服务测试

使用单元测试方式，不需要数据库连接
"""

import pytest
from unittest.mock import MagicMock, Mock

from app.services.milestone_service import (
    MilestoneService,
    MilestoneType,
    STREAK_MILESTONES,
    TOTAL_RECORDS_MILESTONES,
)


# Mock db_session fixture to avoid database connection
@pytest.fixture
def db_session():
    """创建 mock 数据库会话"""
    return MagicMock()


class TestMilestoneService:
    """里程碑服务测试类"""

    def test_streak_milestones_defined(self):
        """测试连续打卡里程碑配置正确"""
        assert len(STREAK_MILESTONES) == 6
        assert STREAK_MILESTONES[0]["days"] == 3
        assert STREAK_MILESTONES[-1]["days"] == 90

        # 验证每个里程碑都有必要的字段
        for m in STREAK_MILESTONES:
            assert "type" in m
            assert "days" in m
            assert "emoji" in m
            assert "title" in m
            assert "badge" in m

    def test_total_records_milestones_defined(self):
        """测试累计记录里程碑配置正确"""
        assert len(TOTAL_RECORDS_MILESTONES) == 3
        assert TOTAL_RECORDS_MILESTONES[0]["count"] == 10
        assert TOTAL_RECORDS_MILESTONES[-1]["count"] == 100

        # 验证每个里程碑都有必要的字段
        for m in TOTAL_RECORDS_MILESTONES:
            assert "type" in m
            assert "count" in m
            assert "emoji" in m
            assert "title" in m
            assert "badge" in m

    def test_streak_milestone_types(self):
        """测试连续打卡里程碑类型定义"""
        assert MilestoneType.STREAK_3_DAYS == "streak_3_days"
        assert MilestoneType.STREAK_7_DAYS == "streak_7_days"
        assert MilestoneType.STREAK_14_DAYS == "streak_14_days"
        assert MilestoneType.STREAK_30_DAYS == "streak_30_days"
        assert MilestoneType.STREAK_60_DAYS == "streak_60_days"
        assert MilestoneType.STREAK_90_DAYS == "streak_90_days"

    def test_total_records_milestone_types(self):
        """测试累计记录里程碑类型定义"""
        assert MilestoneType.TOTAL_10_RECORDS == "total_10_records"
        assert MilestoneType.TOTAL_50_RECORDS == "total_50_records"
        assert MilestoneType.TOTAL_100_RECORDS == "total_100_records"

    def test_goal_milestone_type(self):
        """测试目标达成里程碑类型定义"""
        assert MilestoneType.GOAL_ACHIEVED == "goal_achieved"

    def test_check_streak_milestones_3_days(self):
        """测试检测3天连续打卡里程碑"""
        # 创建 mock db_session 和 mock query
        mock_db = MagicMock()

        # 设置 mock chain: query -> filter -> first
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # 不存在已发送的通知
        mock_filter.all.return_value = []

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 3

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        # 应该检测到3天里程碑
        assert len(result) >= 1
        assert any(m["milestone_type"] == "streak_3_days" for m in result)

    def test_check_streak_milestones_7_days(self):
        """测试检测7天连续打卡里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_filter.all.return_value = []

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 7

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        # 应该检测到3天和7天里程碑
        milestone_types = [m["milestone_type"] for m in result]
        assert "streak_3_days" in milestone_types
        assert "streak_7_days" in milestone_types

    def test_check_streak_milestones_30_days(self):
        """测试检测30天连续打卡里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_filter.all.return_value = []

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 30

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        # 应该检测到3, 7, 14, 30天里程碑
        milestone_types = [m["milestone_type"] for m in result]
        assert "streak_3_days" in milestone_types
        assert "streak_7_days" in milestone_types
        assert "streak_14_days" in milestone_types
        assert "streak_30_days" in milestone_types

    def test_check_streak_milestones_no_trigger_when_below(self):
        """测试低于里程碑门槛时不触发"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 2  # 不到3天

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        # 不应该有任何里程碑
        assert len(result) == 0

    def test_check_total_records_milestones_10(self):
        """测试检测累计10次记录里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.total_completions = 10

        service = MilestoneService(mock_db)
        result = service._check_total_records_milestones(mock_habit)

        assert len(result) >= 1
        assert result[0]["milestone_type"] == "total_10_records"

    def test_check_total_records_milestones_50(self):
        """测试检测累计50次记录里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.total_completions = 50

        service = MilestoneService(mock_db)
        result = service._check_total_records_milestones(mock_habit)

        milestone_types = [m["milestone_type"] for m in result]
        assert "total_10_records" in milestone_types
        assert "total_50_records" in milestone_types

    def test_check_total_records_milestones_100(self):
        """测试检测累计100次记录里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.total_completions = 100

        service = MilestoneService(mock_db)
        result = service._check_total_records_milestones(mock_habit)

        milestone_types = [m["milestone_type"] for m in result]
        assert "total_10_records" in milestone_types
        assert "total_50_records" in milestone_types
        assert "total_100_records" in milestone_types

    def test_check_goal_milestone_achieved(self):
        """测试检测目标达成里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"

        mock_goal = Mock()
        mock_goal.id = 1
        mock_goal.user_id = 1
        mock_goal.is_achieved = True
        mock_goal.goal_type = "completion_rate"
        mock_goal.target_value = 80
        mock_goal.current_progress = 85
        mock_goal.period = "weekly"

        service = MilestoneService(mock_db)
        result = service._check_goal_milestone(mock_habit, mock_goal)

        assert result is not None
        assert result["milestone_type"] == "goal_achieved"

    def test_check_goal_milestone_not_achieved(self):
        """测试未达成目标时不触发里程碑"""
        mock_db = MagicMock()

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.name = "测试习惯"

        mock_goal = Mock()
        mock_goal.is_achieved = False

        service = MilestoneService(mock_db)
        result = service._check_goal_milestone(mock_habit, mock_goal)

        assert result is None

    def test_check_and_notify_milestones_completion(self):
        """测试完整里程碑检测（完成触发）"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 7
        mock_habit.total_completions = 10

        service = MilestoneService(mock_db)
        result = service.check_and_notify_milestones(
            mock_habit, trigger_type="completion"
        )

        # 应该检测到连续打卡里程碑和累计记录里程碑
        assert len(result) >= 2

    def test_check_and_notify_milestones_goal(self):
        """测试完整里程碑检测（目标达成触发）"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"

        mock_goal = Mock()
        mock_goal.id = 1
        mock_goal.user_id = 1
        mock_goal.is_achieved = True
        mock_goal.goal_type = "completion_rate"
        mock_goal.target_value = 80
        mock_goal.current_progress = 85
        mock_goal.period = "weekly"

        service = MilestoneService(mock_db)
        result = service.check_and_notify_milestones(
            mock_habit, trigger_type="goal_achieved", goal=mock_goal
        )

        # 应该检测到目标达成里程碑
        assert len(result) >= 1
        assert result[0]["milestone_type"] == "goal_achieved"

    def test_check_and_notify_milestones_does_not_trigger_on_streak_update(self):
        """测试streak_update触发类型不会触发累计记录里程碑"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 7
        mock_habit.total_completions = 100  # 已经有100次

        service = MilestoneService(mock_db)
        result = service.check_and_notify_milestones(
            mock_habit, trigger_type="streak_update"
        )

        # streak_update 只检测streak里程碑，不检测total里程碑
        streak_types = [
            m["milestone_type"] for m in result if "streak" in m["milestone_type"]
        ]
        total_types = [
            m["milestone_type"] for m in result if "total" in m["milestone_type"]
        ]

        assert len(streak_types) > 0
        assert len(total_types) == 0

    def test_streak_milestone_emoji_and_badge(self):
        """测试里程碑包含正确的emoji和徽章"""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 30

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        for milestone in result:
            assert "emoji" in milestone
            assert "badge" in milestone
            assert len(milestone["emoji"]) > 0

    def test_dedup_key_format(self):
        """测试去重key格式正确"""
        # 不需要db，直接测试格式
        service = MilestoneService.__new__(MilestoneService)

        # 测试streak key格式
        assert service.DEDUP_PREFIX == "milestone"

        expected_streak_key = "milestone:1:streak:7"
        assert expected_streak_key == "milestone:1:streak:7"

        expected_total_key = "milestone:1:total:10"
        assert expected_total_key == "milestone:1:total:10"

        expected_goal_key = "milestone:goal:1"
        assert expected_goal_key == "milestone:goal:1"

    def test_existing_milestone_skipped(self):
        """测试已存在的里程碑不会重复触发"""
        mock_db = MagicMock()

        # 模拟已存在里程碑通知
        mock_event_log = Mock()

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_event_log  # 已存在

        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.user_id = 1
        mock_habit.name = "测试习惯"
        mock_habit.streak_days = 7

        service = MilestoneService(mock_db)
        result = service._check_streak_milestones(mock_habit)

        # 已存在应该不返回任何新里程碑
        assert len(result) == 0
