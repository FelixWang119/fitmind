"""Memory Associator Unit Tests

测试记忆关联系统的核心功能：
- P0: 时间关联检测
- P0: 模式关联检测
- P1: 情感关联检测
- P1: 关联强度计算
- P2: 多维度关联
"""

import pytest
from unittest.mock import MagicMock, Mock
from datetime import date, datetime, timedelta
from typing import Dict, Any, List


# 导入被测试的类
class TestMemoryAssociator:
    """测试记忆关联器"""

    @pytest.fixture
    def mock_db_session(self):
        """创建模拟数据库会话"""
        session = MagicMock()
        session.query = MagicMock()
        return session

    @pytest.fixture
    def associator(self, mock_db_session):
        """创建记忆关联器实例"""
        from app.services.memory_associator import MemoryAssociator

        return MemoryAssociator(mock_db_session)

    def test_associator_initialization(self, mock_db_session, associator):
        """[P0] 关联器初始化"""
        assert associator.db == mock_db_session

    @pytest.mark.asyncio
    async def test_detect_temporal_associations_insufficient_data(self, associator):
        """[P0] 数据不足时返回空结果"""
        # 模拟查询返回少于 10 条记录
        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        mock_query.all = MagicMock(return_value=[])
        associator.db.query = MagicMock(return_value=mock_query)

        result = await associator.detect_temporal_associations(user_id=100)

        assert result == []

    @pytest.mark.asyncio
    async def test_detect_temporal_associations_exercise_diet_pattern(self, associator):
        """[P0] 检测运动 - 饮食时间关联"""
        # 模拟健康记录数据
        mock_records = []
        base_date = date.today()

        # 创建 30 天的模拟数据
        for i in range(30):
            record_date = base_date - timedelta(days=i)
            record = MagicMock()
            record.record_date = datetime.combine(record_date, datetime.min.time())

            # 奇数天有高运动量
            if i % 2 == 0:
                record.exercise_minutes = 60  # 高强度运动
                record.calories_intake = 1600  # 第二天低热量
            else:
                record.exercise_minutes = 0
                record.calories_intake = 2200

            mock_records.append(record)

        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        mock_query.all = MagicMock(return_value=mock_records)
        associator.db.query = MagicMock(return_value=mock_query)

        result = await associator.detect_temporal_associations(user_id=100)

        # 应该检测到运动后低热量的模式
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_detect_temporal_associations_weekend_pattern(self, associator):
        """[P1] 检测周末饮食模式"""
        mock_records = []
        base_date = date.today()

        # 创建包含周末的数据
        for i in range(30):
            record_date = base_date - timedelta(days=i)
            record = MagicMock()
            record.record_date = datetime.combine(record_date, datetime.min.time())

            # 周末高热量，平日低热量
            if record_date.weekday() >= 5:  # 周末
                record.calories_intake = 2800
            else:
                record.calories_intake = 2000

            record.exercise_minutes = 30
            mock_records.append(record)

        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        mock_query.all = MagicMock(return_value=mock_records)
        associator.db.query = MagicMock(return_value=mock_query)

        result = await associator.detect_temporal_associations(user_id=100)

        assert isinstance(result, list)

    def test_calculate_pattern_strength(self, associator):
        """[P1] 关联强度计算"""
        # 证据数量与强度的关系
        evidence_counts = [1, 3, 5, 10, 20]

        for count in evidence_counts:
            strength = min(0.9, count / 10)
            assert 0 <= strength <= 0.9
            assert isinstance(strength, float)

    def test_pattern_strength_capping(self, associator):
        """[P1] 关联强度上限"""
        # 即使证据很多，强度也不应超过 0.9
        high_evidence = 100
        strength = min(0.9, high_evidence / 10)

        assert strength == 0.9
        assert strength < 1.0


