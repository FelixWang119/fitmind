from datetime import datetime
from typing import Dict, List, Optional
import enum

from pydantic import BaseModel, Field


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


class BadgeBase(BaseModel):
    """徽章基础模型"""

    badge_id: str = Field(..., description="徽章标识符")
    badge_name: str = Field(..., description="徽章名称")
    badge_description: str = Field(..., description="徽章描述")
    badge_category: BadgeCategory = Field(..., description="徽章类别")
    badge_level: BadgeLevel = Field(..., description="徽章等级")
    badge_icon: str = Field(..., description="徽章图标")


class UserBadgeCreate(BaseModel):
    """创建用户徽章"""

    badge_id: str = Field(..., description="徽章标识符")
    badge_name: str = Field(..., description="徽章名称")
    badge_description: Optional[str] = Field(None, description="徽章描述")
    badge_category: BadgeCategory = Field(..., description="徽章类别")
    badge_level: BadgeLevel = Field(..., description="徽章等级")
    badge_icon: str = Field(..., description="徽章图标")
    earned_criteria: Optional[str] = Field(None, description="获得条件")
    progress_data: Optional[Dict] = Field(None, description="进度数据")


class UserBadgeInDB(BadgeBase):
    """数据库中的用户徽章"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    earned_at: datetime = Field(..., description="获得时间")
    earned_criteria: Optional[str] = Field(None, description="获得条件")
    progress_data: Optional[Dict] = Field(None, description="进度数据")
    is_showcased: bool = Field(default=False, description="是否展示")
    showcase_order: int = Field(default=0, description="展示顺序")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class PointsBreakdown(BaseModel):
    """积分细分"""

    nutrition_points: int = Field(..., description="营养积分")
    habit_points: int = Field(..., description="习惯积分")
    emotional_points: int = Field(..., description="情感积分")
    login_points: int = Field(..., description="登录积分")
    achievement_points: int = Field(..., description="成就积分")


class UserPointsBase(BaseModel):
    """用户积分基础模型"""

    total_points: int = Field(..., description="总积分")
    current_points: int = Field(..., description="可用积分")
    lifetime_points: int = Field(..., description="历史总积分")


class UserPointsInDB(UserPointsBase):
    """数据库中的用户积分"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    breakdown: PointsBreakdown = Field(..., description="积分细分")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class PointsTransactionBase(BaseModel):
    """积分交易基础模型"""

    points_amount: int = Field(..., description="积分数量（正获得，负消耗）")
    transaction_type: str = Field(..., description="交易类型")
    description: Optional[str] = Field(None, description="描述")


