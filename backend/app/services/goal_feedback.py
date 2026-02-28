"""
AI 目标反馈服务
Story 2.3: AI 反馈策略
根据用户目标完成情况生成智能反馈
"""

import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy.orm import Session

from app.models.goal import UserGoal, GoalProgress, GoalStatus


class FeedbackLevel(str, Enum):
    """反馈级别"""

    MILD = "mild"  # 轻微偏离 (1-2天)
    MODERATE = "moderate"  # 中度偏离 (3-5天)
    SEVERE = "severe"  # 严重偏离 (7天+)
    EXCEEDING = "exceeding"  # 超额完成
    COMPLETED = "completed"  # 达成目标
    NORMAL = "normal"  # 正常，无需反馈


class GoalFeedbackService:
    """AI 目标反馈服务"""

    # 消息模板配置
    MESSAGES = {
        "weight": {
            FeedbackLevel.MILD: [
                "今天还没记录体重哦，早起空腹称重最准确～",
                "记得记录今天的体重数据，这样才能更好地追踪进度呢！",
                "体重管理是每天的小坚持，记录一下看看变化吧！",
            ],
            FeedbackLevel.MODERATE: [
                "注意到这周体重记录少了，是有点忙吗？我们可以慢慢来～",
                "体重波动是正常的，关键是坚持记录。你遇到什么困难了吗？",
                "一周没记录啦～哪怕一周称一次也能追踪趋势呢！",
            ],
            FeedbackLevel.SEVERE: [
                "看起来体重记录暂停了一段时间。要不要我们一起重新制定计划？",
                "健康是一辈子的事情，我们可以调整目标让它更适合你现在的节奏。",
                "别给自己太大压力！哪怕从今天开始重新记录也很好～",
            ],
            FeedbackLevel.EXCEEDING: [
                "太棒了！体重下降趋势很稳定！你是怎么做到的？",
                "看到你的进步太开心了！继续保持这个节奏！",
                "减重效果不错！记得也要注意营养均衡哦～",
            ],
        },
        "exercise": {
            FeedbackLevel.MILD: [
                "今天还没记录运动哦，10分钟散步也算数～要一起完成今天的目标吗？",
                "哪怕站起来的几分钟也算运动！动起来吧 💪",
                "运动不需要很剧烈，舒展身体也很好～",
            ],
            FeedbackLevel.MODERATE: [
                "注意到这几天运动打卡少了，是遇到什么困难了吗？我们可以调整计划让它更容易坚持 🤗",
                "最近运动少了呢～是太累还是没时间？我们可以一起想个办法～",
                "哪怕每天5分钟也比不动好！今天试试？",
            ],
            FeedbackLevel.SEVERE: [
                "看起来当前的运动计划执行起来有些挑战。要不要我们一起重新调整目标？",
                "运动是长久的事，不用急于一时。我们可以从小目标开始～",
                "身体是革命的本钱！哪怕每天散步10分钟也很好哦～",
            ],
            FeedbackLevel.EXCEEDING: [
                "运动达人就是你！💪 连续超额完成，太厉害了！",
                "你是最棒的！看到你的努力我都忍不住要为你鼓掌了 👏",
                "太牛了！继续保持这个状态！你就是榜样！",
            ],
        },
        "diet": {
            FeedbackLevel.MILD: [
                "今天的三餐都记录了吗？哪怕少记一顿也能帮助我们了解饮食习惯～",
                "记得吃饭哦！哪怕简单记录也能帮助分析～",
                "今天的饮食记录了吗？哪怕随便记记也比不记好！",
            ],
            FeedbackLevel.MODERATE: [
                "最近饮食记录有点不规律，是外出就餐多了还是太忙了？我们可以一起看看怎么调整～",
                "饮食是健康的基石～哪怕偶尔没记录也不要紧，重要的是坚持下去！",
                "最近记录少了一些呢～是遇到什么困难了吗？",
            ],
            FeedbackLevel.SEVERE: [
                "饮食记录暂停了一段时间。健康的饮食习惯需要慢慢培养，我们可以从小的改变开始！",
                "别为偶尔的懈怠自责！从今天开始重新，一点点来记录吧～",
                "健康饮食是一辈子的事。我们可以一起制定更容易坚持的计划！",
            ],
            FeedbackLevel.EXCEEDING: [
                "饮食控制得非常好！你的意志力真的太强了！",
                "太厉害了！坚持健康饮食真的不容易，你做到了！",
                "看到你这么认真对待饮食，真的很感动！继续保持！",
            ],
        },
        "habit": {
            FeedbackLevel.MILD: [
                "今天的水喝够了吗？一杯水只需要 30 秒 💧",
                "记得休息哦！良好的睡眠也是健康的重要组成部分～",
                "今天的好习惯打卡了吗？哪怕只是一小步也是进步！",
            ],
            FeedbackLevel.MODERATE: [
                "最近睡眠记录有点少哦，是太忙了吗？哪怕提前 30 分钟上床也是进步呢～",
                "注意到最近习惯打卡少了～是有什么干扰因素吗？我们可以一起看看～",
                "好习惯的养成需要时间，偶尔中断很正常，重新开始就好！",
            ],
            FeedbackLevel.SEVERE: [
                "生活习惯的养成需要时间，我们可以一起制定一个更容易坚持的计划！",
                "健康是日积月累的～别着急，从最小的习惯开始重新培养吧！",
                "改变习惯不容易，但每一次尝试都是进步！我们可以慢慢来～",
            ],
            FeedbackLevel.EXCEEDING: [
                "你的生活习惯越来越健康了！为你骄傲！",
                "太棒了！看到你坚持得这么好，真的很感动！",
                "优秀！你的自律精神值得学习！继续保持！",
            ],
        },
    }

    # 庆祝消息 (所有类型通用)
    COMPLETION_MESSAGES = [
        "🎉 恭喜你达成目标！这是你努力的成果！接下来有什么新目标吗？",
        "太为你骄傲了！这一路走来不容易，你坚持下来了！现在可以好好奖励自己一下～",
        "你做到了！每一次进步都值得庆祝！接下来我们挑战更高的目标吧？",
        "🎊 太棒了！目标达成！这是你应得的！接下来有什么计划？",
        "👏 成功！你的努力得到了回报！为你感到骄傲！",
    ]

    # 首次记录提醒
    FIRST_RECORD_MESSAGES = {
        "weight": "开始记录体重吧！每天早起空腹称重最准确哦～",
        "exercise": "今天运动了吗？哪怕散步10分钟也算数！",
        "diet": "记得记录今天的饮食哦，这样我们才能更好地分析～",
        "habit": "今天的好习惯完成了吗？哪怕一小步也是进步！",
    }

    def __init__(self, db: Session):
        self.db = db

    def check_and_send_feedback(
        self, user_id: int, force: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        检查并生成反馈

        Args:
            user_id: 用户ID
            force: 是否强制检查（即使正常也返回）

        Returns:
            反馈列表，如果没有反馈则返回 None
        """
        # 获取用户所有活跃目标
        goals = (
            self.db.query(UserGoal)
            .filter(
                UserGoal.user_id == user_id,
                UserGoal.status == GoalStatus.ACTIVE.value,
            )
            .all()
        )

        feedback_results = []

        for goal in goals:
            feedback = self._analyze_goal(goal, force=force)
            if feedback:
                feedback_results.append(feedback)

        return feedback_results if feedback_results else None

    def _analyze_goal(
        self, goal: UserGoal, force: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        分析单个目标并生成反馈

        Args:
            goal: 目标对象
            force: 是否强制检查
        """
        # 获取最近进度 (最多14天)
        recent_progress = (
            self.db.query(GoalProgress)
            .filter(GoalProgress.goal_id == goal.goal_id)
            .order_by(GoalProgress.recorded_date.desc())
            .limit(14)
            .all()
        )

        # 如果没有进度记录
        if not recent_progress:
            days_since_start = (datetime.now() - goal.start_date).days
            if days_since_start >= 1:
                # 首次提醒
                return self._generate_feedback(
                    goal,
                    FeedbackLevel.MILD,
                    "首次记录提醒",
                    self.FIRST_RECORD_MESSAGES.get(
                        goal.goal_type, "开始记录你的目标吧！"
                    ),
                )
            return None

        # 分析连续达成/未达成天数
        consecutive_missed = 0
        consecutive_completed = 0
        total_days = len(recent_progress)

        for progress in recent_progress:
            if progress.daily_target_met:
                consecutive_completed += 1
                consecutive_missed = 0
            else:
                consecutive_missed += 1
                consecutive_completed = 0

        # 判断反馈级别
        if goal.status == GoalStatus.COMPLETED.value:
            level = FeedbackLevel.COMPLETED
            reason = "目标达成"
        elif consecutive_completed >= 14:
            level = FeedbackLevel.EXCEEDING
            reason = f"连续{consecutive_completed}天超额完成"
        elif consecutive_missed >= 7:
            level = FeedbackLevel.SEVERE
            reason = f"连续{consecutive_missed}天未达成"
        elif consecutive_missed >= 3:
            level = FeedbackLevel.MODERATE
            reason = f"连续{consecutive_missed}天未达成"
        elif consecutive_missed >= 1:
            level = FeedbackLevel.MILD
            reason = f"{consecutive_missed}天未达成"
        else:
            # 正常进度
            if force:
                return {
                    "goal_id": goal.goal_id,
                    "goal_type": goal.goal_type,
                    "level": FeedbackLevel.NORMAL.value,
                    "reason": "进度正常",
                    "message": "继续保持！💪",
                    "created_at": datetime.now(),
                }
            return None

        return self._generate_feedback(goal, level, reason)

    def _generate_feedback(
        self,
        goal: UserGoal,
        level: FeedbackLevel,
        reason: str,
        custom_message: str = None,
    ) -> Dict[str, Any]:
        """生成反馈消息"""
        if custom_message:
            message = custom_message
        elif level == FeedbackLevel.COMPLETED:
            message = random.choice(self.COMPLETION_MESSAGES)
        else:
            messages = self.MESSAGES.get(goal.goal_type, {}).get(level, [])
            message = random.choice(messages) if messages else "继续加油！💪"

        return {
            "goal_id": goal.goal_id,
            "goal_type": goal.goal_type,
            "level": level.value,
            "reason": reason,
            "message": message,
            "created_at": datetime.now(),
        }

    def get_feedback_summary(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户反馈摘要

        用于前端展示
        """
        goals = (
            self.db.query(UserGoal)
            .filter(
                UserGoal.user_id == user_id,
                UserGoal.status == GoalStatus.ACTIVE.value,
            )
            .all()
        )

        summary = {
            "total_goals": len(goals),
            "on_track": 0,
            "needs_attention": 0,
            "exceeding": 0,
            "feedback": [],
        }

        for goal in goals:
            feedback = self._analyze_goal(goal, force=True)
            if feedback:
                if feedback["level"] == FeedbackLevel.EXCEEDING.value:
                    summary["exceeding"] += 1
                elif feedback["level"] == FeedbackLevel.NORMAL.value:
                    summary["on_track"] += 1
                else:
                    summary["needs_attention"] += 1
                    summary["feedback"].append(feedback)

        # 按严重程度排序
        priority = {
            FeedbackLevel.SEVERE.value: 0,
            FeedbackLevel.MODERATE.value: 1,
            FeedbackLevel.MILD.value: 2,
        }
        summary["feedback"].sort(key=lambda x: priority.get(x["level"], 99))

        return summary
