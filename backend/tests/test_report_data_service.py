"""测试报告数据服务 (Report Data Service)

测试 Story SP-10.1: 报告数据服务
"""

import uuid
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.health_record import HealthRecord
from app.models.nutrition import Meal
from app.models.habit import Habit, HabitCompletion
from app.models.user import User
from app.services.report_data_service import (
    ReportDataService,
    ReportType,
    ReportData,
    WeightMetrics,
    NutritionMetrics,
    ExerciseMetrics,
    HabitMetrics,
    PeriodInfo,
)


# =============================================================================
# Test Cases
# =============================================================================


# =============================================================================
# Test Cases
# =============================================================================


class TestReportDataServiceInitialization:
    """测试服务初始化"""

    def test_service_initialization(self, db_session: Session):
        """Story 10.1: Report Data Service 初始化"""
        service = ReportDataService(db_session)
        assert service is not None
        assert service.db is not None


class TestReportDataModels:
    """测试数据模型"""

    def test_report_type_enum(self):
        """测试报告类型枚举"""
        assert ReportType.DAILY == "daily"
        assert ReportType.WEEKLY == "weekly"
        assert ReportType.MONTHLY == "monthly"

    def test_period_info_model(self):
        """测试时间段信息模型"""
        period = PeriodInfo(
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 1),
            report_type=ReportType.DAILY,
            days_count=1,
        )
        assert period.start_date == date(2026, 3, 1)
        assert period.end_date == date(2026, 3, 1)
        assert period.report_type == "daily"
        assert period.days_count == 1

    def test_weight_metrics_model(self):
        """测试体重指标模型"""
        weight = WeightMetrics(
            current_weight=70.5,
            weight_change=-0.3,
            weight_change_rate=-0.42,
            average_weight=70.6,
            records_count=1,
        )
        assert weight.current_weight == 70.5
        assert weight.weight_change == -0.3

    def test_nutrition_metrics_model(self):
        """测试营养指标模型"""
        nutrition = NutritionMetrics(
            total_calories=1800,
            average_daily_calories=1800,
            meals_count=3,
            meal_breakdown={"breakfast": 1, "lunch": 1, "dinner": 1},
        )
        assert nutrition.total_calories == 1800
        assert nutrition.meals_count == 3

    def test_exercise_metrics_model(self):
        """测试运动指标模型"""
        exercise = ExerciseMetrics(
            total_minutes=45,
            average_daily_minutes=45,
            total_steps=6000,
            total_calories_burned=300,
            sessions_count=1,
        )
        assert exercise.total_minutes == 45
        assert exercise.total_steps == 6000

    def test_habit_metrics_model(self):
        """测试习惯指标模型"""
        habits = HabitMetrics(
            total_checkins=5,
            checkin_rate=83.3,
            habits_completed=["water", "weight"],
            habits_partial=[],
            habits_missed=["meditation"],
        )
        assert habits.total_checkins == 5
        assert habits.checkin_rate == 83.3
        assert len(habits.habits_completed) == 2


class TestDailyReportData:
    """测试日报数据查询"""

    def test_get_daily_report_data(self, db_session: Session, test_user: User):
        """测试日报数据查询"""
        # Arrange
        service = ReportDataService(db_session)
        target_date = date(2026, 3, 2)

        # Act
        result = service.get_daily_report_data(
            user_id=test_user.id,
            target_date=target_date,
        )

        # Assert
        assert result is not None
        assert isinstance(result, ReportData)
        assert result.period.report_type == ReportType.DAILY
        assert result.period.days_count == 1
        assert result.period.start_date == target_date
        assert result.period.end_date == target_date
        assert result.weight is not None
        assert result.nutrition is not None
        assert result.exercise is not None
        assert result.habits is not None

    def test_get_daily_report_data_with_no_data(
        self, db_session: Session, test_user: User
    ):
        """测试无数据时的日报查询"""
        # Arrange
        service = ReportDataService(db_session)
        target_date = date(2026, 3, 2)

        # Act
        result = service.get_daily_report_data(
            user_id=test_user.id,
            target_date=target_date,
        )

        # Assert - should return default values
        assert result.period.report_type == ReportType.DAILY
        assert result.weight.records_count == 0
        assert result.nutrition.meals_count == 0
        assert result.exercise.sessions_count == 0


