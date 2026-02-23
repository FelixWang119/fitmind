"""AI Role Services Tests - Story 2.2, 2.3, 2.4"""

import pytest
from app.services.ai_role_services import (
    NutritionistRole,
    BehaviorCoachRole,
    EmotionalSupportRole,
    get_role_service,
)


class TestNutritionistRole:
    """Story 2.2: Nutritionist Role Tests"""

    def test_analyze_diet_balanced(self):
        """Test analyzing a balanced diet"""
        food_items = ["鸡肉", "蔬菜", "米饭", "水果"]
        result = NutritionistRole.analyze_diet(food_items, {})
        assert "✅" in result or "均衡" in result

    def test_analyze_diet_missing_protein(self):
        """Test analyzing diet missing protein"""
        food_items = ["米饭", "青菜", "苹果"]
        result = NutritionistRole.analyze_diet(food_items, {})
        assert "蛋白质" in result

    def test_analyze_diet_missing_vegetable(self):
        """Test analyzing diet missing vegetables"""
        food_items = ["鸡肉", "米饭", "鸡蛋"]
        result = NutritionistRole.analyze_diet(food_items, {})
        assert "蔬菜" in result

    def test_get_recipe_recommendation(self):
        """Test getting recipe recommendations"""
        result = NutritionistRole.get_recipe_recommendation({})
        assert "早餐" in result
        assert "午餐" in result
        assert "晚餐" in result

    def test_calculate_nutrition_goals(self):
        """Test calculating nutrition goals"""
        user_profile = {
            "weight": 70,
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate",
        }
        result = NutritionistRole.calculate_nutrition_goals(user_profile)

        assert "bmr" in result
        assert "tdee" in result
        assert "protein_g" in result
        assert result["bmr"] > 0
        assert result["tdee"] > result["bmr"]


class TestBehaviorCoachRole:
    """Story 2.3: Behavior Coach Role Tests"""

    def test_get_habit_advice_exercise(self):
        """Test getting exercise habit advice"""
        result = BehaviorCoachRole.get_habit_advice("exercise", "想运动但坚持不了")
        assert "运动" in result or "🎯" in result

    def test_get_habit_advice_diet(self):
        """Test getting diet habit advice"""
        result = BehaviorCoachRole.get_habit_advice("diet", "控制不住饮食")
        assert "饮食" in result or "🍽️" in result

    def test_get_habit_advice_general(self):
        """Test getting general habit advice"""
        result = BehaviorCoachRole.get_habit_advice("unknown", "想养成好习惯")
        assert "习惯" in result or "🎯" in result

    def test_provide_encouragement_long_streak(self):
        """Test providing encouragement for long streak"""
        result = BehaviorCoachRole.provide_encouragement("坚持运动", 30)
        assert "30" in result
        assert "🎉" in result or "棒" in result

    def test_provide_encouragement_short_streak(self):
        """Test providing encouragement for short streak"""
        result = BehaviorCoachRole.provide_encouragement("开始运动", 3)
        assert "3" in result or "开始" in result

    def test_handle_setback(self):
        """Test handling user setbacks"""
        result = BehaviorCoachRole.handle_setback("我中断了运动计划，很沮丧")
        assert "挫折" in result or "理解" in result
        assert "💪" in result or "支持" in result

    def test_set_micro_goals_weight_loss(self):
        """Test setting micro goals for weight loss"""
        result = BehaviorCoachRole.set_micro_goals("减肥")
        assert isinstance(result, list)
        assert len(result) > 0
        assert any("周" in step for step in result)


class TestEmotionalSupportRole:
    """Story 2.4: Emotional Support Role Tests"""

    def test_provide_support_sad(self):
        """Test providing support for sadness"""
        result = EmotionalSupportRole.provide_support("sad", "今天心情不好")
        assert "难过" in result or "感受" in result
        assert "💕" in result or "支持" in result

    def test_provide_support_anxious(self):
        """Test providing support for anxiety"""
        result = EmotionalSupportRole.provide_support("anxious", "感觉很焦虑")
        assert "焦虑" in result
        assert "呼吸" in result or "🌸" in result

    def test_provide_support_frustrated(self):
        """Test providing support for frustration"""
        result = EmotionalSupportRole.provide_support("frustrated", "努力没效果")
        assert "挫败" in result or "沮丧" in result
        assert "💪" in result

    def test_provide_support_default(self):
        """Test providing default support"""
        result = EmotionalSupportRole.provide_support("unknown", "想聊聊")
        assert "感谢" in result or "支持" in result

    def test_daily_affirmation(self):
        """Test getting daily affirmation"""
        result = EmotionalSupportRole.daily_affirmation()
        assert "肯定" in result
        assert any(e in result for e in ["✨", "🌟", "💪", "🎯", "💖", "🌈", "🌱"])


class TestRoleServiceFactory:
    """Test role service factory"""

    def test_get_nutritionist_service(self):
        """Test getting nutritionist service"""
        service = get_role_service("nutritionist")
        assert service == NutritionistRole

    def test_get_behavior_coach_service(self):
        """Test getting behavior coach service"""
        service = get_role_service("behavior_coach")
        assert service == BehaviorCoachRole

    def test_get_emotional_support_service(self):
        """Test getting emotional support service"""
        service = get_role_service("emotional_support")
        assert service == EmotionalSupportRole

    def test_get_unknown_service(self):
        """Test getting unknown service returns None"""
        service = get_role_service("unknown")
        assert service is None

    def test_get_general_service(self):
        """Test getting general service returns None"""
        service = get_role_service("general")
        assert service is None


# Mark tests by story

# Mark tests by story
pytestmark = [pytest.mark.P2]
