import enum
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class EmotionType(str, enum.Enum):
    """情感类型枚举"""

    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    MOTIVATED = "motivated"
    TIRED = "tired"
    FRUSTRATED = "frustrated"
    PEACEFUL = "peaceful"
    NEUTRAL = "neutral"


class SupportType(str, enum.Enum):
    """支持类型枚举"""

    ENCOURAGEMENT = "encouragement"
    VALIDATION = "validation"
    PROBLEM_SOLVING = "problem_solving"
    MINDFULNESS = "mindfulness"
    GRATITUDE = "gratitude"
    PERSPECTIVE_SHIFT = "perspective_shift"
    SELF_COMPASSION = "self_compassion"


class EmotionalStateBase(BaseModel):
    """情感状态基础模型"""

    emotion_type: EmotionType = Field(..., description="情感类型")
    intensity: int = Field(..., ge=1, le=10, description="强度 1-10")
    description: Optional[str] = Field(None, description="描述")
    trigger: Optional[str] = Field(None, max_length=500, description="触发因素")
    context: Optional[str] = Field(None, description="上下文")
    recorded_at: datetime = Field(..., description="记录时间")


class EmotionalStateCreate(EmotionalStateBase):
    """创建情感状态"""

    pass


class EmotionalStateInDB(EmotionalStateBase):
    """数据库中的情感状态"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class EmotionalSupportBase(BaseModel):
    """情感支持基础模型"""

    support_type: SupportType = Field(..., description="支持类型")
    message: str = Field(..., description="支持消息")
    suggested_action: Optional[str] = Field(None, description="建议行动")
    resources: Optional[str] = Field(None, description="资源")
    helpfulness_rating: Optional[int] = Field(None, ge=1, le=5, description="有帮助程度 1-5")
    emotional_impact: Optional[int] = Field(None, ge=1, le=5, description="情感影响 1-5")
    provided_at: datetime = Field(..., description="提供时间")


class EmotionalSupportCreate(EmotionalSupportBase):
    """创建情感支持记录"""

    pass


class EmotionalSupportInDB(EmotionalSupportBase):
    """数据库中的情感支持记录"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class StressLevelBase(BaseModel):
    """压力水平基础模型"""

    stress_level: int = Field(..., ge=1, le=10, description="压力水平 1-10")
    physical_symptoms: Optional[str] = Field(None, description="身体症状")
    emotional_symptoms: Optional[str] = Field(None, description="情感症状")
    cognitive_symptoms: Optional[str] = Field(None, description="认知症状")
    stressors: Optional[str] = Field(None, description="压力源")
    coping_strategies: Optional[str] = Field(None, description="应对策略")
    recorded_at: datetime = Field(..., description="记录时间")


class StressLevelCreate(StressLevelBase):
    """创建压力水平记录"""

    pass


class StressLevelInDB(StressLevelBase):
    """数据库中的压力水平记录"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class GratitudeJournalBase(BaseModel):
    """感恩日记基础模型"""

    entry: str = Field(..., description="感恩条目")
    category: Optional[str] = Field(None, max_length=100, description="类别")
    intensity: Optional[int] = Field(None, ge=1, le=5, description="感恩强度 1-5")
    mood_before: Optional[int] = Field(None, ge=1, le=5, description="记录前心情 1-5")
    mood_after: Optional[int] = Field(None, ge=1, le=5, description="记录后心情 1-5")
    recorded_at: datetime = Field(..., description="记录时间")


class GratitudeJournalCreate(GratitudeJournalBase):
    """创建感恩日记"""

    pass


class GratitudeJournalInDB(GratitudeJournalBase):
    """数据库中的感恩日记"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class PositiveAffirmationBase(BaseModel):
    """积极肯定语基础模型"""

    affirmation: str = Field(..., description="肯定语")
    category: Optional[str] = Field(None, max_length=100, description="类别")
    personalized: bool = Field(default=False, description="是否个性化")


