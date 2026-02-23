"""记忆系统数据库模型"""

import json

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserLongTermMemory(Base):
    """用户长期记忆表"""

    __tablename__ = "user_long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 记忆类型和键
    memory_type = Column(
        String(50), nullable=False
    )  # 'health_trend', 'habit_pattern', 'milestone', 'preference'
    memory_key = Column(String(200), nullable=False)  # 记忆键，如 'weight_trend_30d'

    # 记忆值（JSON格式存储）
    memory_value = Column(Text, nullable=False)

    # 重要性评分和访问记录
    importance_score = Column(Float, default=1.0)
    last_accessed = Column(DateTime(timezone=True))

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    user = relationship("User", back_populates="long_term_memories")

    def __repr__(self):
        return f"<UserLongTermMemory(id={self.id}, user_id={self.user_id}, type={self.memory_type}, key={self.memory_key})>"

    def get_memory_value(self):
        """获取解析后的记忆值"""
        try:
            return json.loads(self.memory_value)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_memory_value(self, value):
        """设置记忆值（自动序列化为JSON）"""
        if isinstance(value, dict):
            self.memory_value = json.dumps(value, ensure_ascii=False)
        else:
            self.memory_value = str(value)


class ContextSummary(Base):
    """上下文摘要表"""

    __tablename__ = "context_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 摘要类型和周期
    summary_type = Column(
        String(50), nullable=False
    )  # 'daily', 'weekly', 'conversation'
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # 摘要内容
    summary_text = Column(Text, nullable=False)

    # 结构化数据（JSON格式存储）
    key_insights = Column(Text)  # 关键洞察
    data_sources = Column(Text)  # 数据来源

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="context_summaries")

    def __repr__(self):
        return f"<ContextSummary(id={self.id}, user_id={self.user_id}, type={self.summary_type}, period={self.period_start} to {self.period_end})>"

    def get_key_insights(self):
        """获取解析后的关键洞察"""
        try:
            return json.loads(self.key_insights) if self.key_insights else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_key_insights(self, insights):
        """设置关键洞察（自动序列化为JSON）"""
        if isinstance(insights, list):
            self.key_insights = json.dumps(insights, ensure_ascii=False)
        else:
            self.key_insights = str(insights)

    def get_data_sources(self):
        """获取解析后的数据来源"""
        try:
            return json.loads(self.data_sources) if self.data_sources else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_data_sources(self, sources):
        """设置数据来源（自动序列化为JSON）"""
        if isinstance(sources, list):
            self.data_sources = json.dumps(sources, ensure_ascii=False)
        else:
            self.data_sources = str(sources)


class HabitPattern(Base):
    """习惯模式表"""

    __tablename__ = "habit_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    habit_id = Column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    # 模式类型和数据
    pattern_type = Column(
        String(50), nullable=False
    )  # 'weekly', 'time_based', 'trigger_based'
    pattern_data = Column(Text, nullable=False)  # 模式数据（JSON格式）

    # 统计信息
    confidence_score = Column(Float, default=0.0)  # 置信度 0-1
    first_detected = Column(Date, nullable=False)
    last_observed = Column(Date, nullable=False)
    observation_count = Column(Integer, default=1)

    # 关系
    user = relationship("User", back_populates="habit_patterns")
    habit = relationship("Habit", back_populates="patterns")

    def __repr__(self):
        return f"<HabitPattern(id={self.id}, user_id={self.user_id}, habit_id={self.habit_id}, type={self.pattern_type}, confidence={self.confidence_score})>"

    def get_pattern_data(self):
        """获取解析后的模式数据"""
        try:
            return json.loads(self.pattern_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_pattern_data(self, data):
        """设置模式数据（自动序列化为JSON）"""
        if isinstance(data, dict):
            self.pattern_data = json.dumps(data, ensure_ascii=False)
        else:
            self.pattern_data = str(data)


class DataAssociation(Base):
    """数据关联表"""

    __tablename__ = "data_associations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 源数据
    source_type = Column(String(50), nullable=False)  # 'habit', 'health_record', 'mood'
    source_id = Column(Integer, nullable=False)

    # 目标数据
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)

    # 关联信息
    association_type = Column(
        String(50), nullable=False
    )  # 'causal', 'temporal', 'correlative'
    strength = Column(Float, default=0.0)  # 关联强度 0-1

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="data_associations")

    def __repr__(self):
        return f"<DataAssociation(id={self.id}, user_id={self.user_id}, source={self.source_type}:{self.source_id}, target={self.target_type}:{self.target_id}, strength={self.strength})>"
