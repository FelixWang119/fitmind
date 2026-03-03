"""Report Data Service Models: Pydantic schemas for health reports"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime
from enum import Enum


class ReportType(str, Enum):
    DAILY = "daily"  # 日报
    WEEKLY = "weekly"  # 周报
    MONTHLY = "monthly"  # 月报


class PeriodInfo(BaseModel):
    """时间段信息"""

    start_date: date
    end_date: date
    report_type: ReportType
    days_count: int


class WeightMetrics(BaseModel):
    """体重指标"""

    current_weight: Optional[float] = None
    weight_change: Optional[float] = None
    weight_change_rate: Optional[float] = None
    average_weight: Optional[float] = None
    records_count: int = 0


class NutritionMetrics(BaseModel):
    """营养指标"""

    total_calories: float = 0
    average_daily_calories: float = 0
    meals_count: int = 0
    meal_breakdown: Dict[str, int] = {}  # breakfast/lunch/dinner/snack


class ExerciseMetrics(BaseModel):
    """运动指标"""

    total_minutes: int = 0
    average_daily_minutes: float = 0
    total_steps: int = 0
    total_calories_burned: float = 0
    sessions_count: int = 0


class HabitMetrics(BaseModel):
    """习惯打卡指标"""

    total_checkins: int = 0
    checkin_rate: float = 0  # 0-100%
    habits_completed: List[str] = []
    habits_partial: List[str] = []
    habits_missed: List[str] = []


class ReportData(BaseModel):
    """报告数据"""

    period: PeriodInfo
    weight: WeightMetrics
    nutrition: NutritionMetrics
    exercise: ExerciseMetrics
    habits: HabitMetrics
    generated_at: datetime
