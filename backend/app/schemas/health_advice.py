from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class PersonalizedRecommendation(BaseModel):
    """个性化建议"""

    category: str = Field(..., description="建议分类")
    title: str = Field(..., description="建议标题")
    content: str = Field(..., description="建议内容")
    priority: str = Field(..., description="优先级", examples=["high", "medium", "low"])
    confidence_score: float = Field(..., description="置信度", ge=0, le=1)
    action_items: List[str] = Field(..., description="行动项")
    timeframe: str = Field(
        ...,
        description="时间范围",
        examples=["immediate", "short_term", "medium_term", "long_term"],
    )

    class Config:
        from_attributes = True


class UserHealthProfile(BaseModel):
    """用户健康画像"""

    user_id: int = Field(..., description="用户ID")
    assessment_date: str = Field(..., description="评估日期")
    weight_status: str = Field(..., description="体重状态")
    nutrition_status: str = Field(..., description="营养状态")
    activity_level: str = Field(..., description="活动水平")
    habit_consistency: str = Field(..., description="习惯一致性")
    emotional_state: str = Field(..., description="情绪状态")
    overall_health_score: float = Field(..., description="总体健康评分", ge=0, le=100)
    risk_factors: List[str] = Field(..., description="风险因素")
    strengths: List[str] = Field(..., description="优势")

    class Config:
        from_attributes = True


class PersonalizedHealthAdviceRequest(BaseModel):
    """个性化健康建议请求"""

    start_date: date = Field(..., description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    include_historical_context: bool = Field(True, description="是否包含历史上下文")
    focus_areas: Optional[List[str]] = Field(None, description="关注领域")
    advice_depth: str = Field(
        "comprehensive",
        description="建议深度",
        examples=["brief", "detailed", "comprehensive"],
    )

    class Config:
        from_attributes = True


class PersonalizedHealthAdviceResponse(BaseModel):
    """个性化健康建议响应"""

    user_id: int = Field(..., description="用户ID")
    request_timestamp: str = Field(..., description="请求时间戳")
    analysis_period: Dict[str, str] = Field(..., description="分析周期")
    user_health_profile: UserHealthProfile = Field(..., description="用户健康画像")
    recommendations: List[PersonalizedRecommendation] = Field(
        ..., description="个性化建议"
    )
    key_insights: List[str] = Field(..., description="关键洞察")
    predicted_outcomes: Dict[str, Any] = Field(..., description="预测结果")
    follow_up_suggestions: List[str] = Field(..., description="后续建议")

    class Config:
        from_attributes = True


class BehavioralPattern(BaseModel):
    """行为模式"""

    pattern_type: str = Field(..., description="模式类型")
    frequency: str = Field(..., description="频率")
    consistency_score: float = Field(..., description="一致性评分", ge=0, le=1)
    impact_on_health: str = Field(..., description="对健康的影响")
    recommendations: List[str] = Field(..., description="建议")

    class Config:
        from_attributes = True


class HealthGoalAlignment(BaseModel):
    """健康目标对齐"""

    goal_type: str = Field(..., description="目标类型")
    current_progress: float = Field(..., description="当前进度", ge=0, le=100)
    alignment_score: float = Field(..., description="对齐评分", ge=0, le=1)
    barriers: List[str] = Field(..., description="障碍")
    enablers: List[str] = Field(..., description="促进因素")

    class Config:
        from_attributes = True