class TestWeeklyReportData:
    """测试周报数据聚合"""

    def test_get_weekly_report_data(self, db_session: Session, test_user: User):
        """测试周报数据聚合"""
        # Arrange
        service = ReportDataService(db_session)
        week_start = date(2026, 2, 24)

        # Act
        result = service.get_weekly_report_data(
            user_id=test_user.id,
            week_start=week_start,
        )

        # Assert
        assert result is not None
        assert isinstance(result, ReportData)
        assert result.period.report_type == ReportType.WEEKLY
        assert result.period.days_count == 7
        assert result.period.start_date == week_start
        assert result.period.end_date == week_start + timedelta(days=6)

    def test_weekly_report_date_range(self, db_session: Session, test_user: User):
        """测试周报日期范围正确"""
        # Arrange
        service = ReportDataService(db_session)
        week_start = date(2026, 2, 24)  # Monday

        # Act
        result = service.get_weekly_report_data(
            user_id=test_user.id,
            week_start=week_start,
        )

        # Assert
        assert result.period.start_date.weekday() == 0  # Monday
        assert result.period.end_date.weekday() == 6  # Sunday


class TestMonthlyReportData:
    """测试月报数据聚合"""

    def test_get_monthly_report_data(self, db_session: Session, test_user: User):
        """测试月报数据聚合"""
        # Arrange
        service = ReportDataService(db_session)
        month_start = date(2026, 3, 1)

        # Act
        result = service.get_monthly_report_data(
            user_id=test_user.id,
            month_start=month_start,
        )

        # Assert
        assert result is not None
        assert isinstance(result, ReportData)
        assert result.period.report_type == ReportType.MONTHLY
        assert result.period.days_count == 30
        assert result.period.start_date == month_start
        assert result.period.end_date == month_start + timedelta(days=29)


class TestUnifiedEntry:
    """测试统一入口"""

    def test_get_report_data_daily(self, db_session: Session, test_user: User):
        """测试统一入口 - 日报"""
        # Arrange
        service = ReportDataService(db_session)
        target_date = date(2026, 3, 2)

        # Act
        result = service.get_report_data(
            user_id=test_user.id,
            report_type=ReportType.DAILY,
            target_date=target_date,
        )

        # Assert
        assert result.period.report_type == ReportType.DAILY

    def test_get_report_data_weekly(self, db_session: Session, test_user: User):
        """测试统一入口 - 周报"""
        # Arrange
        service = ReportDataService(db_session)
        target_date = date(2026, 3, 2)  # Wednesday

        # Act
        result = service.get_report_data(
            user_id=test_user.id,
            report_type=ReportType.WEEKLY,
            target_date=target_date,
        )

        # Assert
        assert result.period.report_type == ReportType.WEEKLY
        assert result.period.days_count == 7
        assert result.period.start_date.weekday() == 0  # Monday

    def test_get_report_data_monthly(self, db_session: Session, test_user: User):
        """测试统一入口 - 月报"""
        # Arrange
        service = ReportDataService(db_session)
        target_date = date(2026, 3, 15)  # Mid-month

        # Act
        result = service.get_report_data(
            user_id=test_user.id,
            report_type=ReportType.MONTHLY,
            target_date=target_date,
        )

        # Assert
        assert result.period.report_type == ReportType.MONTHLY
        assert result.period.start_date.day == 1  # First of month


