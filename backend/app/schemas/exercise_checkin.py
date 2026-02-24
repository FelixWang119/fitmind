from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ExerciseCheckInBase(BaseModel):
    """运动打卡基础模型"""

    exercise_type: str = Field(
        ..., description="运动类型", min_length=1, max_length=100
    )
    category: Optional[str] = Field(
        None, description="分类：有氧/力量/灵活/其他", max_length=50
    )
    duration_minutes: int = Field(..., gt=0, le=1440, description="时长 (分钟)")
    intensity: str = Field(..., description="强度：low/medium/high", max_length=20)

    # 可选字段 (详细模式)
    distance_km: Optional[float] = Field(None, ge=0, le=500, description="距离 (公里)")
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=220, description="平均心率")
    notes: Optional[str] = Field(None, description="备注", max_length=5000)
    rating: Optional[int] = Field(None, ge=1, le=5, description="感受评分 1-5")

    # 运动开始时间
    started_at: Optional[str] = Field(
        None, description="运动开始时间 (ISO 8601)"
    )  # 如果为空，使用当前时间

    @field_validator("started_at")
    @classmethod
    def validate_started_at_not_future(cls, v):
        """F8: 禁止未来日期"""
        if v:
            from datetime import datetime as dt

            try:
                started = dt.fromisoformat(v.replace("Z", "+00:00"))
                if started > dt.utcnow():
                    raise ValueError("运动开始时间不能在未来")
            except ValueError as e:
                if "不能在未来" in str(e):
                    raise
                # ISO 格式错误会由 Pydantic 处理
        return v

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("强度必须是 low、medium 或 high")
        return v


class ExerciseCheckInCreate(ExerciseCheckInBase):
    """创建运动打卡"""

    pass


class ExerciseCheckInUpdate(BaseModel):
    """更新运动打卡"""

    exercise_type: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, gt=0, le=1440)
    intensity: Optional[str] = Field(None, max_length=20)
    distance_km: Optional[float] = Field(None, ge=0, le=500)
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=220)
    notes: Optional[str] = Field(None, max_length=5000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    started_at: Optional[str] = None

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v):
        if v and v not in ["low", "medium", "high"]:
            raise ValueError("强度必须是 low、medium 或 high")
        return v


class EstimationDetails(BaseModel):
    """卡路里估算详情"""

    met_value: float = Field(..., description="MET 值")
    weight_kg: float = Field(..., description="体重 (kg)")
    duration_hours: float = Field(..., description="时长 (小时)")
    intensity_factor: float = Field(..., description="强度系数")
    formula: str = Field(..., description="计算公式")


class ExerciseCheckInResponse(BaseModel):
    """运动打卡响应"""

    id: int
    user_id: int
    exercise_type: str
    category: Optional[str]
    duration_minutes: int
    intensity: str
    distance_km: Optional[float]
    heart_rate_avg: Optional[int]
    notes: Optional[str]
    rating: Optional[int]
    calories_burned: int
    is_estimated: bool
    estimation_details: Optional[Dict] = None
    started_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExerciseCheckInDailySummary(BaseModel):
    """当日运动摘要"""

    date: str = Field(..., description="日期 (ISO 8601)")
    total_duration_minutes: int = Field(0, description="总时长 (分钟)")
    total_calories_burned: int = Field(0, description="总燃烧卡路里")
    sessions_count: int = Field(0, description="打卡次数")
    exercise_types: List[str] = Field([], description="涉及的运动类型")
    average_heart_rate: Optional[int] = Field(None, description="平均心率")


class ExerciseTypeResponse(BaseModel):
    """运动类型响应"""

    type: str = Field(..., description="运动类型")
    met_value: float = Field(..., description="MET 值")
    category: str = Field(..., description="分类")


class DailySummaryResponse(BaseModel):
    """每日摘要响应 (Dashboard 集成)"""

    date: str
    total_duration_minutes: int
    total_calories_burned: int
    sessions_count: int
    exercise_types: List[str]
    average_heart_rate: Optional[int]
    goal_duration: Optional[int] = Field(None, description="目标时长 (分钟)")
    goal_calories: Optional[int] = Field(None, description="目标卡路里")
    progress_percentage: Optional[float] = Field(None, description="进度百分比")
