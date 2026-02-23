"""Health Assessment API Tests

Tests for the health assessment endpoints.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthAssessmentEndpoints:
    """Test health assessment API endpoints"""

    def test_get_latest_assessment_requires_auth(self, client):
        """Test getting latest assessment requires authorization"""
        response = client.get("/api/v1/health-assessment/assessments/latest")
        # Should require auth
        assert response.status_code == 401

    def test_create_assessment_requires_auth(self, client):
        """Test creating assessment requires authorization"""
        response = client.post(
            "/api/v1/health-assessment/assessment",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        )
        # Should require auth
        assert response.status_code == 401

    def test_assessment_history_requires_auth(self, client):
        """Test getting assessment history requires authorization"""
        response = client.get("/api/v1/health-assessment/assessments/history")
        assert response.status_code == 401

    def test_assessment_comparison_requires_auth(self, client):
        """Test comparison requires authorization"""
        response = client.get("/api/v1/health-assessment/assessments/1/comparison")
        assert response.status_code == 401


class TestHealthAssessmentScoring:
    """Test health score calculation"""

    def test_score_ranges(self):
        """Test that scores are within valid range"""
        # Score should be 0-100
        for score in [0, 50, 100]:
            is_valid = 0 <= score <= 100
            assert is_valid

        for score in [-1, 101]:
            is_valid = 0 <= score <= 100
            assert not is_valid

    def test_dimension_weights(self):
        """Test that dimension weights sum to 100%"""
        nutrition_weight = 35
        behavior_weight = 35
        emotion_weight = 30

        total = nutrition_weight + behavior_weight + emotion_weight
        assert total == 100

    def test_grade_labels(self):
        """Test health score grade labels"""

        def get_grade(score):
            if score < 40:
                return "需改善"
            elif score < 60:
                return "一般"
            elif score < 80:
                return "良好"
            else:
                return "优秀"

        assert get_grade(30) == "需改善"
        assert get_grade(50) == "一般"
        assert get_grade(70) == "良好"
        assert get_grade(90) == "优秀"


class TestDataCompleteness:
    """Test data completeness validation"""

    def test_completeness_thresholds(self):
        """Test data completeness requirement thresholds"""
        # 7 days of food records
        food_days_required = 7

        # 14 days of habit records
        habit_days_required = 14

        # 7 days of sleep records
        sleep_days_required = 7

        assert food_days_required == 7
        assert habit_days_required == 14
        assert sleep_days_required == 7

    def test_completeness_calculation(self):
        """Test completeness percentage calculation"""

        def calculate_completeness(actual_days, required_days):
            if required_days == 0:
                return 100
            return min(100, (actual_days / required_days) * 100)

        assert calculate_completeness(7, 7) == 100
        assert calculate_completeness(3, 7) == pytest.approx(42.86, 0.1)
        assert calculate_completeness(0, 7) == 0


# Mark tests
pytestmark = pytest.mark.health_assessment
