"""里程碑检测器服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import UserLongTermMemory
from app.models.user import User

logger = logging.getLogger(__name__)


class MilestoneDetector:
    """里程碑检测器"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 目标达成检测 ==========

    async def check_weight_goal(self, user_id: int) -> Optional[Dict[str, Any]]:
        """检测体重目标达成"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user or not user.target_weight:
                return None

            # 获取最新体重
            latest_record = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id, HealthRecord.weight.isnot(None)
                )
                .order_by(HealthRecord.record_date.desc())
                .first()
            )

            if not latest_record:
                return None

            current_weight = latest_record.weight
            target_weight = user.target_weight
            initial_weight = user.initial_weight

            # 计算进度
            if initial_weight and initial_weight != target_weight:
                total_change_needed = initial_weight - target_weight
                current_change = initial_weight - current_weight
                progress = (
                    (current_change / total_change_needed * 100)
                    if total_change_needed != 0
                    else 0
                )
            else:
                progress = 0

            # 检查是否达成目标
            goal_reached = False
            if target_weight > initial_weight:
                # 增重目标
                goal_reached = current_weight >= target_weight
            else:
                # 减重目标
                goal_reached = current_weight <= target_weight

            # 检查里程碑
            milestones = []

            if progress >= 100:
                milestones.append(
                    {
                        "type": "goal_reached",
                        "title": "🎉 目标达成！",
                        "description": f"恭喜！您已达成目标体重 {target_weight / 1000}kg",
                    }
                )
            elif progress >= 75:
                milestones.append(
                    {
                        "type": "milestone_75",
                        "title": "🔥 进度75%",
                        "description": "距离目标只差25%了！",
                    }
                )
            elif progress >= 50:
                milestones.append(
                    {
                        "type": "milestone_50",
                        "title": "💪 进度50%",
                        "description": "已完成一半，继续加油！",
                    }
                )
            elif progress >= 25:
                milestones.append(
                    {
                        "type": "milestone_25",
                        "title": "🌟 进度25%",
                        "description": "良好的开始，继续保持！",
                    }
                )

            return {
                "user_id": user_id,
                "current_weight": current_weight / 1000,
                "target_weight": target_weight / 1000,
                "initial_weight": initial_weight / 1000 if initial_weight else None,
                "progress": round(progress, 1),
                "goal_reached": goal_reached,
                "milestones": milestones,
                "last_check": date.today().isoformat(),
            }

        except Exception as e:
            logger.error(f"检测体重目标失败: {e}")
            return None

    # ========== 连续记录检测 ==========

    async def check_streak_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """检测连续记录里程碑"""
        try:
            milestones = []

            # 检查每个活跃习惯的连续记录
            habits = (
                self.db.query(Habit)
                .filter(Habit.user_id == user_id, Habit.is_active == True)
                .all()
            )

            for habit in habits:
                streak = habit.streak_days or 0

                # 检查连续记录里程碑
                if streak >= 30:
                    milestones.append(
                        {
                            "type": "streak_30",
                            "habit_id": habit.id,
                            "habit_name": habit.name,
                            "streak_days": streak,
                            "title": f"🏆 30天连续记录！",
                            "description": f"您已连续30天完成「{habit.name}」！",
                        }
                    )
                elif streak >= 14:
                    milestones.append(
                        {
                            "type": "streak_14",
                            "habit_id": habit.id,
                            "habit_name": habit.name,
                            "streak_days": streak,
                            "title": f"⭐ 14天连续记录",
                            "description": f"您已连续14天完成「{habit.name}」！",
                        }
                    )
                elif streak >= 7:
                    milestones.append(
                        {
                            "type": "streak_7",
                            "habit_id": habit.id,
                            "habit_name": habit.name,
                            "streak_days": streak,
                            "title": f"🔥 7天连续记录",
                            "description": f"您已连续7天完成「{habit.name}」！",
                        }
                    )

            return milestones

        except Exception as e:
            logger.error(f"检测连续记录里程碑失败: {e}")
            return []

    # ========== 突破性进展检测 ==========

    async def check_breakthrough_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """检测突破性进展里程碑"""
        try:
            milestones = []
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            # 检查体重突破
            weight_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.weight.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if len(weight_records) >= 7:
                # 检查是否持续下降
                weights = [r.weight for r in weight_records]
                if weights[-1] < weights[0] - 1000:  # 下降超过1kg
                    total_change = (weights[0] - weights[-1]) / 1000
                    milestones.append(
                        {
                            "type": "weight_breakthrough",
                            "title": "💪 体重突破！",
                            "description": f"过去30天体重下降了{total_change:.1f}kg！",
                        }
                    )

            # 检查运动突破
            exercise_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.exercise_minutes.isnot(None),
                    HealthRecord.exercise_minutes > 0,
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .all()
            )

            if len(exercise_records) >= 20:  # 一个月运动超过20天
                milestones.append(
                    {
                        "type": "exercise_consistency",
                        "title": "🏃 运动达人！",
                        "description": f"过去30天您运动了{len(exercise_records)}天！",
                    }
                )

            # 检查饮食改善
            diet_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.calories_intake.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if len(diet_records) >= 14:
                first_half = diet_records[: len(diet_records) // 2]
                second_half = diet_records[len(diet_records) // 2 :]

                first_avg = sum(r.calories_intake for r in first_half) / len(first_half)
                second_avg = sum(r.calories_intake for r in second_half) / len(
                    second_half
                )

                if second_avg < first_avg * 0.9:  # 卡路里减少超过10%
                    reduction = (1 - second_avg / first_avg) * 100
                    milestones.append(
                        {
                            "type": "diet_improvement",
                            "title": "🥗 饮食改善！",
                            "description": f"您的日均卡路里摄入减少了{int(reduction)}%",
                        }
                    )

            return milestones

        except Exception as e:
            logger.error(f"检测突破性进展失败: {e}")
            return []

    # ========== 负面趋势预警 ==========

    async def check_warning_signs(self, user_id: int) -> List[Dict[str, Any]]:
        """检测负面趋势并预警"""
        try:
            warnings = []
            end_date = date.today()
            start_date = end_date - timedelta(days=14)

            # 检查体重反弹
            weight_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.weight.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if len(weight_records) >= 3:
                weights = [r.weight for r in weight_records]
                # 检查是否连续上升
                if weights[-1] > weights[0] + 500:  # 上升超过0.5kg
                    warnings.append(
                        {
                            "type": "weight_gain_warning",
                            "title": "⚠️ 体重回升提醒",
                            "description": "近期体重有所上升，请注意饮食控制",
                            "severity": "medium",
                        }
                    )

            # 检查打卡中断
            habits = (
                self.db.query(Habit)
                .filter(
                    Habit.user_id == user_id,
                    Habit.is_active == True,
                    Habit.streak_days > 0,
                )
                .all()
            )

            for habit in habits:
                if habit.streak_days < 3:
                    recent_completions = (
                        self.db.query(HabitCompletion)
                        .filter(
                            HabitCompletion.habit_id == habit.id,
                            HabitCompletion.completion_date
                            >= datetime.combine(
                                end_date - timedelta(days=3), datetime.min.time()
                            ),
                        )
                        .count()
                    )

                    if recent_completions == 0:
                        warnings.append(
                            {
                                "type": "habit_interruption",
                                "title": "📌 打卡提醒",
                                "description": f"您已连续{habit.streak_days}天未完成「{habit.name}」",
                                "severity": "low",
                            }
                        )

            # 检查运动减少
            exercise_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.exercise_minutes.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .all()
            )

            if len(exercise_records) >= 7:
                avg_exercise = sum(
                    r.exercise_minutes for r in exercise_records if r.exercise_minutes
                ) / len(exercise_records)

                if avg_exercise < 15:  # 每天平均运动少于15分钟
                    warnings.append(
                        {
                            "type": "low_activity",
                            "title": "🏃 增加运动提醒",
                            "description": "近期运动量较少，建议每天保持适量运动",
                            "severity": "medium",
                        }
                    )

            return warnings

        except Exception as e:
            logger.error(f"检测预警信号失败: {e}")
            return []

    # ========== 综合里程碑检测 ==========

    async def detect_all_milestones(self, user_id: int) -> Dict[str, Any]:
        """综合检测所有里程碑"""
        try:
            # 目标达成
            weight_goal = await self.check_weight_goal(user_id)

            # 连续记录
            streak_milestones = await self.check_streak_milestones(user_id)

            # 突破性进展
            breakthroughs = await self.check_breakthrough_milestones(user_id)

            # 负面预警
            warnings = await self.check_warning_signs(user_id)

            return {
                "success": True,
                "user_id": user_id,
                "detection_date": date.today().isoformat(),
                "weight_goal": weight_goal,
                "streak_milestones": streak_milestones,
                "breakthroughs": breakthroughs,
                "warnings": warnings,
                "total_milestones": len(streak_milestones) + len(breakthroughs),
                "total_warnings": len(warnings),
            }

        except Exception as e:
            logger.error(f"综合里程碑检测失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 特殊里程碑检测 ==========

    async def check_special_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """检测特殊里程碑"""
        try:
            milestones = []

            # 获取用户总习惯完成次数
            total_completions = (
                self.db.query(func.count(HabitCompletion.id))
                .join(Habit)
                .filter(Habit.user_id == user_id)
                .scalar()
                or 0
            )

            # 习惯完成里程碑
            if total_completions >= 100:
                milestones.append(
                    {
                        "type": "completions_100",
                        "title": "🎯 100次完成！",
                        "description": "您已完成100次习惯打卡！",
                    }
                )
            elif total_completions >= 50:
                milestones.append(
                    {
                        "type": "completions_50",
                        "title": "⭐ 50次完成",
                        "description": "您已完成50次习惯打卡！",
                    }
                )
            elif total_completions >= 10:
                milestones.append(
                    {
                        "type": "completions_10",
                        "title": "🌟 10次完成",
                        "description": "您已完成10次习惯打卡！",
                    }
                )

            # 获取用户健康记录天数
            record_days = (
                self.db.query(func.count(func.distinct(HealthRecord.record_date)))
                .filter(HealthRecord.user_id == user_id)
                .scalar()
                or 0
            )

            # 持续记录里程碑
            if record_days >= 30:
                milestones.append(
                    {
                        "type": "records_30",
                        "title": "📊 30天持续记录！",
                        "description": "您已持续记录健康数据30天！",
                    }
                )
            elif record_days >= 7:
                milestones.append(
                    {
                        "type": "records_7",
                        "title": "📈 7天持续记录",
                        "description": "您已持续记录健康数据7天！",
                    }
                )

            return milestones

        except Exception as e:
            logger.error(f"检测特殊里程碑失败: {e}")
            return []


def get_milestone_detector(db: Session) -> MilestoneDetector:
    """获取里程碑检测器实例"""
    return MilestoneDetector(db)