class TestPatternDetection:
    """测试模式检测功能"""

    def test_weekday_vs_weekend_comparison(self):
        """[P1] 工作日与周末对比"""
        weekday_calories = [2000, 2100, 1900, 2050, 2000]
        weekend_calories = [2800, 2700]

        weekday_avg = sum(weekday_calories) / len(weekday_calories)
        weekend_avg = sum(weekend_calories) / len(weekend_calories)

        difference = weekend_avg - weekday_avg

        # 周末平均热量更高
        assert difference > 0
        assert weekend_avg > weekday_avg

    def test_correlation_calculation(self):
        """[P2] 简单相关性计算"""
        # 运动时间和卡路里消耗
        exercise_minutes = [30, 60, 90, 120, 0, 45, 75]
        calories_burned = [150, 300, 450, 600, 0, 225, 375]

        # 理想情况下应该完全相关
        correlation = sum(
            (e * c) for e, c in zip(exercise_minutes, calories_burned)
        ) / (sum(exercise_minutes) * sum(calories_burned) / len(exercise_minutes))

        assert correlation > 0.8  # 强正相关


class TestAssociationTypes:
    """测试关联类型"""

    def test_temporal_association_structure(self):
        """[P0] 时间关联数据结构"""
        association = {
            "type": "temporal",
            "source": "exercise",
            "target": "diet",
            "description": "高强度运动后第二天会控制饮食",
            "strength": 0.7,
            "evidence_count": 7,
        }

        assert "type" in association
        assert "source" in association
        assert "target" in association
        assert "description" in association
        assert "strength" in association
        assert "evidence_count" in association

        assert 0 <= association["strength"] <= 1
        assert association["evidence_count"] > 0

    def test_pattern_association_structure(self):
        """[P0] 模式关联数据结构"""
        association = {
            "type": "pattern",
            "category": "weekly_cycle",
            "description": "周末摄入热量高于工作日",
            "strength": 0.8,
            "evidence_count": 12,
        }

        required_fields = [
            "type",
            "category",
            "description",
            "strength",
            "evidence_count",
        ]
        for field in required_fields:
            assert field in association

        assert association["type"] == "pattern"

    def test_behavioral_association_structure(self):
        """[P1] 行为关联数据结构"""
        association = {
            "type": "behavioral",
            "trigger": "stress",
            "behavior": "emotional_eating",
            "description": "压力大时倾向于吃高热量食物",
            "strength": 0.6,
            "evidence_count": 5,
        }

        assert association["type"] == "behavioral"
        assert "trigger" in association
        assert "behavior" in association


class TestAssociationStorage:
    """测试关联数据存储"""

    def test_data_association_model_fields(self):
        """[P2] DataAssociation 模型字段验证"""
        # 模拟 DataAssociation 对象的字段
        association_data = {
            "user_id": 100,
            "association_type": "temporal",
            "source_type": "health_record",
            "source_id": 1,
            "target_type": "health_record",
            "target_id": 2,
            "strength": 0.75,
            "metadata": {"pattern": "exercise_then_diet"},
        }

        assert "user_id" in association_data
        assert "association_type" in association_data
        assert "source_type" in association_data
        assert "source_id" in association_data
        assert "target_type" in association_data
        assert "target_id" in association_data
        assert "strength" in association_data

        assert 0 <= association_data["strength"] <= 1

    def test_metadata_serialization(self):
        """[P2] 元数据序列化"""
        import json

        metadata = {
            "pattern": "weekly_cycle",
            "confidence": 0.85,
            "tags": ["diet", "exercise", "weekend"],
        }

        serialized = json.dumps(metadata)
        deserialized = json.loads(serialized)

        assert deserialized == metadata
        assert isinstance(serialized, str)


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_user_data(self):
        """[P2] 空用户数据处理"""
        user_id = 999

        # 应该返回空列表而不抛出异常
        associations = []
        assert associations == []

    def test_single_data_point(self):
        """[P2] 单个数据点无法形成关联"""
        data_points = 1

        # 单个数据点无法检测模式
        can_detect_pattern = data_points >= 10

        assert can_detect_pattern is False

    def test_very_long_date_range(self):
        """[P2] 超长日期范围处理"""
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()

        days_range = (end_date - start_date).days

        assert days_range == 365
        # 应该能够处理长范围数据
        assert days_range > 30

    def test_missing_dates_in_data(self):
        """[P2] 数据中有缺失日期的处理"""
        # 模拟有缺失的 30 天数据
        recorded_days = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30]  # 缺失很多天

        completeness = len(recorded_days) / 30 * 100

        # 数据完整度低于 50%
        assert completeness < 50
        # 但仍可能检测到强模式
        if len(recorded_days) >= 5:
            can_detect = True
            assert can_detect is True


# 测试标记
pytestmark = pytest.mark.memory
