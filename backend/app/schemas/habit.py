import enum
from datetime import datetime, date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class HabitFrequency(str, enum.Enum):
    """习惯频率枚举"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class HabitCategory(str, enum.Enum):
    """习惯类别枚举"""

    DIET = "diet"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    MENTAL_HEALTH = "mental_health"
    HYDRATION = "hydration"
    OTHER = "other"


class HabitGoalType(str, enum.Enum):
    """习惯目标类型枚举"""

    COMPLETION_RATE = "completion_rate"
    STREAK = "streak"
    TOTAL_COUNT = "total_count"


class HabitGoalPeriod(str, enum.Enum):
    """习惯目标周期枚举"""

    WEEKLY = "weekly"
    MONTHLY = "monthly"


class HabitBase(BaseModel):
    """习惯基础模型"""

    name: str = Field(..., min_length=1, max_length=200, description="习惯名称")
    description: Optional[str] = Field(None, description="习惯描述")
    category: HabitCategory = Field(..., description="习惯类别")
    frequency: HabitFrequency = Field(
        default=HabitFrequency.DAILY, description="习惯频率"
    )

    # 目标设置
    target_value: Optional[int] = Field(None, ge=1, description="目标值")
    target_unit: Optional[str] = Field(None, max_length=50, description="单位")

    # 时间设置
    preferred_time: Optional[str] = Field(None, max_length=50, description="偏好时间")
    reminder_enabled: bool = Field(default=False, description="是否启用提醒")
    reminder_time: Optional[str] = Field(
        None,
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="提醒时间(HH:MM)",
    )


class HabitCreate(HabitBase):
    """创建习惯"""

    pass


class HabitUpdate(BaseModel):
    """更新习惯"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="习惯名称"
    )
    description: Optional[str] = Field(None, description="习惯描述")
    category: Optional[HabitCategory] = Field(None, description="习惯类别")
    frequency: Optional[HabitFrequency] = Field(None, description="习惯频率")
    target_value: Optional[int] = Field(None, ge=1, description="目标值")
    target_unit: Optional[str] = Field(None, max_length=50, description="单位")
    preferred_time: Optional[str] = Field(None, max_length=50, description="偏好时间")
    reminder_enabled: Optional[bool] = Field(None, description="是否启用提醒")
    reminder_time: Optional[str] = Field(
        None,
        pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="提醒时间(HH:MM)",
    )
    is_active: Optional[bool] = Field(None, description="是否活跃")