class PositiveAffirmationCreate(PositiveAffirmationBase):
    """创建积极肯定语"""

    pass


class PositiveAffirmationInDB(PositiveAffirmationBase):
    """数据库中的积极肯定语"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    times_used: int = Field(..., description="使用次数")
    last_used: Optional[datetime] = Field(None, description="最后使用时间")
    effectiveness: Optional[int] = Field(None, ge=1, le=5, description="有效性 1-5")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class MindfulnessExerciseBase(BaseModel):
    """正念练习基础模型"""

    exercise_type: str = Field(..., max_length=100, description="练习类型")
    duration_minutes: int = Field(..., ge=1, description="持续时间(分钟)")
    focus_area: Optional[str] = Field(None, max_length=200, description="关注区域")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="难度级别 1-5")
    relaxation_level: Optional[int] = Field(None, ge=1, le=5, description="放松程度 1-5")
    focus_level: Optional[int] = Field(None, ge=1, le=5, description="专注程度 1-5")
    notes: Optional[str] = Field(None, description="备注")
    completed_at: datetime = Field(..., description="完成时间")


class MindfulnessExerciseCreate(MindfulnessExerciseBase):
    """创建正念练习记录"""

    pass


class MindfulnessExerciseInDB(MindfulnessExerciseBase):
    """数据库中的正念练习记录"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class EmotionalInsight(BaseModel):
    """情感洞察"""

    emotion_trend: Dict[str, int] = Field(..., description="情感趋势")
    dominant_emotion: EmotionType = Field(..., description="主导情感")
    stress_trend: List[int] = Field(..., description="压力趋势")
    avg_stress_level: float = Field(..., description="平均压力水平")
    coping_effectiveness: float = Field(..., description="应对策略有效性")
    gratitude_frequency: int = Field(..., description="感恩记录频率")
    mindfulness_practice: int = Field(..., description="正念练习次数")


class SupportRecommendation(BaseModel):
    """支持建议"""

    support_type: SupportType = Field(..., description="建议的支持类型")
    message: str = Field(..., description="建议消息")
    rationale: str = Field(..., description="建议理由")
    suggested_actions: List[str] = Field(..., description="建议行动")
    resources: List[str] = Field(..., description="资源")


class EmotionalCheckIn(BaseModel):
    """情感签到"""

    current_emotion: EmotionType = Field(..., description="当前情感")
    intensity: int = Field(..., ge=1, le=10, description="强度")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="压力水平")
    needs_support: bool = Field(..., description="是否需要支持")
    support_recommendation: Optional[SupportRecommendation] = Field(
        None, description="支持建议"
    )


class DailyEmotionalSummary(BaseModel):
    """每日情感总结"""

    date: str = Field(..., description="日期")
    emotional_states: List[EmotionalStateInDB] = Field(..., description="情感状态记录")
    stress_levels: List[StressLevelInDB] = Field(..., description="压力水平记录")
    gratitude_entries: List[GratitudeJournalInDB] = Field(..., description="感恩日记")
    mindfulness_exercises: List[MindfulnessExerciseInDB] = Field(
        ..., description="正念练习"
    )
    emotional_insight: EmotionalInsight = Field(..., description="情感洞察")


class CopingStrategy(BaseModel):
    """应对策略"""

    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    category: str = Field(..., description="类别")
    duration_minutes: int = Field(..., description="建议持续时间(分钟)")
    difficulty: str = Field(..., description="难度")
    effectiveness_rating: float = Field(..., description="有效性评分")


class EmotionalWellnessPlan(BaseModel):
    """情感健康计划"""

    daily_practices: List[str] = Field(..., description="每日练习")
    weekly_goals: List[str] = Field(..., description="每周目标")
    coping_strategies: List[CopingStrategy] = Field(..., description="应对策略")
    support_resources: List[str] = Field(..., description="支持资源")
    progress_tracking: Dict[str, float] = Field(..., description="进度跟踪")
