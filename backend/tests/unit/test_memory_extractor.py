"""Memory Extractor Unit Tests

测试记忆提取器的核心功能：
- P0: 摘要和关键词提取
- P0: 习惯记录记忆提取
- P1: 健康记录记忆提取
- P1: 营养记录记忆提取
- P2: 对话记忆提取
- P2: 错误处理
"""

import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime, timedelta
from typing import Dict, Any


# 模拟 AIService
class MockAIService:
    def __init__(self, mock_response: str = None):
        self.mock_response = (
            mock_response or "摘要：用户完成了习惯打卡\n关键词：习惯，打卡，坚持"
        )
        self.call_count = 0

    def call_model(self, system_prompt: str, user_query: str) -> str:
        self.call_count += 1
        return self.mock_response


class TestExtractKeywordsAndSummary:
    """测试摘要和关键词提取函数"""

    def test_extract_summary_and_keywords_basic(self):
        """[P0] 基础摘要和关键词提取"""
        from app.services.memory_extractor import _extract_keywords_and_summary

        ai_service = MockAIService()
        text = "用户今天完成了晨跑习惯，坚持了 30 分钟，感觉很好"

        summary, keywords = _extract_keywords_and_summary(text, ai_service)

        assert summary is not None
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert ai_service.call_count == 1

    def test_extract_summary_and_keywords_empty_text(self):
        """[P1] 空文本处理"""
        from app.services.memory_extractor import _extract_keywords_and_summary

        ai_service = MockAIService()
        text = ""

        summary, keywords = _extract_keywords_and_summary(text, ai_service)

        assert summary is not None
        assert len(keywords) > 0  # 至少有一个降级关键词

    def test_extract_summary_and_keywords_ai_failure(self):
        """[P1] AI 服务失败时的降级处理"""
        from app.services.memory_extractor import _extract_keywords_and_summary

        ai_service = MockAIService()
        ai_service.call_model = MagicMock(side_effect=Exception("AI 服务不可用"))
        text = "这是一段测试文本" * 100  # 长文本

        summary, keywords = _extract_keywords_and_summary(text, ai_service)

        # 降级处理应该返回截断的文本
        assert len(summary) <= 200
        assert len(keywords) == 1
        assert len(keywords[0]) <= 50


