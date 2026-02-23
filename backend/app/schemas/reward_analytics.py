from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class RewardTrendData(BaseModel):
    """奖励趋势数据"""

    period: str = Field(
        ..., description="周期", examples=["daily", "weekly", "monthly"]
    )
    dates: List[str] = Field(..., description="日期列表")
    points_earned: List[int] = Field(..., description="获得积分")
    badges_earned: List[int] = Field(..., description="获得徽章")
    challenges_completed: List[int] = Field(..., description="完成挑战")
    engagement_score: List[float] = Field(..., description="参与度评分", ge=0, le=100)

    class Config:
        from_attributes = True


class UserRewardSummary(BaseModel):
    """用户奖励摘要"""

    user_id: int = Field(..., description="用户ID")
    total_points: int = Field(..., description="总积分")
    current_level: int = Field(..., description="当前等级")
    badges_count: int = Field(..., description="徽章数量")
    challenges_completed: int = Field(..., description="完成挑战数")
    streak_days: int = Field(..., description="连续天数")
    last_reward_date: Optional[str] = Field(None, description="最后奖励日期")
    next_level_points_needed: int = Field(..., description="下一等级所需积分")

    class Config:
        from_attributes = True


class RewardEffectivenessData(BaseModel):
    """奖励有效性数据"""

    reward_type: str = Field(..., description="奖励类型")
    engagement_impact: float = Field(..., description="参与度影响", ge=0, le=1)
    retention_impact: float = Field(..., description="留存影响", ge=0, le=1)
    behavior_change_impact: float = Field(..., description="行为改变影响", ge=0, le=1)
    user_satisfaction: float = Field(..., description="用户满意度", ge=0, le=1)
    recommendations: List[str] = Field(..., description="建议")

    class Config:
        from_attributes = True


class RewardAnalyticsResponse(BaseModel):
    """奖励分析响应"""

    user_id: int = Field(..., description="用户ID")
    analysis_period: Dict[str, str] = Field(..., description="分析周期")
    user_summary: UserRewardSummary = Field(..., description="用户摘要")
    trend_data: RewardTrendData = Field(..., description="趋势数据")
    effectiveness_data: List[RewardEffectivenessData] = Field(
        ..., description="有效性数据"
    )
    top_performing_rewards: List[str] = Field(..., description="表现最佳奖励")
    areas_for_improvement: List[str] = Field(..., description="改进领域")
    predictive_insights: Dict[str, Any] = Field(..., description="预测性洞察")

    class Config:
        from_attributes = True


class GamificationImpact(BaseModel):
    """游戏化影响"""

    metric: str = Field(..., description="指标")
    before_gamification: float = Field(..., description="游戏化前")
    after_gamification: float = Field(..., description="游戏化后")
    improvement_percentage: float = Field(..., description="改进百分比")
    statistical_significance: float = Field(..., description="统计显著性", ge=0, le=1)

    class Config:
        from_attributes = True


class UserEngagementProfile(BaseModel):
    """用户参与度画像"""

    user_id: int = Field(..., description="用户ID")
    engagement_level: str = Field(
        ..., description="参与度水平", examples=["low", "medium", "high", "very_high"]
    )
    preferred_reward_types: List[str] = Field(..., description="偏好奖励类型")
    response_to_challenges: float = Field(..., description="对挑战的响应", ge=0, le=1)
    social_engagement: float = Field(..., description="社交参与度", ge=0, le=1)
    intrinsic_motivation_score: float = Field(
        ..., description="内在动机评分", ge=0, le=1
    )
    extrinsic_motivation_score: float = Field(
        ..., description="外在动机评分", ge=0, le=1
    )

    class Config:
        from_attributes = True
