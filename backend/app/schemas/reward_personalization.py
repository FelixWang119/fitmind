from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class AchievementRecommendation(BaseModel):
    """成就推荐"""

    achievement_id: int = Field(..., description="成就ID")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    reason: str = Field(..., description="推荐理由")
    estimated_difficulty: str = Field(
        ..., description="预估难度", examples=["easy", "medium", "hard"]
    )
    estimated_time_to_complete: str = Field(..., description="预估完成时间")
    confidence_score: float = Field(..., description="置信度", ge=0, le=1)

    class Config:
        from_attributes = True


class ChallengeRecommendation(BaseModel):
    """挑战推荐"""

    challenge_id: int = Field(..., description="挑战ID")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    challenge_type: str = Field(..., description="挑战类型")
    duration_days: int = Field(..., description="持续时间（天）")
    reward_points: int = Field(..., description="奖励积分")
    personalization_reason: str = Field(..., description="个性化理由")
    match_score: float = Field(..., description="匹配度", ge=0, le=1)

    class Config:
        from_attributes = True


class CustomizationRequest(BaseModel):
    """自定义请求"""

    preferences: Dict[str, Any] = Field(..., description="偏好设置")
    feedback: Optional[str] = Field(None, description="反馈")
    customization_type: str = Field(
        ...,
        description="自定义类型",
        examples=["notification", "challenge", "reward", "ui"],
    )

    class Config:
        from_attributes = True


class RewardPersonalizationResponse(BaseModel):
    """奖励个性化响应"""

    user_id: int = Field(..., description="用户ID")
    personalization_timestamp: str = Field(..., description="个性化时间戳")
    user_preferences: Dict[str, Any] = Field(..., description="用户偏好")
    achievement_recommendations: List[AchievementRecommendation] = Field(
        ..., description="成就推荐"
    )
    challenge_recommendations: List[ChallengeRecommendation] = Field(
        ..., description="挑战推荐"
    )
    reward_suggestions: List[str] = Field(..., description="奖励建议")
    engagement_strategies: List[str] = Field(..., description="参与策略")
    predicted_engagement_impact: float = Field(
        ..., description="预测参与度影响", ge=0, le=1
    )

    class Config:
        from_attributes = True


class UserMotivationProfile(BaseModel):
    """用户动机画像"""

    user_id: int = Field(..., description="用户ID")
    intrinsic_motivation_score: float = Field(
        ..., description="内在动机评分", ge=0, le=1
    )
    extrinsic_motivation_score: float = Field(
        ..., description="外在动机评分", ge=0, le=1
    )
    achievement_oriented: bool = Field(..., description="成就导向")
    social_oriented: bool = Field(..., description="社交导向")
    competition_oriented: bool = Field(..., description="竞争导向")
    learning_oriented: bool = Field(..., description="学习导向")
    preferred_reward_types: List[str] = Field(..., description="偏好奖励类型")
    avoidance_factors: List[str] = Field(..., description="回避因素")

    class Config:
        from_attributes = True


class EngagementOptimization(BaseModel):
    """参与度优化"""

    strategy: str = Field(..., description="策略")
    target_metric: str = Field(..., description="目标指标")
    expected_improvement: float = Field(..., description="预期改进", ge=0, le=1)
    implementation_complexity: str = Field(
        ..., description="实施复杂度", examples=["low", "medium", "high"]
    )
    timeframe: str = Field(
        ...,
        description="时间范围",
        examples=["immediate", "short_term", "medium_term", "long_term"],
    )

    class Config:
        from_attributes = True


class PersonalizedRecommendation(BaseModel):
    """个性化推荐"""

    recommendation_type: str = Field(..., description="推荐类型")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    reason: str = Field(..., description="理由")
    priority: str = Field(..., description="优先级", examples=["high", "medium", "low"])
    estimated_impact: float = Field(..., description="预估影响", ge=0, le=1)

    class Config:
        from_attributes = True


class PersonalizedRecommendationResponse(BaseModel):
    """个性化推荐响应"""

    user_id: int = Field(..., description="用户ID")
    recommendations: List[PersonalizedRecommendation] = Field(
        ..., description="推荐列表"
    )
    timestamp: str = Field(..., description="时间戳")
    confidence_score: float = Field(..., description="置信度", ge=0, le=1)

    class Config:
        from_attributes = True


class UserPreferenceProfile(BaseModel):
    """用户偏好画像"""

    user_id: int = Field(..., description="用户ID")
    preferred_challenge_types: List[str] = Field(..., description="偏好挑战类型")
    preferred_reward_types: List[str] = Field(..., description="偏好奖励类型")
    notification_preferences: Dict[str, bool] = Field(..., description="通知偏好")
    difficulty_preference: str = Field(
        ..., description="难度偏好", examples=["easy", "medium", "hard"]
    )
    time_commitment_preference: str = Field(
        ..., description="时间投入偏好", examples=["low", "medium", "high"]
    )

    class Config:
        from_attributes = True


class UserIncentiveProfileResponse(BaseModel):
    """用户激励画像响应"""

    user_id: int = Field(..., description="用户ID")
    motivation_type: str = Field(
        ..., description="动机类型", examples=["intrinsic", "extrinsic", "mixed"]
    )
    incentive_preferences: Dict[str, Any] = Field(..., description="激励偏好")
    engagement_patterns: List[str] = Field(..., description="参与模式")
    optimization_suggestions: List[str] = Field(..., description="优化建议")

    class Config:
        from_attributes = True


class TaskRecommendation(BaseModel):
    """任务推荐"""

    task_id: int = Field(..., description="任务ID")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    estimated_time_minutes: int = Field(..., description="预估时间（分钟）")
    difficulty: str = Field(
        ..., description="难度", examples=["easy", "medium", "hard"]
    )
    relevance_score: float = Field(..., description="相关性评分", ge=0, le=1)

    class Config:
        from_attributes = True


class RewardRecommendation(BaseModel):
    """奖励推荐"""

    reward_type: str = Field(..., description="奖励类型")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    points_value: int = Field(..., description="积分价值")
    unlock_conditions: List[str] = Field(..., description="解锁条件")
    personalization_reason: str = Field(..., description="个性化理由")

    class Config:
        from_attributes = True
