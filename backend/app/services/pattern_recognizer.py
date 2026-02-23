"""模式识别引擎服务"""

import json
import logging
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import HabitPattern, UserLongTermMemory
from app.services.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """模式识别引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.memory_manager = MemoryManager(db)

    # ========== 习惯模式检测 ==========

    async def detect_weekly_pattern(
        self, user_id: int, habit_id: int
    ) -> Optional[Dict[str, Any]]:
        """检测周模式（周末vs工作日）"""
        try:
            habit = (
                self.db.query(Habit)
                .filter(Habit.id == habit_id, Habit.user_id == user_id)
                .first()
            )

            if not habit:
                return None

            # 获取最近30天的完成记录
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            completions = (
                self.db.query(HabitCompletion)
                .filter(
                    HabitCompletion.habit_id == habit_id,
                    HabitCompletion.completion_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HabitCompletion.completion_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .all()
            )

            if len(completions) < 7:
                return None

            # 统计工作日和周末的完成率
            weekday_completions = 0
            weekend_completions = 0
            weekday_total = 0
            weekend_total = 0

            for day_offset in range(30):
                current_date = end_date - timedelta(days=day_offset)
                is_weekend = current_date.weekday() >= 5  # 5=Saturday, 6=Sunday

                # 检查这天是否有完成记录
                has_completion = any(
                    c.completion_date.date() == current_date for c in completions
                )

                if is_weekend:
                    weekend_total += 1
                    if has_completion:
                        weekend_completions += 1
                else:
                    weekday_total += 1
                    if has_completion:
                        weekday_completions += 1

            weekday_rate = (
                weekday_completions / weekday_total if weekday_total > 0 else 0
            )
            weekend_rate = (
                weekend_completions / weekend_total if weekend_total > 0 else 0
            )

            # 判断模式
            if weekday_rate > 0.7 and weekend_rate < 0.3:
                pattern_type = "weekday_focused"
                description = "主要在工作日完成，周末较少"
            elif weekend_rate > 0.7 and weekday_rate < 0.3:
                pattern_type = "weekend_focused"
                description = "主要在周末完成，工作日较少"
            elif weekday_rate > weekend_rate * 1.3:
                pattern_type = "weekday_preferred"
                description = "更倾向于在工作日完成"
            elif weekend_rate > weekday_rate * 1.3:
                pattern_type = "weekend_preferred"
                description = "更倾向于在周末完成"
            else:
                pattern_type = "balanced"
                description = "工作日和周末完成率相近"

            # 计算置信度
            confidence = abs(weekday_rate - weekend_rate)

            result = {
                "pattern_type": pattern_type,
                "description": description,
                "weekday_rate": round(weekday_rate * 100, 1),
                "weekend_rate": round(weekend_rate * 100, 1),
                "confidence": round(confidence, 2),
                "habit_id": habit_id,
                "habit_name": habit.name,
            }

            # 保存到数据库
            await self._save_pattern(
                user_id=user_id,
                habit_id=habit_id,
                pattern_type=pattern_type,
                pattern_data=result,
                confidence=confidence,
            )

            return result

        except Exception as e:
            logger.error(f"检测周模式失败: {e}")
            return None

    async def detect_time_based_pattern(
        self, user_id: int, habit_id: int
    ) -> Optional[Dict[str, Any]]:
        """检测时间模式（每天完成的时间）"""
        try:
            habit = (
                self.db.query(Habit)
                .filter(Habit.id == habit_id, Habit.user_id == user_id)
                .first()
            )

            if not habit:
                return None

            # 获取完成记录
            completions = (
                self.db.query(HabitCompletion)
                .filter(HabitCompletion.habit_id == habit_id)
                .order_by(HabitCompletion.completion_date)
                .all()
            )

            if len(completions) < 5:
                return None

            # 统计完成时间分布
            morning = 0  # 6-12
            afternoon = 0  # 12-18
            evening = 0  # 18-24
            night = 0  # 0-6

            for completion in completions:
                hour = completion.completion_date.hour
                if 6 <= hour < 12:
                    morning += 1
                elif 12 <= hour < 18:
                    afternoon += 1
                elif 18 <= hour < 24:
                    evening += 1
                else:
                    night += 1

            total = len(completions)
            rates = {
                "morning": morning / total,
                "afternoon": afternoon / total,
                "evening": evening / total,
                "night": night / total,
            }

            # 找出主要时间
            main_time = max(rates, key=rates.get)

            if rates[main_time] > 0.7:
                pattern_type = f"{main_time}_focused"
                description = f"主要在{main_time}完成"
            elif rates[main_time] > 0.5:
                pattern_type = f"{main_time}_preferred"
                description = f"更倾向于在{main_time}完成"
            else:
                pattern_type = "varied"
                description = "完成时间较分散"

            confidence = rates[main_time]

            result = {
                "pattern_type": pattern_type,
                "description": description,
                "time_distribution": {
                    "morning": round(rates["morning"] * 100, 1),
                    "afternoon": round(rates["afternoon"] * 100, 1),
                    "evening": round(rates["evening"] * 100, 1),
                    "night": round(rates["night"] * 100, 1),
                },
                "main_time": main_time,
                "confidence": round(confidence, 2),
                "habit_id": habit_id,
                "habit_name": habit.name,
            }

            # 保存到数据库
            await self._save_pattern(
                user_id=user_id,
                habit_id=habit_id,
                pattern_type=pattern_type,
                pattern_data=result,
                confidence=confidence,
            )

            return result

        except Exception as e:
            logger.error(f"检测时间模式失败: {e}")
            return None

    async def detect_trigger_pattern(
        self, user_id: int, habit_id: int
    ) -> Optional[Dict[str, Any]]:
        """检测触发模式（习惯之间的关联）"""
        try:
            # 获取该习惯的完成记录
            completions = (
                self.db.query(HabitCompletion)
                .filter(HabitCompletion.habit_id == habit_id)
                .order_by(HabitCompletion.completion_date)
                .all()
            )

            if len(completions) < 10:
                return None

            # 获取用户的其他习惯
            other_habits = (
                self.db.query(Habit)
                .filter(
                    Habit.user_id == user_id,
                    Habit.id != habit_id,
                    Habit.is_active == True,
                )
                .all()
            )

            if not other_habits:
                return None

            # 分析与其他习惯的时间关联
            habit_completion_dates = {c.completion_date.date() for c in completions}

            correlations = []

            for other_habit in other_habits:
                other_completions = (
                    self.db.query(HabitCompletion)
                    .filter(HabitCompletion.habit_id == other_habit.id)
                    .all()
                )

                other_dates = {c.completion_date.date() for c in other_completions}

                # 计算同时完成的概率
                same_day = len(habit_completion_dates & other_dates)
                correlation = (
                    same_day / len(habit_completion_dates)
                    if habit_completion_dates
                    else 0
                )

                if correlation > 0.3:  # 超过30%的概率
                    correlations.append(
                        {
                            "habit_id": other_habit.id,
                            "habit_name": other_habit.name,
                            "correlation": round(correlation * 100, 1),
                        }
                    )

            if not correlations:
                return None

            # 按相关性排序
            correlations.sort(key=lambda x: x["correlation"], reverse=True)

            result = {
                "pattern_type": "trigger_based",
                "description": f"与{correlations[0]['habit_name']}关联性最强",
                "correlations": correlations[:3],
                "confidence": correlations[0]["correlation"] / 100,
                "habit_id": habit_id,
            }

            # 保存到数据库
            await self._save_pattern(
                user_id=user_id,
                habit_id=habit_id,
                pattern_type="trigger_based",
                pattern_data=result,
                confidence=correlations[0]["correlation"] / 100,
            )

            return result

        except Exception as e:
            logger.error(f"检测触发模式失败: {e}")
            return None

    # ========== 健康数据模式 ==========

    async def detect_behavioral_patterns(self, user_id: int) -> List[Dict[str, Any]]:
        """检测综合行为模式"""
        try:
            patterns = []

            # 获取用户的所有活跃习惯
            habits = (
                self.db.query(Habit)
                .filter(Habit.user_id == user_id, Habit.is_active == True)
                .all()
            )

            for habit in habits:
                # 检测周模式
                weekly_pattern = await self.detect_weekly_pattern(user_id, habit.id)
                if weekly_pattern:
                    patterns.append(weekly_pattern)

                # 检测时间模式
                time_pattern = await self.detect_time_based_pattern(user_id, habit.id)
                if time_pattern:
                    patterns.append(time_pattern)

                # 检测触发模式
                trigger_pattern = await self.detect_trigger_pattern(user_id, habit.id)
                if trigger_pattern:
                    patterns.append(trigger_pattern)

            return patterns

        except Exception as e:
            logger.error(f"检测行为模式失败: {e}")
            return []

    # ========== 饮食/运动模式 ==========

    async def detect_diet_exercise_pattern(
        self, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """检测饮食与运动的关联模式"""
        try:
            # 获取最近30天的健康记录
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if len(records) < 10:
                return None

            # 分析高热量日后第二天的运动模式
            high_cal_days = []
            normal_cal_days = []

            avg_calories = sum(
                r.calories_intake for r in records if r.calories_intake
            ) / len(records)

            for i, record in enumerate(records):
                if (
                    record.calories_intake
                    and record.calories_intake > avg_calories * 1.2
                ):
                    high_cal_days.append(record)
                else:
                    normal_cal_days.append(record)

            # 分析高热量日后第二天的运动
            high_cal_exercise = []
            normal_cal_exercise = []

            for i, record in enumerate(records[:-1]):
                next_record = records[i + 1]

                if (
                    record.calories_intake
                    and record.calories_intake > avg_calories * 1.2
                ):
                    if next_record.exercise_minutes:
                        high_cal_exercise.append(next_record.exercise_minutes)
                else:
                    if next_record.exercise_minutes:
                        normal_cal_exercise.append(next_record.exercise_minutes)

            if high_cal_exercise and normal_cal_exercise:
                high_avg = sum(high_cal_exercise) / len(high_cal_exercise)
                normal_avg = sum(normal_cal_exercise) / len(normal_cal_exercise)

                if high_avg > normal_avg * 1.3:
                    pattern = "compensatory_exercise"
                    description = "高热量摄入后第二天会增加运动"
                elif normal_avg > high_avg * 1.3:
                    pattern = "preemptive_exercise"
                    description = "在预计高热量摄入前会增加运动"
                else:
                    pattern = "independent"
                    description = "饮食和运动相对独立"
            else:
                pattern = "insufficient_data"
                description = "数据不足以分析"

            result = {
                "pattern_type": pattern,
                "description": description,
                "avg_calories": round(avg_calories, 1),
                "high_cal_days_count": len(high_cal_days),
                "normal_cal_days_count": len(normal_cal_days),
                "analysis_date": date.today().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"检测饮食运动模式失败: {e}")
            return None

    # ========== 情绪模式 ==========

    async def detect_mood_patterns(self, user_id: int) -> Optional[Dict[str, Any]]:
        """检测情绪模式"""
        try:
            # 获取健康记录中的压力和能量数据
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .all()
            )

            stress_levels = [r.stress_level for r in records if r.stress_level]
            energy_levels = [r.energy_level for r in records if r.energy_level]

            if not stress_levels or not energy_levels:
                return None

            avg_stress = sum(stress_levels) / len(stress_levels)
            avg_energy = sum(energy_levels) / len(energy_levels)

            # 分析压力和能量的相关性
            stress_energy_pairs = [
                (r.stress_level, r.energy_level)
                for r in records
                if r.stress_level and r.energy_level
            ]

            # 简单相关分析
            high_stress_low_energy = sum(
                1 for s, e in stress_energy_pairs if s > 7 and e < 5
            )

            if high_stress_low_energy > len(stress_energy_pairs) * 0.3:
                pattern = "stress_drains_energy"
                description = "高压力时能量水平较低"
            elif avg_stress > 6:
                pattern = "chronic_stress"
                description = "长期处于较高压力状态"
            elif avg_energy > 7:
                pattern = "high_energy"
                description = "整体能量水平较好"
            else:
                pattern = "balanced"
                description = "压力和能量处于平衡状态"

            result = {
                "pattern_type": pattern,
                "description": description,
                "avg_stress_level": round(avg_stress, 1),
                "avg_energy_level": round(avg_energy, 1),
                "high_stress_days": len([s for s in stress_levels if s > 7]),
                "data_points": len(stress_levels),
                "analysis_date": date.today().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"检测情绪模式失败: {e}")
            return None

    # ========== 辅助方法 ==========

    async def _save_pattern(
        self,
        user_id: int,
        habit_id: int,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float,
    ):
        """保存模式到数据库"""
        try:
            today = date.today()

            # 检查是否已存在
            existing = (
                self.db.query(HabitPattern)
                .filter(
                    HabitPattern.user_id == user_id,
                    HabitPattern.habit_id == habit_id,
                    HabitPattern.pattern_type == pattern_type,
                )
                .first()
            )

            if existing:
                # 更新
                existing.pattern_data = json.dumps(pattern_data, ensure_ascii=False)
                existing.confidence_score = confidence
                existing.last_observed = today
                existing.observation_count += 1
                self.db.commit()
            else:
                # 创建
                pattern = HabitPattern(
                    user_id=user_id,
                    habit_id=habit_id,
                    pattern_type=pattern_type,
                    pattern_data=json.dumps(pattern_data, ensure_ascii=False),
                    confidence_score=confidence,
                    first_detected=today,
                    last_observed=today,
                    observation_count=1,
                )
                self.db.add(pattern)
                self.db.commit()

        except Exception as e:
            logger.error(f"保存模式失败: {e}")
            self.db.rollback()

    async def get_pattern_summary(self, user_id: int) -> Dict[str, Any]:
        """获取模式摘要"""
        try:
            patterns = (
                self.db.query(HabitPattern)
                .filter(HabitPattern.user_id == user_id)
                .all()
            )

            summary = {
                "total_patterns": len(patterns),
                "by_type": {},
                "high_confidence": [],
            }

            for pattern in patterns:
                # 按类型统计
                ptype = pattern.pattern_type
                if ptype not in summary["by_type"]:
                    summary["by_type"][ptype] = 0
                summary["by_type"][ptype] += 1

                # 高置信度模式
                if pattern.confidence_score >= 0.7:
                    summary["high_confidence"].append(
                        {
                            "habit_id": pattern.habit_id,
                            "pattern_type": ptype,
                            "confidence": pattern.confidence_score,
                            "last_observed": pattern.last_observed.isoformat()
                            if pattern.last_observed
                            else None,
                        }
                    )

            return summary

        except Exception as e:
            logger.error(f"获取模式摘要失败: {e}")
            return {"error": str(e)}


def get_pattern_recognizer(db: Session) -> PatternRecognizer:
    """获取模式识别器实例"""
    return PatternRecognizer(db)
