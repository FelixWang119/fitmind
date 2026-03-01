import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HabitFrequency(enum.Enum):
    """习惯频率枚举"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class HabitCategory(enum.Enum):
    """习惯类别枚举"""

    DIET = "DIET"
    EXERCISE = "EXERCISE"
    SLEEP = "SLEEP"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    HYDRATION = "HYDRATION"
    OTHER = "OTHER"


class Habit(Base):
    """习惯模型"""

    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 习惯基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 改为 String 以支持 SQLite
    frequency = Column(String(50), nullable=False, default="daily")  # 改为 String

    # 目标设置
    target_value = Column(Integer)  # 目标值（如：每天8杯水）
    target_unit = Column(String(50))  # 单位（如：cups, minutes, times）

    # 时间设置
    preferred_time = Column(String(50))  # 偏好时间（如：morning, afternoon, evening）
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(String(50))  # 提醒时间（HH:MM格式）

    # 状态
    is_active = Column(Boolean, default=True)
    streak_days = Column(Integer, default=0)  # 连续天数
    total_completions = Column(Integer, default=0)  # 总完成次数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="habits")
    completions = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan"
    )
    # Note: patterns relation commented out as it causes import issues
    patterns = relationship(
        "HabitPattern", back_populates="habit", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Habit(id={self.id}, user_id={self.user_id}, name={self.name})>"


class HabitCompletion(Base):
    """习惯完成记录模型"""

    __tablename__ = "habit_completions"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    # 完成信息
    completion_date = Column(DateTime(timezone=True), nullable=False)
    actual_value = Column(Integer)  # 实际完成值
    notes = Column(Text)  # 备注

    # 情绪反馈
    mood_rating = Column(Integer)  # 心情评分 1-5
    difficulty_rating = Column(Integer)  # 难度评分 1-5

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    habit = relationship("Habit", back_populates="completions")

    def __repr__(self):
        return f"<HabitCompletion(id={self.id}, habit_id={self.habit_id}, date={self.completion_date})>"


class HabitGoalType(enum.Enum):
    """习惯目标类型枚举"""

    COMPLETION_RATE = "completion_rate"
    STREAK = "streak"
    TOTAL_COUNT = "total_count"


class HabitGoalPeriod(enum.Enum):
    """习惯目标周期枚举"""

    WEEKLY = "weekly"
    MONTHLY = "monthly"


class HabitGoal(Base):
    """习惯目标模型"""

    __tablename__ = "habit_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    habit_id = Column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    # 目标信息
    goal_type = Column(String(50), nullable=False)  # completion_rate/streak/total_count
    target_value = Column(Integer, nullable=False)  # 目标值
    period = Column(String(50), nullable=False)  # weekly/monthly

    # 时间范围
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # 状态
    is_active = Column(Boolean, default=True)
    is_achieved = Column(Boolean, default=False)
    current_progress = Column(Integer, default=0)  # 当前进度

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="habit_goals")
    habit = relationship("Habit", back_populates="goals")

    def __repr__(self):
        return f"<HabitGoal(id={self.id}, habit_id={self.habit_id}, goal_type={self.goal_type}, target_value={self.target_value})>"


# Add goals relationship to Habit model
Habit.goals = relationship(
    "HabitGoal", back_populates="habit", cascade="all, delete-orphan"
)
