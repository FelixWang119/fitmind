from datetime import datetime, timedelta
from typing import Dict, List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.emotional_support import EmotionalState
from app.schemas.health_score import HealthScoreResponse

logger = structlog.get_logger()

router = APIRouter()


class HealthScoreService:
    """健康评分服务"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_health_score(self, user: UserModel) -> HealthScoreResponse:
        """计算综合健康评分"""
        logger.info("Calculating health score", user_id=user.id)

        # 计算各项子分数
        weight_score = self._calculate_weight_score(user)
        nutrition_score = self._calculate_nutrition_score(user)
        exercise_score = self._calculate_exercise_score(user)
        habit_score = self._calculate_habit_score(user)
        emotional_score = self._calculate_emotional_score(user)

        # 计算综合分数（加权平均）
        overall_score = (
            weight_score * 0.25
            + nutrition_score * 0.20
            + exercise_score * 0.20
            + habit_score * 0.20
            + emotional_score * 0.15
        )

        # 确定趋势
        trend = self._determine_trend(user)

        # 生成洞察和建议
        insights = self._generate_insights(
            weight_score,
            nutrition_score,
            exercise_score,
            habit_score,
            emotional_score,
            overall_score,
        )
        recommendations = self._generate_recommendations(
            weight_score, nutrition_score, exercise_score, habit_score, emotional_score
        )

        return HealthScoreResponse(
            overall_score=round(overall_score, 1),
            weight_score=round(weight_score, 1),
            nutrition_score=round(nutrition_score, 1),
            exercise_score=round(exercise_score, 1),
            habit_score=round(habit_score, 1),
            emotional_score=round(emotional_score, 1),
            trend=trend,
            insights=insights,
            recommendations=recommendations,
        )

    def _calculate_weight_score(self, user: UserModel) -> float:
        """计算体重管理分数"""
        # 获取最近30天的体重记录
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        weight_records = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user.id,
                HealthRecord.record_date >= thirty_days_ago,
                HealthRecord.weight.isnot(None),
            )
            .order_by(HealthRecord.record_date.desc())
            .all()
        )

        if len(weight_records) < 2:
            return 60.0  # 数据不足，返回基础分

        # 计算体重变化趋势
        latest_weight = weight_records[0].weight
        oldest_weight = weight_records[-1].weight

        if user.target_weight:
            # 如果有目标体重，计算进度
            if user.initial_weight:
                total_change_needed = user.initial_weight - user.target_weight
                current_change = user.initial_weight - latest_weight

                if total_change_needed > 0:  # 减重目标
                    progress = min(current_change / total_change_needed, 1.0)
                    score = 40 + (progress * 60)  # 40-100分
                else:  # 增重目标
                    progress = min(abs(current_change) / abs(total_change_needed), 1.0)
                    score = 40 + (progress * 60)
            else:
                score = 70.0
        else:
            # 没有目标体重，检查体重稳定性
            weights = [r.weight for r in weight_records]
            avg_weight = sum(weights) / len(weights)
            std_dev = (
                sum((w - avg_weight) ** 2 for w in weights) / len(weights)
            ) ** 0.5

            # 稳定性评分：波动越小分数越高
            if avg_weight > 0:
                cv = (std_dev / avg_weight) * 100
                if cv < 2:
                    score = 90.0
                elif cv < 5:
                    score = 75.0
                elif cv < 10:
                    score = 60.0
                else:
                    score = 40.0
            else:
                score = 70.0

        # 考虑记录频率
        record_frequency = len(weight_records) / 30  # 过去30天的记录频率
        if record_frequency >= 0.8:  # 每周至少5-6次
            score = min(score * 1.1, 100.0)
        elif record_frequency < 0.3:  # 每周少于2次
            score = score * 0.8

        return max(0, min(100, score))

    def _calculate_nutrition_score(self, user: UserModel) -> float:
        """计算营养摄入分数"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # 获取营养记录
        nutrition_records = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user.id,
                HealthRecord.record_date >= thirty_days_ago,
                or_(
                    HealthRecord.daily_calories.isnot(None),
                    HealthRecord.water_ml.isnot(None),
                ),
            )
            .all()
        )

        if not nutrition_records:
            return 50.0

        # 计算记录完整性
        total_days = 30
        recorded_days = len(set(r.record_date.date() for r in nutrition_records))
        completeness = recorded_days / total_days

        # 计算水分摄入评分
        water_scores = []
        for record in nutrition_records:
            if record.water_ml:
                # 假设目标水分摄入为2000ml
                water_ratio = min(record.water_ml / 2000, 1.5)  # 最多150%
                water_score = min(water_ratio * 100, 100)
                water_scores.append(water_score)

        avg_water_score = (
            sum(water_scores) / len(water_scores) if water_scores else 70.0
        )

        # 计算热量摄入稳定性
        calorie_records = [r for r in nutrition_records if r.daily_calories]
        if len(calorie_records) >= 7:
            calories = [r.daily_calories for r in calorie_records]
            avg_calories = sum(calories) / len(calories)

            # 检查是否在合理范围内（假设基础代谢+活动）
            if user.age and user.height and user.initial_weight:
                # 简单估算基础代谢率
                if user.gender == "male":
                    bmr = (
                        10 * user.initial_weight / 1000
                        + 6.25 * user.height
                        - 5 * user.age
                        + 5
                    )
                else:
                    bmr = (
                        10 * user.initial_weight / 1000
                        + 6.25 * user.height
                        - 5 * user.age
                        - 161
                    )

                # 考虑活动水平
                activity_multipliers = {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "very_active": 1.9,
                }

                tdee = bmr * activity_multipliers.get(
                    user.activity_level or "sedentary", 1.2
                )

                # 计算热量摄入与TDEE的偏差
                calorie_deviation = abs(avg_calories - tdee) / tdee
                if calorie_deviation < 0.1:
                    calorie_score = 90.0
                elif calorie_deviation < 0.2:
                    calorie_score = 75.0
                elif calorie_deviation < 0.3:
                    calorie_score = 60.0
                else:
                    calorie_score = 40.0
            else:
                calorie_score = 70.0
        else:
            calorie_score = 60.0

        # 综合评分
        score = (
            completeness * 30  # 记录完整性占30%
            + avg_water_score * 0.3  # 水分摄入占30%
            + calorie_score * 0.4  # 热量摄入占40%
        )

        return max(0, min(100, score))

    def _calculate_exercise_score(self, user: UserModel) -> float:
        """计算运动锻炼分数"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # 获取运动记录
        exercise_records = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user.id,
                HealthRecord.record_date >= thirty_days_ago,
                HealthRecord.steps.isnot(None),
            )
            .all()
        )

        if not exercise_records:
            return 50.0

        # 计算步数统计
        steps_list = [r.steps for r in exercise_records if r.steps]
        avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0

        # 步数评分
        if avg_steps >= 10000:
            step_score = 90.0
        elif avg_steps >= 7500:
            step_score = 75.0
        elif avg_steps >= 5000:
            step_score = 60.0
        elif avg_steps >= 3000:
            step_score = 50.0
        else:
            step_score = 30.0

        # 计算运动频率
        exercise_days = len(set(r.record_date.date() for r in exercise_records))
        frequency_ratio = exercise_days / 30

        if frequency_ratio >= 0.8:  # 每周5-6天
            frequency_score = 90.0
        elif frequency_ratio >= 0.6:  # 每周4-5天
            frequency_score = 75.0
        elif frequency_ratio >= 0.4:  # 每周3天
            frequency_score = 60.0
        elif frequency_ratio >= 0.2:  # 每周1-2天
            frequency_score = 40.0
        else:
            frequency_score = 20.0

        # 计算一致性（变异系数）
        if len(steps_list) >= 7:
            std_dev = (
                sum((s - avg_steps) ** 2 for s in steps_list) / len(steps_list)
            ) ** 0.5
            if avg_steps > 0:
                cv = (std_dev / avg_steps) * 100
                if cv < 30:
                    consistency_score = 90.0
                elif cv < 50:
                    consistency_score = 70.0
                elif cv < 80:
                    consistency_score = 50.0
                else:
                    consistency_score = 30.0
            else:
                consistency_score = 50.0
        else:
            consistency_score = 50.0

        # 综合评分
        score = (
            step_score * 0.4  # 步数占40%
            + frequency_score * 0.3  # 频率占30%
            + consistency_score * 0.3  # 一致性占30%
        )

        return max(0, min(100, score))

    def _calculate_habit_score(self, user: UserModel) -> float:
        """计算习惯养成分数"""
        # 获取活跃习惯
        active_habits = (
            self.db.query(Habit)
            .filter(Habit.user_id == user.id, Habit.is_active == True)
            .all()
        )

        if not active_habits:
            return 50.0

        habit_scores = []

        for habit in active_habits:
            # 获取最近30天的完成记录
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            completions = (
                self.db.query(HabitCompletion)
                .filter(
                    HabitCompletion.habit_id == habit.id,
                    HabitCompletion.completion_date >= thirty_days_ago,
                )
                .all()
            )

            # 计算完成率
            if habit.frequency == "daily":
                expected_completions = 30
            elif habit.frequency == "weekly":
                expected_completions = 4  # 大约4周
            else:  # monthly
                expected_completions = 1

            actual_completions = len(completions)
            completion_rate = (
                actual_completions / expected_completions
                if expected_completions > 0
                else 0
            )

            # 计算连击奖励
            streak_bonus = 0
            if habit.streak_days >= 30:
                streak_bonus = 20
            elif habit.streak_days >= 14:
                streak_bonus = 10
            elif habit.streak_days >= 7:
                streak_bonus = 5

            # 习惯分数
            habit_score = min(completion_rate * 100, 100) + streak_bonus
            habit_scores.append(min(habit_score, 100))

        # 平均习惯分数
        avg_habit_score = (
            sum(habit_scores) / len(habit_scores) if habit_scores else 50.0
        )

        # 考虑习惯多样性
        categories = set(habit.category for habit in active_habits)
        diversity_bonus = min(len(categories) * 5, 15)  # 最多15分

        score = avg_habit_score + diversity_bonus

        return max(0, min(100, score))

    def _calculate_emotional_score(self, user: UserModel) -> float:
        """计算情感健康分数"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # 获取情感记录
        emotional_states = (
            self.db.query(EmotionalState)
            .filter(
                EmotionalState.user_id == user.id,
                EmotionalState.recorded_at >= thirty_days_ago,
            )
            .all()
        )

        if not emotional_states:
            return 60.0  # 没有记录时返回中等分数

        # 计算平均情感强度（假设1-10分，越高越积极）
        positive_emotions = ["happy", "excited", "calm", "content", "grateful"]
        negative_emotions = ["sad", "angry", "anxious", "stressed", "tired"]

        positive_scores = []
        negative_scores = []

        for state in emotional_states:
            if state.emotion_type in positive_emotions:
                positive_scores.append(state.intensity)
            elif state.emotion_type in negative_emotions:
                negative_scores.append(state.intensity)

        # 计算积极情感比例
        total_states = len(emotional_states)
        positive_ratio = len(positive_scores) / total_states if total_states > 0 else 0

        # 计算情感稳定性
        all_intensities = [state.intensity for state in emotional_states]
        if len(all_intensities) >= 7:
            avg_intensity = sum(all_intensities) / len(all_intensities)
            std_dev = (
                sum((i - avg_intensity) ** 2 for i in all_intensities)
                / len(all_intensities)
            ) ** 0.5

            # 稳定性评分：波动越小分数越高
            if avg_intensity > 0:
                cv = (std_dev / avg_intensity) * 100
                if cv < 20:
                    stability_score = 90.0
                elif cv < 40:
                    stability_score = 70.0
                elif cv < 60:
                    stability_score = 50.0
                else:
                    stability_score = 30.0
            else:
                stability_score = 60.0
        else:
            stability_score = 60.0

        # 计算记录频率
        recorded_days = len(set(state.recorded_at.date() for state in emotional_states))
        frequency_ratio = recorded_days / 30

        # 综合评分
        score = (
            positive_ratio * 40  # 积极情感比例占40%
            + stability_score * 0.3  # 稳定性占30%
            + (frequency_ratio * 100) * 0.3  # 记录频率占30%
        )

        return max(0, min(100, score))

    def _determine_trend(self, user: UserModel) -> str:
        """确定健康趋势"""
        # 获取最近60天的健康记录用于趋势分析
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)

        # 这里简化处理，实际应该分析历史数据
        # 暂时返回稳定趋势
        return "stable"

    def _generate_insights(
        self,
        weight_score: float,
        nutrition_score: float,
        exercise_score: float,
        habit_score: float,
        emotional_score: float,
        overall_score: float,
    ) -> List[str]:
        """生成健康洞察"""
        insights = []

        if overall_score >= 90:
            insights.append("您的整体健康状况非常优秀！继续保持良好的生活习惯。")
        elif overall_score >= 75:
            insights.append("您的健康状况良好，仍有提升空间。")
        elif overall_score >= 60:
            insights.append("您的健康状况处于中等水平，建议关注薄弱环节。")
        else:
            insights.append("您的健康状况需要改善，建议制定具体的健康计划。")

        # 各项分数洞察
        if weight_score < 60:
            insights.append(
                "体重管理方面需要更多关注，建议定期记录体重并设定合理目标。"
            )

        if nutrition_score < 60:
            insights.append("营养摄入记录不够完整，建议每天记录饮食和水分摄入。")

        if exercise_score < 60:
            insights.append("运动锻炼频率或强度不足，建议增加日常活动量。")

        if habit_score < 60:
            insights.append("习惯养成需要加强，建议从简单习惯开始建立规律。")

        if emotional_score < 60:
            insights.append("情感健康需要关注，建议多记录情绪状态并寻找放松方式。")

        # 找出最强项和最弱项
        scores = {
            "体重管理": weight_score,
            "营养摄入": nutrition_score,
            "运动锻炼": exercise_score,
            "习惯养成": habit_score,
            "情感健康": emotional_score,
        }

        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])

        insights.append(f"您的{strongest[0]}表现最佳，继续保持！")
        insights.append(f"建议重点改善{weakest[0]}，这是提升整体健康的关键。")

        return insights[:5]  # 最多返回5条洞察

    def _generate_recommendations(
        self,
        weight_score: float,
        nutrition_score: float,
        exercise_score: float,
        habit_score: float,
        emotional_score: float,
    ) -> List[str]:
        """生成个性化建议"""
        recommendations = []

        # 通用建议
        recommendations.append("每天保持7-8小时充足睡眠，有助于身体恢复和代谢调节。")
        recommendations.append("保持均衡饮食，多吃蔬菜水果，控制加工食品摄入。")

        # 针对性建议
        if weight_score < 70:
            recommendations.append("建议每周测量体重2-3次，记录变化趋势。")
            recommendations.append("设定切实可行的体重目标，每周减重0.5-1公斤为宜。")

        if nutrition_score < 70:
            recommendations.append("每天记录饮食，关注热量和营养素摄入。")
            recommendations.append("确保每天饮水2000ml以上，分多次饮用。")

        if exercise_score < 70:
            recommendations.append("设定每日步数目标，建议从8000步开始逐步增加。")
            recommendations.append("每周进行3-5次中等强度运动，每次30分钟以上。")

        if habit_score < 70:
            recommendations.append("从1-2个简单习惯开始，建立稳定的日常规律。")
            recommendations.append("利用习惯打卡功能，记录完成情况并保持连续性。")

        if emotional_score < 70:
            recommendations.append("每天花5分钟记录情绪状态，提高自我觉察能力。")
            recommendations.append("尝试正念冥想或深呼吸练习，缓解压力改善情绪。")

        return recommendations[:5]  # 最多返回5条建议


def get_health_score_service(db: Session) -> HealthScoreService:
    """获取健康评分服务实例"""
    return HealthScoreService(db)


@router.get("/score", response_model=HealthScoreResponse)
async def get_health_score(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康综合评分"""
    logger.info("Getting health score", user_id=current_user.id)

    try:
        service = get_health_score_service(db)
        health_score = service.calculate_health_score(current_user)
        return health_score

    except Exception as e:
        logger.error(
            "Failed to calculate health score", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate health score",
        )
