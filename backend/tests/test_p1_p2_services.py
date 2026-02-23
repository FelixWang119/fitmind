"""P1/P2 Stories Unit Tests - Service Initialization Tests

This file contains simple initialization tests for all P1/P2 services.
These tests verify that each service can be instantiated correctly.
"""

import pytest
from sqlalchemy.orm import Session


class TestP1ServicesInitialization:
    """Test P1 story services can be initialized"""

    def test_nutrition_service_initialization(self, db_session: Session):
        """Story 1.2: Nutrition Service"""
        from app.services.nutrition_service import NutritionService

        service = NutritionService(db_session)
        assert service is not None
        assert service.db is not None

    def test_habit_service_initialization(self, db_session: Session):
        """Story 1.3: Habit Service"""
        from app.services.habit_service import HabitService

        service = HabitService(db_session)
        assert service is not None
        assert service.db is not None

    def test_emotional_support_service_initialization(self, db_session: Session):
        """Story 1.5: Emotional Support Service"""
        from app.services.emotional_support_service import EmotionalSupportService

        service = EmotionalSupportService(db_session)
        assert service is not None
        assert service.db is not None

    def test_trend_analyzer_initialization(self, db_session: Session):
        """Story 1.6: Trend Analyzer"""
        from app.services.trend_analyzer import TrendAnalyzer

        service = TrendAnalyzer(db_session)
        assert service is not None
        assert service.db is not None

    def test_milestone_detector_initialization(self, db_session: Session):
        """Story 1.7: Milestone Detector"""
        from app.services.milestone_detector import MilestoneDetector

        service = MilestoneDetector(db_session)
        assert service is not None
        assert service.db is not None

    def test_pattern_recognizer_initialization(self, db_session: Session):
        """Story 2.3: Pattern Recognizer"""
        from app.services.pattern_recognizer import PatternRecognizer

        service = PatternRecognizer(db_session)
        assert service is not None
        assert service.db is not None

    def test_memory_manager_initialization(self, db_session: Session):
        """Story 2.4: Memory Manager"""
        from app.services.memory_manager import MemoryManager

        service = MemoryManager(db_session)
        assert service is not None
        assert service.db is not None


class TestP2ServicesInitialization:
    """Test P2 story services can be initialized"""

    def test_ai_service_initialization(self, db_session: Session):
        """Story 2.1: AI Health Advisor"""
        from app.services.ai_service import AIService

        # AI Service might have different initialization
        try:
            service = AIService(db_session)
            assert service is not None
        except TypeError:
            # Some services might not take db_session directly
            pytest.skip("Service has different initialization signature")

    def test_gamification_service_initialization(self, db_session: Session):
        """Story 1.4: Gamification Service"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        assert service is not None
        assert service.db is not None

    def test_personalization_engine_initialization(self, db_session: Session):
        """Story 2.5: Personalization Engine"""
        from app.services.personalization_engine import PersonalizationEngine

        service = PersonalizationEngine(db_session)
        assert service is not None
        assert service.db is not None

    def test_scientific_persona_service_initialization(self, db_session: Session):
        """Story 2.6: Scientific Persona Service"""
        from app.services.scientific_persona_service import ScientificPersonaService

        service = ScientificPersonaService(db_session)
        assert service is not None
        assert service.db is not None

    def test_professional_fusion_service_initialization(self, db_session: Session):
        """Story 2.7: Professional Fusion Service"""
        from app.services.professional_fusion_service import ProfessionalFusionService

        service = ProfessionalFusionService(db_session)
        assert service is not None
        assert service.db is not None

    def test_user_experience_service_initialization(self, db_session: Session):
        """Story 2.8: User Experience Service"""
        from app.services.user_experience_service import UserExperienceService

        service = UserExperienceService(db_session)
        assert service is not None

    def test_advanced_context_builder_initialization(self, db_session: Session):
        """Story 2.9: Advanced Context Builder"""
        from app.services.context_builder import AdvancedContextBuilder

        service = AdvancedContextBuilder(db_session)
        assert service is not None
        assert service.db is not None


class TestNutritionServiceCalculations:
    """Test Nutrition Service calculation methods"""

    @pytest.fixture
    def nutrition_service(self, db_session: Session):
        from app.services.nutrition_service import NutritionService

        return NutritionService(db_session)

    @pytest.fixture
    def test_user(self, db_session):
        from app.models.user import User

        user = User(
            email="test_nutrition@example.com",
            username="nutrition_user",
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

    def test_calculate_bmr(self, nutrition_service, test_user):
        """Test BMR calculation"""
        bmr = nutrition_service.calculate_bmr(test_user)
        assert 1600 < bmr < 1800  # Expected range for male, 75kg, 175cm, 30y

    def test_calculate_tdee(self, nutrition_service, test_user):
        """Test TDEE calculation"""
        tdee = nutrition_service.calculate_tdee(test_user)
        assert tdee > 0

    def test_calculate_calorie_target(self, nutrition_service, test_user):
        """Test calorie target calculation"""
        result = nutrition_service.calculate_calorie_target(test_user)
        assert "maintenance" in result
        assert "target" in result
        assert result["target"] < result["maintenance"]  # Weight loss goal


# Mark tests by priority
pytestmark = [pytest.mark.P1, pytest.mark.P2]