class PointsTransactionInDB(PointsTransactionBase):
    """数据库中的积分交易"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    reference_id: Optional[str] = Field(None, description="关联记录ID")
    reference_type: Optional[str] = Field(None, description="关联记录类型")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class UserLevelBase(BaseModel):
    """用户等级基础模型"""

    current_level: int = Field(..., description="当前等级")
    current_title: str = Field(..., description="当前称号")
    experience_points: int = Field(..., description="经验值")
    points_to_next_level: int = Field(..., description="升级所需积分")


class UserLevelInDB(UserLevelBase):
    """数据库中的用户等级"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    level_up_count: int = Field(..., description="升级次数")
    last_level_up: Optional[datetime] = Field(None, description="最后升级时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class LevelProgress(BaseModel):
    """等级进度"""

    current_level: int = Field(..., description="当前等级")
    current_title: str = Field(..., description="当前称号")
    experience_points: int = Field(..., description="当前经验值")
    points_to_next_level: int = Field(..., description="升级所需积分")
    progress_percentage: float = Field(..., description="进度百分比")
    next_level_title: Optional[str] = Field(None, description="下一级称号")


class AchievementBase(BaseModel):
    """成就基础模型"""

    achievement_id: str = Field(..., description="成就标识符")
    achievement_name: str = Field(..., description="成就名称")
    achievement_description: Optional[str] = Field(None, description="成就描述")
    achievement_category: Optional[str] = Field(None, description="成就类别")


class AchievementCreate(AchievementBase):
    """创建成就"""

    target_value: int = Field(..., description="目标值")
    points_reward: int = Field(default=0, description="积分奖励")
    badge_reward: Optional[str] = Field(None, description="徽章奖励")


class AchievementInDB(AchievementBase):
    """数据库中的成就"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    target_value: int = Field(..., description="目标值")
    current_value: int = Field(..., description="当前值")
    progress_percentage: float = Field(..., description="进度百分比")
    is_completed: bool = Field(..., description="是否完成")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    points_reward: int = Field(..., description="积分奖励")
    badge_reward: Optional[str] = Field(None, description="徽章奖励")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class ChallengeBase(BaseModel):
    """挑战基础模型"""

    challenge_id: str = Field(..., description="挑战标识符")
    challenge_name: str = Field(..., description="挑战名称")
    challenge_description: Optional[str] = Field(None, description="挑战描述")
    challenge_type: Optional[str] = Field(None, description="挑战类型")


class ChallengeCreate(ChallengeBase):
    """创建挑战"""

    duration_days: int = Field(..., description="持续时间(天)")
    target_metric: str = Field(..., description="目标指标")
    target_value: int = Field(..., description="目标值")
    points_reward: int = Field(default=0, description="积分奖励")


class ChallengeInDB(ChallengeBase):
    """数据库中的挑战"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    duration_days: int = Field(..., description="持续时间(天)")
    target_metric: str = Field(..., description="目标指标")
    target_value: int = Field(..., description="目标值")
    current_value: int = Field(..., description="当前值")
    status: str = Field(..., description="状态")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    points_reward: int = Field(..., description="积分奖励")
    badge_reward: Optional[str] = Field(None, description="徽章奖励")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class StreakRecordBase(BaseModel):
    """连续记录基础模型"""

    streak_type: str = Field(..., description="连续类型")
    streak_name: str = Field(..., description="连续记录名称")


class StreakRecordInDB(StreakRecordBase):
    """数据库中的连续记录"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    current_streak: int = Field(..., description="当前连续天数")
    longest_streak: int = Field(..., description="最长连续天数")
    streak_start_date: Optional[datetime] = Field(None, description="连续开始日期")
    last_activity_date: Optional[datetime] = Field(None, description="最后活动日期")
    milestones_reached: List[int] = Field(default=[], description="达到的里程碑")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class LeaderboardEntryBase(BaseModel):
    """排行榜条目基础模型"""

    leaderboard_type: str = Field(..., description="排行榜类型")
    period: str = Field(..., description="周期")
    rank: int = Field(..., description="排名")
    score: int = Field(..., description="分数")


class LeaderboardEntryInDB(LeaderboardEntryBase):
    """数据库中的排行榜条目"""

    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="用户ID")
    previous_rank: Optional[int] = Field(None, description="上次排名")
    rank_change: int = Field(..., description="排名变化")
    total_users: Optional[int] = Field(None, description="总用户数")
    percentile: Optional[float] = Field(None, description="百分位")
    calculated_at: datetime = Field(..., description="计算时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class GamificationStats(BaseModel):
    """游戏化统计"""

    total_badges: int = Field(..., description="徽章总数")
    total_points: int = Field(..., description="总积分")
    current_level: int = Field(..., description="当前等级")
    completed_achievements: int = Field(..., description="完成成就数")
    active_challenges: int = Field(..., description="活跃挑战数")
    longest_streak: int = Field(..., description="最长连续天数")


class GamificationOverview(BaseModel):
    """游戏化概览"""

    user_points: UserPointsInDB = Field(..., description="用户积分")
    user_level: LevelProgress = Field(..., description="用户等级进度")
    recent_badges: List[UserBadgeInDB] = Field(..., description="最近徽章")
    active_achievements: List[AchievementInDB] = Field(..., description="活跃成就")
    active_challenges: List[ChallengeInDB] = Field(..., description="活跃挑战")
    streaks: List[StreakRecordInDB] = Field(..., description="连续记录")
    gamification_stats: GamificationStats = Field(..., description="游戏化统计")


class PointsEarned(BaseModel):
    """获得积分"""

    points: int = Field(..., description="获得积分")
    reason: str = Field(..., description="原因")
    new_total: int = Field(..., description="新总分")
    level_up: bool = Field(..., description="是否升级")
    new_level: Optional[int] = Field(None, description="新等级")


class BadgeUnlocked(BaseModel):
    """解锁徽章"""

    badge: UserBadgeInDB = Field(..., description="徽章")
    points_reward: int = Field(..., description="积分奖励")
    message: str = Field(..., description="祝贺消息")


class AchievementCompleted(BaseModel):
    """完成成就"""

    achievement: AchievementInDB = Field(..., description="成就")
    points_reward: int = Field(..., description="积分奖励")
    badge_reward: Optional[UserBadgeInDB] = Field(None, description="徽章奖励")


class DailyReward(BaseModel):
    """每日奖励"""

    day: int = Field(..., description="连续登录天数")
    points: int = Field(..., description="积分奖励")
    bonus: Optional[str] = Field(None, description="额外奖励")
    claimed: bool = Field(..., description="是否已领取")
