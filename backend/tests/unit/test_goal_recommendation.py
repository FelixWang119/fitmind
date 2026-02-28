"""
目标推荐服务单元测试
Story 2.1: 目标数据模型设计
"""

import pytest
from datetime import datetime

from app.services.goal_recommendation import (
    GoalRecommendationService,
    ActivityLevel,
    GoalType,
    DietGoalType,
)


class TestGoalRecommendationService:
    """测试目标推荐服务"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return GoalRecommendationService()

    # ==================== 体重目标测试 ====================

    def test_calculate_weight_goal_normal_bmi(self, service):
        """测试正常 BMI 的体重目标推荐"""
        # 身高 170cm，体重 65kg (BMI = 22.5，正常范围)
        result = service.calculate_weight_goal(
            height_cm=170,
            current_weight_g=65000,  # 65kg
        )

        assert result["current_bmi"] == 22.5
        assert result["bmi_category"] == "正常"
        assert 63000 <= result["ideal_g"] <= 64000  # ~63.6kg
        assert 53 <= result["recommended_range"]["min_kg"] <= 54  # BMI 18.5
        assert 69 <= result["recommended_range"]["max_kg"] <= 70  # BMI 24

    def test_calculate_weight_goal_overweight(self, service):
        """测试超重的体重目标推荐"""
        # 身高 170cm，体重 85kg (BMI = 29.4，超重)
        result = service.calculate_weight_goal(
            height_cm=170,
            current_weight_g=85000,
        )

        assert result["current_bmi"] == 29.4
        assert result["bmi_category"] == "肥胖"  # 28+ = 肥胖
        assert 53000 <= result["recommended_target_g"] <= 54000  # 推荐到 min weight

    def test_calculate_weight_goal_underweight(self, service):
        """测试偏瘦的体重目标推荐"""
        # 身高 170cm，体重 45kg (BMI = 15.6，偏瘦)
        result = service.calculate_weight_goal(
            height_cm=170,
            current_weight_g=45000,
        )

        assert result["current_bmi"] == 15.6
        assert result["bmi_category"] == "偏瘦"

    def test_calculate_weight_goal_with_target(self, service):
        """测试带目标体重的推荐"""
        result = service.calculate_weight_goal(
            height_cm=170,
            current_weight_g=80000,
            target_weight_g=60000,
        )

        assert result["recommended_target_g"] == 60000

    # ==================== 运动目标测试 ====================

    def test_calculate_exercise_goal_sedentary(self, service):
        """测试久坐活动水平的运动目标"""
        result = service.calculate_exercise_goal(
            activity_level="sedentary",
        )

        assert result["daily_steps"] == 5000
        assert result["weekly_exercise_minutes"] == 90
        assert result["activity_level"] == "sedentary"

    def test_calculate_exercise_goal_moderate(self, service):
        """测试中度活动水平的运动目标"""
        result = service.calculate_exercise_goal(
            activity_level="moderate",
        )

        assert result["daily_steps"] == 10000
        assert result["weekly_exercise_minutes"] == 225

    def test_calculate_exercise_goal_active(self, service):
        """测试高度活动水平的运动目标"""
        result = service.calculate_exercise_goal(
            activity_level="active",
        )

        assert result["daily_steps"] == 12000
        assert result["weekly_exercise_minutes"] == 300

    def test_calculate_exercise_goal_with_current_steps(self, service):
        """测试带当前步数的推荐"""
        result = service.calculate_exercise_goal(
            activity_level="moderate",
            current_steps=5000,
        )

        assert result["current_steps"] == 5000
        assert result["progress_percentage"] == 50.0
        assert "encouragement" in result

    # ==================== 饮食目标测试 ====================

    def test_calculate_diet_goal_male_lose(self, service):
        """测试男性减重饮食目标"""
        result = service.calculate_diet_goal(
            weight_g=80000,  # 80kg
            height_cm=175,
            age=30,
            gender="male",
            activity_level="moderate",
            diet_goal_type="lose",
        )

        assert result["bmr"] > 0
        assert result["tdee"] > result["bmr"]
        assert result["target_calories"] < result["tdee"]  # 减重
        assert result["diet_goal_type"] == "lose"
        assert result["macros"]["protein_g"] > 0
        assert result["macros"]["carbs_g"] > 0
        assert result["macros"]["fat_g"] > 0

    def test_calculate_diet_goal_female_maintain(self, service):
        """测试女性维持饮食目标"""
        result = service.calculate_diet_goal(
            weight_g=60000,  # 60kg
            height_cm=165,
            age=25,
            gender="female",
            activity_level="light",
            diet_goal_type="maintain",
        )

        assert result["target_calories"] == result["tdee"]  # 维持

    def test_calculate_diet_goal_male_gain(self, service):
        """测试男性增重饮食目标"""
        result = service.calculate_diet_goal(
            weight_g=70000,
            height_cm=180,
            age=25,
            gender="male",
            activity_level="moderate",
            diet_goal_type="gain",
        )

        assert result["target_calories"] > result["tdee"]  # 增重

    def test_diet_goal_macro_calculation(self, service):
        """测试宏量营养素计算"""
        result = service.calculate_diet_goal(
            weight_g=70000,
            height_cm=175,
            age=30,
            gender="male",
            activity_level="moderate",
            diet_goal_type="lose",
        )

        # 验证宏量营养素热量占比
        protein_cal = result["macros"]["protein_g"] * 4
        carbs_cal = result["macros"]["carbs_g"] * 4
        fat_cal = result["macros"]["fat_g"] * 9
        total_macro_cal = protein_cal + carbs_cal + fat_cal

        # 允许 10% 的误差
        assert (
            abs(total_macro_cal - result["target_calories"]) / result["target_calories"]
            < 0.1
        )

    # ==================== 习惯目标测试 ====================

    def test_calculate_habit_goals(self, service):
        """测试习惯目标推荐"""
        result = service.calculate_habit_goals(
            weight_g=70000,  # 70kg
        )

        assert result["water_ml"] == 2310  # 70 * 33
        assert 9.0 <= result["water_glasses"] <= 9.5  # 2310 / 250
        assert result["sleep_hours"] == 7.5
        assert result["defecation_per_day"] == 1

    def test_calculate_habit_goals_with_current_data(self, service):
        """测试带当前数据的习惯目标"""
        result = service.calculate_habit_goals(
            weight_g=70000,
            current_water_ml=1500,
            current_sleep_hours=6.5,
        )

        assert result["water_progress_percentage"] > 0
        assert result["sleep_progress_percentage"] > 0

    # ==================== 预测日期测试 ====================

    def test_predict_completion_date_weight_goal(self, service):
        """测试体重目标完成日期预测"""
        result = service.predict_completion_date(
            current_value=80000,  # 80kg
            target_value=65000,  # 65kg
            goal_type="weight",
            daily_progress=500,  # 每天减重 500g
        )

        assert result is not None
        assert result["is_achieved"] is False
        assert result["days_remaining"] > 0
        assert "predicted_date" in result

    def test_predict_completion_date_exercise_goal(self, service):
        """测试运动目标完成日期预测"""
        result = service.predict_completion_date(
            current_value=5000,  # 当前 5000 步
            target_value=10000,  # 目标 10000 步
            goal_type="exercise",
            daily_progress=1000,  # 每天增加 1000 步
        )

        assert result is not None
        assert result["days_remaining"] == 5

    def test_predict_completion_date_already_achieved(self, service):
        """测试已达成目标"""
        result = service.predict_completion_date(
            current_value=60000,
            target_value=65000,
            goal_type="weight",
            daily_progress=500,
        )

        assert result["is_achieved"] is True
        assert result["days_remaining"] == 0

    def test_predict_completion_date_with_progress_list(self, service):
        """测试使用历史进度列表预测"""
        recent_progress = [400, 450, 500, 480, 520]  # 最近 5 天
        result = service.predict_completion_date(
            current_value=80000,
            target_value=65000,
            goal_type="weight",
            recent_progress_list=recent_progress,
        )

        assert result is not None
        # 平均每天减重约 470g
        assert result["avg_daily_progress"] == 470

    # ==================== 全部推荐测试 ====================

    def test_get_all_recommendations_complete_profile(self, service):
        """测试完整用户资料的全面推荐"""
        user_profile = {
            "height": 175,
            "current_weight": 80000,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate",
        }

        result = service.get_all_recommendations(user_profile)

        assert "weight" in result
        assert "exercise" in result
        assert "diet" in result
        assert "habit" in result

    def test_get_all_recommendations_partial_profile(self, service):
        """测试部分用户资料的推荐"""
        user_profile = {
            "height": 175,
            "current_weight": 80000,
        }

        result = service.get_all_recommendations(user_profile)

        assert "weight" in result
        assert "habit" in result
        # 注意: 当有默认 activity_level 时，仍会返回 exercise
        # 这是预期行为，用户可以在前端覆盖

    # ==================== BMI 分类测试 ====================

    def test_bmi_category_underweight(self, service):
        """测试偏瘦分类"""
        assert service._get_bmi_category(17.0) == "偏瘦"
        assert service._get_bmi_category(18.4) == "偏瘦"

    def test_bmi_category_normal(self, service):
        """测试正常分类"""
        assert service._get_bmi_category(18.5) == "正常"
        assert service._get_bmi_category(22.0) == "正常"
        assert service._get_bmi_category(23.9) == "正常"

    def test_bmi_category_overweight(self, service):
        """测试超重分类"""
        assert service._get_bmi_category(24.0) == "超重"
        assert service._get_bmi_category(27.9) == "超重"

    def test_bmi_category_obese(self, service):
        """测试肥胖分类"""
        assert service._get_bmi_category(28.0) == "肥胖"
        assert service._get_bmi_category(35.0) == "肥胖"
