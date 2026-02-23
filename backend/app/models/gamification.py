import enum

from sqlalchemy import (
    JSON,
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


class BadgeCategory(str, enum.Enum):
    """徽章类别枚举"""

    WEIGHT_LOSS = "weight_loss"
    HABIT_MASTERY = "habit_mastery"
    NUTRITION = "nutrition"
    EMOTIONAL_WELLNESS = "emotional_wellness"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SOCIAL = "social"
    SPECIAL = "special"


class BadgeLevel(str, enum.Enum):
    """徽章等级枚举"""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class UserBadge(Base):
    """用户徽章模型"""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 徽章信息
    badge_id = Column(String(100), nullable=False)  # 徽章标识符
    badge_name = Column(String(200), nullable=False)
    badge_description = Column(Text)
    badge_category = Column(Enum(BadgeCategory), nullable=False)
    badge_level = Column(Enum(BadgeLevel), nullable=False)
    badge_icon = Column(String(500))  # 图标URL或emoji

    # 获得信息
    earned_at = Column(DateTime(timezone=True), nullable=False)
    earned_criteria = Column(Text)  # 获得条件描述
    progress_data = Column(JSON)  # 获得时的进度数据

    # 展示设置
    is_showcased = Column(Boolean, default=False)  # 是否展示在资料中
    showcase_order = Column(Integer, default=0)  # 展示顺序

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge={self.badge_name})>"


class UserPoints(Base):
    """用户积分模型"""

    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # 积分信息
    total_points = Column(Integer, default=0)
    current_points = Column(Integer, default=0)  # 可用积分
    lifetime_points = Column(Integer, default=0)  # 历史总积分

    # 积分细分
    nutrition_points = Column(Integer, default=0)
    habit_points = Column(Integer, default=0)
    emotional_points = Column(Integer, default=0)
    login_points = Column(Integer, default=0)
    achievement_points = Column(Integer, default=0)

    # 时间戳
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserPoints(id={self.id}, user_id={self.user_id}, total={self.total_points})>"


class PointsTransaction(Base):
    """积分交易记录模型"""

    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 交易信息
    points_amount = Column(Integer, nullable=False)  # 正数为获得，负数为消耗
    transaction_type = Column(String(100), nullable=False)  # 交易类型
    description = Column(Text)
    reference_id = Column(String(100))  # 关联记录ID
    reference_type = Column(String(100))  # 关联记录类型

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<PointsTransaction(id={self.id}, user_id={self.user_id}, amount={self.points_amount})>"


class UserLevel(Base):
    """用户等级模型"""

    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # 等级信息
    current_level = Column(Integer, default=1)
    current_title = Column(String(100), default="新手")
    experience_points = Column(Integer, default=0)
    points_to_next_level = Column(Integer, default=100)

    # 等级历史
    level_up_count = Column(Integer, default=0)
    last_level_up = Column(DateTime(timezone=True))

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserLevel(id={self.id}, user_id={self.user_id}, level={self.current_level})>"


class Achievement(Base):
    """成就模型"""

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 成就信息
    achievement_id = Column(String(100), nullable=False)
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(Text)
    achievement_category = Column(String(100))

    # 进度信息
    target_value = Column(Integer, nullable=False)  # 目标值
    current_value = Column(Integer, default=0)  # 当前值
    progress_percentage = Column(Float, default=0.0)  # 进度百分比

    # 状态
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))

    # 奖励
    points_reward = Column(Integer, default=0)
    badge_reward = Column(String(100))  # 奖励徽章ID

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, name={self.achievement_name})>"


class Challenge(Base):
    """挑战模型"""

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 挑战信息
    challenge_id = Column(String(100), nullable=False)
    challenge_name = Column(String(200), nullable=False)
    challenge_description = Column(Text)
    challenge_type = Column(String(100))  # 挑战类型

    # 时间设置
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_days = Column(Integer, nullable=False)

    # 目标设置
    target_metric = Column(String(100))  # 目标指标
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)

    # 状态
    status = Column(
        String(50), default="active"
    )  # active, completed, failed, abandoned
    completed_at = Column(DateTime(timezone=True))

    # 奖励
    points_reward = Column(Integer, default=0)
    badge_reward = Column(String(100))

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<Challenge(id={self.id}, user_id={self.user_id}, name={self.challenge_name})>"


class StreakRecord(Base):
    """连续记录模型"""

    __tablename__ = "streak_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 连续记录信息
    streak_type = Column(String(100), nullable=False)  # 连续类型
    streak_name = Column(String(200), nullable=False)

    # 连续数据
    current_streak = Column(Integer, default=0)  # 当前连续天数
    longest_streak = Column(Integer, default=0)  # 最长连续天数
    streak_start_date = Column(DateTime(timezone=True))
    last_activity_date = Column(DateTime(timezone=True))

    # 里程碑
    milestones_reached = Column(JSON, default=list)  # 达到的里程碑

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<StreakRecord(id={self.id}, user_id={self.user_id}, type={self.streak_type})>"


class LeaderboardEntry(Base):
    """排行榜条目模型"""

    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 排行榜信息
    leaderboard_type = Column(String(100), nullable=False)  # 排行榜类型
    period = Column(String(50), nullable=False)  # 周期: weekly, monthly, all_time

    # 排名信息
    rank = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    previous_rank = Column(Integer)
    rank_change = Column(Integer, default=0)  # 排名变化

    # 统计信息
    total_users = Column(Integer)
    percentile = Column(Float)  # 百分位

    # 时间戳
    calculated_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<LeaderboardEntry(id={self.id}, user_id={self.user_id}, rank={self.rank})>"
