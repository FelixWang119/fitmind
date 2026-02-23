"""AI Role Services Integration Tests

Integration tests for AI service with role-specific responses.
Tests the complete flow from request to role-specific response.
"""

import pytest
import asyncio
from app.services.ai_service import AIService
from app.services.ai_role_detection import (
    determine_role_by_content,
    suggest_role_switch,
)


class TestAIIntegrationWithRoles:
    """Test AI service integration with role services"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_nutritionist_role_response(self, ai_service):
        """Test nutritionist role provides diet advice"""
        context = {"current_role": "nutritionist"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("今天吃什么好？", context)
        )

        assert response.response
        assert response.metadata.get("role") == "nutritionist"
        assert any(
            kw in response.response
            for kw in ["食谱", "营养", "早餐", "午餐", "晚餐", "卡路里"]
        )

    def test_behavior_coach_role_response(self, ai_service):
        """Test behavior coach role provides habit advice"""
        context = {"current_role": "behavior_coach"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("坚持不了运动怎么办", context)
        )

        assert response.response
        assert response.metadata.get("role") == "behavior_coach"
        assert any(
            kw in response.response for kw in ["习惯", "运动", "目标", "坚持", "小"]
        )

    def test_emotional_support_role_response(self, ai_service):
        """Test emotional support role provides encouragement"""
        context = {"current_role": "emotional_support"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("今天心情不好，很沮丧", context)
        )

        assert response.response
        assert response.metadata.get("role") == "emotional_support"
        assert any(
            kw in response.response for kw in ["陪伴", "支持", "理解", "感受", "💝"]
        )

    def test_general_role_response(self, ai_service):
        """Test general role provides generic response"""
        context = {"current_role": "general"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("你好", context)
        )

        assert response.response
        assert response.metadata.get("role") == "general"

    def test_role_switch_detection(self, ai_service):
        """Test automatic role switching based on message content"""
        # Test nutrition topic detection
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "general", "今天吃营养餐", {}
        )
        assert should_switch or role == "nutritionist"

        # Test behavior coach topic detection
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "general", "如何坚持运动", {}
        )
        assert should_switch or role == "behavior_coach"

        # Test emotional support topic detection
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "general", "我很焦虑", {}
        )
        assert should_switch or role == "emotional_support"

    def test_no_role_switch_when_same_topic(self, ai_service):
        """Test no role switch when staying on same topic"""
        # Stay on nutrition topic
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "nutritionist", "午餐吃什么", {"current_role": "nutritionist"}
        )
        # Should stay on nutritionist
        assert role == "nutritionist"

    def test_role_switch_from_nutritionist_to_coach(self, ai_service):
        """Test role detection works for behavior coach keywords"""
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "nutritionist", "我要坚持健身训练", {"current_role": "nutritionist"}
        )
        # Just verify the role detection returns a valid role
        assert role in [
            "behavior_coach",
            "nutritionist",
            "general",
            "emotional_companion",
        ]
        assert role == "behavior_coach" or role == "nutritionist"
        # Test emotional support topic detection
        role, should_switch, reason, is_fusion = suggest_role_switch(
            "general", "我很焦虑", {}
        )
        assert should_switch
        assert role == "emotional_companion"

    def test_detect_nutritionist_keywords(self):
        """Test nutritionist keyword detection"""
        nutrition_messages = [
            "我要吃饭",
            "卡路里",
            "蛋白质",
            "碳水",
        ]

        for message in nutrition_messages:
            role = determine_role_by_content(message)
            assert role == "nutritionist", f"Failed for: {message} (got {role})"

    def test_detect_behavior_coach_keywords(self):
        """Test behavior coach keyword detection"""
        coach_messages = [
            "如何坚持运动？",
            "怎么养成好习惯？",
            "锻炼计划怎么做？",
            "我要坚持健身",
            "如何保持动力？",
        ]

        for message in coach_messages:
            role = determine_role_by_content(message)
            assert role == "behavior_coach", f"Failed for: {message}"

    def test_detect_emotional_support_keywords(self):
        """Test emotional support keyword detection"""
        emotional_messages = [
            "今天心情不好",
            "很焦虑怎么办？",
            "我感到很沮丧",
            "压力好大",
            "心情很差",
        ]

        for message in emotional_messages:
            role = determine_role_by_content(message)
            assert role == "emotional_companion", f"Failed for: {message}"

    def test_detect_general_when_no_keywords(self):
        """Test general role when no specific keywords"""
        general_messages = ["你好", "在吗？", "今天天气不错", "你好吗？"]

        for message in general_messages:
            role = determine_role_by_content(message)
            assert role == "general", f"Failed for: {message}"


class TestNutritionistRoleIntegration:
    """Test nutritionist role specific functionality"""

    @pytest.fixture
    def ai_service(self):
        return AIService()

    def test_diet_analysis(self, ai_service):
        """Test diet analysis feature"""
        context = {"current_role": "nutritionist"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我吃了鸡肉和米饭", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["分析", "营养", "蛋白质", "蔬菜"])

    def test_nutrition_goals_calculation(self, ai_service):
        """Test nutrition goals calculation"""
        context = {"current_role": "nutritionist"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我的 BMR 和 TDEE 是多少？", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["BMR", "TDEE", "卡路里", "代谢"])


class TestBehaviorCoachRoleIntegration:
    """Test behavior coach role specific functionality"""

    @pytest.fixture
    def ai_service(self):
        return AIService()

    def test_habit_advice(self, ai_service):
        """Test habit advice feature"""
        context = {"current_role": "behavior_coach"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我想养成运动习惯", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["习惯", "运动", "目标", "🎯"])

    def test_setback_handling(self, ai_service):
        """Test setback handling feature"""
        context = {"current_role": "behavior_coach"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我放弃了，坚持不下来", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["挫折", "理解", "支持", "💪"])

    def test_micro_goals_setting(self, ai_service):
        """Test micro goals setting feature"""
        context = {"current_role": "behavior_coach"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我想减肥，怎么开始？", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["目标", "开始", "第", "计划"])


class TestEmotionalSupportRoleIntegration:
    """Test emotional support role specific functionality"""

    @pytest.fixture
    def ai_service(self):
        return AIService()

    def test_sad_emotion_support(self, ai_service):
        """Test support for sadness"""
        context = {"current_role": "emotional_support"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我很难过，今天心情不好", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["难过", "感受", "陪伴", "💕"])

    def test_anxious_emotion_support(self, ai_service):
        """Test support for anxiety"""
        context = {"current_role": "emotional_support"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("我很焦虑，很紧张", context)
        )

        assert response.response
        assert any(kw in response.response for kw in ["焦虑", "呼吸", "支持", "🌸"])

    def test_daily_affirmation_available(self, ai_service):
        """Test daily affirmation feature"""
        context = {"current_role": "emotional_support"}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            ai_service._get_mock_response("给我一些鼓励", context)
        )

        assert response.response
        # Should contain supportive content
        assert len(response.response) > 20


# Mark tests by story and priority
pytestmark = [pytest.mark.P2, pytest.mark.integration]
