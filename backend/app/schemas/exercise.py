from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ExerciseLogBase(BaseModel):
    """运动记录基础模型"""

    exercise_type: str = Field(..., description="运动类型", max_length=100)
    duration_minutes: int = Field(..., ge=1, description="运动时长(分钟)")
    calories_burned: Optional[int] = Field(None, ge=0, description="燃烧热量")
    distance_km: Optional[float] = Field(None, ge=0, description="运动距离(公里)")
    intensity: Optional[str] = Field(
        None, description="运动强度: low, medium, high", max_length=20
    )
    heart_rate_avg: Optional[int] = Field(None, ge=0, description="平均心率")
    notes: Optional[str] = Field(None, description="备注", max_length=500)


class ExerciseLogCreate(ExerciseLogBase):
    """创建运动记录"""

    pass


class ExerciseLogUpdate(BaseModel):
    """更新运动记录"""

    exercise_type: Optional[str] = Field(None, max_length=100)
    duration_minutes: Optional[int] = Field(None, ge=1)
    calories_burned: Optional[int] = Field(None, ge=0)
    distance_km: Optional[float] = Field(None, ge=0)
    intensity: Optional[str] = Field(None, max_length=20)
    heart_rate_avg: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class ExerciseLog(ExerciseLogBase):
    """运动记录"""

    id: int
    user_id: int
    workout_session_id: Optional[int] = None
    date: str  # ISO格式日期
    created_at: datetime

    @validator("intensity")
    def validate_intensity(cls, v):
        if v and v not in ["low", "medium", "high"]:
            raise ValueError("强度必须为: low, medium, 或 high")
        return v

    class Config:
        from_attributes = True


class WorkoutSessionBase(BaseModel):
    """运动会话基础模型"""

    date: str  # ISO格式日期
    exercise_type: str = Field(..., description="运动类型", max_length=100)
    duration_minutes: Optional[int] = Field(0, ge=0, description="运动时长(分钟)")
    steps_count: Optional[int] = Field(None, ge=0, description="步数")
    calories_burned: Optional[int] = Field(None, ge=0, description="燃烧热量")
    notes: Optional[str] = Field(None, description="备注", max_length=500)


class WorkoutSessionCreate(WorkoutSessionBase):
    """创建运动会话"""

    pass


class WorkoutSessionUpdate(BaseModel):
    """更新运动会话"""

    date: Optional[str] = None
    exercise_type: Optional[str] = Field(None, max_length=100)
    duration_minutes: Optional[int] = Field(None, ge=0)
    steps_count: Optional[int] = Field(None, ge=0)
    calories_burned: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutSession(WorkoutSessionBase):
    """运动会话"""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseRecommendation(BaseModel):
    """运动建议"""

    type: str = Field(..., description="运动类型")
    duration: int = Field(..., ge=1, description="推荐时长(分钟)")
    intensity: str = Field(..., description="推荐强度")
    benefits: List[str] = Field(..., description="运动益处")
    cautions: List[str] = Field(..., description="运动注意事项")


class WeeklyExerciseSummary(BaseModel):
    """周度运动摘要"""

    week_start: str  # ISO格式
    total_duration: int = Field(0, description="总时长(分钟)")
    total_calories_burned: int = Field(0, description="总燃烧热量")
    total_steps: int = Field(0, description="总步数")
    exercise_days: int = Field(0, description="有运动的天数")
    activity_types: List[str] = Field(..., description="涉及的运动类型")
    goals_achievement: float = Field(0.0, ge=0, le=1, description="目标完成度(0-1)")


class ExerciseProgress(BaseModel):
    """运动进度跟踪"""

    current_week: WeeklyExerciseSummary
    weekly_average: Optional[WeeklyExerciseSummary] = None
    goals_progress: dict  # 运动目标完成进度
