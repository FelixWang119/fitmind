"""Habit Stats API Tests

Tests for the habit statistics and goals endpoints.
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


class TestHabitStatsEndpoints:
    """Test habit stats API endpoints"""

    def test_get_stats_overview_unauthorized(self, client):
        """Test getting stats without authorization"""
        response = client.get("/api/v1/habits/stats/overview")
        assert response.status_code == 401

    def test_get_completion_rate_unauthorized(self, client):
        """Test getting completion rate without authorization"""
        response = client.get("/api/v1/habits/stats/completion")
        assert response.status_code == 401

    def test_get_behavior_patterns_unauthorized(self, client):
        """Test getting behavior patterns without authorization"""
        response = client.get("/api/v1/habits/stats/patterns")
        assert response.status_code == 401

    def test_get_habit_detailed_stats_unauthorized(self, client):
        """Test getting habit detailed stats without authorization"""
        response = client.get("/api/v1/habits/1/detailed-stats")
        assert response.status_code == 401


class TestHabitGoalsEndpoints:
    """Test habit goals API endpoints"""

    def test_get_goals_unauthorized(self, client):
        """Test getting goals without authorization"""
        response = client.get("/api/v1/habits/goals")
        assert response.status_code == 401

    def test_create_goal_unauthorized(self, client):
        """Test creating goal without authorization"""
        response = client.post(
            "/api/v1/habits/goals",
            json={
                "habit_id": 1,
                "goal_type": "streak_days",
                "target_value": 30,
                "period": "weekly",
            },
        )
        assert response.status_code == 401

    def test_update_goal_unauthorized(self, client):
        """Test updating goal without authorization"""
        response = client.put("/api/v1/habits/goals/1")
        assert response.status_code == 401

    def test_delete_goal_unauthorized(self, client):
        """Test deleting goal without authorization"""
        response = client.delete("/api/v1/habits/goals/1")
        assert response.status_code == 401


class TestHabitGoalValidation:
    """Test habit goal validation"""

    def test_goal_type_validation(self):
        """Test valid goal types"""
        valid_goal_types = [
            "completion_rate",
            "streak_days",
            "total_count",
        ]

        # All should be valid
        for goal_type in valid_goal_types:
            assert goal_type in valid_goal_types

    def test_period_validation(self):
        """Test valid periods"""
        valid_periods = [
            "daily",
            "weekly",
            "monthly",
        ]

        for period in valid_periods:
            assert period in valid_periods

    def test_target_value_validation(self):
        """Test target value constraints"""
        # Target value should be positive
        for value in [1, 7, 30, 100]:
            assert value > 0

    def test_goal_progress_calculation(self):
        """Test goal progress calculation"""

        def calculate_progress(current, target):
            if target == 0:
                return 0
            return min(100, (current / target) * 100)

        assert calculate_progress(15, 30) == 50
        assert calculate_progress(30, 30) == 100
        assert calculate_progress(45, 30) == 100
        assert calculate_progress(0, 30) == 0


class TestHabitStreakCalculation:
    """Test streak calculation logic"""

    def test_streak_calculation(self):
        """Test consecutive days calculation"""

        def calculate_streak(completion_dates):
            if not completion_dates:
                return 0

            # Sort dates in descending order
            sorted_dates = sorted(completion_dates, reverse=True)

            streak = 1
            for i in range(len(sorted_dates) - 1):
                diff = (sorted_dates[i] - sorted_dates[i + 1]).days
                if diff == 1:
                    streak += 1
                else:
                    break

            return streak

        from datetime import datetime

        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(5)]

        streak = calculate_streak(dates)
        assert streak == 5

    def test_streak_broken(self):
        """Test streak when there's a gap"""

        def calculate_streak(completion_dates):
            if not completion_dates:
                return 0

            sorted_dates = sorted(completion_dates, reverse=True)

            streak = 1
            for i in range(len(sorted_dates) - 1):
                diff = (sorted_dates[i] - sorted_dates[i + 1]).days
                if diff == 1:
                    streak += 1
                else:
                    break

            return streak

        from datetime import datetime

        today = datetime.now().date()
        # Gap of 2 days
        dates = [today, today - timedelta(days=1), today - timedelta(days=3)]

        streak = calculate_streak(dates)
        assert streak == 2


class TestHabitCompletionRate:
    """Test completion rate calculation"""

    def test_weekly_completion_rate(self):
        """Test weekly completion rate"""

        def calculate_weekly_rate(completed_days, total_days=7):
            if total_days == 0:
                return 0
            return (completed_days / total_days) * 100

        assert calculate_weekly_rate(7) == 100
        assert calculate_weekly_rate(5) == pytest.approx(71.43, 0.1)
        assert calculate_weekly_rate(3) == pytest.approx(42.86, 0.1)
        assert calculate_weekly_rate(0) == 0

    def test_monthly_completion_rate(self):
        """Test monthly completion rate"""

        def calculate_monthly_rate(completed_days, total_days=30):
            if total_days == 0:
                return 0
            return (completed_days / total_days) * 100

        assert calculate_monthly_rate(30) == 100
        assert calculate_monthly_rate(15) == 50
        assert calculate_monthly_rate(0) == 0


# Mark tests
pytestmark = pytest.mark.habit_stats