class HabitInDB(HabitBase):
    """数据库中的习惯"""

    id: int = Field(..., description="习惯ID")
    user_id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否活跃")
    streak_days: int = Field(..., description="连续天数")
    total_completions: int = Field(..., description="总完成次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class HabitCompletionBase(BaseModel):
    """习惯完成记录基础模型"""

    completion_date: datetime = Field(..., description="完成日期")
    actual_value: Optional[int] = Field(None, ge=0, description="实际完成值")
    notes: Optional[str] = Field(None, description="备注")
    mood_rating: Optional[int] = Field(None, ge=1, le=5, description="心情评分(1-5)")
    difficulty_rating: Optional[int] = Field(
        None, ge=1, le=5, description="难度评分(1-5)"
    )


class HabitCompletionCreate(HabitCompletionBase):
    """创建习惯完成记录"""

    pass


class HabitCompletionInDB(HabitCompletionBase):
    """数据库中的习惯完成记录"""

    id: int = Field(..., description="完成记录ID")
    habit_id: int = Field(..., description="习惯ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class HabitWithCompletions(HabitInDB):
    """包含完成记录的习惯"""

    completions: List[HabitCompletionInDB] = Field(default=[], description="完成记录")


class HabitStats(BaseModel):
    """习惯统计"""

    total_habits: int = Field(..., description="总习惯数")
    active_habits: int = Field(..., description="活跃习惯数")
    total_completions: int = Field(..., description="总完成次数")
    current_streak: int = Field(..., description="当前最长连续天数")
    completion_rate: float = Field(..., description="完成率(0-100)")

    # 按类别统计
    category_stats: Dict[str, int] = Field(..., description="按类别统计")

    # 最近7天完成情况
    weekly_completions: List[int] = Field(..., description="最近7天完成情况")


class HabitRecommendation(BaseModel):
    """习惯建议"""

    category: HabitCategory = Field(..., description="习惯类别")
    name: str = Field(..., description="习惯名称")
    description: str = Field(..., description="习惯描述")
    why_important: str = Field(..., description="为什么重要")
    difficulty: str = Field(..., description="难度: easy, medium, hard")
    estimated_time: str = Field(..., description="预计时间")
    suggested_frequency: HabitFrequency = Field(..., description="建议频率")


class DailyHabitChecklist(BaseModel):
    """每日习惯检查清单"""

    date: datetime = Field(..., description="日期")
    habits: List[Dict] = Field(..., description="习惯列表")
    completed_count: int = Field(..., description="已完成数量")
    total_count: int = Field(..., description="总数量")
    completion_percentage: float = Field(..., description="完成百分比")


class StreakInfo(BaseModel):
    """连续天数信息"""

    current_streak: int = Field(..., description="当前连续天数")
    longest_streak: int = Field(..., description="最长连续天数")
    streak_start_date: Optional[datetime] = Field(None, description="连续开始日期")
    last_completion_date: Optional[datetime] = Field(None, description="最后完成日期")
    is_streak_active: bool = Field(..., description="连续是否活跃")


# ============== New schemas for Story 4.2 ==============


class DailyStats(BaseModel):
    """每日统计"""

    date: str = Field(..., description="日期")
    completed: bool = Field(..., description="是否完成")
    actual_value: Optional[int] = Field(None, description="实际完成值")


class HabitStatsOverview(BaseModel):
    """习惯统计概览"""

    total_habits: int = Field(..., description="总习惯数")
    active_habits: int = Field(..., description="活跃习惯数")
    completion_rate: float = Field(..., description="完成率(0-100)")
    total_checkins: int = Field(..., description="总打卡次数")
    current_longest_streak: int = Field(..., description="当前最长连续天数")
    best_streak_ever: int = Field(..., description="历史最长连续天数")
    weekly_checkins: int = Field(..., description="本周打卡次数")
    monthly_checkins: int = Field(..., description="本月打卡次数")
    by_category: Dict[str, float] = Field(..., description="按类别完成率")


class CompletionRateStats(BaseModel):
    """完成率统计"""

    period: str = Field(..., description="周期(weekly/monthly/quarterly)")
    completion_rate: float = Field(..., description="完成率")
    total_required: int = Field(..., description="应完成次数")
    total_completed: int = Field(..., description="实际完成次数")
    trend: List[float] = Field(default_factory=list, description="趋势数据")


class HabitDetailedStats(BaseModel):
    """单个习惯详细统计"""

    habit_id: int = Field(..., description="习惯ID")
    habit_name: str = Field(..., description="习惯名称")
    total_checkins: int = Field(..., description="总打卡次数")
    current_streak: int = Field(..., description="当前连续天数")
    best_streak: int = Field(..., description="历史最长连续天数")
    completion_rate: float = Field(..., description="完成率")
    last_30_days_trend: List[DailyStats] = Field(
        default_factory=list, description="最近30天趋势"
    )
    checkin_time_distribution: Dict[str, int] = Field(
        default_factory=dict, description="打卡时间分布"
    )
    weekly_pattern: Dict[str, float] = Field(
        default_factory=dict, description="每周完成模式"
    )
    monthly_pattern: Dict[str, float] = Field(
        default_factory=dict, description="每月完成模式"
    )


class HabitCorrelation(BaseModel):
    """习惯关联性"""

    habit_ids: List[int] = Field(..., description="相关习惯ID")
    habit_names: List[str] = Field(..., description="相关习惯名称")
    correlation_strength: float = Field(..., description="关联强度(0-1)")
    description: str = Field(..., description="关联描述")


class BehaviorPatterns(BaseModel):
    """行为模式分析"""

    time_preference: str = Field(..., description="时间偏好(morning/afternoon/evening)")
    checkin_time_histogram: Dict[str, int] = Field(
        default_factory=dict, description="打卡时间分布"
    )
    weekly_pattern: Dict[str, float] = Field(
        default_factory=dict, description="每周完成模式"
    )
    weekend_vs_weekday: Dict[str, float] = Field(
        default_factory=dict, description="周末vs工作日"
    )
    habit_correlations: List[HabitCorrelation] = Field(
        default_factory=list, description="习惯关联性"
    )
    insights: List[str] = Field(default_factory=list, description="行为洞察")


class HabitGoalBase(BaseModel):
    """习惯目标基础模型"""

    habit_id: int = Field(..., description="习惯ID")
    goal_type: HabitGoalType = Field(..., description="目标类型")
    target_value: int = Field(..., ge=1, description="目标值")
    period: HabitGoalPeriod = Field(..., description="周期")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")


class HabitGoalCreate(HabitGoalBase):
    """创建习惯目标"""

    pass


class HabitGoalUpdate(BaseModel):
    """更新习惯目标"""

    target_value: Optional[int] = Field(None, ge=1, description="目标值")
    period: Optional[HabitGoalPeriod] = Field(None, description="周期")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class HabitGoalInDB(HabitGoalBase):
    """数据库中的习惯目标"""

    id: int = Field(..., description="目标ID")
    user_id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否活跃")
    is_achieved: bool = Field(..., description="是否达成")
    current_progress: int = Field(..., description="当前进度")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class HabitGoalWithProgress(HabitGoalInDB):
    """带进度的习惯目标"""

    progress_percentage: float = Field(..., description="进度百分比")
    days_remaining: int = Field(..., description="剩余天数")
    status: str = Field(..., description="状态(achieved/in_progress/expired)")