class TestEdgeCases:
    """边界情况测试"""

    def test_weight_metrics_with_no_data(self, db_session: Session, test_user: User):
        """测试无体重数据时返回默认值"""
        service = ReportDataService(db_session)

        weight = service._get_weight_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert weight.records_count == 0
        assert weight.current_weight is None

    def test_nutrition_metrics_with_no_data(self, db_session: Session, test_user: User):
        """测试无饮食数据时返回默认值"""
        service = ReportDataService(db_session)

        nutrition = service._get_nutrition_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert nutrition.meals_count == 0
        assert nutrition.total_calories == 0

    def test_exercise_metrics_with_no_data(self, db_session: Session, test_user: User):
        """测试无运动数据时返回默认值"""
        service = ReportDataService(db_session)

        exercise = service._get_exercise_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert exercise.sessions_count == 0
        assert exercise.total_minutes == 0

    def test_habits_metrics_with_no_habits(self, db_session: Session, test_user: User):
        """测试无习惯数据时返回默认值"""
        service = ReportDataService(db_session)

        habits = service._get_habit_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert habits.total_checkins == 0
        assert habits.checkin_rate == 0
        assert habits.habits_completed == []

    def test_unsupported_report_type(self, db_session: Session, test_user: User):
        """测试不支持的报告类型"""
        service = ReportDataService(db_session)

        with pytest.raises(ValueError, match="Unsupported report type"):
            service.get_report_data(
                user_id=test_user.id, report_type="yearly", target_date=date(2026, 3, 1)
            )


class TestDataAggregation:
    """测试数据聚合"""

    def test_weight_change_calculation(self, db_session: Session, test_user: User):
        """测试体重变化计算"""
        # Create two weight records with different weights
        record1 = HealthRecord(
            user_id=test_user.id,
            weight=72000,  # 72kg
            record_date=datetime(2026, 3, 1),
        )
        record2 = HealthRecord(
            user_id=test_user.id,
            weight=70000,  # 70kg
            record_date=datetime(2026, 3, 7),
        )
        db_session.add_all([record1, record2])
        db_session.commit()

        service = ReportDataService(db_session)

        weight = service._get_weight_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 7)
        )

        assert weight.records_count == 2
        assert weight.current_weight == 70.0
        assert weight.weight_change == -2.0
        assert weight.weight_change_rate == pytest.approx(-2.78, rel=0.01)

    def test_nutrition_calories_aggregation(self, db_session: Session, test_user: User):
        """测试营养热量聚合"""
        # Create meals with different calories
        meal1 = Meal(
            user_id=test_user.id,
            meal_type="breakfast",
            name="Breakfast",
            calories=500,
            meal_datetime=datetime(2026, 3, 1, 8, 0),
        )
        meal2 = Meal(
            user_id=test_user.id,
            meal_type="lunch",
            name="Lunch",
            calories=700,
            meal_datetime=datetime(2026, 3, 1, 12, 0),
        )
        db_session.add_all([meal1, meal2])
        db_session.commit()

        service = ReportDataService(db_session)

        nutrition = service._get_nutrition_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert nutrition.meals_count == 2
        assert nutrition.total_calories == 1200
        assert nutrition.meal_breakdown["breakfast"] == 1
        assert nutrition.meal_breakdown["lunch"] == 1

    def test_exercise_minutes_aggregation(self, db_session: Session, test_user: User):
        """测试运动分钟数聚合"""
        # Create exercise records
        record = HealthRecord(
            user_id=test_user.id,
            exercise_minutes=45,
            steps_count=6000,
            record_date=datetime(2026, 3, 1),
        )
        db_session.add(record)
        db_session.commit()

        service = ReportDataService(db_session)

        exercise = service._get_exercise_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 1)
        )

        assert exercise.sessions_count == 1
        assert exercise.total_minutes == 45
        assert exercise.total_steps == 6000

    def test_habit_checkin_rate(self, db_session: Session, test_user: User):
        """测试习惯打卡率计算"""
        # Create a habit
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            category="health",
            frequency="daily",
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()

        # Create completions for 3 out of 7 days
        for i in range(3):
            completion = HabitCompletion(
                habit_id=habit.id,
                completion_date=datetime(2026, 3, 1 + i),
            )
            db_session.add(completion)
        db_session.commit()

        service = ReportDataService(db_session)

        habits = service._get_habit_metrics(
            user_id=test_user.id, start_date=date(2026, 3, 1), end_date=date(2026, 3, 7)
        )

        assert habits.total_checkins == 3
        assert habits.checkin_rate == pytest.approx(42.86, rel=0.1)
        assert "Test Habit" in habits.habits_partial