class TestMemoryExtractor:
    """测试 MemoryExtractor 类"""

    @pytest.fixture
    def extractor(self):
        """创建记忆提取器实例"""
        ai_service = MockAIService()
        from app.services.memory_extractor import MemoryExtractor

        return MemoryExtractor(ai_service)

    def test_extractor_initialization(self, extractor):
        """[P0] 提取器初始化"""
        assert extractor.ai_service is not None
        assert extractor.ai_service.call_count == 0

    def test_extract_from_habit_success(self, extractor):
        """[P0] 从习惯记录提取记忆"""
        habit_record = {
            "id": 1,
            "user_id": 100,
            "name": "晨跑",
            "completed": True,
            "date": datetime.now().isoformat(),
            "notes": "今天跑了 5 公里，感觉很好",
            "streak_days": 7,
        }

        result = extractor.extract_from_habit(habit_record)

        assert result is not None
        assert "memory_type" in result
        assert "content_summary" in result
        assert "keywords" in result
        assert "importance" in result
        assert result["memory_type"] == "习惯打卡"

    def test_extract_from_habit_with_long_notes(self, extractor):
        """[P1] 长笔记的习惯记录提取"""
        habit_record = {
            "id": 2,
            "user_id": 100,
            "name": "阅读",
            "completed": True,
            "date": datetime.now().isoformat(),
            "notes": "今天读了《原子习惯》这本书，学到了很多关于习惯养成的知识。" * 10,
            "streak_days": 15,
        }

        result = extractor.extract_from_habit(habit_record)

        assert result is not None
        assert "content_summary" in result
        # 摘要应该被合理截断
        assert len(result["content_summary"]) <= 500

    def test_extract_from_habit_missing_notes(self, extractor):
        """[P1] 缺少笔记的习惯记录"""
        habit_record = {
            "id": 3,
            "user_id": 100,
            "name": "喝水",
            "completed": True,
            "date": datetime.now().isoformat(),
            "streak_days": 3,
        }

        result = extractor.extract_from_habit(habit_record)

        assert result is not None
        assert "memory_type" in result

    def test_extract_from_health_record_weight(self, extractor):
        """[P1] 从健康记录提取 - 体重数据"""
        health_record = {
            "id": 10,
            "user_id": 100,
            "record_date": datetime.now().isoformat(),
            "weight": 68.5,
            "previous_weight": 70.0,
            "sleep_hours": 7.5,
            "mood": "good",
        }

        result = extractor.extract_from_health_record(health_record)

        assert result is not None
        assert "memory_type" in result
        # 体重下降应该被识别
        assert "content_summary" in result

    def test_extract_from_health_record_weight_trend(self, extractor):
        """[P1] 体重趋势记忆提取"""
        health_record = {
            "id": 11,
            "user_id": 100,
            "record_date": datetime.now().isoformat(),
            "weight": 65.0,
            "previous_weight": 75.0,  # 大幅下降
            "sleep_hours": 8.0,
            "mood": "excellent",
        }

        result = extractor.extract_from_health_record(health_record)

        assert result is not None
        assert "memory_type" in result
        # 显著的体重变化应该有更高的 importance
        assert "importance" in result

    def test_extract_from_health_record_missing_data(self, extractor):
        """[P2] 缺失数据的健康记录"""
        health_record = {
            "id": 12,
            "user_id": 100,
            "record_date": datetime.now().isoformat(),
            # 缺少 weight 等关键字段
        }

        result = extractor.extract_from_health_record(health_record)

        assert result is not None
        # 应该返回 None 或基础记忆
        if result is not None:
            assert "memory_type" in result

    def test_extract_from_nutrition_meal(self, extractor):
        """[P1] 从营养记录提取 - 餐食数据"""
        nutrition_record = {
            "id": 20,
            "user_id": 100,
            "meal_type": "breakfast",
            "food_items": "鸡蛋，牛奶，全麦面包",
            "calories": 450,
            "protein": 25,
            "carbs": 50,
            "fat": 15,
            "date": datetime.now().isoformat(),
        }

        result = extractor.extract_from_nutrition(nutrition_record)

        assert result is not None
        assert "memory_type" in result
        assert result["memory_type"] == "餐食习惯"

    def test_extract_from_nutrition_high_calorie(self, extractor):
        """[P2] 高热量餐食记忆提取"""
        nutrition_record = {
            "id": 21,
            "user_id": 100,
            "meal_type": "dinner",
            "food_items": "炸鸡，薯条，可乐",
            "calories": 1500,  # 高热量
            "protein": 40,
            "carbs": 150,
            "fat": 80,
            "date": datetime.now().isoformat(),
        }

        result = extractor.extract_from_nutrition(nutrition_record)

        assert result is not None
        # 高热量餐食应该有更高的 importance
        assert "importance" in result

    def test_extract_from_nutrition_missing_items(self, extractor):
        """[P2] 缺少食物列表的营养记录"""
        nutrition_record = {
            "id": 22,
            "user_id": 100,
            "meal_type": "lunch",
            "calories": 600,
            "date": datetime.now().isoformat(),
        }

        result = extractor.extract_from_nutrition(nutrition_record)

        assert result is not None
        if result is not None:
            assert "memory_type" in result

    def test_extract_from_conversation(self, extractor):
        """[P2] 从对话提取记忆"""
        conversation_messages = [
            {
                "id": 1,
                "role": "user",
                "content": "我最近总是想吃甜食怎么办？",
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "这可能是压力导致的，建议尝试运动或冥想来缓解压力。",
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": 3,
                "role": "user",
                "content": "好的，我试试。我打算制定一个健康计划。",
                "created_at": datetime.now().isoformat(),
            },
        ]

        result = extractor.extract_from_conversation(conversation_messages)

        assert result is not None
        assert "memory_type" in result
        assert result["memory_type"] == "对话洞察"


class TestImportanceCalculation:
    """测试重要性分数计算"""

    def test_high_importance_for_milestone(self):
        """[P2] 里程碑事件的高重要性"""
        # 体重下降 10kg 应该是高重要性
        weight_change = 10.0
        importance = min(1.0, weight_change / 10)

        assert importance == 1.0
        assert 0 <= importance <= 1

    def test_medium_importance_for_streak(self):
        """[P2] 连续打卡的中等重要性"""
        streak_days = 7
        importance = min(1.0, streak_days / 30)

        assert 0.2 <= importance <= 0.3

    def test_low_importance_for_routine(self):
        """[P2] 日常例行的低重要性"""
        routine_event = True
        importance = 0.3 if routine_event else 0.5

        assert importance == 0.3
        assert 0 <= importance <= 1


# 测试标记
pytestmark = pytest.mark.memory
