"""
目标追踪数据模型
Story 1.6: 目标数据模型
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class GoalType(str, Enum):
    """目标类型枚举"""

    WEIGHT = "weight"  # 体重目标
    EXERCISE = "exercise"  # 运动目标
    DIET = "diet"  # 饮食目标
    HABIT = "habit"  # 习惯目标


class GoalStatus(str, Enum):
    """目标状态枚举"""

    ACTIVE = "active"  # 进行中
    COMPLETED = "completed"  # 已完成
    PAUSED = "paused"  # 已暂停
    CANCELLED = "cancelled"  # 已取消


class UserGoal(Base):
    """
    用户目标模型
    支持 4 维度目标追踪：体重/运动/饮食/习惯
    """

    __tablename__ = "user_goals"
    # P1-4: 添加数据验证约束
    __table_args__ = (
        CheckConstraint(
            "current_value >= 0 OR current_value IS NULL",
            name="check_current_value_non_negative",
        ),
        CheckConstraint("target_value > 0", name="check_target_value_positive"),
    )

    # 主键
    goal_id = Column(Integer, primary_key=True, index=True)

    # 外键
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 目标基本信息
    goal_type = Column(String(50), nullable=False, index=True)  # GoalType
    current_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # kg, steps, kcal, hours, etc.

    # 时间信息
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True), nullable=True)
    predicted_date = Column(DateTime(timezone=True), nullable=True)

    # 状态
    status = Column(String(20), default="active")  # GoalStatus

    # 关系
    user = relationship("User", back_populates="goals")
    progress = relationship(
        "GoalProgress", back_populates="goal", cascade="all, delete-orphan"
    )
    history = relationship(
        "GoalHistory", back_populates="goal", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UserGoal(goal_id={self.goal_id}, user_id={self.user_id}, type={self.goal_type}, status={self.status})>"


class GoalProgress(Base):
    """
    目标进度记录
    记录每次目标的进展数据
    """

    __tablename__ = "goal_progress"

    # 主键
    progress_id = Column(Integer, primary_key=True, index=True)

    # 外键
    goal_id = Column(
        Integer, ForeignKey("user_goals.goal_id"), nullable=False, index=True
    )

    # 进度数据
    recorded_date = Column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    value = Column(Float, nullable=False)
    daily_target_met = Column(Boolean, default=False)
    streak_count = Column(Integer, default=0)

    # 关系
    goal = relationship("UserGoal", back_populates="progress")

    def __repr__(self):
        return f"<GoalProgress(progress_id={self.progress_id}, goal_id={self.goal_id}, value={self.value})>"


class GoalHistory(Base):
    """
    目标变更历史
    记录目标的所有变更，支持追溯和审计
    """

    __tablename__ = "goal_history"

    # 主键
    history_id = Column(Integer, primary_key=True, index=True)

    # 外键
    goal_id = Column(
        Integer, ForeignKey("user_goals.goal_id"), nullable=False, index=True
    )

    # 变更信息
    change_type = Column(
        String(50), nullable=False
    )  # created, updated, completed, paused, cancelled, resumed
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=False)
    reason = Column(Text, nullable=True)
    ai_suggested = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    goal = relationship("UserGoal", back_populates="history")

    def __repr__(self):
        return f"<GoalHistory(history_id={self.history_id}, goal_id={self.goal_id}, type={self.change_type})>"
