from typing import List, Optional
from pydantic import BaseModel


class WeightTrend(BaseModel):
    dates: List[str]
    weights: List[float]


class NutritionBreakdown(BaseModel):
    carbs: float
    protein: float
    fat: float


class ChartData(BaseModel):
    weight_trend: WeightTrend
    nutrition_breakdown: NutritionBreakdown


class WeekOverviewItem(BaseModel):
    day: str
    mood: float
    stress: float


class EmotionalData(BaseModel):
    stress_level: int
    mood_score: int
    week_overview: List[WeekOverviewItem]


class BadgeInfo(BaseModel):
    id: int
    name: str
    description: str
    earned: bool
    icon: str


class OverviewData(BaseModel):
    total_weight_loss: float
    bmi: float
    weekly_average: float
    days_tracked: int
    active_habits: int
    streak_days: int
    total_points: int


class DashboardOverview(BaseModel):
    greeting: Optional[str] = "欢迎回来！"
    daily_tip: Optional[dict] = {
        "title": "今日健康提醒",
        "content": "今天多喝水保持身体水分平衡",
    }
    progress_summary: Optional[dict] = {
        "weight_progress": 0,
        "habit_completion": 0,
        "current_level": 1,
        "total_points": 0,
    }
    next_steps: Optional[list] = []
    overview: Optional[OverviewData] = None
    chart_data: Optional[ChartData] = None
    emotional_data: Optional[EmotionalData] = None
    badges: Optional[List[BadgeInfo]] = []


class QuickStats(BaseModel):
    today_calories: int
    daily_step_count: int
    water_intake: int
    sleep_hours: float
