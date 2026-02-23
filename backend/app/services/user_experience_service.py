"""用户体验优化服务"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.orm import Session

from app.core.cache import get_cache
from app.models.user import User

logger = structlog.get_logger()


class UserExperienceService:
    """用户体验优化服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_personalized_greeting(self, user: User) -> str:
        """获取个性化问候"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        elif 18 <= hour < 22:
            time_greeting = "晚上好"
        else:
            time_greeting = "夜深了"

        name = user.full_name or user.username

        # 根据用户活跃时间定制问候
        return f"{time_greeting}，{name}！"

    def get_daily_tip(self, user: User) -> Dict[str, str]:
        """获取每日提示"""
        # 根据用户数据和偏好提供个性化提示
        tips = [
            {
                "title": "健康小贴士",
                "content": "每天喝够8杯水可以帮助新陈代谢，建议起床后先喝一杯温水。",
                "category": "hydration",
            },
            {
                "title": "营养建议",
                "content": "每餐先吃蔬菜，再吃蛋白质，最后吃碳水化合物，有助于控制血糖。",
                "category": "nutrition",
            },
            {
                "title": "运动提醒",
                "content": "久坐1小时后，起来活动5分钟，可以显著降低健康风险。",
                "category": "exercise",
            },
            {
                "title": "睡眠优化",
                "content": "睡前1小时避免使用电子屏幕，可以提高睡眠质量。",
                "category": "sleep",
            },
            {
                "title": "正念练习",
                "content": "每天花3分钟做深呼吸练习，可以有效降低压力水平。",
                "category": "mindfulness",
            },
        ]

        # 根据星期几选择不同的提示
        day_of_week = datetime.now().weekday()
        return tips[day_of_week % len(tips)]

    def get_quick_actions(self, user: User) -> List[Dict[str, Any]]:
        """获取快速操作"""
        actions = [
            {
                "id": "record_weight",
                "title": "记录体重",
                "icon": "⚖️",
                "action": "/api/v1/health/records",
                "method": "POST",
            },
            {
                "id": "check_habits",
                "title": "完成习惯",
                "icon": "✅",
                "action": "/api/v1/habits/daily-checklist",
                "method": "GET",
            },
            {
                "id": "record_meal",
                "title": "记录饮食",
                "icon": "🥗",
                "action": "/api/v1/health/records",
                "method": "POST",
            },
            {
                "id": "emotion_check",
                "title": "情感签到",
                "icon": "😊",
                "action": "/api/v1/emotional-support/check-in",
                "method": "GET",
            },
        ]

        return actions

    def get_progress_summary(self, user: User) -> Dict[str, Any]:
        """获取进度摘要"""
        cache = get_cache()
        cache_key = f"progress_summary:{user.id}"

        cached = cache.get(cache_key)
        if cached:
            return cached

        # 获取各项进度
        from app.services.dashboard_service import get_dashboard_service
        from app.services.gamification_service import get_gamification_service

        dashboard_service = get_dashboard_service(self.db)
        gamification_service = get_gamification_service(self.db)

        try:
            overview = dashboard_service.get_overview(user)
            gamification = gamification_service.get_gamification_overview(user)

            summary = {
                "weight_progress": overview["user_info"]["weight_progress"].get(
                    "percentage", 0
                ),
                "habit_completion": overview["today_todos"]["completion_percentage"],
                "current_level": gamification.user_level.current_level,
                "total_points": gamification.user_points.total_points,
                "streak_days": gamification.gamification_stats.longest_streak,
                "badges_earned": gamification.gamification_stats.total_badges,
            }

            # 缓存5分钟
            cache.set(cache_key, summary, 300)

            return summary

        except Exception as e:
            logger.error(
                "Failed to get progress summary", user_id=user.id, error=str(e)
            )
            return {
                "weight_progress": 0,
                "habit_completion": 0,
                "current_level": 1,
                "total_points": 0,
                "streak_days": 0,
                "badges_earned": 0,
            }

    def get_recommended_next_steps(self, user: User) -> List[Dict[str, Any]]:
        """获取推荐的下一步行动"""
        recommendations = []

        # 检查今日习惯完成情况
        from app.services.habit_service import get_habit_service

        habit_service = get_habit_service(self.db)

        from datetime import date

        checklist = habit_service.get_daily_checklist(user, date.today())

        if checklist["completed_count"] < checklist["total_count"]:
            incomplete_habits = [
                h for h in checklist["habits"] if not h["is_completed"]
            ][:3]

            for habit in incomplete_habits:
                recommendations.append(
                    {
                        "type": "habit",
                        "priority": "high",
                        "title": f"完成习惯: {habit['name']}",
                        "action": f"/api/v1/habits/{habit['habit_id']}/completions",
                        "estimated_time": "5分钟",
                    }
                )

        # 检查是否记录今日体重
        from datetime import datetime

        from app.models.health_record import HealthRecord

        today_start = datetime.combine(date.today(), datetime.min.time())
        today_weight = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user.id,
                HealthRecord.record_date >= today_start,
                HealthRecord.weight.isnot(None),
            )
            .first()
        )

        if not today_weight:
            recommendations.append(
                {
                    "type": "health",
                    "priority": "medium",
                    "title": "记录今日体重",
                    "action": "/api/v1/health/records",
                    "estimated_time": "1分钟",
                }
            )

        # 检查情感记录
        from app.models.emotional_support import EmotionalState

        today_emotion = (
            self.db.query(EmotionalState)
            .filter(
                EmotionalState.user_id == user.id,
                EmotionalState.recorded_at >= today_start,
            )
            .first()
        )

        if not today_emotion:
            recommendations.append(
                {
                    "type": "emotional",
                    "priority": "low",
                    "title": "情感签到",
                    "action": "/api/v1/emotional-support/check-in",
                    "estimated_time": "2分钟",
                }
            )

        return recommendations[:5]

    def get_achievements_preview(self, user: User) -> List[Dict[str, Any]]:
        """获取成就预览"""
        from app.services.gamification_service import get_gamification_service

        gamification_service = get_gamification_service(self.db)

        try:
            achievements = gamification_service.get_user_achievements(
                user, completed_only=False
            )

            # 获取最接近完成的成就
            near_complete = [
                a
                for a in achievements
                if not a.is_completed and a.progress_percentage >= 50
            ][:3]

            return [
                {
                    "name": a.achievement_name,
                    "progress": round(a.progress_percentage, 1),
                    "remaining": a.target_value - a.current_value,
                    "reward_points": a.points_reward,
                }
                for a in near_complete
            ]

        except Exception as e:
            logger.error(
                "Failed to get achievements preview", user_id=user.id, error=str(e)
            )
            return []

    def generate_onboarding_flow(self, user: User) -> List[Dict[str, Any]]:
        """生成新手引导流程"""
        onboarding_steps = [
            {
                "step": 1,
                "title": "完善个人资料",
                "description": "设置您的身高、体重目标等基本信息",
                "action": "/api/v1/auth/me",
                "method": "PUT",
                "is_completed": bool(user.initial_weight and user.target_weight),
            },
            {
                "step": 2,
                "title": "记录第一次体重",
                "description": "开始追踪您的体重变化",
                "action": "/api/v1/health/records",
                "method": "POST",
                "is_completed": False,  # 需要检查
            },
            {
                "step": 3,
                "title": "创建第一个习惯",
                "description": "选择一个健康习惯开始培养",
                "action": "/api/v1/habits",
                "method": "POST",
                "is_completed": False,
            },
            {
                "step": 4,
                "title": "完成首次情感签到",
                "description": "了解自己的情绪状态",
                "action": "/api/v1/emotional-support/check-in",
                "method": "GET",
                "is_completed": False,
            },
            {
                "step": 5,
                "title": "查看科学报告",
                "description": "了解您的健康状况分析",
                "action": "/api/v1/scientific-persona/scientific-report",
                "method": "GET",
                "is_completed": False,
            },
        ]

        return onboarding_steps

    def get_notification_preferences(self, user: User) -> Dict[str, Any]:
        """获取通知偏好"""
        return {
            "reminders": {
                "weight": {"enabled": True, "time": "08:00"},
                "habits": {"enabled": True, "time": "09:00"},
                "meals": {"enabled": True, "time": ["08:00", "12:00", "18:00"]},
                "water": {"enabled": True, "interval": "every_2_hours"},
            },
            "motivational": {
                "daily_quote": True,
                "achievement_notifications": True,
                "streak_reminders": True,
            },
            "scientific": {
                "weekly_report": True,
                "progress_insights": True,
                "recommendation_updates": True,
            },
        }

    def get_app_tour_steps(self) -> List[Dict[str, Any]]:
        """获取应用导览步骤"""
        return [
            {
                "step": 1,
                "title": "欢迎",
                "description": "欢迎使用体重管理AI助手",
                "highlight": None,
            },
            {
                "step": 2,
                "title": "仪表板",
                "description": "在这里查看您的整体进度和今日任务",
                "highlight": "dashboard",
            },
            {
                "step": 3,
                "title": "习惯追踪",
                "description": "建立健康习惯，养成良好生活方式",
                "highlight": "habits",
            },
            {
                "step": 4,
                "title": "营养管理",
                "description": "记录饮食，获得个性化营养建议",
                "highlight": "nutrition",
            },
            {
                "step": 5,
                "title": "情感支持",
                "description": "关注心理健康，获得情感支持",
                "highlight": "emotional",
            },
            {
                "step": 6,
                "title": "开始吧",
                "description": "现在就开始您的健康之旅！",
                "highlight": None,
            },
        ]


def get_user_experience_service(db: Session) -> UserExperienceService:
    """获取用户体验服务实例"""
    return UserExperienceService(db)
