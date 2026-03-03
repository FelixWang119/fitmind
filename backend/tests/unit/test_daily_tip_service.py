"""
DailyTip Service 单元测试
Story 9.1: 科普内容生成服务
"""

import pytest
from datetime import date
from app.services.daily_tip_service import (
    DailyTipService,
    get_daily_tip_service,
    TOPICS,
    TOPIC_NAMES,
    DEFAULT_DISCLAIMER,
)
from app.models.daily_tip import TipTopic


class TestDailyTipService:
    """测试科普内容生成服务"""

    def test_get_current_topic(self):
        """
        测试获取当前主题
        AC #2: 每周一个主题（营养/运动/睡眠/心理）
        """
        service = DailyTipService()

        # 测试不同日期的主题轮换
        # 使用特定日期确保测试可重复
        test_date = date(2026, 3, 2)  # 周一
        topic = service.get_current_topic(test_date)

        assert topic in TOPICS
        assert isinstance(topic, str)

    def test_get_current_topic_default(self):
        """测试默认使用今天"""
        service = DailyTipService()
        topic = service.get_current_topic()

        assert topic in TOPICS

    def test_topic_cycles_weekly(self):
        """
        测试主题按周轮换
        同一周内主题相同，不同周主题切换
        """
        service = DailyTipService()

        # 同一周的不同日期应该返回相同主题
        monday = date(2026, 3, 2)
        tuesday = date(2026, 3, 3)
        wednesday = date(2026, 3, 4)

        assert service.get_current_topic(monday) == service.get_current_topic(tuesday)
        assert service.get_current_topic(tuesday) == service.get_current_topic(
            wednesday
        )

    def test_topic_changes_next_week(self):
        """测试下周主题会变化"""
        service = DailyTipService()

        # 不同周的主题可能不同
        week1_monday = date(2026, 3, 2)
        week2_monday = date(2026, 3, 9)

        # 主题应该轮换
        topic1 = service.get_current_topic(week1_monday)
        topic2 = service.get_current_topic(week2_monday)

        assert topic1 in TOPICS
        assert topic2 in TOPICS

    def test_get_topic_name(self):
        """测试获取主题中文名称"""
        service = DailyTipService()

        assert service.get_topic_name(TipTopic.NUTRITION.value) == "营养健康"
        assert service.get_topic_name(TipTopic.EXERCISE.value) == "科学运动"
        assert service.get_topic_name(TipTopic.SLEEP.value) == "优质睡眠"
        assert service.get_topic_name(TipTopic.PSYCHOLOGY.value) == "心理健康"

    def test_build_prompt(self):
        """测试构建 Prompt"""
        service = DailyTipService()

        prompt = service.build_prompt(TipTopic.NUTRITION.value)

        assert "营养健康" in prompt
        assert "JSON" in prompt
        assert "title" in prompt
        assert "summary" in prompt
        assert "content" in prompt
        assert "disclaimer" in prompt

    def test_generate_tip_content_mock(self):
        """测试生成科普内容（模拟模式）"""
        service = DailyTipService()

        # 在 mock 模式下生成内容
        content = service._get_mock_content(TipTopic.NUTRITION.value)

        assert "title" in content
        assert "summary" in content
        assert "content" in content
        assert "disclaimer" in content
        assert len(content["summary"]) <= 50
        assert 300 <= len(content["content"]) <= 500

    def test_generate_tip_content_all_topics(self):
        """测试所有主题的生成"""
        service = DailyTipService()

        for topic in TOPICS:
            content = service._get_mock_content(topic)

            assert "title" in content
            assert "summary" in content
            assert "content" in content
            assert "disclaimer" in content
            assert len(content["summary"]) <= 50

    def test_default_disclaimer(self):
        """测试默认免责声明"""
        assert "医疗" in DEFAULT_DISCLAIMER or "专业" in DEFAULT_DISCLAIMER

    def test_mock_content_contains_disclaimer(self):
        """测试模拟内容包含免责声明"""
        service = DailyTipService()

        content = service._get_mock_content(TipTopic.NUTRITION.value)

        assert content["disclaimer"] == DEFAULT_DISCLAIMER

    def test_get_daily_tip_service_singleton(self):
        """测试服务单例"""
        service1 = get_daily_tip_service()
        service2 = get_daily_tip_service()

        assert service1 is service2


class TestTopicConfiguration:
    """测试主题配置"""

    def test_topics_list(self):
        """测试主题列表包含所有预期主题"""
        assert TipTopic.NUTRITION.value in TOPICS
        assert TipTopic.EXERCISE.value in TOPICS
        assert TipTopic.SLEEP.value in TOPICS
        assert TipTopic.PSYCHOLOGY.value in TOPICS

    def test_topic_names_mapping(self):
        """测试主题名称映射"""
        assert len(TOPIC_NAMES) == len(TOPICS)

        for topic in TOPICS:
            assert topic in TOPIC_NAMES
            assert isinstance(TOPIC_NAMES[topic], str)
            assert len(TOPIC_NAMES[topic]) > 0


class TestContentStructure:
    """测试内容结构"""

    def test_nutrition_content_structure(self):
        """测试营养内容结构"""
        service = DailyTipService()
        content = service._get_mock_content(TipTopic.NUTRITION.value)

        # 验证字段存在
        assert "title" in content
        assert "summary" in content
        assert "content" in content
        assert "disclaimer" in content

        # 验证标题长度
        assert len(content["title"]) <= 20

        # 验证摘要长度
        assert len(content["summary"]) <= 50

        # 验证正文长度
        assert 300 <= len(content["content"]) <= 500

    def test_exercise_content_structure(self):
        """测试运动内容结构"""
        service = DailyTipService()
        content = service._get_mock_content(TipTopic.EXERCISE.value)

        assert "title" in content
        assert len(content["summary"]) <= 50
        assert 300 <= len(content["content"]) <= 500

    def test_sleep_content_structure(self):
        """测试睡眠内容结构"""
        service = DailyTipService()
        content = service._get_mock_content(TipTopic.SLEEP.value)

        assert "title" in content
        assert len(content["summary"]) <= 50
        assert 300 <= len(content["content"]) <= 500

    def test_psychology_content_structure(self):
        """测试心理内容结构"""
        service = DailyTipService()
        content = service._get_mock_content(TipTopic.PSYCHOLOGY.value)

        assert "title" in content
        assert len(content["summary"]) <= 50
        assert 300 <= len(content["content"]) <= 500
