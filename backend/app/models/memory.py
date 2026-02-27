"""记忆系统数据库模型"""

import json
import uuid
from typing import List, Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Index,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


# 使用 JSON 类型代替 JSONB，兼容 SQLite 和 PostgreSQL
# PostgreSQL 会自动将 JSON 映射为 JSONB
JsonType = JSON

# pgvector 向量维度
EMBEDDING_DIM = 768


class UnifiedMemory(Base):
    """统一记忆模型 - 长期记忆的核心存储"""

    __tablename__ = "unified_memory"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 记忆内容
    memory_type = Column(
        String(50), nullable=False, index=True
    )  # '打卡_pattern', '偏好_inferred', '目标_explicit', '习惯_completed', '里程碑_achieved', '趋势_insight', '关联_causal'
    content_raw = Column(Text)  # 原始内容（可选）
    content_summary = Column(Text, nullable=False)  # LLM 摘要（核心内容）
    content_keywords = Column(JsonType, default=list)  # 关键词（可检索）

    # 向量存储 - 使用 pgvector
    embedding_legacy = Column(
        Text, nullable=True
    )  # 旧字段：向量数据，存储为 JSON 字符串（迁移期间保留）
    embedding = Column(
        Vector(EMBEDDING_DIM), nullable=True
    )  # 新字段：pgvector VECTOR 类型

    # 来源信息
    source_type = Column(
        String(50), nullable=False, index=True
    )  # 'habit_record', 'conversation', 'health_record', 'meal_record', 'exercise_record'
    source_id = Column(String(100), nullable=False)  # 来源数据ID（可追溯）

    # 元数据
    importance_score = Column(Float, default=5.0)  # 重要性评分 (0-10)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_accessed = Column(DateTime(timezone=True))

    # 状态
    is_active = Column(Boolean, default=True, index=True)
    is_indexed = Column(Boolean, default=False, index=True)

    # 关系
    user = relationship("User", back_populates="unified_memories")

    # 索引
    __table_args__ = (
        # 单字段索引
        Index("idx_unified_memory_user_id", "user_id"),
        Index("idx_unified_memory_memory_type", "memory_type"),
        Index("idx_unified_memory_source_type", "source_type"),
        Index("idx_unified_memory_created_at", "created_at"),
        Index("idx_unified_memory_is_active", "is_active"),
        # 复合索引 - 优化常用查询模式
        Index("idx_unified_memory_user_type", "user_id", "memory_type"),
        Index("idx_unified_memory_user_active", "user_id", "is_active"),
        # 关键查询优化：获取用户活跃记忆（按时间排序）
        Index(
            "idx_unified_memory_user_active_created",
            "user_id",
            "is_active",
            "created_at",
        ),
        # 关键查询优化：按来源追溯
        Index(
            "idx_unified_memory_source",
            "source_type",
            "source_id",
        ),
    )

    def __repr__(self):
        return f"<UnifiedMemory(id={self.id}, user_id={self.user_id}, type={self.memory_type})>"

    def get_embedding(self) -> Optional[List[float]]:
        """获取解析后的向量 - 优先使用新的 Vector 字段"""
        # 优先使用新的 pgvector 字段
        if self.embedding is not None:
            # pgvector 的 Vector 类型返回 array 或 list
            if isinstance(self.embedding, (list, tuple)):
                return list(self.embedding)
            return self.embedding

        # 回退到旧字段（兼容迁移期间）
        if self.embedding_legacy:
            try:
                return json.loads(self.embedding_legacy)
            except (json.JSONDecodeError, TypeError):
                return None

        return None

    def set_embedding(self, vector: List[float]):
        """设置向量 - 同时写入新字段（pgvector）和旧字段（兼容）"""
        if vector:
            # 新字段使用 pgvector 类型
            self.embedding = vector
            # 旧字段保留 JSON 格式（向后兼容）
            self.embedding_legacy = json.dumps(vector)
        else:
            self.embedding = None
            self.embedding_legacy = None

    def get_keywords(self) -> List[str]:
        """获取解析后的关键词"""
        if not self.content_keywords:
            return []
        if isinstance(self.content_keywords, list):
            return self.content_keywords
        try:
            return (
                json.loads(self.content_keywords)
                if isinstance(self.content_keywords, str)
                else []
            )
        except (json.JSONDecodeError, TypeError):
            return []

    def set_keywords(self, keywords: List[str]):
        """设置关键词"""
        self.content_keywords = keywords


class MemoryIndexLog(Base):
    """记忆索引日志 - 追踪记忆的生命周期和索引状态"""

    __tablename__ = "memory_index_log"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_id = Column(
        PGUUID(as_uuid=True), ForeignKey("unified_memory.id", ondelete="CASCADE")
    )
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(100), nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 索引状态
    status = Column(
        String(20), default="pending", index=True
    )  # pending / indexed / failed
    indexed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    memory = relationship("UnifiedMemory")

    def __repr__(self):
        return f"<MemoryIndexLog(id={self.id}, memory_id={self.memory_id}, status={self.status})>"


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
