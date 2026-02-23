"""趋势分析引擎服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import UserLongTermMemory
from app.services.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """趋势分析引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.memory_manager = MemoryManager(db)

    # ========== 体重趋势分析 ==========

    async def analyze_weight_trend(
        self, user_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """分析体重趋势

        返回：
        - current_weight: 当前体重（kg）
        - start_weight: 起始体重（kg）
        - change: 体重变化（kg）
        - change_rate: 变化率（%）
        - trend: 趋势方向（up/down/stable）
        - moving_average_7d: 7天移动平均
        - moving_average_30d: 30天移动平均
        - data_points: 数据点数量
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # 获取体重记录
            records = (
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

            if not records:
                return {
                    "success": False,
                    "error": "No weight data available",
                    "data_points": 0,
                }

            weights = [
                (r.record_date.date(), r.weight / 1000) for r in records
            ]  # 转换为kg

            # 计算当前体重（最新记录）
            current_weight = weights[-1][1]

            # 计算起始体重
            start_weight = weights[0][1]

            # 计算变化
            change = current_weight - start_weight
            change_rate = (change / start_weight * 100) if start_weight > 0 else 0

            # 计算趋势
            if change < -0.5:
                trend = "down"
            elif change > 0.5:
                trend = "up"
            else:
                trend = "stable"

            # 计算移动平均
            moving_average_7d = self._calculate_moving_average(weights, 7)
            moving_average_30d = self._calculate_moving_average(weights, 30)

            result = {
                "success": True,
                "current_weight": round(current_weight, 1),
                "start_weight": round(start_weight, 1),
                "change": round(change, 1),
                "change_rate": round(change_rate, 1),
                "trend": trend,
                "moving_average_7d": round(moving_average_7d, 1)
                if moving_average_7d
                else None,
                "moving_average_30d": round(moving_average_30d, 1)
                if moving_average_30d
                else None,
                "data_points": len(weights),
                "period_days": days,
                "analysis_date": date.today().isoformat(),
            }

            # 保存到记忆系统
            await self.memory_manager.create_memory(
                user_id=user_id,
                memory_type="health_trend",
                memory_key=f"weight_trend_{days}d",
                memory_value=result,
                importance_score=8.0,
            )

            return result

        except Exception as e:
            logger.error(f"分析体重趋势失败: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_moving_average(
        self, data: List[Tuple[date, float]], window: int
    ) -> Optional[float]:
        """计算移动平均"""
        if len(data) < window:
            return None

        # 取最后window个数据点
        recent_data = [d[1] for d in data[-window:]]
        return sum(recent_data) / len(recent_data)

    # ========== 运动趋势分析 ==========

    async def analyze_exercise_trend(
        self, user_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """分析运动趋势"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # 获取运动记录
            records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.exercise_minutes.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if not records:
                return {
                    "success": False,
                    "error": "No exercise data available",
                    "data_points": 0,
                }

            # 统计运动数据
            exercise_minutes = [r.exercise_minutes for r in records]
            total_minutes = sum(exercise_minutes)
            avg_minutes = total_minutes / len(exercise_minutes)
            max_minutes = max(exercise_minutes)

            # 计算运动天数
            exercise_days = len([m for m in exercise_minutes if m > 0])
            exercise_rate = (exercise_days / days * 100) if days > 0 else 0

            # 计算趋势（对比前后半段）
            mid_point = len(records) // 2
            first_half_avg = (
                sum(exercise_minutes[:mid_point]) / mid_point if mid_point > 0 else 0
            )
            second_half_avg = (
                sum(exercise_minutes[mid_point:]) / (len(records) - mid_point)
                if mid_point < len(records)
                else 0
            )

            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"

            # 按星期几统计
            weekly_pattern = self._analyze_weekly_pattern(records, "exercise_minutes")

            result = {
                "success": True,
                "total_minutes": total_minutes,
                "avg_minutes_per_day": round(avg_minutes, 1),
                "max_minutes": max_minutes,
                "exercise_days": exercise_days,
                "exercise_rate": round(exercise_rate, 1),
                "trend": trend,
                "first_half_avg": round(first_half_avg, 1),
                "second_half_avg": round(second_half_avg, 1),
                "weekly_pattern": weekly_pattern,
                "data_points": len(records),
                "period_days": days,
                "analysis_date": date.today().isoformat(),
            }

            # 保存到记忆系统
            await self.memory_manager.create_memory(
                user_id=user_id,
                memory_type="exercise_trend",
                memory_key=f"exercise_trend_{days}d",
                memory_value=result,
                importance_score=7.0,
            )

            return result

        except Exception as e:
            logger.error(f"分析运动趋势失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 饮食趋势分析 ==========

    async def analyze_diet_trend(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """分析饮食趋势"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # 获取饮食记录
            records = (
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

            if not records:
                return {
                    "success": False,
                    "error": "No diet data available",
                    "data_points": 0,
                }

            # 统计卡路里数据
            calories = [r.calories_intake for r in records]
            total_calories = sum(calories)
            avg_calories = total_calories / len(calories)
            max_calories = max(calories)
            min_calories = min(calories)

            # 计算趋势
            mid_point = len(records) // 2
            first_half_avg = (
                sum(calories[:mid_point]) / mid_point if mid_point > 0 else 0
            )
            second_half_avg = (
                sum(calories[mid_point:]) / (len(records) - mid_point)
                if mid_point < len(records)
                else 0
            )

            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"

            # 营养素分析
            protein = [r.protein_intake for r in records if r.protein_intake]
            carbs = [r.carbs_intake for r in records if r.carbs_intake]
            fat = [r.fat_intake for r in records if r.fat_intake]

            nutrition_avg = {}
            if protein:
                nutrition_avg["protein"] = round(sum(protein) / len(protein), 1)
            if carbs:
                nutrition_avg["carbs"] = round(sum(carbs) / len(carbs), 1)
            if fat:
                nutrition_avg["fat"] = round(sum(fat) / len(fat), 1)

            result = {
                "success": True,
                "total_calories": total_calories,
                "avg_calories_per_day": round(avg_calories, 1),
                "max_calories": max_calories,
                "min_calories": min_calories,
                "trend": trend,
                "first_half_avg": round(first_half_avg, 1),
                "second_half_avg": round(second_half_avg, 1),
                "nutrition_avg": nutrition_avg,
                "data_points": len(records),
                "period_days": days,
                "analysis_date": date.today().isoformat(),
            }

            # 保存到记忆系统
            await self.memory_manager.create_memory(
                user_id=user_id,
                memory_type="diet_trend",
                memory_key=f"diet_trend_{days}d",
                memory_value=result,
                importance_score=7.0,
            )

            return result

        except Exception as e:
            logger.error(f"分析饮食趋势失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 睡眠趋势分析 ==========

    async def analyze_sleep_trend(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """分析睡眠趋势"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # 获取睡眠记录
            records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.sleep_hours.isnot(None),
                    HealthRecord.record_date
                    >= datetime.combine(start_date, datetime.min.time()),
                    HealthRecord.record_date
                    <= datetime.combine(end_date, datetime.max.time()),
                )
                .order_by(HealthRecord.record_date)
                .all()
            )

            if not records:
                return {
                    "success": False,
                    "error": "No sleep data available",
                    "data_points": 0,
                }

            # 统计睡眠数据
            sleep_hours = [r.sleep_hours for r in records]
            avg_sleep = sum(sleep_hours) / len(sleep_hours)
            max_sleep = max(sleep_hours)
            min_sleep = min(sleep_hours)

            # 计算趋势
            mid_point = len(records) // 2
            first_half_avg = (
                sum(sleep_hours[:mid_point]) / mid_point if mid_point > 0 else 0
            )
            second_half_avg = (
                sum(sleep_hours[mid_point:]) / (len(records) - mid_point)
                if mid_point < len(records)
                else 0
            )

            if second_half_avg > first_half_avg + 0.5:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"

            # 睡眠质量评估
            if avg_sleep >= 7:
                quality = "good"
            elif avg_sleep >= 6:
                quality = "fair"
            else:
                quality = "poor"

            result = {
                "success": True,
                "avg_sleep_hours": round(avg_sleep, 1),
                "max_sleep_hours": round(max_sleep, 1),
                "min_sleep_hours": round(min_sleep, 1),
                "trend": trend,
                "quality": quality,
                "first_half_avg": round(first_half_avg, 1),
                "second_half_avg": round(second_half_avg, 1),
                "data_points": len(records),
                "period_days": days,
                "analysis_date": date.today().isoformat(),
            }

            # 保存到记忆系统
            await self.memory_manager.create_memory(
                user_id=user_id,
                memory_type="sleep_trend",
                memory_key=f"sleep_trend_{days}d",
                memory_value=result,
                importance_score=6.0,
            )

            return result

        except Exception as e:
            logger.error(f"分析睡眠趋势失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 习惯一致性分析 ==========

    async def analyze_habit_consistency(
        self, user_id: int, habit_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """分析习惯一致性"""
        try:
            # 获取习惯
            if habit_id:
                habits = (
                    self.db.query(Habit)
                    .filter(Habit.id == habit_id, Habit.user_id == user_id)
                    .all()
                )
            else:
                habits = (
                    self.db.query(Habit)
                    .filter(Habit.user_id == user_id, Habit.is_active == True)
                    .all()
                )

            if not habits:
                return {"success": False, "error": "No active habits found"}

            habit_stats = []

            for habit in habits:
                # 获取最近30天的完成记录
                end_date = date.today()
                start_date = end_date - timedelta(days=30)

                completions = (
                    self.db.query(HabitCompletion)
                    .filter(
                        HabitCompletion.habit_id == habit.id,
                        HabitCompletion.completion_date
                        >= datetime.combine(start_date, datetime.min.time()),
                        HabitCompletion.completion_date
                        <= datetime.combine(end_date, datetime.max.time()),
                    )
                    .all()
                )

                # 计算完成率
                completion_count = len(completions)
                completion_rate = (completion_count / 30 * 100) if 30 > 0 else 0

                # 计算连续完成天数
                streak = self._calculate_streak(habit.id)

                habit_stats.append(
                    {
                        "habit_id": habit.id,
                        "habit_name": habit.name,
                        "category": habit.category.value if habit.category else None,
                        "completion_count": completion_count,
                        "completion_rate": round(completion_rate, 1),
                        "current_streak": streak,
                        "total_completions": habit.total_completions or 0,
                        "target_value": habit.target_value,
                        "target_unit": habit.target_unit,
                    }
                )

            # 计算整体一致性
            overall_rate = (
                sum(h["completion_rate"] for h in habit_stats) / len(habit_stats)
                if habit_stats
                else 0
            )

            result = {
                "success": True,
                "habits": habit_stats,
                "overall_consistency": round(overall_rate, 1),
                "total_habits": len(habits),
                "analysis_date": date.today().isoformat(),
            }

            # 保存到记忆系统
            await self.memory_manager.create_memory(
                user_id=user_id,
                memory_type="habit_consistency",
                memory_key="habit_consistency_30d",
                memory_value=result,
                importance_score=7.0,
            )

            return result

        except Exception as e:
            logger.error(f"分析习惯一致性失败: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_streak(self, habit_id: int) -> int:
        """计算连续完成天数"""
        completions = (
            self.db.query(HabitCompletion)
            .filter(HabitCompletion.habit_id == habit_id)
            .order_by(HabitCompletion.completion_date.desc())
            .all()
        )

        if not completions:
            return 0

        streak = 0
        expected_date = date.today()

        for completion in completions:
            completion_date = completion.completion_date.date()

            # 允许今天或昨天的记录
            if (
                completion_date == expected_date
                or completion_date == expected_date - timedelta(days=1)
            ):
                streak += 1
                expected_date = completion_date - timedelta(days=1)
            elif completion_date < expected_date - timedelta(days=1):
                break

        return streak

    def _analyze_weekly_pattern(
        self, records: List[HealthRecord], field: str
    ) -> Dict[str, int]:
        """分析星期模式"""
        weekly = {i: 0 for i in range(7)}  # 0=Monday, 6=Sunday

        for record in records:
            day_of_week = record.record_date.weekday()
            value = getattr(record, field, None)
            if value:
                weekly[day_of_week] += value

        return weekly

    # ========== 综合趋势分析 ==========

    async def analyze_all_trends(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """综合趋势分析"""
        weight_trend = await self.analyze_weight_trend(user_id, days)
        exercise_trend = await self.analyze_exercise_trend(user_id, days)
        diet_trend = await self.analyze_diet_trend(user_id, days)
        sleep_trend = await self.analyze_sleep_trend(user_id, days)
        habit_consistency = await self.analyze_habit_consistency(user_id)

        # 生成综合评估
        assessment = self._generate_assessment(
            weight_trend, exercise_trend, diet_trend, sleep_trend, habit_consistency
        )

        return {
            "success": True,
            "user_id": user_id,
            "analysis_date": date.today().isoformat(),
            "period_days": days,
            "weight_trend": weight_trend,
            "exercise_trend": exercise_trend,
            "diet_trend": diet_trend,
            "sleep_trend": sleep_trend,
            "habit_consistency": habit_consistency,
            "overall_assessment": assessment,
        }

    def _generate_assessment(
        self, weight, exercise, diet, sleep, habits
    ) -> Dict[str, Any]:
        """生成综合评估"""
        scores = []

        # 体重评估
        if weight.get("success"):
            if weight.get("trend") == "down":
                scores.append(("体重", 90, "体重呈下降趋势，很好！"))
            elif weight.get("trend") == "stable":
                scores.append(("体重", 70, "体重保持稳定"))
            else:
                scores.append(("体重", 50, "体重有所上升，需要注意"))

        # 运动评估
        if exercise.get("success"):
            if exercise.get("trend") == "increasing":
                scores.append(("运动", 90, "运动量在增加，继续保持！"))
            elif exercise.get("exercise_rate", 0) > 50:
                scores.append(("运动", 80, "运动频率很好"))
            else:
                scores.append(("运动", 60, "建议增加运动频率"))

        # 饮食评估
        if diet.get("success"):
            if diet.get("trend") == "decreasing":
                scores.append(("饮食", 80, "卡路里摄入有所控制"))
            else:
                scores.append(("饮食", 70, "饮食控制良好"))

        # 睡眠评估
        if sleep.get("success"):
            if sleep.get("quality") == "good":
                scores.append(("睡眠", 90, "睡眠质量良好"))
            else:
                scores.append(("睡眠", 60, "建议改善睡眠"))

        # 习惯评估
        if habits.get("success"):
            overall = habits.get("overall_consistency", 0)
            if overall >= 80:
                scores.append(("习惯", 90, "习惯养成非常好"))
            elif overall >= 60:
                scores.append(("习惯", 75, "习惯养成不错"))
            else:
                scores.append(("习惯", 55, "需要加强习惯养成"))

        # 计算总分
        if scores:
            avg_score = sum(s[1] for s in scores) / len(scores)
        else:
            avg_score = 0

        return {
            "categories": scores,
            "overall_score": round(avg_score, 1),
            "recommendation": self._generate_recommendation(scores),
        }

    def _generate_recommendation(self, scores: List[Tuple[str, int, str]]) -> str:
        """生成建议"""
        low_scores = [s for s in scores if s[1] < 70]

        if not low_scores:
            return "继续保持当前状态，各项指标都很优秀！"

        recommendations = []
        for category, score, comment in low_scores:
            recommendations.append(comment)

        return " & ".join(recommendations)


def get_trend_analyzer(db: Session) -> TrendAnalyzer:
    """获取趋势分析器实例"""
    return TrendAnalyzer(db)
