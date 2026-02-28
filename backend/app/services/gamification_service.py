import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.gamification import (
    Achievement,
    Challenge,
    LeaderboardEntry,
    PointsTransaction,
    StreakRecord,
    UserBadge,
    UserLevel,
    UserPoints,
)
from app.models.user import User
from app.schemas.gamification import (
    AchievementCompleted,
    AchievementCreate,
    AchievementInDB,
    BadgeUnlocked,
    ChallengeCreate,
    ChallengeInDB,
    GamificationOverview,
    GamificationStats,
    LeaderboardEntryInDB,
    LevelProgress,
    PointsBreakdown,
    PointsEarned,
    PointsTransactionInDB,
    StreakRecordInDB,
    UserBadgeCreate,
    UserBadgeInDB,
    UserPointsInDB,
)

logger = structlog.get_logger()


class GamificationService:
    """游戏化服务"""

    # 等级配置
    LEVEL_CONFIG = {
        1: {"title": "新手", "points_required": 0, "next_level_points": 100},
        2: {"title": "初学者", "points_required": 100, "next_level_points": 250},
        3: {"title": "探索者", "points_required": 250, "next_level_points": 500},
        4: {"title": "实践者", "points_required": 500, "next_level_points": 1000},
        5: {"title": "坚持者", "points_required": 1000, "next_level_points": 2000},
        6: {"title": "进阶者", "points_required": 2000, "next_level_points": 3500},
        7: {"title": "熟练者", "points_required": 3500, "next_level_points": 5500},
        8: {"title": "精通者", "points_required": 5500, "next_level_points": 8000},
        9: {"title": "专家", "points_required": 8000, "next_level_points": 11000},
        10: {"title": "大师", "points_required": 11000, "next_level_points": 15000},
    }

    # 徽章定义
    BADGES = {
        # 减重徽章
        "weight_loss_1kg": {
            "name": "减重先锋",
            "description": "成功减重1公斤",
            "category": "weight_loss",
            "level": "bronze",
            "icon": "🥉",
            "points": 50,
        },
        "weight_loss_5kg": {
            "name": "减重勇士",
            "description": "成功减重5公斤",
            "category": "weight_loss",
            "level": "silver",
            "icon": "🥈",
            "points": 200,
        },
        "weight_loss_10kg": {
            "name": "减重英雄",
            "description": "成功减重10公斤",
            "category": "weight_loss",
            "level": "gold",
            "icon": "🥇",
            "points": 500,
        },
        # 习惯徽章
        "habit_7days": {
            "name": "习惯新手",
            "description": "连续坚持习惯7天",
            "category": "habit_mastery",
            "level": "bronze",
            "icon": "🔰",
            "points": 30,
        },
        "habit_30days": {
            "name": "习惯建立者",
            "description": "连续坚持习惯30天",
            "category": "habit_mastery",
            "level": "silver",
            "icon": "🎯",
            "points": 150,
        },
        "habit_100days": {
            "name": "习惯大师",
            "description": "连续坚持习惯100天",
            "category": "habit_mastery",
            "level": "gold",
            "icon": "👑",
            "points": 500,
        },
        # 营养徽章
        "nutrition_beginner": {
            "name": "营养新手",
            "description": "完成7天饮食记录",
            "category": "nutrition",
            "level": "bronze",
            "icon": "🥗",
            "points": 40,
        },
        "nutrition_tracker": {
            "name": "营养追踪者",
            "description": "完成30天饮食记录",
            "category": "nutrition",
            "level": "silver",
            "icon": "🥕",
            "points": 150,
        },
        "nutrition_expert": {
            "name": "营养专家",
            "description": "坚持营养目标90天",
            "category": "nutrition",
            "level": "gold",
            "icon": "🥑",
            "points": 400,
        },
        # 情感徽章
        "mindfulness_practitioner": {
            "name": "正念练习者",
            "description": "完成10次正念练习",
            "category": "emotional_wellness",
            "level": "bronze",
            "icon": "🧘",
            "points": 50,
        },
        "gratitude_journalist": {
            "name": "感恩记者",
            "description": "记录30条感恩日记",
            "category": "emotional_wellness",
            "level": "silver",
            "icon": "🙏",
            "points": 150,
        },
        "emotion_master": {
            "name": "情感大师",
            "description": "连续30天记录情感状态",
            "category": "emotional_wellness",
            "level": "gold",
            "icon": "💝",
            "points": 300,
        },
        # 连续性徽章
        "login_7days": {
            "name": "忠实用户",
            "description": "连续登录7天",
            "category": "consistency",
            "level": "bronze",
            "icon": "📅",
            "points": 20,
        },
        "login_30days": {
            "name": "忠诚用户",
            "description": "连续登录30天",
            "category": "consistency",
            "level": "silver",
            "icon": "📆",
            "points": 100,
        },
        "login_100days": {
            "name": "超级用户",
            "description": "连续登录100天",
            "category": "consistency",
            "level": "gold",
            "icon": "⭐",
            "points": 300,
        },
        # 里程碑徽章
        "first_goal": {
            "name": "目标达成",
            "description": "完成第一个目标",
            "category": "milestone",
            "level": "bronze",
            "icon": "🎯",
            "points": 50,
        },
        "perfect_week": {
            "name": "完美一周",
            "description": "一周内完成所有习惯",
            "category": "milestone",
            "level": "silver",
            "icon": "✨",
            "points": 100,
        },
        "transformer": {
            "name": "蜕变者",
            "description": "完成为期12周的计划",
            "category": "milestone",
            "level": "gold",
            "icon": "🦋",
            "points": 500,
        },
    }

    # 积分规则
    POINTS_RULES = {
        "login_daily": 10,
        "login_streak": 5,  # 连续登录奖励
        "record_weight": 15,
        "record_meal": 10,
        "complete_habit": 20,
        "habit_streak_7": 50,
        "habit_streak_30": 200,
        "record_emotion": 10,
        "complete_mindfulness": 25,
        "write_gratitude": 15,
        "achieve_goal": 100,
        "earn_badge": 50,
        "complete_challenge": 200,
        "share_progress": 30,
    }

    def __init__(self, db: Session):
        self.db = db

    # ========== 积分系统 ==========

    def initialize_user_gamification(self, user: User) -> None:
        """初始化用户游戏化数据"""
        logger.info("Initializing gamification for user", user_id=user.id)

        # 检查是否已存在
        existing_points = (
            self.db.query(UserPoints).filter(UserPoints.user_id == user.id).first()
        )

        if existing_points:
            return

        # 创建积分记录
        user_points = UserPoints(
            user_id=user.id,
            total_points=0,
            current_points=0,
            lifetime_points=0,
        )
        self.db.add(user_points)

        # 创建等级记录
        user_level = UserLevel(
            user_id=user.id,
            current_level=1,
            current_title="新手",
            experience_points=0,
            points_to_next_level=100,
        )
        self.db.add(user_level)

        # 创建默认成就
        self._create_default_achievements(user)

        self.db.commit()

        logger.info("Gamification initialized", user_id=user.id)

    def _create_default_achievements(self, user: User) -> None:
        """创建默认成就"""
        default_achievements = [
            {
                "achievement_id": "first_weight_record",
                "achievement_name": "初次记录",
                "achievement_description": "记录第一次体重",
                "achievement_category": "milestone",
                "target_value": 1,
                "points_reward": 50,
            },
            {
                "achievement_id": "first_habit_complete",
                "achievement_name": "习惯起步",
                "achievement_description": "完成第一个习惯",
                "achievement_category": "habit_mastery",
                "target_value": 1,
                "points_reward": 30,
            },
            {
                "achievement_id": "first_emotion_record",
                "achievement_name": "情感觉察",
                "achievement_description": "记录第一次情感状态",
                "achievement_category": "emotional_wellness",
                "target_value": 1,
                "points_reward": 20,
            },
            {
                "achievement_id": "week_complete_habits",
                "achievement_name": "习惯周冠军",
                "achievement_description": "一周内完成所有习惯",
                "achievement_category": "habit_mastery",
                "target_value": 7,
                "points_reward": 100,
            },
            {
                "achievement_id": "month_login",
                "achievement_name": "月度活跃用户",
                "achievement_description": "一个月内登录15天",
                "achievement_category": "consistency",
                "target_value": 15,
                "points_reward": 150,
            },
            # 营养成就 (Story 4.1)
            {
                "achievement_id": "nutrition_streak_7",
                "achievement_name": "饮食记录达人",
                "achievement_description": "连续7天记录饮食",
                "achievement_category": "nutrition",
                "target_value": 7,
                "points_reward": 100,
            },
            {
                "achievement_id": "nutrition_streak_30",
                "achievement_name": "营养追踪专家",
                "achievement_description": "连续30天记录饮食",
                "achievement_category": "nutrition",
                "target_value": 30,
                "points_reward": 500,
            },
            {
                "achievement_id": "calorie_goal_met_10",
                "achievement_name": "热量控制者",
                "achievement_description": "达成热量目标10次",
                "achievement_category": "nutrition",
                "target_value": 10,
                "points_reward": 150,
            },
            {
                "achievement_id": "calorie_goal_met_50",
                "achievement_name": "热量管理大师",
                "achievement_description": "达成热量目标50次",
                "achievement_category": "nutrition",
                "target_value": 50,
                "points_reward": 500,
            },
            {
                "achievement_id": "macro_balance_7",
                "achievement_name": "营养均衡师",
                "achievement_description": "7天营养均衡达标",
                "achievement_category": "nutrition",
                "target_value": 7,
                "points_reward": 200,
            },
            {
                "achievement_id": "variety_explorer_10",
                "achievement_name": "美食探险家",
                "achievement_description": "尝试10种新食物",
                "achievement_category": "nutrition",
                "target_value": 10,
                "points_reward": 100,
            },
            {
                "achievement_id": "variety_explorer_30",
                "achievement_name": "饮食多样化达人",
                "achievement_description": "尝试30种新食物",
                "achievement_category": "nutrition",
                "target_value": 30,
                "points_reward": 300,
            },
            # 运动成就 (Story 4.2)
            {
                "achievement_id": "exercise_streak_7",
                "achievement_name": "运动达人",
                "achievement_description": "连续7天运动",
                "achievement_category": "exercise",
                "target_value": 7,
                "points_reward": 100,
            },
            {
                "achievement_id": "exercise_streak_30",
                "achievement_name": "运动冠军",
                "achievement_description": "连续30天运动",
                "achievement_category": "exercise",
                "target_value": 30,
                "points_reward": 500,
            },
            {
                "achievement_id": "cardio_10_hours",
                "achievement_name": "有氧达人",
                "achievement_description": "累计有氧运动10小时",
                "achievement_category": "exercise",
                "target_value": 600,  # 10小时 = 600分钟
                "points_reward": 150,
            },
            {
                "achievement_id": "cardio_50_hours",
                "achievement_name": "有氧大师",
                "achievement_description": "累计有氧运动50小时",
                "achievement_category": "exercise",
                "target_value": 3000,  # 50小时 = 3000分钟
                "points_reward": 500,
            },
            {
                "achievement_id": "strength_10_sessions",
                "achievement_name": "力量入门",
                "achievement_description": "完成10次力量训练",
                "achievement_category": "exercise",
                "target_value": 10,
                "points_reward": 100,
            },
            {
                "achievement_id": "strength_50_sessions",
                "achievement_name": "力量训练师",
                "achievement_description": "完成50次力量训练",
                "achievement_category": "exercise",
                "target_value": 50,
                "points_reward": 300,
            },
            {
                "achievement_id": "total_100km",
                "achievement_name": "百里挑一",
                "achievement_description": "累计跑步100公里",
                "achievement_category": "exercise",
                "target_value": 100000,  # 米
                "points_reward": 500,
            },
            {
                "achievement_id": "total_500km",
                "achievement_name": "跑步达人",
                "achievement_description": "累计跑步500公里",
                "achievement_category": "exercise",
                "target_value": 500000,  # 米
                "points_reward": 1000,
            },
            {
                "achievement_id": "total_1000_mins",
                "achievement_name": "运动时长达人",
                "achievement_description": "累计运动1000分钟",
                "achievement_category": "exercise",
                "target_value": 1000,
                "points_reward": 300,
            },
            {
                "achievement_id": "exercise_types_3",
                "achievement_name": "全能运动者",
                "achievement_description": "尝试3种不同运动类型",
                "achievement_category": "exercise",
                "target_value": 3,
                "points_reward": 150,
            },
            {
                "achievement_id": "exercise_types_5",
                "achievement_name": "运动探险家",
                "achievement_description": "尝试5种不同运动类型",
                "achievement_category": "exercise",
                "target_value": 5,
                "points_reward": 300,
            },
        ]

        for achievement_data in default_achievements:
            achievement = Achievement(user_id=user.id, **achievement_data)
            self.db.add(achievement)

    def award_points(
        self,
        user: User,
        points: int,
        transaction_type: str,
        description: str,
        reference_id: Optional[str] = None,
        reference_type: Optional[str] = None,
    ) -> PointsEarned:
        """授予积分"""
        logger.info(
            "Awarding points",
            user_id=user.id,
            points=points,
            type=transaction_type,
        )

        # 获取或创建用户积分记录
        user_points = (
            self.db.query(UserPoints).filter(UserPoints.user_id == user.id).first()
        )

        if not user_points:
            self.initialize_user_gamification(user)
            user_points = (
                self.db.query(UserPoints).filter(UserPoints.user_id == user.id).first()
            )

        # 更新积分
        user_points.total_points += points
        user_points.current_points += points
        user_points.lifetime_points += points

        # 更新分类积分
        if "nutrition" in transaction_type:
            user_points.nutrition_points += points
        elif "habit" in transaction_type:
            user_points.habit_points += points
        elif "emotion" in transaction_type:
            user_points.emotional_points += points
        elif "login" in transaction_type:
            user_points.login_points += points
        elif "achievement" in transaction_type:
            user_points.achievement_points += points

        user_points.last_updated = datetime.utcnow()

        # 创建交易记录
        transaction = PointsTransaction(
            user_id=user.id,
            points_amount=points,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id,
            reference_type=reference_type,
        )
        self.db.add(transaction)

        # 检查等级提升
        level_up, new_level = self._check_level_up(user, user_points.total_points)

        self.db.commit()

        logger.info(
            "Points awarded",
            user_id=user.id,
            points=points,
            new_total=user_points.total_points,
            level_up=level_up,
        )

        return PointsEarned(
            points=points,
            reason=description,
            new_total=user_points.total_points,
            level_up=level_up,
            new_level=new_level if level_up else None,
        )

    def _check_level_up(
        self, user: User, total_points: int
    ) -> Tuple[bool, Optional[int]]:
        """检查是否升级"""
        user_level = (
            self.db.query(UserLevel).filter(UserLevel.user_id == user.id).first()
        )

        if not user_level:
            return False, None

        current_level = user_level.current_level
        next_level = current_level + 1

        # 检查是否有下一级
        if next_level not in self.LEVEL_CONFIG:
            return False, None

        next_level_config = self.LEVEL_CONFIG[next_level]

        if total_points >= next_level_config["points_required"]:
            # 升级
            user_level.current_level = next_level
            user_level.current_title = next_level_config["title"]
            user_level.experience_points = total_points
            user_level.points_to_next_level = next_level_config.get(
                "next_level_points", total_points + 1000
            )
            user_level.level_up_count += 1
            user_level.last_level_up = datetime.utcnow()

            return True, next_level

        return False, None

    def get_user_points(self, user: User) -> UserPointsInDB:
        """获取用户积分"""
        user_points = (
            self.db.query(UserPoints).filter(UserPoints.user_id == user.id).first()
        )

        if not user_points:
            self.initialize_user_gamification(user)
            user_points = (
                self.db.query(UserPoints).filter(UserPoints.user_id == user.id).first()
            )

        return UserPointsInDB(
            id=user_points.id,
            user_id=user_points.user_id,
            total_points=user_points.total_points,
            current_points=user_points.current_points,
            lifetime_points=user_points.lifetime_points,
            breakdown=PointsBreakdown(
                nutrition_points=user_points.nutrition_points,
                habit_points=user_points.habit_points,
                emotional_points=user_points.emotional_points,
                login_points=user_points.login_points,
                achievement_points=user_points.achievement_points,
            ),
            last_updated=user_points.last_updated,
            created_at=user_points.created_at,
        )

    def get_points_history(
        self, user: User, limit: int = 50
    ) -> List[PointsTransactionInDB]:
        """获取积分历史"""
        transactions = (
            self.db.query(PointsTransaction)
            .filter(PointsTransaction.user_id == user.id)
            .order_by(PointsTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            PointsTransactionInDB(
                id=t.id,
                user_id=t.user_id,
                points_amount=t.points_amount,
                transaction_type=t.transaction_type,
                description=t.description,
                reference_id=t.reference_id,
                reference_type=t.reference_type,
                created_at=t.created_at,
            )
            for t in transactions
        ]

    # ========== 等级系统 ==========

    def get_level_progress(self, user: User) -> LevelProgress:
        """获取等级进度"""
        user_level = (
            self.db.query(UserLevel).filter(UserLevel.user_id == user.id).first()
        )

        if not user_level:
            self.initialize_user_gamification(user)
            user_level = (
                self.db.query(UserLevel).filter(UserLevel.user_id == user.id).first()
            )

        current_level = user_level.current_level
        current_config = self.LEVEL_CONFIG.get(current_level, {})
        next_level_config = self.LEVEL_CONFIG.get(current_level + 1, {})

        points_required = current_config.get("points_required", 0)
        points_to_next = next_level_config.get(
            "points_required", points_required + 1000
        )
        current_points = user_level.experience_points

        progress = (
            (current_points - points_required)
            / (points_to_next - points_required)
            * 100
            if points_to_next > points_required
            else 100
        )

        return LevelProgress(
            current_level=current_level,
            current_title=user_level.current_title,
            experience_points=current_points,
            points_to_next_level=points_to_next - current_points,
            progress_percentage=round(max(0, min(100, progress)), 1),
            next_level_title=next_level_config.get("title"),
        )

    # ========== 徽章系统 ==========

    def check_and_award_badges(self, user: User) -> List[BadgeUnlocked]:
        """检查并授予徽章"""
        logger.info("Checking badges for user", user_id=user.id)

        awarded_badges = []

        # 获取用户已有的徽章
        existing_badges = {
            b.badge_id
            for b in self.db.query(UserBadge).filter(UserBadge.user_id == user.id).all()
        }

        # 检查每个徽章条件
        for badge_id, badge_info in self.BADGES.items():
            if badge_id in existing_badges:
                continue

            if self._check_badge_eligibility(user, badge_id):
                # 授予徽章
                badge = UserBadge(
                    user_id=user.id,
                    badge_id=badge_id,
                    badge_name=badge_info["name"],
                    badge_description=badge_info["description"],
                    badge_category=badge_info["category"],
                    badge_level=badge_info["level"],
                    badge_icon=badge_info["icon"],
                    earned_at=datetime.utcnow(),
                    earned_criteria=f"达成{badge_info['description']}",
                )
                self.db.add(badge)

                # 授予积分
                points_reward = badge_info.get("points", 50)
                self.award_points(
                    user,
                    points_reward,
                    "badge_earned",
                    f"获得徽章: {badge_info['name']}",
                    badge_id,
                    "badge",
                )

                awarded_badges.append(
                    BadgeUnlocked(
                        badge=UserBadgeInDB(
                            id=badge.id,
                            user_id=badge.user_id,
                            badge_id=badge.badge_id,
                            badge_name=badge.badge_name,
                            badge_description=badge.badge_description,
                            badge_category=badge.badge_category,
                            badge_level=badge.badge_level,
                            badge_icon=badge.badge_icon,
                            earned_at=badge.earned_at,
                            earned_criteria=badge.earned_criteria,
                            progress_data=badge.progress_data,
                            is_showcased=badge.is_showcased,
                            showcase_order=badge.showcase_order,
                            created_at=badge.created_at,
                        ),
                        points_reward=points_reward,
                        message=f"恭喜！您获得了{badge_info['name']}徽章！",
                    )
                )

        self.db.commit()

        if awarded_badges:
            logger.info(
                "Badges awarded",
                user_id=user.id,
                count=len(awarded_badges),
            )

        return awarded_badges

    def _check_badge_eligibility(self, user: User, badge_id: str) -> bool:
        """检查徽章资格"""
        # 体重徽章
        if badge_id == "weight_loss_1kg":
            return self._check_weight_loss(user, 1000)
        elif badge_id == "weight_loss_5kg":
            return self._check_weight_loss(user, 5000)
        elif badge_id == "weight_loss_10kg":
            return self._check_weight_loss(user, 10000)

        # 习惯徽章
        elif badge_id == "habit_7days":
            return self._check_habit_streak(user, 7)
        elif badge_id == "habit_30days":
            return self._check_habit_streak(user, 30)
        elif badge_id == "habit_100days":
            return self._check_habit_streak(user, 100)

        # 营养徽章
        elif badge_id == "nutrition_beginner":
            return self._check_nutrition_records(user, 7)
        elif badge_id == "nutrition_tracker":
            return self._check_nutrition_records(user, 30)
        elif badge_id == "nutrition_expert":
            return self._check_nutrition_goal_days(user, 90)

        # 情感徽章
        elif badge_id == "mindfulness_practitioner":
            return self._check_mindfulness_count(user, 10)
        elif badge_id == "gratitude_journalist":
            return self._check_gratitude_count(user, 30)
        elif badge_id == "emotion_master":
            return self._check_emotion_streak(user, 30)

        # 登录徽章
        elif badge_id == "login_7days":
            return self._check_login_streak(user, 7)
        elif badge_id == "login_30days":
            return self._check_login_streak(user, 30)
        elif badge_id == "login_100days":
            return self._check_login_streak(user, 100)

        # 里程碑徽章
        elif badge_id == "first_goal":
            return self._check_first_goal(user)
        elif badge_id == "perfect_week":
            return self._check_perfect_week(user)
        elif badge_id == "transformer":
            return self._check_transformer(user)

        return False

    def _check_weight_loss(self, user: User, target_loss_grams: int) -> bool:
        """检查减重目标"""
        from app.models.health_record import HealthRecord

        if not user.initial_weight:
            return False

        # 获取最新体重记录
        latest_record = (
            self.db.query(HealthRecord)
            .filter(HealthRecord.user_id == user.id, HealthRecord.weight.isnot(None))
            .order_by(HealthRecord.record_date.desc())
            .first()
        )

        if not latest_record:
            return False

        weight_loss = user.initial_weight - latest_record.weight
        return weight_loss >= target_loss_grams

    def _check_habit_streak(self, user: User, target_streak: int) -> bool:
        """检查习惯连续天数"""
        from app.models.habit import Habit

        habits = (
            self.db.query(Habit)
            .filter(Habit.user_id == user.id, Habit.is_active == True)
            .all()
        )

        for habit in habits:
            if habit.streak_days >= target_streak:
                return True

        return False

    def _check_nutrition_records(self, user: User, target_days: int) -> bool:
        """检查营养记录天数"""
        from app.models.health_record import HealthRecord

        count = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user.id, HealthRecord.daily_calories.isnot(None)
            )
            .count()
        )

        return count >= target_days

    def _check_nutrition_goal_days(self, user: User, target_days: int) -> bool:
        """检查营养目标达成天数"""
        # 简化版：检查有记录的天数
        return self._check_nutrition_records(user, target_days)

    def _check_mindfulness_count(self, user: User, target_count: int) -> bool:
        """检查正念练习次数"""
        from app.models.emotional_support import MindfulnessExercise

        count = (
            self.db.query(MindfulnessExercise)
            .filter(MindfulnessExercise.user_id == user.id)
            .count()
        )

        return count >= target_count

    def _check_gratitude_count(self, user: User, target_count: int) -> bool:
        """检查感恩日记数量"""
        from app.models.emotional_support import GratitudeJournal

        count = (
            self.db.query(GratitudeJournal)
            .filter(GratitudeJournal.user_id == user.id)
            .count()
        )

        return count >= target_count

    def _check_emotion_streak(self, user: User, target_streak: int) -> bool:
        """检查情感记录连续天数"""
        from app.models.emotional_support import EmotionalState

        # 获取最近的情感记录
        recent_states = (
            self.db.query(EmotionalState)
            .filter(EmotionalState.user_id == user.id)
            .order_by(EmotionalState.recorded_at.desc())
            .limit(target_streak)
            .all()
        )

        if len(recent_states) < target_streak:
            return False

        # 检查是否连续
        dates = {s.recorded_at.date() for s in recent_states}
        expected_dates = {
            (datetime.utcnow().date() - timedelta(days=i)) for i in range(target_streak)
        }

        return dates == expected_dates

    def _check_login_streak(self, user: User, target_streak: int) -> bool:
        """检查登录连续天数"""
        # 简化版：基于用户创建时间和活动记录
        # 实际应用中应该使用登录日志
        streak_record = (
            self.db.query(StreakRecord)
            .filter(
                StreakRecord.user_id == user.id, StreakRecord.streak_type == "login"
            )
            .first()
        )

        if streak_record:
            return streak_record.current_streak >= target_streak

        return False

    def _check_first_goal(self, user: User) -> bool:
        """检查是否完成第一个目标"""
        from app.models.habit import HabitCompletion

        count = (
            self.db.query(HabitCompletion)
            .filter(
                HabitCompletion.habit_id.in_(
                    self.db.query(Habit.id).filter(Habit.user_id == user.id)
                )
            )
            .count()
        )

        return count >= 1

    def _check_perfect_week(self, user: User) -> bool:
        """检查是否有一周完美完成"""
        # 简化版：检查最近7天完成率100%
        from app.services.habit_service import HabitService

        habit_service = HabitService(self.db)
        today = date.today()
        week_ago = today - timedelta(days=6)

        total_habits = 0
        total_completions = 0

        for i in range(7):
            day_date = week_ago + timedelta(days=i)
            checklist = habit_service.get_daily_checklist(user, day_date)
            total_habits += checklist["total_count"]
            total_completions += checklist["completed_count"]

        return total_habits > 0 and total_habits == total_completions

    def _check_transformer(self, user: User) -> bool:
        """检查是否完成12周计划"""
        # 检查用户创建时间
        weeks_since_join = (datetime.utcnow() - user.created_at).days / 7

        # 检查是否有持续的习惯记录
        from app.models.habit import Habit

        long_term_habits = (
            self.db.query(Habit)
            .filter(Habit.user_id == user.id, Habit.total_completions >= 30)
            .count()
        )

        return weeks_since_join >= 12 and long_term_habits > 0

    def get_user_badges(
        self, user: User, category: Optional[str] = None, limit: int = 50
    ) -> List[UserBadgeInDB]:
        """获取用户徽章"""
        query = self.db.query(UserBadge).filter(UserBadge.user_id == user.id)

        if category:
            query = query.filter(UserBadge.badge_category == category)

        badges = query.order_by(UserBadge.earned_at.desc()).limit(limit).all()

        return [
            UserBadgeInDB(
                id=b.id,
                user_id=b.user_id,
                badge_id=b.badge_id,
                badge_name=b.badge_name,
                badge_description=b.badge_description,
                badge_category=b.badge_category,
                badge_level=b.badge_level,
                badge_icon=b.badge_icon,
                earned_at=b.earned_at,
                earned_criteria=b.earned_criteria,
                progress_data=b.progress_data,
                is_showcased=b.is_showcased,
                showcase_order=b.showcase_order,
                created_at=b.created_at,
            )
            for b in badges
        ]

    def showcase_badge(self, user: User, badge_id: str, order: int) -> bool:
        """展示徽章"""
        badge = (
            self.db.query(UserBadge)
            .filter(UserBadge.user_id == user.id, UserBadge.badge_id == badge_id)
            .first()
        )

        if not badge:
            return False

        badge.is_showcased = True
        badge.showcase_order = order
        self.db.commit()

        return True

    # ========== 成就系统 ==========

    def update_achievement_progress(
        self, user: User, achievement_id: str, progress: int
    ) -> Optional[AchievementCompleted]:
        """更新成就进度"""
        achievement = (
            self.db.query(Achievement)
            .filter(
                Achievement.user_id == user.id,
                Achievement.achievement_id == achievement_id,
            )
            .first()
        )

        if not achievement or achievement.is_completed:
            return None

        # 更新进度
        achievement.current_value = min(
            achievement.current_value + progress, achievement.target_value
        )
        achievement.progress_percentage = (
            achievement.current_value / achievement.target_value * 100
        )

        # 检查是否完成
        if achievement.current_value >= achievement.target_value:
            achievement.is_completed = True
            achievement.completed_at = datetime.utcnow()

            # 授予积分
            if achievement.points_reward > 0:
                self.award_points(
                    user,
                    achievement.points_reward,
                    "achievement_completed",
                    f"完成成就: {achievement.achievement_name}",
                    str(achievement.id),
                    "achievement",
                )

            # 检查徽章奖励
            badge_reward = None
            if achievement.badge_reward:
                badge_reward_data = self.BADGES.get(achievement.badge_reward)
                if badge_reward_data:
                    badge = UserBadge(
                        user_id=user.id,
                        badge_id=achievement.badge_reward,
                        badge_name=badge_reward_data["name"],
                        badge_description=badge_reward_data["description"],
                        badge_category=badge_reward_data["category"],
                        badge_level=badge_reward_data["level"],
                        badge_icon=badge_reward_data["icon"],
                        earned_at=datetime.utcnow(),
                        earned_criteria=f"通过成就获得: {achievement.achievement_name}",
                    )
                    self.db.add(badge)
                    self.db.flush()

                    badge_reward = UserBadgeInDB(
                        id=badge.id,
                        user_id=badge.user_id,
                        badge_id=badge.badge_id,
                        badge_name=badge.badge_name,
                        badge_description=badge.badge_description,
                        badge_category=badge.badge_category,
                        badge_level=badge.badge_level,
                        badge_icon=badge.badge_icon,
                        earned_at=badge.earned_at,
                        earned_criteria=badge.earned_criteria,
                        progress_data=badge.progress_data,
                        is_showcased=badge.is_showcased,
                        showcase_order=badge.showcase_order,
                        created_at=badge.created_at,
                    )

            self.db.commit()

            return AchievementCompleted(
                achievement=AchievementInDB(
                    id=achievement.id,
                    user_id=achievement.user_id,
                    achievement_id=achievement.achievement_id,
                    achievement_name=achievement.achievement_name,
                    achievement_description=achievement.achievement_description,
                    achievement_category=achievement.achievement_category,
                    target_value=achievement.target_value,
                    current_value=achievement.current_value,
                    progress_percentage=achievement.progress_percentage,
                    is_completed=achievement.is_completed,
                    completed_at=achievement.completed_at,
                    points_reward=achievement.points_reward,
                    badge_reward=achievement.badge_reward,
                    created_at=achievement.created_at,
                    updated_at=achievement.updated_at,
                ),
                points_reward=achievement.points_reward,
                badge_reward=badge_reward,
            )

        self.db.commit()
        return None

    def get_user_achievements(
        self, user: User, completed_only: bool = False
    ) -> List[AchievementInDB]:
        """获取用户成就"""
        query = self.db.query(Achievement).filter(Achievement.user_id == user.id)

        if completed_only:
            query = query.filter(Achievement.is_completed == True)

        achievements = query.order_by(Achievement.created_at.desc()).all()

        return [
            AchievementInDB(
                id=a.id,
                user_id=a.user_id,
                achievement_id=a.achievement_id,
                achievement_name=a.achievement_name,
                achievement_description=a.achievement_description,
                achievement_category=a.achievement_category,
                target_value=a.target_value,
                current_value=a.current_value,
                progress_percentage=a.progress_percentage,
                is_completed=a.is_completed,
                completed_at=a.completed_at,
                points_reward=a.points_reward,
                badge_reward=a.badge_reward,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in achievements
        ]

    # ========== 营养成就系统 (Story 4.1) ==========

    def get_nutrition_achievements(
        self, user: User, completed_only: bool = False
    ) -> List[AchievementInDB]:
        """获取用户营养成就"""
        query = self.db.query(Achievement).filter(
            Achievement.user_id == user.id,
            Achievement.achievement_category == "nutrition",
        )

        if completed_only:
            query = query.filter(Achievement.is_completed == True)

        achievements = query.order_by(Achievement.created_at.desc()).all()

        return [
            AchievementInDB(
                id=a.id,
                user_id=a.user_id,
                achievement_id=a.achievement_id,
                achievement_name=a.achievement_name,
                achievement_description=a.achievement_description,
                achievement_category=a.achievement_category,
                target_value=a.target_value,
                current_value=a.current_value,
                progress_percentage=a.progress_percentage,
                is_completed=a.is_completed,
                completed_at=a.completed_at,
                points_reward=a.points_reward,
                badge_reward=a.badge_reward,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in achievements
        ]

    def update_nutrition_achievement(
        self, user: User, achievement_id: str, increment: int = 1
    ) -> Optional[AchievementInDB]:
        """更新营养成就进度"""
        achievement = (
            self.db.query(Achievement)
            .filter(
                Achievement.user_id == user.id,
                Achievement.achievement_id == achievement_id,
            )
            .first()
        )

        if not achievement or achievement.is_completed:
            return None

        # 更新进度
        achievement.current_value += increment
        achievement.progress_percentage = min(
            100.0, (achievement.current_value / achievement.target_value) * 100
        )

        # 检查是否完成
        if achievement.current_value >= achievement.target_value:
            achievement.is_completed = True
            achievement.completed_at = datetime.utcnow()

            # 发放积分奖励
            self.award_points(
                user=user,
                points=achievement.points_reward,
                transaction_type="achievement_nutrition",
                description=f"完成成就: {achievement.achievement_name}",
                reference_id=achievement.achievement_id,
                reference_type="achievement",
            )

            logger.info(
                "Nutrition achievement completed",
                user_id=user.id,
                achievement_id=achievement.achievement_id,
                points_reward=achievement.points_reward,
            )

        self.db.commit()

        return AchievementInDB(
            id=achievement.id,
            user_id=achievement.user_id,
            achievement_id=achievement.achievement_id,
            achievement_name=achievement.achievement_name,
            achievement_description=achievement.achievement_description,
            achievement_category=achievement.achievement_category,
            target_value=achievement.target_value,
            current_value=achievement.current_value,
            progress_percentage=achievement.progress_percentage,
            is_completed=achievement.is_completed,
            completed_at=achievement.completed_at,
            points_reward=achievement.points_reward,
            badge_reward=achievement.badge_reward,
            created_at=achievement.created_at,
            updated_at=achievement.updated_at,
        )

    def check_and_update_nutrition_streak(
        self, user: User, has_meal_today: bool
    ) -> None:
        """检查并更新饮食连续记录"""
        # 查找饮食连续成就
        streak_achievements = ["nutrition_streak_7", "nutrition_streak_30"]

        for achievement_id in streak_achievements:
            if has_meal_today:
                self.update_nutrition_achievement(user, achievement_id)
            # 如果今天没有记录，不减少连续天数（保持宽容）

    # ========== 运动成就系统 (Story 4.2) ==========

    def get_exercise_achievements(
        self, user: User, completed_only: bool = False
    ) -> List[AchievementInDB]:
        """获取用户运动成就"""
        query = self.db.query(Achievement).filter(
            Achievement.user_id == user.id,
            Achievement.achievement_category == "exercise",
        )

        if completed_only:
            query = query.filter(Achievement.is_completed == True)

        achievements = query.order_by(Achievement.created_at.desc()).all()

        return [
            AchievementInDB(
                id=a.id,
                user_id=a.user_id,
                achievement_id=a.achievement_id,
                achievement_name=a.achievement_name,
                achievement_description=a.achievement_description,
                achievement_category=a.achievement_category,
                target_value=a.target_value,
                current_value=a.current_value,
                progress_percentage=a.progress_percentage,
                is_completed=a.is_completed,
                completed_at=a.completed_at,
                points_reward=a.points_reward,
                badge_reward=a.badge_reward,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in achievements
        ]

    def update_exercise_achievement(
        self, user: User, achievement_id: str, increment: int = 1
    ) -> Optional[AchievementInDB]:
        """更新运动成就进度"""
        achievement = (
            self.db.query(Achievement)
            .filter(
                Achievement.user_id == user.id,
                Achievement.achievement_id == achievement_id,
            )
            .first()
        )

        if not achievement or achievement.is_completed:
            return None

        # 更新进度
        achievement.current_value += increment
        achievement.progress_percentage = min(
            100.0, (achievement.current_value / achievement.target_value) * 100
        )

        # 检查是否完成
        if achievement.current_value >= achievement.target_value:
            achievement.is_completed = True
            achievement.completed_at = datetime.utcnow()

            # 发放积分奖励
            self.award_points(
                user=user,
                points=achievement.points_reward,
                transaction_type="achievement_exercise",
                description=f"完成成就: {achievement.achievement_name}",
                reference_id=achievement.achievement_id,
                reference_type="achievement",
            )

            logger.info(
                "Exercise achievement completed",
                user_id=user.id,
                achievement_id=achievement.achievement_id,
                points_reward=achievement.points_reward,
            )

        self.db.commit()

        return AchievementInDB(
            id=achievement.id,
            user_id=achievement.user_id,
            achievement_id=achievement.achievement_id,
            achievement_name=achievement.achievement_name,
            achievement_description=achievement.achievement_description,
            achievement_category=achievement.achievement_category,
            target_value=achievement.target_value,
            current_value=achievement.current_value,
            progress_percentage=achievement.progress_percentage,
            is_completed=achievement.is_completed,
            completed_at=achievement.completed_at,
            points_reward=achievement.points_reward,
            badge_reward=achievement.badge_reward,
            created_at=achievement.created_at,
            updated_at=achievement.updated_at,
        )

    def check_and_update_exercise_streak(
        self, user: User, has_exercise_today: bool
    ) -> None:
        """检查并更新运动连续记录"""
        streak_achievements = ["exercise_streak_7", "exercise_streak_30"]

        for achievement_id in streak_achievements:
            if has_exercise_today:
                self.update_exercise_achievement(user, achievement_id)

    def process_exercise_checkin_achievements(
        self,
        user: User,
        exercise_type: str,
        duration_minutes: int = 0,
        distance_meters: int = 0,
    ) -> List[AchievementInDB]:
        """处理运动打卡后的成就检查"""
        completed_achievements = []

        # 1. 更新连续运动成就
        self.check_and_update_exercise_streak(user, has_exercise_today=True)

        # 2. 更新运动时长成就 (cardio)
        if duration_minutes > 0:
            # 将分钟转换为累计分钟数
            self.update_exercise_achievement(
                user, "cardio_10_hours", increment=duration_minutes
            )
            self.update_exercise_achievement(
                user, "cardio_50_hours", increment=duration_minutes
            )
            self.update_exercise_achievement(
                user, "total_1000_mins", increment=duration_minutes
            )

        # 3. 更新距离成就 (跑步)
        if distance_meters > 0:
            self.update_exercise_achievement(
                user, "total_100km", increment=distance_meters
            )
            self.update_exercise_achievement(
                user, "total_500km", increment=distance_meters
            )

        # 4. 更新力量训练成就
        if exercise_type == "strength":
            self.update_exercise_achievement(user, "strength_10_sessions")
            self.update_exercise_achievement(user, "strength_50_sessions")

        # 5. 更新运动类型多样性成就
        # 这里简化处理，实际应该跟踪用户尝试过的运动类型
        # 可以通过查询不同的运动类型来更新

        return completed_achievements

    # ========== 连续记录系统 ==========

    def update_streak(
        self, user: User, streak_type: str, streak_name: str
    ) -> StreakRecordInDB:
        """更新连续记录"""
        streak = (
            self.db.query(StreakRecord)
            .filter(
                StreakRecord.user_id == user.id, StreakRecord.streak_type == streak_type
            )
            .first()
        )

        today = datetime.utcnow().date()

        if not streak:
            # 创建新记录
            streak = StreakRecord(
                user_id=user.id,
                streak_type=streak_type,
                streak_name=streak_name,
                current_streak=1,
                longest_streak=1,
                streak_start_date=datetime.utcnow(),
                last_activity_date=datetime.utcnow(),
                milestones_reached=[],
            )
            self.db.add(streak)
        else:
            # 检查是否连续
            last_date = (
                streak.last_activity_date.date() if streak.last_activity_date else None
            )

            if last_date == today:
                # 今天已经记录过
                pass
            elif last_date == today - timedelta(days=1):
                # 连续一天
                streak.current_streak += 1
                streak.last_activity_date = datetime.utcnow()

                # 更新最长连续
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak

                # 检查里程碑
                milestones = [7, 30, 100, 365]
                if (
                    streak.current_streak in milestones
                    and streak.current_streak not in streak.milestones_reached
                ):
                    streak.milestones_reached.append(streak.current_streak)

                    # 授予连续奖励积分
                    points = streak.current_streak * 2  # 连续天数 * 2
                    self.award_points(
                        user,
                        points,
                        "streak_milestone",
                        f"连续{streak.current_streak}天达成",
                    )
            else:
                # 连续中断，重置
                streak.current_streak = 1
                streak.streak_start_date = datetime.utcnow()
                streak.last_activity_date = datetime.utcnow()

        self.db.commit()
        self.db.refresh(streak)

        return StreakRecordInDB(
            id=streak.id,
            user_id=streak.user_id,
            streak_type=streak.streak_type,
            streak_name=streak.streak_name,
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            streak_start_date=streak.streak_start_date,
            last_activity_date=streak.last_activity_date,
            milestones_reached=streak.milestones_reached or [],
            created_at=streak.created_at,
            updated_at=streak.updated_at,
        )

    def get_user_streaks(self, user: User) -> List[StreakRecordInDB]:
        """获取用户连续记录"""
        streaks = (
            self.db.query(StreakRecord)
            .filter(StreakRecord.user_id == user.id)
            .order_by(StreakRecord.current_streak.desc())
            .all()
        )

        return [
            StreakRecordInDB(
                id=s.id,
                user_id=s.user_id,
                streak_type=s.streak_type,
                streak_name=s.streak_name,
                current_streak=s.current_streak,
                longest_streak=s.longest_streak,
                streak_start_date=s.streak_start_date,
                last_activity_date=s.last_activity_date,
                milestones_reached=s.milestones_reached or [],
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in streaks
        ]

    # ========== 挑战系统 ==========

    def create_challenge(
        self, user: User, challenge_data: ChallengeCreate
    ) -> ChallengeInDB:
        """创建挑战"""
        challenge = Challenge(
            user_id=user.id,
            challenge_id=challenge_data.challenge_id,
            challenge_name=challenge_data.challenge_name,
            challenge_description=challenge_data.challenge_description,
            challenge_type=challenge_data.challenge_type,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=challenge_data.duration_days),
            duration_days=challenge_data.duration_days,
            target_metric=challenge_data.target_metric,
            target_value=challenge_data.target_value,
            current_value=0,
            status="active",
            points_reward=challenge_data.points_reward,
        )

        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)

        return ChallengeInDB(
            id=challenge.id,
            user_id=challenge.user_id,
            challenge_id=challenge.challenge_id,
            challenge_name=challenge.challenge_name,
            challenge_description=challenge.challenge_description,
            challenge_type=challenge.challenge_type,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            duration_days=challenge.duration_days,
            target_metric=challenge.target_metric,
            target_value=challenge.target_value,
            current_value=challenge.current_value,
            status=challenge.status,
            completed_at=challenge.completed_at,
            points_reward=challenge.points_reward,
            badge_reward=challenge.badge_reward,
            created_at=challenge.created_at,
            updated_at=challenge.updated_at,
        )

    def update_challenge_progress(
        self, user: User, challenge_id: str, progress: int
    ) -> Optional[ChallengeInDB]:
        """更新挑战进度"""
        challenge = (
            self.db.query(Challenge)
            .filter(
                Challenge.user_id == user.id,
                Challenge.challenge_id == challenge_id,
                Challenge.status == "active",
            )
            .first()
        )

        if not challenge:
            return None

        # 更新进度
        challenge.current_value = min(
            challenge.current_value + progress, challenge.target_value
        )

        # 检查是否完成
        if challenge.current_value >= challenge.target_value:
            challenge.status = "completed"
            challenge.completed_at = datetime.utcnow()

            # 授予奖励
            if challenge.points_reward > 0:
                self.award_points(
                    user,
                    challenge.points_reward,
                    "challenge_completed",
                    f"完成挑战: {challenge.challenge_name}",
                    str(challenge.id),
                    "challenge",
                )

        self.db.commit()
        self.db.refresh(challenge)

        return ChallengeInDB(
            id=challenge.id,
            user_id=challenge.user_id,
            challenge_id=challenge.challenge_id,
            challenge_name=challenge.challenge_name,
            challenge_description=challenge.challenge_description,
            challenge_type=challenge.challenge_type,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            duration_days=challenge.duration_days,
            target_metric=challenge.target_metric,
            target_value=challenge.target_value,
            current_value=challenge.current_value,
            status=challenge.status,
            completed_at=challenge.completed_at,
            points_reward=challenge.points_reward,
            badge_reward=challenge.badge_reward,
            created_at=challenge.created_at,
            updated_at=challenge.updated_at,
        )

    def get_user_challenges(
        self, user: User, status: Optional[str] = None
    ) -> List[ChallengeInDB]:
        """获取用户挑战"""
        query = self.db.query(Challenge).filter(Challenge.user_id == user.id)

        if status:
            query = query.filter(Challenge.status == status)

        challenges = query.order_by(Challenge.created_at.desc()).all()

        return [
            ChallengeInDB(
                id=c.id,
                user_id=c.user_id,
                challenge_id=c.challenge_id,
                challenge_name=c.challenge_name,
                challenge_description=c.challenge_description,
                challenge_type=c.challenge_type,
                start_date=c.start_date,
                end_date=c.end_date,
                duration_days=c.duration_days,
                target_metric=c.target_metric,
                target_value=c.target_value,
                current_value=c.current_value,
                status=c.status,
                completed_at=c.completed_at,
                points_reward=c.points_reward,
                badge_reward=c.badge_reward,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in challenges
        ]

    # ========== 综合概览 ==========

    def get_gamification_overview(self, user: User) -> GamificationOverview:
        """获取游戏化概览"""
        # 确保数据已初始化
        self.initialize_user_gamification(user)

        # 获取各项数据
        user_points = self.get_user_points(user)
        level_progress = self.get_level_progress(user)
        badges = self.get_user_badges(user, limit=5)
        achievements = self.get_user_achievements(user, completed_only=False)
        challenges = self.get_user_challenges(user, status="active")
        streaks = self.get_user_streaks(user)

        # 计算统计
        completed_achievements = len([a for a in achievements if a.is_completed])
        longest_streak = max([s.longest_streak for s in streaks], default=0)

        stats = GamificationStats(
            total_badges=len(self.get_user_badges(user)),
            total_points=user_points.total_points,
            current_level=level_progress.current_level,
            completed_achievements=completed_achievements,
            active_challenges=len(challenges),
            longest_streak=longest_streak,
        )

        return GamificationOverview(
            user_points=user_points,
            user_level=level_progress,
            recent_badges=badges,
            active_achievements=[a for a in achievements if not a.is_completed][:5],
            active_challenges=challenges[:3],
            streaks=streaks[:3],
            gamification_stats=stats,
        )

    def get_daily_reward(self, user: User) -> Dict[str, any]:
        """获取每日奖励"""
        # 获取登录连续天数
        login_streak = (
            self.db.query(StreakRecord)
            .filter(
                StreakRecord.user_id == user.id, StreakRecord.streak_type == "login"
            )
            .first()
        )

        streak_days = login_streak.current_streak if login_streak else 1

        # 计算奖励
        base_points = 10
        streak_bonus = min(streak_days * 2, 50)  # 连续登录奖励，最高50
        total_points = base_points + streak_bonus

        # 特殊里程碑奖励
        bonus = None
        if streak_days in [7, 30, 100]:
            bonus = f"连续登录{streak_days}天特别奖励"

        return {
            "day": streak_days,
            "points": total_points,
            "base_points": base_points,
            "streak_bonus": streak_bonus,
            "bonus": bonus,
            "claimed": False,
        }

    def claim_daily_reward(self, user: User) -> PointsEarned:
        """领取每日奖励"""
        reward = self.get_daily_reward(user)

        # 更新登录连续记录
        self.update_streak(user, "login", "每日登录")

        # 授予积分
        return self.award_points(
            user,
            reward["points"],
            "daily_login",
            f"第{reward['day']}天登录奖励",
        )


def get_gamification_service(db: Session) -> GamificationService:
    """获取游戏化服务实例"""
    return GamificationService(db)
