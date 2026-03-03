"""
Tests for the report data service
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import date, datetime
from app.services.report_data_service import ReportDataService
from app.models.habit import Habit
from app.models.habit import HabitCompletion
from app.models.nutrition import Meal
from app.models.health_record import HealthRecord
from app.schemas.report_data import ReportType


class TestReportDataService:
    """Test cases for Report Data Service"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_mock = Mock()
        self.service = ReportDataService(self.db_mock)

    def test_get_period_dates_daily(self):
        """Test getting dates for daily report"""
        target_date = date(2023, 10, 15)
        start, end = self.service._get_period_dates(ReportType.DAILY, target_date)

        assert start == date(2023, 10, 15)
        assert end == date(2023, 10, 15)

    def test_get_period_dates_weekly(self):
        """Test getting dates for weekly report (monday to sunday)"""
        # This Sunday is 2023-10-15, so Monday should be 2023-10-09
        target_date = date(2023, 10, 15)
        start, end = self.service._get_period_dates(ReportType.WEEKLY, target_date)

        assert start == date(2023, 10, 9)  # Monday
        assert end == date(2023, 10, 15)  # Sunday (7 days)

    def test_get_period_dates_monthly(self):
        """Test getting dates for monthly report"""
        target_date = date(2023, 10, 15)
        start, end = self.service._get_period_dates(ReportType.MONTHLY, target_date)

        assert start == date(2023, 10, 1)
        assert end == date(2023, 10, 31)

    def test_get_weight_metrics(self, mocker):
        """Test getting weight metrics"""
        # Mock a user record
        user_id = 1

        # Create mock weight records
        mock_weight_record = Mock()
        mock_weight_record.weight_kg = 70.5
        self.db_mock.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_weight_record
        ]

        # Test the method
        result = self.service._get_weight_metrics(
            user_id, date(2023, 10, 1), date(2023, 10, 31)
        )

        assert result.records_count == 1
        assert result.current_weight == 70.5

    def test_get_nutrition_metrics(self):
        """Test getting nutrition metrics"""
        user_id = 1

        # Create mock meal records
        mock_meal = Mock()
        mock_meal.total_calories = 500
        mock_meal.meal_datetime = datetime(2023, 10, 15, 12, 0)
        self.db_mock.query.return_value.filter.return_value.all.return_value = [
            mock_meal
        ]

        # Test the method
        result = self.service._get_nutrition_metrics(
            user_id, date(2023, 10, 1), date(2023, 10, 31)
        )

        assert result.meals_count == 1
        assert result.total_calories == 500

    def test_get_exercise_metrics(self):
        """Test getting exercise metrics"""
        user_id = 1

        # Create mock health records
        mock_record = Mock()
        mock_record.exercise_minutes = 60
        mock_record.steps_count = 5000
        mock_record.calories_burned = 400.0
        self.db_mock.query.return_value.filter.return_value.all.return_value = [
            mock_record
        ]

        # Test the method
        result = self.service._get_exercise_metrics(
            user_id, date(2023, 10, 1), date(2023, 10, 31)
        )

        assert result.sessions_count == 1
        assert result.total_minutes == 60
        assert result.total_steps == 5000

    def test_get_habit_metrics(self):
        """Test getting habit metrics"""
        user_id = 1

        # Create mock habit data
        mock_habit = Mock()
        mock_habit.id = 1
        mock_habit.name = "Drink Water"
        mock_habit.frequency = "daily"
        mock_habit.user_id = user_id
        self.db_mock.query.return_value.filter.return_value.all.return_value = [
            mock_habit
        ]

        # Create mock completion data
        mock_completion = Mock()
        mock_completion.habit_id = 1
        mock_completion.completion_date = date(2023, 10, 15)
        mock_completion.user_id = user_id
        self.db_mock.query.return_value.filter.return_value.all.return_value = [
            mock_completion
        ]

        # Test the method
        result = self.service._get_habit_metrics(
            user_id, date(2023, 10, 1), date(2023, 10, 31)
        )

        assert result.total_checkins == 1
        # The habit name should be in one of the categories
        assert (
            "Drink Water"
            in result.habits_completed + result.habits_partial + result.habits_missed
        )
