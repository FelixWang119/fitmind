import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


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


class EmotionalState(Base):
    """情感状态模型"""

    __tablename__ = "emotional_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 情感状态
    emotion_type = Column(Enum(EmotionType), nullable=False)
    intensity = Column(Integer, nullable=False)  # 强度 1-10
    description = Column(Text)  # 描述

    # 触发因素
    trigger = Column(String(500))  # 触发因素
    context = Column(Text)  # 上下文

    # 时间戳
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<EmotionalState(id={self.id}, user_id={self.user_id}, emotion={self.emotion_type.value})>"


class EmotionalSupport(Base):
    """情感支持记录模型"""

    __tablename__ = "emotional_supports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 支持内容
    support_type = Column(Enum(SupportType), nullable=False)
    message = Column(Text, nullable=False)  # 支持消息
    suggested_action = Column(Text)  # 建议行动
    resources = Column(Text)  # 资源链接或建议

    # 效果评估
    helpfulness_rating = Column(Integer)  # 有帮助程度 1-5
    emotional_impact = Column(Integer)  # 情感影响 1-5

    # 时间戳
    provided_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<EmotionalSupport(id={self.id}, user_id={self.user_id}, type={self.support_type.value})>"


class StressLevel(Base):
    """压力水平模型"""

    __tablename__ = "stress_levels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 压力评估
    stress_level = Column(Integer, nullable=False)  # 压力水平 1-10
    physical_symptoms = Column(Text)  # 身体症状
    emotional_symptoms = Column(Text)  # 情感症状
    cognitive_symptoms = Column(Text)  # 认知症状

    # 压力源
    stressors = Column(Text)  # 压力源
    coping_strategies = Column(Text)  # 应对策略

    # 时间戳
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<StressLevel(id={self.id}, user_id={self.user_id}, level={self.stress_level})>"


class GratitudeJournal(Base):
    """感恩日记模型"""

    __tablename__ = "gratitude_journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 感恩内容
    entry = Column(Text, nullable=False)  # 感恩条目
    category = Column(String(100))  # 类别: health, relationships, work, etc.
    intensity = Column(Integer)  # 感恩强度 1-5

    # 情感影响
    mood_before = Column(Integer)  # 记录前心情 1-5
    mood_after = Column(Integer)  # 记录后心情 1-5

    # 时间戳
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<GratitudeJournal(id={self.id}, user_id={self.user_id})>"


class PositiveAffirmation(Base):
    """积极肯定语模型"""

    __tablename__ = "positive_affirmations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 肯定语内容
    affirmation = Column(Text, nullable=False)  # 肯定语
    category = Column(String(100))  # 类别: self_worth, health, growth, etc.
    personalized = Column(Boolean, default=False)  # 是否个性化

    # 使用情况
    times_used = Column(Integer, default=0)  # 使用次数
    last_used = Column(DateTime(timezone=True))  # 最后使用时间
    effectiveness = Column(Integer)  # 有效性 1-5

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<PositiveAffirmation(id={self.id}, user_id={self.user_id})>"


class MindfulnessExercise(Base):
    """正念练习模型"""

    __tablename__ = "mindfulness_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 练习信息
    exercise_type = Column(String(100), nullable=False)  # 练习类型
    duration_minutes = Column(Integer, nullable=False)  # 持续时间(分钟)
    focus_area = Column(String(200))  # 关注区域

    # 体验反馈
    difficulty_level = Column(Integer)  # 难度级别 1-5
    relaxation_level = Column(Integer)  # 放松程度 1-5
    focus_level = Column(Integer)  # 专注程度 1-5
    notes = Column(Text)  # 备注

    # 时间戳
    completed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<MindfulnessExercise(id={self.id}, user_id={self.user_id}, type={self.exercise_type})>"
