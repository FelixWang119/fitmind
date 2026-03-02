"""里程碑检测服务

负责检测各种类型的里程碑并触发相应的通知
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion, HabitGoal
from app.models.notification import EventLog, NotificationChannel
from app.services.notification.notification_service import NotificationService

logger = logging.getLogger(__name__)


class MilestoneType:
    """里程碑类型常量"""

    # 连续打卡天数里程碑
    STREAK_3_DAYS = "streak_3_days"
    STREAK_7_DAYS = "streak_7_days"
    STREAK_14_DAYS = "streak_14_days"
    STREAK_30_DAYS = "streak_30_days"
    STREAK_60_DAYS = "streak_60_days"
    STREAK_90_DAYS = "streak_90_days"

    # 累计记录里程碑
    TOTAL_10_RECORDS = "total_10_records"
    TOTAL_50_RECORDS = "total_50_records"
    TOTAL_100_RECORDS = "total_100_records"

    # 目标达成里程碑
    GOAL_ACHIEVED = "goal_achieved"


# 里程碑定义配置
STREAK_MILESTONES = [
    {
        "type": MilestoneType.STREAK_3_DAYS,
        "days": 3,
        "emoji": "🌟",
        "title": "3天坚持",
        "badge": "初出茅庐",
    },
    {
        "type": MilestoneType.STREAK_7_DAYS,
        "days": 7,
        "emoji": "🔥",
        "title": "一周坚持",
        "badge": "小有所成",
    },
    {
        "type": MilestoneType.STREAK_14_DAYS,
        "days": 14,
        "emoji": "💪",
        "title": "两周坚持",
        "badge": "持之以恒",
    },
    {
        "type": MilestoneType.STREAK_30_DAYS,
        "days": 30,
        "emoji": "🏆",
        "title": "一个月坚持",
        "badge": "习惯养成者",
    },
    {
        "type": MilestoneType.STREAK_60_DAYS,
        "days": 60,
        "emoji": "🌟",
        "title": "两个月坚持",
        "badge": "坚持不懈",
    },
    {
        "type": MilestoneType.STREAK_90_DAYS,
        "days": 90,
        "emoji": "💎",
        "title": "三个月坚持",
        "badge": "习惯大师",
    },
]

TOTAL_RECORDS_MILESTONES = [
    {
        "type": MilestoneType.TOTAL_10_RECORDS,
        "count": 10,
        "emoji": "📝",
        "title": "累计10次",
        "badge": "记录达人",
    },
    {
        "type": MilestoneType.TOTAL_50_RECORDS,
        "count": 50,
        "emoji": "📚",
        "title": "累计50次",
        "badge": "记录高手",
    },
    {
        "type": MilestoneType.TOTAL_100_RECORDS,
        "count": 100,
        "emoji": "🎖️",
        "title": "累计100次",
        "badge": "记录大师",
    },
]


class MilestoneService:
    """里程碑检测服务"""

    # 用于去重的key前缀
    DEDUP_PREFIX = "milestone"

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def check_and_notify_milestones(
        self,
        habit: Habit,
        trigger_type: str = "completion",
        goal: Optional[HabitGoal] = None,
    ) -> List[Dict[str, Any]]:
        """
        检测并通知里程碑

        Args:
            habit: 习惯对象
            trigger_type: 触发类型 ("completion", "streak_update", "goal_achieved")
            goal: 目标对象（可选，用于目标达成里程碑）

        Returns:
            List[Dict]: 达成的里程碑列表
        """
        achieved_milestones = []

        # 检测连续打卡里程碑
        if trigger_type in ["completion", "streak_update"]:
            streak_milestones = self._check_streak_milestones(habit)
            achieved_milestones.extend(streak_milestones)

        # 检测累计记录里程碑
        if trigger_type == "completion":
            total_milestones = self._check_total_records_milestones(habit)
            achieved_milestones.extend(total_milestones)

        # 检测目标达成里程碑
        if trigger_type == "goal_achieved" and goal:
            goal_milestone = self._check_goal_milestone(habit, goal)
            if goal_milestone:
                achieved_milestones.append(goal_milestone)

        return achieved_milestones

    def _check_streak_milestones(self, habit: Habit) -> List[Dict[str, Any]]:
        """检测连续打卡天数里程碑"""
        achieved = []
        current_streak = habit.streak_days

        for milestone in STREAK_MILESTONES:
            if current_streak >= milestone["days"]:
                # 检查是否已发送过通知（通过去重key）
                dedup_key = f"{self.DEDUP_PREFIX}:{habit.id}:streak:{milestone['days']}"

                # 检查事件日志中是否已存在
                existing = (
                    self.db.query(EventLog)
                    .filter(
                        EventLog.user_id == habit.user_id,
                        EventLog.deduplication_key == dedup_key,
                        EventLog.notification_status.in_(["sent", "pending"]),
                    )
                    .first()
                )

                if not existing:
                    # 创建里程碑通知
                    milestone_data = {
                        "milestone_type": milestone["type"],
                        "milestone_days": milestone["days"],
                        "emoji": milestone["emoji"],
                        "badge": milestone["badge"],
                        "title": milestone["title"],
                        "habit_id": habit.id,
                        "habit_name": habit.name,
                        "current_streak": current_streak,
                    }

                    self._send_milestone_notification(
                        habit.user_id, milestone_data, dedup_key, habit
                    )

                    achieved.append(milestone_data)
                    logger.info(
                        f"Streak milestone achieved: user={habit.user_id}, habit={habit.name}, days={milestone['days']}"
                    )

        return achieved

    def _check_total_records_milestones(self, habit: Habit) -> List[Dict[str, Any]]:
        """检测累计记录里程碑"""
        achieved = []
        total_completions = habit.total_completions

        for milestone in TOTAL_RECORDS_MILESTONES:
            if total_completions >= milestone["count"]:
                # 检查是否已发送过通知
                dedup_key = f"{self.DEDUP_PREFIX}:{habit.id}:total:{milestone['count']}"

                existing = (
                    self.db.query(EventLog)
                    .filter(
                        EventLog.user_id == habit.user_id,
                        EventLog.deduplication_key == dedup_key,
                        EventLog.notification_status.in_(["sent", "pending"]),
                    )
                    .first()
                )

                if not existing:
                    milestone_data = {
                        "milestone_type": milestone["type"],
                        "milestone_count": milestone["count"],
                        "emoji": milestone["emoji"],
                        "badge": milestone["badge"],
                        "title": milestone["title"],
                        "habit_id": habit.id,
                        "habit_name": habit.name,
                        "total_completions": total_completions,
                    }

                    self._send_milestone_notification(
                        habit.user_id, milestone_data, dedup_key, habit
                    )

                    achieved.append(milestone_data)
                    logger.info(
                        f"Total records milestone achieved: user={habit.user_id}, habit={habit.name}, count={milestone['count']}"
                    )

        return achieved

    def _check_goal_milestone(
        self, habit: Habit, goal: HabitGoal
    ) -> Optional[Dict[str, Any]]:
        """检测目标达成里程碑"""
        if not goal.is_achieved:
            return None

        # 检查是否已发送过通知
        dedup_key = f"{self.DEDUP_PREFIX}:goal:{goal.id}"

        existing = (
            self.db.query(EventLog)
            .filter(
                EventLog.user_id == goal.user_id,
                EventLog.deduplication_key == dedup_key,
                EventLog.notification_status.in_(["sent", "pending"]),
            )
            .first()
        )

        if existing:
            return None

        # 根据目标类型确定里程碑信息
        goal_type_display = {
            "completion_rate": "完成率",
            "streak": "连续天数",
            "total_count": "累计次数",
        }.get(goal.goal_type, "目标")

        milestone_data = {
            "milestone_type": MilestoneType.GOAL_ACHIEVED,
            "emoji": "🎯",
            "badge": "目标达成",
            "title": f"{goal_type_display}目标达成",
            "habit_id": habit.id,
            "habit_name": habit.name,
            "goal_id": goal.id,
            "goal_type": goal.goal_type,
            "target_value": goal.target_value,
            "current_progress": goal.current_progress,
            "period": goal.period,
        }

        self._send_milestone_notification(
            goal.user_id, milestone_data, dedup_key, habit
        )

        logger.info(
            f"Goal milestone achieved: user={goal.user_id}, habit={habit.name}, goal_id={goal.id}"
        )

        return milestone_data

    def _send_milestone_notification(
        self,
        user_id: int,
        milestone_data: Dict[str, Any],
        dedup_key: str,
        habit: Habit,
    ):
        """发送里程碑通知"""
        try:
            # 创建事件日志
            self.notification_service.create_event_log(
                user_id=user_id,
                event_type="milestone.achieved",
                event_data=milestone_data,
                business_type="habit",
                business_id=str(habit.id),
                deduplication_key=dedup_key,
            )

            # 直接发送通知（简化的实现方式）
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果在异步环境中，创建新任务
                import nest_asyncio

                nest_asyncio.apply()

            # 同步方式发送通知
            self._send_sync_notification(user_id, milestone_data)

        except Exception as e:
            logger.error(f"Failed to send milestone notification: {e}")

    def _send_sync_notification(self, user_id: int, milestone_data: Dict[str, Any]):
        """同步发送里程碑通知"""
        emoji = milestone_data.get("emoji", "🎉")
        badge = milestone_data.get("badge", "")
        habit_name = milestone_data.get("habit_name", "")
        title = milestone_data.get("title", "里程碑达成")

        # 构建通知内容
        content = (
            f"{emoji} 恭喜！你已达成「{habit_name}」{title}，获得「{badge}」徽章！"
        )

        # 构建元数据（用于前端展示徽章）
        metadata = {
            "milestone": True,
            "badge": badge,
            "emoji": emoji,
            "milestone_type": milestone_data.get("milestone_type"),
        }

        # 添加额外的里程碑信息
        if "current_streak" in milestone_data:
            metadata["streak_days"] = milestone_data["current_streak"]
        if "total_completions" in milestone_data:
            metadata["total_count"] = milestone_data["total_completions"]
        if "goal_id" in milestone_data:
            metadata["goal_id"] = milestone_data["goal_id"]

        try:
            # 同步方式创建通知记录
            from app.models.notification import (
                Notification,
                NotificationStatus,
                NotificationChannel,
            )

            notification = Notification(
                user_id=user_id,
                notification_type="milestone.achieved",
                title=f"{emoji} {title}",
                content=content,
                channel=NotificationChannel.IN_APP,
                status=NotificationStatus.SENT,
                metadata_=metadata,
            )

            self.db.add(notification)
            self.db.commit()

            logger.info(
                f"Milestone notification sent: user={user_id}, milestone={milestone_data.get('milestone_type')}"
            )

        except Exception as e:
            logger.error(f"Failed to create milestone notification: {e}")
            self.db.rollback()

    def get_user_milestones(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """获取用户已解锁的所有里程碑"""
        from app.models.notification import EventLog

        # 获取所有里程碑相关的事件日志
        events = (
            self.db.query(EventLog)
            .filter(
                EventLog.user_id == user_id,
                EventLog.event_type == "milestone.achieved",
                EventLog.notification_status == "sent",
            )
            .order_by(EventLog.occurred_at.desc())
            .all()
        )

        milestones = {
            "streak": [],
            "total_records": [],
            "goal": [],
        }

        for event in events:
            data = event.event_data
            milestone_type = data.get("milestone_type", "")

            if "streak" in milestone_type:
                milestones["streak"].append(data)
            elif "total_" in milestone_type:
                milestones["total_records"].append(data)
            elif "goal" in milestone_type:
                milestones["goal"].append(data)

        return milestones


def get_milestone_service(db: Session) -> MilestoneService:
    """获取里程碑服务实例"""
    return MilestoneService(db)
