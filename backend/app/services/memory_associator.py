"""记忆关联系统服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import DataAssociation, UserLongTermMemory

logger = logging.getLogger(__name__)


class MemoryAssociator:
    """记忆关联系统"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 时间关联检测 ==========

    async def detect_temporal_associations(self, user_id: int) -> List[Dict[str, Any]]:
        """检测时间关联"""
        try:
            associations = []
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            # 获取健康记录
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

            if len(records) < 10:
                return []

            # 分析运动与饮食的关联
            exercise_days = {}
            calorie_days = {}

            for record in records:
                day = record.record_date.date()

                if record.exercise_minutes and record.exercise_minutes > 0:
                    if day not in exercise_days:
                        exercise_days[day] = []
                    exercise_days[day].append(record.exercise_minutes)

                if record.calories_intake:
                    calorie_days[day] = record.calories_intake

            # 运动日后 exercise_then_low第二天饮食
            exercise_then_low_cal = 0
            exercise_then_normal_cal = 0

            for day, exercises in exercise_days.items():
                next_day = day + timedelta(days=1)
                if next_day in calorie_days:
                    avg_exercise = sum(exercises) / len(exercises)
                    if avg_exercise > 30:  # 高强度运动
                        if calorie_days[next_day] < 1800:
                            exercise_then_low_cal += 1
                        else:
                            exercise_then_normal_cal += 1

            if exercise_then_low_cal > 3:
                associations.append(
                    {
                        "type": "temporal",
                        "source": "exercise",
                        "target": "diet",
                        "description": "高强度运动后第二天会控制饮食",
                        "strength": min(0.9, exercise_then_low_cal / 10),
                        "evidence_count": exercise_then_low_cal,
                    }
                )

            # 周末饮食模式
            weekday_cal = []
            weekend_cal = []

            for record in records:
                if not record.calories_intake:
                    continue
                if record.record_date.weekday() >= 5:  # 周末
                    weekend_cal.append(record.calories_intake)
                else:
                    weekday_cal.append(record.calories_intake)

            if weekday_cal and weekend_cal:
                weekday_avg = sum(weekday_cal) / len(weekday_cal)
                weekend_avg = sum(weekend_cal) / len(weekend_cal)

                if weekend_avg > weekday_avg * 1.2:
                    associations.append(
                        {
                            "type": "temporal",
                            "source": "weekend",
                            "target": "diet",
                            "description": f"周末比工作日摄入更多卡路里 (周末:{int(weekend_avg)}kcal, 工作日:{int(weekday_avg)}kcal)",
                            "strength": min(0.9, (weekend_avg / weekday_avg - 1) * 2),
                            "evidence_count": len(weekend_cal) + len(weekday_cal),
                        }
                    )

            # 保存关联
            for assoc in associations:
                await self._save_association(user_id, assoc)

            return associations

        except Exception as e:
            logger.error(f"检测时间关联失败: {e}")
            return []

    # ========== 因果关联检测 ==========

    async def detect_causal_associations(self, user_id: int) -> List[Dict[str, Any]]:
        """检测因果关联"""
        try:
            associations = []
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            # 获取健康记录
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

            if len(records) < 14:
                return []

            # 分析运动与体重的因果关系
            exercise_days = []
            rest_days = []

            for i, record in enumerate(records[:-7]):  # 排除最后7天
                if record.exercise_minutes and record.exercise_minutes >= 30:
                    exercise_days.append(record)
                else:
                    rest_days.append(record)

            # 运动后体重变化
            if exercise_days:
                weight_after_exercise = []
                for record in exercise_days:
                    # 找接下来7天的体重记录
                    for later_record in records:
                        if (
                            later_record.record_date > record.record_date
                            and (later_record.record_date - record.record_date).days
                            <= 7
                            and later_record.weight
                        ):
                            weight_after_exercise.append(later_record.weight)
                            break

                if rest_days:
                    weight_after_rest = []
                    for record in rest_days:
                        for later_record in records:
                            if (
                                later_record.record_date > record.record_date
                                and (later_record.record_date - record.record_date).days
                                <= 7
                                and later_record.weight
                            ):
                                weight_after_rest.append(later_record.weight)
                                break

                    if weight_after_exercise and weight_after_rest:
                        avg_exercise = sum(weight_after_exercise) / len(
                            weight_after_exercise
                        )
                        avg_rest = sum(weight_after_rest) / len(weight_after_rest)

                        if avg_exercise < avg_rest - 200:  # 运动后体重下降超过0.2kg
                            associations.append(
                                {
                                    "type": "causal",
                                    "source": "exercise",
                                    "target": "weight",
                                    "description": "运动后体重有明显下降趋势",
                                    "strength": min(
                                        0.85, (avg_rest - avg_exercise) / 1000
                                    ),
                                    "evidence_count": len(weight_after_exercise),
                                }
                            )

            # 分析饮食与体重
            high_cal_days = []
            low_cal_days = []

            for record in records[:-7]:
                if not record.calories_intake or not record.weight:
                    continue
                if record.calories_intake > 2200:
                    high_cal_days.append(record)
                elif record.calories_intake < 1800:
                    low_cal_days.append(record)

            if high_cal_days and low_cal_days:
                # 高热量后体重
                high_cal_weight = []
                for record in high_cal_days:
                    for later_record in records:
                        if (
                            later_record.record_date > record.record_date
                            and (later_record.record_date - record.record_date).days
                            <= 7
                            and later_record.weight
                        ):
                            high_cal_weight.append(later_record.weight)
                            break

                # 低热量后体重
                low_cal_weight = []
                for record in low_cal_days:
                    for later_record in records:
                        if (
                            later_record.record_date > record.record_date
                            and (later_record.record_date - record.record_date).days
                            <= 7
                            and later_record.weight
                        ):
                            low_cal_weight.append(later_record.weight)
                            break

                if high_cal_weight and low_cal_weight:
                    avg_high = sum(high_cal_weight) / len(high_cal_weight)
                    avg_low = sum(low_cal_weight) / len(low_cal_weight)

                    if avg_high > avg_low + 200:
                        associations.append(
                            {
                                "type": "causal",
                                "source": "diet",
                                "target": "weight",
                                "description": "高热量摄入后体重上升，低热量摄入后体重下降",
                                "strength": min(0.8, (avg_high - avg_low) / 1000),
                                "evidence_count": len(high_cal_weight)
                                + len(low_cal_weight),
                            }
                        )

            # 保存关联
            for assoc in associations:
                await self._save_association(user_id, assoc)

            return associations

        except Exception as e:
            logger.error(f"检测因果关联失败: {e}")
            return []

    # ========== 相关性分析 ==========

    async def detect_correlative_associations(
        self, user_id: int
    ) -> List[Dict[str, Any]]:
        """检测统计相关性"""
        try:
            associations = []
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            # 获取健康记录
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

            if len(records) < 14:
                return []

            # 提取数据对
            sleep_exercise = [
                (r.sleep_hours, r.exercise_minutes)
                for r in records
                if r.sleep_hours and r.exercise_minutes
            ]

            stress_energy = [
                (r.stress_level, r.energy_level)
                for r in records
                if r.stress_level and r.energy_level
            ]

            exercise_calories = [
                (r.exercise_minutes, r.calories_intake)
                for r in records
                if r.exercise_minutes and r.calories_intake
            ]

            # 睡眠与运动相关性
            if len(sleep_exercise) >= 10:
                correlation = self._calculate_correlation(sleep_exercise)
                if correlation > 0.5:
                    associations.append(
                        {
                            "type": "correlative",
                            "source": "sleep",
                            "target": "exercise",
                            "description": "睡眠时长与运动量正相关",
                            "strength": correlation,
                            "evidence_count": len(sleep_exercise),
                        }
                    )
                elif correlation < -0.5:
                    associations.append(
                        {
                            "type": "correlative",
                            "source": "sleep",
                            "target": "exercise",
                            "description": "睡眠时长与运动量负相关",
                            "strength": abs(correlation),
                            "evidence_count": len(sleep_exercise),
                        }
                    )

            # 压力与能量相关性
            if len(stress_energy) >= 10:
                correlation = self._calculate_correlation(stress_energy)
                if correlation < -0.5:
                    associations.append(
                        {
                            "type": "correlative",
                            "source": "stress",
                            "target": "energy",
                            "description": "压力与能量水平负相关",
                            "strength": abs(correlation),
                            "evidence_count": len(stress_energy),
                        }
                    )

            # 运动与卡路里摄入相关性
            if len(exercise_calories) >= 10:
                correlation = self._calculate_correlation(exercise_calories)
                if correlation > 0.4:
                    associations.append(
                        {
                            "type": "correlative",
                            "source": "exercise",
                            "target": "diet",
                            "description": "运动时会摄入更多卡路里",
                            "strength": correlation,
                            "evidence_count": len(exercise_calories),
                        }
                    )

            # 保存关联
            for assoc in associations:
                await self._save_association(user_id, assoc)

            return associations

        except Exception as e:
            logger.error(f"检测相关性失败: {e}")
            return []

    def _calculate_correlation(self, data: List[tuple]) -> float:
        """计算简单相关系数"""
        if len(data) < 2:
            return 0

        x = [d[0] for d in data]
        y = [d[1] for d in data]

        n = len(data)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in data)
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)

        denominator = (
            (n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)
        ) ** 0.5

        if denominator == 0:
            return 0

        correlation = (n * sum_xy - sum_x * sum_y) / denominator

        return correlation

    # ========== 习惯关联 ==========

    async def detect_habit_associations(self, user_id: int) -> List[Dict[str, Any]]:
        """检测习惯之间的关联"""
        try:
            associations = []

            # 获取用户习惯
            habits = (
                self.db.query(Habit)
                .filter(Habit.user_id == user_id, Habit.is_active == True)
                .all()
            )

            if len(habits) < 2:
                return []

            # 分析习惯完成的时间关联
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            for i, habit1 in enumerate(habits):
                completions1 = (
                    self.db.query(HabitCompletion)
                    .filter(
                        HabitCompletion.habit_id == habit1.id,
                        HabitCompletion.completion_date
                        >= datetime.combine(start_date, datetime.min.time()),
                        HabitCompletion.completion_date
                        <= datetime.combine(end_date, datetime.max.time()),
                    )
                    .all()
                )

                dates1 = {c.completion_date.date() for c in completions1}

                for habit2 in habits[i + 1 :]:
                    completions2 = (
                        self.db.query(HabitCompletion)
                        .filter(
                            HabitCompletion.habit_id == habit2.id,
                            HabitCompletion.completion_date
                            >= datetime.combine(start_date, datetime.min.time()),
                            HabitCompletion.completion_date
                            <= datetime.combine(end_date, datetime.max.time()),
                        )
                        .all()
                    )

                    dates2 = {c.completion_date.date() for c in completions2}

                    # 计算同时完成的概率
                    same_day = len(dates1 & dates2)
                    total_days = len(dates1 | dates2)

                    if total_days > 0:
                        correlation = same_day / total_days

                        if correlation > 0.5:  # 超过50%同时完成
                            associations.append(
                                {
                                    "type": "habit_correlation",
                                    "source": "habit",
                                    "target": "habit",
                                    "source_id": habit1.id,
                                    "target_id": habit2.id,
                                    "description": f"「{habit1.name}」和「{habit2.name}」经常同时完成",
                                    "strength": correlation,
                                    "evidence_count": same_day,
                                }
                            )

            # 保存关联
            for assoc in associations:
                await self._save_association(user_id, assoc)

            return associations

        except Exception as e:
            logger.error(f"检测习惯关联失败: {e}")
            return []

    # ========== 关联保存 ==========

    async def _save_association(self, user_id: int, association: Dict[str, Any]):
        """保存关联到数据库"""
        try:
            # 检查是否已存在
            source_type = association.get("source", "")
            target_type = association.get("target", "")
            source_id = association.get("source_id", 0) or 0
            target_id = association.get("target_id", 0) or 0

            existing = (
                self.db.query(DataAssociation)
                .filter(
                    DataAssociation.user_id == user_id,
                    DataAssociation.source_type == source_type,
                    DataAssociation.target_type == target_type,
                )
                .first()
            )

            if existing:
                # 更新
                existing.strength = association.get("strength", 0.5)
                existing.association_type = association.get("type", "correlative")
                self.db.commit()
            else:
                # 创建
                new_assoc = DataAssociation(
                    user_id=user_id,
                    source_type=source_type,
                    source_id=source_id,
                    target_type=target_type,
                    target_id=target_id,
                    association_type=association.get("type", "correlative"),
                    strength=association.get("strength", 0.5),
                )
                self.db.add(new_assoc)
                self.db.commit()

        except Exception as e:
            logger.error(f"保存关联失败: {e}")
            self.db.rollback()

    # ========== 获取所有关联 ==========

    async def get_all_associations(
        self, user_id: int, min_strength: float = 0.3
    ) -> List[Dict[str, Any]]:
        """获取所有关联"""
        try:
            associations = (
                self.db.query(DataAssociation)
                .filter(
                    DataAssociation.user_id == user_id,
                    DataAssociation.strength >= min_strength,
                )
                .order_by(DataAssociation.strength.desc())
                .all()
            )

            result = []
            for assoc in associations:
                result.append(
                    {
                        "id": assoc.id,
                        "source_type": assoc.source_type,
                        "source_id": assoc.source_id,
                        "target_type": assoc.target_type,
                        "target_id": assoc.target_id,
                        "association_type": assoc.association_type,
                        "strength": assoc.strength,
                        "created_at": assoc.created_at.isoformat()
                        if assoc.created_at
                        else None,
                    }
                )

            return result

        except Exception as e:
            logger.error(f"获取关联失败: {e}")
            return []

    # ========== 综合关联检测 ==========

    async def detect_all_associations(self, user_id: int) -> Dict[str, Any]:
        """综合检测所有关联"""
        try:
            # 时间关联
            temporal = await self.detect_temporal_associations(user_id)

            # 因果关联
            causal = await self.detect_causal_associations(user_id)

            # 相关性
            correlative = await self.detect_correlative_associations(user_id)

            # 习惯关联
            habits = await self.detect_habit_associations(user_id)

            return {
                "success": True,
                "user_id": user_id,
                "detection_date": date.today().isoformat(),
                "temporal_associations": temporal,
                "causal_associations": causal,
                "correlative_associations": correlative,
                "habit_associations": habits,
                "total_associations": len(temporal)
                + len(causal)
                + len(correlative)
                + len(habits),
            }

        except Exception as e:
            logger.error(f"综合关联检测失败: {e}")
            return {"success": False, "error": str(e)}


def get_memory_associator(db: Session) -> MemoryAssociator:
    """获取记忆关联器实例"""
    return MemoryAssociator(db)
