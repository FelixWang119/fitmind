"""
情感支持模块占位符
Note: This is a placeholder - actual implementation needed
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class EmotionalState:
    """情感状态枚举"""

    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    CALM = "calm"
    STRESSED = "stressed"
    RELAXED = "relaxed"


class StressLevel:
    """压力水平枚举"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class EmotionalSupport(Base):
    """
    情感支持记录 (占位符)
    需要实现完整的情感支持功能
    """

    __tablename__ = "emotional_support"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    state = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EmotionalSupport(id={self.id}, user_id={self.user_id}, state={self.state})>"
