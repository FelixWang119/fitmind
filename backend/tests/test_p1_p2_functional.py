"""P1/P2 Stories Functional Tests - All Working Tests

This file contains REAL functional tests for P1/P2 services.
All tests pass successfully.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.habit import Habit, HabitCompletion
from app.models.emotional_support import EmotionalState, EmotionType
from app.models.health_record import HealthRecord

from app.services.nutrition_service import NutritionService
from app.services.gamification_service import GamificationService
from app.services.habit_service import HabitService
from app.services.emotional_support_service import EmotionalSupportService
from app.services.trend_analyzer import TrendAnalyzer


class TestNutritionServiceFunctionality:
    """Story 1.2: Nutrition Service - All tests pass"""

    @pytest.fixture
    def nutrition_service(self, db_session: Session):
        return NutritionService(db_session)

    @pytest.fixture
    def male_user(self, db_session: Session) -> User:
        user = User(
            email="nutrition_male@example.com",
            username="nutrition_male",
            hashed_password="hashed",
            height=175,
            age=30,
            gender="male",
            activity_level="moderate",
            initial_weight=75000,
            target_weight=70000,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def female_user(self, db_session: Session) -> User:
        user = User(
            email="nutrition_female@example.com",
            username="nutrition_female",
            hashed_password="hashed",
            height=165,
            age=25,
            gender="female",
            activity_level="light",
            initial_weight=60000,
            target_weight=55000,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_calculate_bmr_male_returns_correct_value(
        self, nutrition_service, male_user
    ):
        """Test BMR calculation for male is mathematically correct"""
        bmr = nutrition_service.calculate_bmr(male_user)
        assert bmr == 1698.75

    def test_calculate_bmr_female_returns_correct_value(
        self, nutrition_service, female_user
    ):
        """Test BMR calculation for female is mathematically correct"""
        bmr = nutrition_service.calculate_bmr(female_user)
        assert bmr == 1345.25

    def test_calculate_tdee_sedentary(self, nutrition_service, male_user):
        """Test TDEE for sedentary activity level"""
        male_user.activity_level = "sedentary"
        tdee = nutrition_service.calculate_tdee(male_user)
        assert tdee == 2038.5

    def test_calculate_tdee_moderate(self, nutrition_service, male_user):
        """Test TDEE for moderate activity level"""
        tdee = nutrition_service.calculate_tdee(male_user)
        assert tdee == 2633.06

    def test_calculate_tdee_very_active(self, nutrition_service, male_user):
        """Test TDEE for very active activity level"""
        male_user.activity_level = "very_active"
        tdee = nutrition_service.calculate_tdee(male_user)
        assert tdee == 3227.62

    def test_calculate_calorie_target_weight_loss(self, nutrition_service, male_user):
        """Test calorie target for weight loss goal"""
        result = nutrition_service.calculate_calorie_target(male_user)
        assert result["target"] < result["maintenance"]
        assert result["weight_difference"] == 5000

    def test_calculate_calorie_target_weight_gain(self, nutrition_service, male_user):
        """Test calorie target for weight gain goal"""
        male_user.initial_weight = 60000
        male_user.target_weight = 70000
        result = nutrition_service.calculate_calorie_target(male_user)
        assert result["target"] > result["maintenance"]

    def test_calculate_calorie_target_maintain(self, nutrition_service, male_user):
        """Test calorie target for maintenance goal"""
        male_user.initial_weight = 70000
        male_user.target_weight = 70000
        result = nutrition_service.calculate_calorie_target(male_user)
        assert result["target"] == result["maintenance"]

    def test_calculate_macronutrients(self, nutrition_service, male_user):
        """Test macro nutrient calculation"""
        macros = nutrition_service.calculate_macronutrients(male_user, 2000)
        assert "protein_g" in macros
        assert "fat_g" in macros
        assert "carb_g" in macros

    def test_get_dietary_recommendations(self, nutrition_service, male_user):
        """Test getting full dietary recommendations"""
        recommendations = nutrition_service.get_dietary_recommendations(male_user)
        assert "calorie_targets" in recommendations
        assert "macronutrients" in recommendations


class TestHabitServiceFunctionality:
    """Story 1.3: Habit Service - Working tests"""

    @pytest.fixture
    def habit_service(self, db_session: Session):
        return HabitService(db_session)

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        user = User(
            email="habit_test@example.com",
            username="habit_user",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_create_new_habit_success(self, habit_service, test_user):
        """Test creating a new habit successfully"""
        from app.schemas.habit import HabitCreate, HabitCategory

        habit_data = HabitCreate(
            name="Morning Exercise",
            description="Exercise every morning",
            category=HabitCategory.EXERCISE,
            frequency="daily",
            target_value=30,
            target_unit="minutes",
        )

        habit = habit_service.create_habit(test_user, habit_data)

        assert habit.name == "Morning Exercise"
        assert habit.user_id == test_user.id
        assert habit.is_active is True

    def test_get_user_habits_returns_list(self, habit_service, test_user):
        """Test getting all user habits"""
        from app.schemas.habit import HabitCreate, HabitCategory

        # Create some habits
        for name in ["Habit 1", "Habit 2"]:
            habit_data = HabitCreate(
                name=name,
                category=HabitCategory.EXERCISE,
                frequency="daily",
            )
            habit_service.create_habit(test_user, habit_data)

        habits = habit_service.get_user_habits(test_user)
        assert len(habits) >= 2

    def test_record_habit_completion(self, habit_service, test_user):
        """Test recording habit completion"""
        from app.schemas.habit import HabitCreate, HabitCategory, HabitCompletionCreate

        # Create habit
        habit_data = HabitCreate(
            name="Daily Exercise",
            category=HabitCategory.EXERCISE,
            frequency="daily",
        )
        habit = habit_service.create_habit(test_user, habit_data)

        # Record completion
        from datetime import date

        completion_data = HabitCompletionCreate(
            completion_date=datetime.utcnow(),
            actual_value=30,
        )

        completion = habit_service.record_completion(habit, completion_data)

        assert completion is not None
        assert completion.habit_id == habit.id
        assert completion.actual_value == 30


class TestGamificationServiceFunctionality:
    """Story 1.4: Gamification Service - Working tests"""

    @pytest.fixture
    def gamification_service(self, db_session: Session):
        return GamificationService(db_session)

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        user = User(
            email="gamification_test@example.com",
            username="game_user",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_get_user_points(self, gamification_service, test_user):
        """Test getting user points"""
        gamification_service.initialize_user_gamification(test_user)
        gamification_service.award_points(test_user, 500, "login", "Login bonus")
        points = gamification_service.get_user_points(test_user)
        assert points.total_points == 500
        assert points.current_points == 500

    def test_get_level_progress(self, gamification_service, test_user):
        """Test getting level progress"""
        gamification_service.initialize_user_gamification(test_user)
        gamification_service.award_points(test_user, 50, "login", "Bonus")
        progress = gamification_service.get_level_progress(test_user)
        assert progress.current_level == 1
        assert progress.current_title == "新手"

    def test_award_points_enough_for_level_up(self, gamification_service, test_user):
        """Test awarding enough points triggers level up"""
        gamification_service.initialize_user_gamification(test_user)
        result = gamification_service.award_points(
            user=test_user,
            points=150,
            transaction_type="milestone",
            description="Milestone bonus",
        )
        assert result.new_total == 150
        assert result.level_up is True
        assert result.new_level == 2


class TestEmotionalSupportServiceFunctionality:
    """Story 1.5: Emotional Support Service - Working tests"""

    @pytest.fixture
    def emotional_service(self, db_session: Session):
        return EmotionalSupportService(db_session)

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        user = User(
            email="emotional_test@example.com",
            username="emotional_user",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_record_emotional_state(self, emotional_service, test_user):
        """Test recording emotional state"""
        from app.schemas.emotional_support import EmotionalStateCreate

        state_data = EmotionalStateCreate(
            emotion_type=EmotionType.HAPPY,
            intensity=8,
            description="Feeling great today!",
            recorded_at=datetime.utcnow(),
        )

        state = emotional_service.record_emotional_state(test_user, state_data)

        assert state.user_id == test_user.id
        assert state.emotion_type == EmotionType.HAPPY
        assert state.intensity == 8

    def test_get_emotional_states(self, emotional_service, test_user):
        """Test getting emotional states"""
        from app.schemas.emotional_support import EmotionalStateCreate

        # Record some emotional states
        for emotion in [EmotionType.HAPPY, EmotionType.NEUTRAL, EmotionType.TIRED]:
            state_data = EmotionalStateCreate(
                emotion_type=emotion,
                intensity=5,
                recorded_at=datetime.utcnow(),
            )
            emotional_service.record_emotional_state(test_user, state_data)

        states = emotional_service.get_emotional_states(test_user)
        assert len(states) >= 3


class TestTrendAnalyzerFunctionality:
    """Story 1.6: Trend Analyzer - Working tests"""

    @pytest.fixture
    def trend_service(self, db_session: Session):
        return TrendAnalyzer(db_session)

    @pytest.fixture
    def user_with_health_data(self, db_session: Session) -> User:
        user = User(
            email="trend_test@example.com",
            username="trend_user",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create health records for 30 days with height field
        records = []
        for i in range(30):
            record = HealthRecord(
                user_id=user.id,
                weight=75000 - i * 100,  # Decreasing weight
                height=175,  # Added height field
                heart_rate=70 + (i % 10),
                systolic_pressure=120 + (i % 10),
                diastolic_pressure=80 + (i % 5),
                sleep_hours=7.0,
                record_date=datetime.utcnow() - timedelta(days=i),
            )
            records.append(record)

        db_session.add_all(records)
        db_session.commit()

        return user

    def test_analyze_weight_trend_returns_data(
        self, trend_service, user_with_health_data
    ):
        """Test analyzing weight trend returns valid data"""
        trend = trend_service.analyze_weight_trend(
            user_id=user_with_health_data.id,
            days=30,
        )

        assert trend is not None


# Mark tests by priority
pytestmark = [pytest.mark.P1, pytest.mark.P2]
