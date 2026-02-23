from typing import List, Optional
from pydantic import BaseModel, Field


class HealthScoreResponse(BaseModel):
    """健康评分响应"""

    overall_score: float = Field(..., description="综合健康评分", ge=0, le=100)
    weight_score: float = Field(..., description="体重管理评分", ge=0, le=100)
    nutrition_score: float = Field(..., description="营养摄入评分", ge=0, le=100)
    exercise_score: float = Field(..., description="运动锻炼评分", ge=0, le=100)
    habit_score: float = Field(..., description="习惯养成评分", ge=0, le=100)
    emotional_score: float = Field(..., description="情感健康评分", ge=0, le=100)
    trend: str = Field(
        ..., description="健康趋势", examples=["improving", "stable", "declining"]
    )
    insights: List[str] = Field(..., description="健康洞察")
    recommendations: List[str] = Field(..., description="个性化建议")

    class Config:
        from_attributes = True


class HealthScoreHistory(BaseModel):
    """健康评分历史记录"""

    date: str = Field(..., description="评分日期")
    overall_score: float = Field(..., description="综合评分")
    weight_score: float = Field(..., description="体重管理评分")
    nutrition_score: float = Field(..., description="营养摄入评分")
    exercise_score: float = Field(..., description="运动锻炼评分")
    habit_score: float = Field(..., description="习惯养成评分")
    emotional_score: float = Field(..., description="情感健康评分")

    class Config:
        from_attributes = True


class HealthScoreComparison(BaseModel):
    """健康评分对比"""

    current_score: HealthScoreResponse = Field(..., description="当前评分")
    previous_score: Optional[HealthScoreResponse] = Field(None, description="上次评分")
    improvement: Optional[float] = Field(None, description="改善幅度")
    areas_improved: List[str] = Field(default=[], description="改善领域")
    areas_declined: List[str] = Field(default=[], description="下降领域")

    class Config:
        from_attributes = True


class HealthScoreBreakdown(BaseModel):
    """健康评分细分"""

    category: str = Field(..., description="评分类别")
    score: float = Field(..., description="分数")
    weight: float = Field(..., description="权重")
    contribution: float = Field(..., description="对总分的贡献")
    status: str = Field(
        ..., description="状态", examples=["excellent", "good", "fair", "poor"]
    )
    suggestions: List[str] = Field(..., description="改进建议")

    class Config:
        from_attributes = True


class HealthScoreTrend(BaseModel):
    """健康评分趋势"""

    period: str = Field(
        ..., description="时间段", examples=["week", "month", "quarter"]
    )
    scores: List[HealthScoreHistory] = Field(..., description="评分历史")
    average_score: float = Field(..., description="平均分")
    trend_direction: str = Field(
        ..., description="趋势方向", examples=["up", "down", "stable"]
    )
    trend_strength: float = Field(..., description="趋势强度", ge=0, le=1)

    class Config:
        from_attributes = True


class HealthGoalProgress(BaseModel):
    """健康目标进度"""

    goal_type: str = Field(..., description="目标类型")
    current_value: float = Field(..., description="当前值")
    target_value: float = Field(..., description="目标值")
    progress_percentage: float = Field(..., description="进度百分比")
    estimated_completion: Optional[str] = Field(None, description="预计完成时间")
    confidence_level: float = Field(..., description="置信度", ge=0, le=1)

    class Config:
        from_attributes = True
