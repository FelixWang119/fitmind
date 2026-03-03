"""Basic Report Data Service with correct type hints for SQLAlchemy"""

from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import UserModel
from app.models.health_record import HealthRecord
from app.models.nutrition import Meal
from app.models.habit import HabitCompletion, Habit
from app.schemas.report_data import (
    ReportType,
    PeriodInfo,
    WeightMetrics,
    NutritionMetrics,
    ExerciseMetrics,
    HabitMetrics,
    ReportData,
)


class ReportDataService:
    """报告数据服务 - 聚合用户数据用于健康报告生成"""

    def __init__(self, db: Session):
        self.db = db

    def _get_period_dates(
        self, report_type: ReportType, target_date: date = None
    ) -> Tuple[date, date]:
        """获取报告期间的开始和结束日期"""
        if target_date is None:
            target_date = date.today()

        if report_type == ReportType.DAILY:
            return target_date, target_date
        elif report_type == ReportType.WEEKLY:
            # 周: 本周的周一到周日
            start_of_week = target_date - timedelta(days=target_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return start_of_week, end_of_week
        elif report_type == ReportType.MONTHLY:
            # 月: 本月第一天到最后一天
            start_of_month = target_date.replace(day=1)
            # 计算月末日期
            if target_date.month == 12:
                end_of_month = target_date.replace(
                    year=target_date.year + 1, month=1, day=1
                ) - timedelta(days=1)
            else:
                end_of_month = target_date.replace(
                    month=target_date.month + 1, day=1
                ) - timedelta(days=1)
            return start_of_month, end_of_month
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

    def get_report_data(
        self, user: UserModel, report_type: ReportType, target_date: date = None
    ) -> ReportData:
        """获取指定报告类型的数据"""
        start_date, end_date = self._get_period_dates(report_type, target_date)

        # 获取各项指标
        weight_metrics = self._get_weight_metrics(user.id, start_date, end_date)
        nutrition_metrics = self._get_nutrition_metrics(user.id, start_date, end_date)
        exercise_metrics = self._get_exercise_metrics(user.id, start_date, end_date)
        habit_metrics = self._get_habit_metrics(user.id, start_date, end_date)

        days_count = (end_date - start_date).days + 1

        period_info = PeriodInfo(
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            days_count=days_count,
        )

        return ReportData(
            period=period_info,
            weight=weight_metrics,
            nutrition=nutrition_metrics,
            exercise=exercise_metrics,
            habits=habit_metrics,
            generated_at=datetime.now(),
        )

    def _get_weight_metrics(
        self, user_id: int, start_date: date, end_date: date
    ) -> WeightMetrics:
        """获取体重相关指标"""
        # 获取体重记录
        weight_records_query = (
            self.db.query(HealthRecord.weight_kg)
            .filter(
                HealthRecord.user_id == user_id,
                HealthRecord.weight_kg.isnot(None),
                HealthRecord.record_date >= start_date,
                HealthRecord.record_date <= end_date,
            )
            .order_by(HealthRecord.record_date.desc())
            .all()
        )

        # 正确处理数据库查询结果
        weight_records = []
        for r in weight_records_query:
            if r.weight_kg is not None:
                weight_records.append(float(r.weight_kg))

        # 计算指标
        records_count = len(weight_records)
        current_weight = weight_records[0] if records_count > 0 else None
        average_weight = (
            sum(weight_records) / records_count if records_count > 0 else 0.0
        )

        # 如果有多条记录，计算体重变化
        weight_change = None
        weight_change_rate = None
        if records_count > 1:
            oldest_weight = weight_records[-1]
            if (
                current_weight is not None
                and oldest_weight is not None
                and oldest_weight != 0
            ):
                weight_change = round(current_weight - oldest_weight, 2)
                weight_change_rate = round(
                    (weight_change / abs(oldest_weight)) * 100, 2
                )

        return WeightMetrics(
            current_weight=current_weight,
            weight_change=weight_change,
            weight_change_rate=weight_change_rate,
            average_weight=average_weight,
            records_count=records_count,
        )

    def _get_nutrition_metrics(
        self, user_id: int, start_date: date, end_date: date
    ) -> NutritionMetrics:
        """获取营养相关指标"""
        # 查询指定期间的餐食记录
        meals = (
            self.db.query(Meal)
            .filter(
                Meal.user_id == user_id,
                func.date(Meal.meal_datetime) >= start_date,
                func.date(Meal.meal_datetime) <= end_date,
            )
            .all()
        )

        total_calories = 0.0
        meals_count = 0
        meal_breakdown = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}

        for meal in meals:
            if meal.total_calories is not None:
                total_calories += float(meal.total_calories)
                meals_count += 1

            # 根据用餐时间分类
            meal_time = meal.meal_datetime.time()
            if meal_time < datetime.strptime("11:00", "%H:%M").time():
                meal_breakdown["breakfast"] += 1
            elif meal_time < datetime.strptime("16:00", "%H:%M").time():
                meal_breakdown["lunch"] += 1
            elif meal_time < datetime.strptime("22:00", "%H:%M").time():
                meal_breakdown["dinner"] += 1
            else:
                meal_breakdown["snack"] += 1

        available_days = max((end_date - start_date).days + 1, 1)
        average_daily_calories = total_calories / available_days

        return NutritionMetrics(
            total_calories=round(total_calories, 2),
            average_daily_calories=round(average_daily_calories, 2),
            meals_count=meals_count,
            meal_breakdown=meal_breakdown,
        )

    def _get_exercise_metrics(
        self, user_id: int, start_date: date, end_date: date
    ) -> ExerciseMetrics:
        """获取运动相关指标"""
        # 查询指定期间的运动数据
        health_records = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user_id,
                HealthRecord.record_date >= start_date,
                HealthRecord.record_date <= end_date,
                (HealthRecord.exercise_minutes.isnot(None))
                | (HealthRecord.steps_count.isnot(None)),
            )
            .all()
        )

        total_minutes = 0
        total_steps = 0
        total_calories_burned = 0.0
        sessions_count = 0

        for record in health_records:
            if record.exercise_minutes is not None:
                exercise_minutes = record.exercise_minutes
                total_minutes += (
                    int(exercise_minutes)
                    if isinstance(exercise_minutes, (int, float))
                    else 0
                )
                sessions_count += 1
            if record.steps_count is not None:
                steps_count = record.steps_count
                total_steps += (
                    int(steps_count) if isinstance(steps_count, (int, float)) else 0
                )
            if record.calories_burned is not None:
                calories_burned = record.calories_burned
                total_calories_burned += (
                    float(calories_burned)
                    if isinstance(calories_burned, (int, float))
                    else 0.0
                )

        available_days = max((end_date - start_date).days + 1, 1)
        average_daily_minutes = total_minutes / available_days

        return ExerciseMetrics(
            total_minutes=total_minutes,
            average_daily_minutes=round(average_daily_minutes, 2),
            total_steps=total_steps,
            total_calories_burned=round(total_calories_burned, 2),
            sessions_count=sessions_count,
        )

    def _get_habit_metrics(
        self, user_id: int, start_date: date, end_date: date
    ) -> HabitMetrics:
        """获取习惯相关指标"""
        # 查询有效的用户习惯（活跃状态）
        habits = (
            self.db.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active == True)
            .all()
        )

        # 查询指定期间的习惯打卡记录
        habit_completions = (
            self.db.query(HabitCompletion)
            .filter(
                HabitCompletion.user_id == user_id,
                func.date(HabitCompletion.completion_date) >= start_date,
                func.date(HabitCompletion.completion_date) <= end_date,
            )
            .all()
        )

        # 统计各项习惯的完成情况
        total_checkins = len(habit_completions)

        # 按习惯ID分组统计完成情况
        habit_completion_counts = {}
        for completion in habit_completions:
            habit_id = completion.habit_id
            if habit_id not in habit_completion_counts:
                habit_completion_counts[habit_id] = 0
            habit_completion_counts[habit_id] += 1

        # 计算完成天数范围内的统计数据
        available_days = max((end_date - start_date).days + 1, 1)

        checkin_rate_sum = 0.0
        active_daily_habits_count = 0

        habits_completed = []
        habits_partial = []
        habits_missed = []

        for habit in habits:
            completion_count = habit_completion_counts.get(habit.id, 0)

            # 计算完成率，只对有效习惯（频率为daily）计算
            if habit.frequency == "daily":
                expected_completions = available_days
                completion_rate = (
                    round((completion_count / expected_completions) * 100, 2)
                    if expected_completions > 0
                    else 0.0
                )
                checkin_rate_sum += completion_rate
                active_daily_habits_count += 1

                # 根据完成率分类习惯完成情况
                if completion_rate >= 90:
                    habits_completed.append(habit.name)
                elif completion_rate > 0:
                    habits_partial.append(habit.name)
                else:
                    habits_missed.append(habit.name)

        # 计算平均完成率
        avg_checkin_rate = (
            checkin_rate_sum / active_daily_habits_count
            if active_daily_habits_count > 0
            else 0.0
        )

        return HabitMetrics(
            total_checkins=total_checkins,
            checkin_rate=round(avg_checkin_rate, 2),
            habits_completed=habits_completed,
            habits_partial=habits_partial,
            habits_missed=habits_missed,
        )
