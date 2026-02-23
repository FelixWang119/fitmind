import json
import math
from datetime import date, datetime, timedelta
from statistics import mean, median, stdev
from typing import Any, Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.emotional_support import EmotionalState, StressLevel
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.user import User
from app.services.emotional_support_service import EmotionalSupportService
from app.services.habit_service import HabitService
from app.services.nutrition_service import NutritionService

logger = structlog.get_logger()


class ScientificPersonaService:
    """科学量化人设服务"""

    def __init__(self, db: Session):
        self.db = db
        self.nutrition_service = NutritionService(db)
        self.habit_service = HabitService(db)
        self.emotional_service = EmotionalSupportService(db)

    def generate_scientific_report(self, user: User, days: int = 30) -> Dict[str, Any]:
        """生成科学报告"""
        logger.info("Generating scientific report", user_id=user.id, days=days)

        # 体重分析
        weight_analysis = self._analyze_weight_scientifically(user, days)

        # 营养分析
        nutrition_analysis = self._analyze_nutrition_scientifically(user, days)

        # 行为分析
        behavior_analysis = self._analyze_behavior_scientifically(user, days)

        # 心理分析
        psychological_analysis = self._analyze_psychological_scientifically(user, days)

        # 综合健康评分
        health_score = self._calculate_comprehensive_health_score(
            weight_analysis,
            nutrition_analysis,
            behavior_analysis,
            psychological_analysis,
        )

        # 生成循证建议
        evidence_based_recommendations = self._generate_evidence_based_recommendations(
            weight_analysis,
            nutrition_analysis,
            behavior_analysis,
            psychological_analysis,
        )

        return {
            "report_type": "科学量化健康报告",
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "user_profile": {
                "bmi": self._calculate_bmi(user),
                "bmi_category": self._get_bmi_category(user),
                "metabolic_age": self._estimate_metabolic_age(user),
                "health_risk_level": self._assess_health_risk(user),
            },
            "weight_analysis": weight_analysis,
            "nutrition_analysis": nutrition_analysis,
            "behavior_analysis": behavior_analysis,
            "psychological_analysis": psychological_analysis,
            "comprehensive_health_score": health_score,
            "evidence_based_recommendations": evidence_based_recommendations,
            "data_quality_assessment": self._assess_data_quality(user, days),
        }

    def _analyze_weight_scientifically(self, user: User, days: int) -> Dict[str, Any]:
        """科学分析体重数据"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        records = (
            self.db.query(HealthRecord)
            .filter(
                and_(
                    HealthRecord.user_id == user.id,
                    HealthRecord.weight.isnot(None),
                    HealthRecord.record_date >= start_date,
                    HealthRecord.record_date <= end_date,
                )
            )
            .order_by(HealthRecord.record_date.asc())
            .all()
        )

        if not records:
            return {
                "data_available": False,
                "message": "期间内无体重记录",
                "recommendation": "建议每日同一时间称重，以获得准确趋势分析",
            }

        weights = [r.weight for r in records]
        dates = [r.record_date for r in records]

        # 基础统计
        current_weight = weights[-1]
        initial_weight = weights[0]
        weight_change = current_weight - initial_weight
        weight_change_percent = (
            (weight_change / initial_weight) * 100 if initial_weight > 0 else 0
        )

        # 统计分析
        avg_weight = mean(weights)
        weight_std = stdev(weights) if len(weights) > 1 else 0
        weight_cv = (weight_std / avg_weight) * 100 if avg_weight > 0 else 0  # 变异系数

        # 趋势分析
        trend = self._calculate_weight_trend(weights, dates)

        # 波动性分析
        daily_changes = [weights[i] - weights[i - 1] for i in range(1, len(weights))]
        avg_daily_change = mean(daily_changes) if daily_changes else 0
        volatility = stdev(daily_changes) if len(daily_changes) > 1 else 0

        # 目标进度
        target_progress = self._calculate_target_progress(user, current_weight)

        return {
            "data_available": True,
            "record_count": len(records),
            "current_weight_kg": round(current_weight / 1000, 2),
            "initial_weight_kg": round(initial_weight / 1000, 2),
            "weight_change_kg": round(weight_change / 1000, 2),
            "weight_change_percent": round(weight_change_percent, 2),
            "statistics": {
                "mean_weight_kg": round(avg_weight / 1000, 2),
                "std_deviation_kg": round(weight_std / 1000, 3),
                "coefficient_of_variation": round(weight_cv, 2),
                "median_weight_kg": round(median(weights) / 1000, 2),
                "min_weight_kg": round(min(weights) / 1000, 2),
                "max_weight_kg": round(max(weights) / 1000, 2),
            },
            "trend_analysis": trend,
            "volatility": {
                "daily_change_avg_g": round(avg_daily_change, 1),
                "volatility_index": round(volatility, 2),
                "stability_assessment": "稳定"
                if volatility < 200
                else "中等波动"
                if volatility < 500
                else "高波动",
            },
            "target_progress": target_progress,
            "clinical_significance": self._assess_clinical_significance(
                weight_change_percent, days
            ),
        }

    def _calculate_weight_trend(
        self, weights: List[int], dates: List[datetime]
    ) -> Dict[str, Any]:
        """计算体重趋势（线性回归）"""
        if len(weights) < 2:
            return {"trend": "数据不足", "slope": 0, "r_squared": 0}

        n = len(weights)
        sum_x = sum(range(n))
        sum_y = sum(weights)
        sum_xy = sum(i * weights[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))

        # 线性回归斜率
        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            if (n * sum_x2 - sum_x * sum_x) != 0
            else 0
        )

        # 计算R²
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in weights)
        ss_res = sum(
            (weights[i] - (slope * i + (sum_y - slope * sum_x) / n)) ** 2
            for i in range(n)
        )
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # 趋势判断
        slope_g_per_day = slope
        if slope_g_per_day < -50:
            trend = "快速下降"
        elif slope_g_per_day < -20:
            trend = "稳定下降"
        elif slope_g_per_day < 20:
            trend = "稳定"
        elif slope_g_per_day < 50:
            trend = "轻微上升"
        else:
            trend = "上升"

        # 预测
        days_to_target = None
        if (
            user := self.db.query(User)
            .filter(
                User.id
                == self.db.query(HealthRecord)
                .filter(HealthRecord.weight.in_(weights))
                .first()
                .user_id
            )
            .first()
        ):
            if user.target_weight and slope_g_per_day < 0:
                current_weight = weights[-1]
                remaining = current_weight - user.target_weight
                days_to_target = (
                    abs(remaining / slope_g_per_day) if slope_g_per_day != 0 else None
                )

        return {
            "trend": trend,
            "slope_g_per_day": round(slope_g_per_day, 2),
            "r_squared": round(r_squared, 3),
            "trend_reliability": "高"
            if r_squared > 0.7
            else "中"
            if r_squared > 0.4
            else "低",
            "predicted_days_to_target": round(days_to_target, 0)
            if days_to_target and days_to_target < 365
            else None,
        }

    def _calculate_target_progress(
        self, user: User, current_weight: int
    ) -> Dict[str, Any]:
        """计算目标进度"""
        if not user.initial_weight or not user.target_weight:
            return {"has_goal": False}

        total_to_lose = user.initial_weight - user.target_weight
        lost_so_far = user.initial_weight - current_weight

        if total_to_lose <= 0:
            return {"has_goal": False, "message": "目标设置不合理"}

        percentage = (lost_so_far / total_to_lose) * 100
        remaining = total_to_lose - lost_so_far

        # 评估健康减重速度
        weeks_elapsed = (datetime.utcnow() - user.created_at).days / 7
        avg_weekly_loss = (
            (lost_so_far / 1000) / weeks_elapsed if weeks_elapsed > 0 else 0
        )

        if 0.25 <= avg_weekly_loss <= 1.0:
            pace_assessment = "健康速度"
        elif avg_weekly_loss < 0.25:
            pace_assessment = "偏慢"
        else:
            pace_assessment = "偏快"

        return {
            "has_goal": True,
            "target_weight_kg": round(user.target_weight / 1000, 2),
            "initial_weight_kg": round(user.initial_weight / 1000, 2),
            "current_weight_kg": round(current_weight / 1000, 2),
            "progress_percent": round(percentage, 1),
            "remaining_kg": round(remaining / 1000, 2),
            "weeks_elapsed": round(weeks_elapsed, 1),
            "avg_weekly_loss_kg": round(avg_weekly_loss, 2),
            "pace_assessment": pace_assessment,
            "estimated_weeks_remaining": round((remaining / 1000) / 0.5, 0)
            if avg_weekly_loss > 0
            else None,
        }

    def _assess_clinical_significance(
        self, weight_change_percent: float, days: int
    ) -> Dict[str, Any]:
        """评估临床意义"""
        # 基于研究：5%体重下降有临床意义
        if weight_change_percent <= -5:
            significance = "显著临床意义"
            health_benefits = [
                "改善胰岛素敏感性",
                "降低心血管疾病风险",
                "改善睡眠质量",
                "减少关节压力",
            ]
        elif weight_change_percent <= -3:
            significance = "有临床意义"
            health_benefits = [
                "血糖控制改善",
                "血压可能降低",
                "能量水平提升",
            ]
        elif weight_change_percent <= -1:
            significance = "轻微意义"
            health_benefits = ["良好的开始", "建立健康习惯基础"]
        elif weight_change_percent <= 1:
            significance = "体重维持"
            health_benefits = ["防止体重反弹", "保持当前成果"]
        else:
            significance = "需要关注"
            health_benefits = []

        return {
            "clinical_significance": significance,
            "health_benefits": health_benefits,
            "recommended_next_steps": self._get_recommended_steps(
                weight_change_percent
            ),
        }

    def _get_recommended_steps(self, weight_change_percent: float) -> List[str]:
        """获取推荐步骤"""
        if weight_change_percent < -5:
            return [
                "继续保持当前策略",
                "考虑增加力量训练",
                "监测营养摄入确保充足",
            ]
        elif weight_change_percent < -1:
            return [
                "微调饮食计划",
                "增加日常活动量",
                "保持行为一致性",
            ]
        elif weight_change_percent < 1:
            return [
                "审查饮食日志",
                "增加运动强度或频率",
                "检查睡眠和压力水平",
            ]
        else:
            return [
                "全面审查当前计划",
                "咨询专业人士",
                "重新设定现实目标",
            ]

    def _analyze_nutrition_scientifically(
        self, user: User, days: int
    ) -> Dict[str, Any]:
        """科学分析营养数据"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        records = (
            self.db.query(HealthRecord)
            .filter(
                and_(
                    HealthRecord.user_id == user.id,
                    HealthRecord.daily_calories.isnot(None),
                    HealthRecord.record_date >= start_date,
                    HealthRecord.record_date <= end_date,
                )
            )
            .all()
        )

        if not records:
            return {
                "data_available": False,
                "message": "期间内无营养记录",
            }

        calories = [r.daily_calories for r in records]
        protein = [r.protein_g for r in records if r.protein_g]
        carbs = [r.carbs_g for r in records if r.carbs_g]
        fat = [r.fat_g for r in records if r.fat_g]

        # 获取目标值
        nutrition_targets = self.nutrition_service.calculate_calorie_target(user)
        target_calories = nutrition_targets.get(
            "target", nutrition_targets.get("maintenance", 2000)
        )
        target_macros = self.nutrition_service.calculate_macronutrients(
            user, target_calories
        )

        # 卡路里分析
        avg_calories = mean(calories)
        calorie_adherence = (
            1 - abs(avg_calories - target_calories) / target_calories
        ) * 100
        calorie_variance = stdev(calories) if len(calories) > 1 else 0

        # 宏量营养素分析
        macro_analysis = {}
        if protein:
            avg_protein = mean(protein)
            target_protein = target_macros.get("protein_g", 100)
            macro_analysis["protein"] = {
                "avg_daily_g": round(avg_protein, 1),
                "target_g": round(target_protein, 1),
                "adherence_percent": round((avg_protein / target_protein) * 100, 1),
                "adequacy": "充足" if avg_protein >= target_protein * 0.9 else "偏低",
            }

        # 营养评分
        nutrition_score = self._calculate_nutrition_score(
            calorie_adherence, macro_analysis, calorie_variance
        )

        return {
            "data_available": True,
            "record_count": len(records),
            "calorie_analysis": {
                "avg_daily_calories": round(avg_calories, 0),
                "target_calories": round(target_calories, 0),
                "adherence_percent": round(calorie_adherence, 1),
                "variance": round(calorie_variance, 0),
                "consistency": "高"
                if calorie_variance < 200
                else "中"
                if calorie_variance < 400
                else "低",
            },
            "macronutrient_analysis": macro_analysis,
            "nutrition_score": nutrition_score,
            "dietary_patterns": self._identify_dietary_patterns(calories),
        }

    def _calculate_nutrition_score(
        self, calorie_adherence: float, macro_analysis: Dict, calorie_variance: float
    ) -> Dict[str, Any]:
        """计算营养评分"""
        # 基础分
        score = 0

        # 卡路里依从性 (40%)
        calorie_score = min(calorie_adherence, 100) * 0.4
        score += calorie_score

        # 宏量营养素 (30%)
        macro_score = 0
        if macro_analysis:
            for macro, data in macro_analysis.items():
                macro_score += min(data.get("adherence_percent", 0), 100)
            macro_score = (
                (macro_score / len(macro_analysis)) * 0.3 if macro_analysis else 0
            )
        score += macro_score

        # 一致性 (30%)
        consistency_score = max(0, 100 - (calorie_variance / 10)) * 0.3
        score += consistency_score

        return {
            "overall_score": round(score, 1),
            "calorie_component": round(calorie_score, 1),
            "macro_component": round(macro_score, 1),
            "consistency_component": round(consistency_score, 1),
            "grade": "A"
            if score >= 90
            else "B"
            if score >= 80
            else "C"
            if score >= 70
            else "D",
        }

    def _identify_dietary_patterns(self, calories: List[float]) -> Dict[str, Any]:
        """识别饮食模式"""
        if len(calories) < 7:
            return {"pattern": "数据不足", "confidence": 0}

        # 周末vs工作日分析（简化版）
        # 实际应该根据日期判断
        high_days = sum(1 for c in calories if c > mean(calories) * 1.2)
        low_days = sum(1 for c in calories if c < mean(calories) * 0.8)

        if high_days > len(calories) * 0.3:
            pattern = "波动性饮食"
            recommendation = "建议保持更稳定的每日摄入"
        elif low_days > len(calories) * 0.3:
            pattern = "限制性饮食"
            recommendation = "避免过度限制，确保营养均衡"
        else:
            pattern = "稳定饮食"
            recommendation = "保持当前的稳定模式"

        return {
            "pattern": pattern,
            "high_calorie_days": high_days,
            "low_calorie_days": low_days,
            "recommendation": recommendation,
            "confidence": min(len(calories) / 14, 1.0),  # 置信度随数据量增加
        }

    def _analyze_behavior_scientifically(self, user: User, days: int) -> Dict[str, Any]:
        """科学分析行为数据"""
        # 获取习惯统计
        habit_stats = self.habit_service.get_habit_stats(user)

        # 获取习惯详细数据
        habits = self.habit_service.get_user_habits(user, active_only=True)

        # 计算习惯一致性
        consistency_metrics = self._calculate_habit_consistency(user, habits, days)

        # 行为改变阶段评估
        behavior_stage = self._assess_behavior_change_stage(user, habits, habit_stats)

        return {
            "habit_statistics": {
                "total_active_habits": habit_stats.total_habits,
                "overall_completion_rate": round(habit_stats.completion_rate, 1),
                "current_longest_streak": habit_stats.current_streak,
                "category_distribution": habit_stats.category_stats,
            },
            "consistency_metrics": consistency_metrics,
            "behavior_change_stage": behavior_stage,
            "behavioral_momentum": self._calculate_behavioral_momentum(user, days),
        }

    def _calculate_habit_consistency(
        self, user: User, habits: List[Habit], days: int
    ) -> Dict[str, Any]:
        """计算习惯一致性"""
        if not habits:
            return {"overall_consistency": 0}

        consistencies = []
        for habit in habits:
            # 计算每个习惯的完成一致性
            completions = self.habit_service.get_completions(habit)
            if completions:
                # 计算实际完成与期望完成的比率
                expected = days if habit.frequency.value == "daily" else days / 7
                actual = len(completions)
                consistency = min(actual / expected, 1.0) if expected > 0 else 0
                consistencies.append(consistency)

        avg_consistency = mean(consistencies) if consistencies else 0

        return {
            "overall_consistency": round(avg_consistency * 100, 1),
            "individual_habits": len(consistencies),
            "consistency_trend": "提升"
            if avg_consistency > 0.7
            else "稳定"
            if avg_consistency > 0.4
            else "需关注",
        }

    def _assess_behavior_change_stage(
        self, user: User, habits: List[Habit], habit_stats
    ) -> Dict[str, Any]:
        """评估行为改变阶段（基于跨理论模型）"""
        # 简单的阶段评估逻辑
        if not habits:
            stage = "思考期"
            description = "开始考虑改变，但尚未行动"
        elif habit_stats.completion_rate >= 80 and habit_stats.current_streak >= 21:
            stage = "维持期"
            description = "行为已稳定，关注长期保持"
        elif habit_stats.completion_rate >= 60 or habit_stats.current_streak >= 7:
            stage = "行动期"
            description = "积极改变行为，需要持续支持"
        elif any(h.total_completions > 0 for h in habits):
            stage = "准备期"
            description = "已开始尝试，建立初期习惯"
        else:
            stage = "思考期"
            description = "开始考虑改变，但尚未行动"

        return {
            "current_stage": stage,
            "stage_description": description,
            "stage_duration_estimate": "建议持续至少6个月以达到维持期",
            "interventions_for_stage": self._get_stage_interventions(stage),
        }

    def _get_stage_interventions(self, stage: str) -> List[str]:
        """获取阶段特定干预"""
        interventions = {
            "思考期": [
                "提供行为改变的好处教育",
                "帮助设定具体目标",
                "探索改变的障碍和解决方案",
            ],
            "准备期": [
                "制定详细的行动计划",
                "建立支持系统",
                "准备应对挫折",
            ],
            "行动期": [
                "提供持续的正向强化",
                "监控进展并提供反馈",
                "帮助解决障碍",
            ],
            "维持期": [
                "预防复发策略",
                "庆祝里程碑",
                "建立长期生活方式",
            ],
        }
        return interventions.get(stage, [])

    def _calculate_behavioral_momentum(self, user: User, days: int) -> Dict[str, Any]:
        """计算行为动量"""
        # 基于最近7天vs之前7天的比较
        today = date.today()

        recent_week = []
        previous_week = []

        for i in range(7):
            recent_date = today - timedelta(days=i)
            previous_date = today - timedelta(days=i + 7)

            recent_checklist = self.habit_service.get_daily_checklist(user, recent_date)
            previous_checklist = self.habit_service.get_daily_checklist(
                user, previous_date
            )

            recent_week.append(recent_checklist["completion_percentage"])
            previous_week.append(previous_checklist["completion_percentage"])

        recent_avg = mean(recent_week)
        previous_avg = mean(previous_week)

        momentum = recent_avg - previous_avg

        if momentum > 10:
            trend = "强劲上升"
        elif momentum > 0:
            trend = "温和上升"
        elif momentum > -10:
            trend = "轻微下降"
        else:
            trend = "显著下降"

        return {
            "momentum_score": round(momentum, 1),
            "trend": trend,
            "recent_week_avg": round(recent_avg, 1),
            "previous_week_avg": round(previous_avg, 1),
            "recommendation": ("保持良好势头" if momentum > 0 else "需要调整策略"),
        }

    def _analyze_psychological_scientifically(
        self, user: User, days: int
    ) -> Dict[str, Any]:
        """科学分析心理数据"""
        # 获取情感洞察
        emotional_insights = self.emotional_service.get_emotional_insights(user, days)

        # 获取压力趋势
        stress_trend = self.emotional_service.get_stress_trend(user, days)

        # 计算心理韧性指标
        resilience_metrics = self._calculate_resilience_metrics(user, days)

        # 评估心理健康状态
        mental_health_status = self._assess_mental_health_status(
            emotional_insights, stress_trend
        )

        return {
            "emotional_wellness": {
                "dominant_emotion": emotional_insights.dominant_emotion.value,
                "emotional_variety": len(emotional_insights.emotion_trend),
                "positive_emotion_ratio": self._calculate_positive_emotion_ratio(
                    emotional_insights.emotion_trend
                ),
            },
            "stress_analysis": {
                "average_stress_level": round(emotional_insights.avg_stress_level, 1),
                "stress_trend": stress_trend,
                "stress_management_effectiveness": round(
                    emotional_insights.coping_effectiveness * 100, 1
                ),
            },
            "resilience_metrics": resilience_metrics,
            "mental_health_status": mental_health_status,
        }

    def _calculate_positive_emotion_ratio(self, emotion_trend: Dict) -> float:
        """计算积极情感比例"""
        positive_emotions = ["happy", "motivated", "peaceful"]
        total = sum(emotion_trend.values())
        positive = sum(emotion_trend.get(e, 0) for e in positive_emotions)

        return round((positive / total) * 100, 1) if total > 0 else 0

    def _calculate_resilience_metrics(self, user: User, days: int) -> Dict[str, Any]:
        """计算心理韧性指标"""
        # 获取感恩记录
        gratitude_count = (
            self.db.query(func.count())
            .select_from(
                self.db.query(GratitudeJournal)
                .filter(GratitudeJournal.user_id == user.id)
                .subquery()
            )
            .scalar()
        )

        # 获取正念练习次数
        mindfulness_count = (
            self.db.query(func.count())
            .select_from(
                self.db.query(MindfulnessExercise)
                .filter(MindfulnessExercise.user_id == user.id)
                .subquery()
            )
            .scalar()
        )

        # 计算韧性分数
        resilience_score = 0
        if gratitude_count >= 10:
            resilience_score += 30
        if mindfulness_count >= 5:
            resilience_score += 30

        return {
            "resilience_score": resilience_score,
            "gratitude_practice_frequency": gratitude_count,
            "mindfulness_practice_frequency": mindfulness_count,
            "resilience_level": "高"
            if resilience_score >= 50
            else "中"
            if resilience_score >= 25
            else "低",
        }

    def _assess_mental_health_status(
        self, emotional_insights, stress_trend
    ) -> Dict[str, Any]:
        """评估心理健康状态"""
        avg_stress = emotional_insights.avg_stress_level
        coping = emotional_insights.coping_effectiveness

        if avg_stress <= 3 and coping >= 0.7:
            status = "优秀"
            recommendations = ["继续保持当前的应对策略", "定期监控情绪状态"]
        elif avg_stress <= 5 and coping >= 0.5:
            status = "良好"
            recommendations = ["增加放松练习", "关注压力源"]
        elif avg_stress <= 7:
            status = "需关注"
            recommendations = [
                "每天进行正念练习",
                "记录压力触发因素",
                "考虑寻求专业支持",
            ]
        else:
            status = "需干预"
            recommendations = [
                "强烈建议寻求专业心理健康支持",
                "立即实施压力管理技巧",
                "减少不必要的压力源",
            ]

        return {
            "overall_status": status,
            "risk_level": "低"
            if avg_stress <= 5
            else "中"
            if avg_stress <= 7
            else "高",
            "recommendations": recommendations,
            "warning_signs": self._identify_warning_signs(avg_stress, coping),
        }

    def _identify_warning_signs(self, avg_stress: float, coping: float) -> List[str]:
        """识别警告信号"""
        warnings = []
        if avg_stress >= 7:
            warnings.append("持续高压力水平")
        if coping < 0.4:
            warnings.append("应对策略效果不佳")
        return warnings

    def _calculate_comprehensive_health_score(
        self,
        weight_analysis: Dict,
        nutrition_analysis: Dict,
        behavior_analysis: Dict,
        psychological_analysis: Dict,
    ) -> Dict[str, Any]:
        """计算综合健康评分"""
        score_components = {}

        # 体重评分 (25%)
        if weight_analysis.get("data_available"):
            weight_score = 0
            # 目标进度
            if weight_analysis.get("target_progress", {}).get("has_goal"):
                progress = weight_analysis["target_progress"]["progress_percent"]
                weight_score = min(progress, 100) * 0.5

            # 趋势
            trend_score = 0
            if weight_analysis.get("trend_analysis", {}).get("trend") in [
                "稳定下降",
                "快速下降",
            ]:
                trend_score = 25
            elif weight_analysis["trend_analysis"]["trend"] == "稳定":
                trend_score = 15

            # 稳定性
            stability = weight_analysis.get("volatility", {}).get(
                "stability_assessment"
            )
            stability_score = (
                25 if stability == "稳定" else 15 if stability == "中等波动" else 5
            )

            score_components["weight"] = round(
                weight_score + trend_score + stability_score, 1
            )
        else:
            score_components["weight"] = 0

        # 营养评分 (25%)
        if nutrition_analysis.get("data_available"):
            score_components["nutrition"] = (
                nutrition_analysis.get("nutrition_score", {}).get("overall_score", 0)
                * 0.25
            )
        else:
            score_components["nutrition"] = 0

        # 行为评分 (25%)
        if behavior_analysis.get("habit_statistics"):
            completion_rate = behavior_analysis["habit_statistics"].get(
                "overall_completion_rate", 0
            )
            consistency = behavior_analysis.get("consistency_metrics", {}).get(
                "overall_consistency", 0
            )
            score_components["behavior"] = round(
                (completion_rate + consistency) / 2 * 0.25, 1
            )
        else:
            score_components["behavior"] = 0

        # 心理评分 (25%)
        stress_level = psychological_analysis.get("stress_analysis", {}).get(
            "average_stress_level", 5
        )
        resilience = psychological_analysis.get("resilience_metrics", {}).get(
            "resilience_score", 0
        )
        mental_status = psychological_analysis.get("mental_health_status", {}).get(
            "overall_status", "良好"
        )

        stress_score = max(0, 25 - (stress_level - 3) * 5)  # 压力越低分越高
        resilience_score = resilience * 0.25
        status_bonus = (
            10 if mental_status == "优秀" else 5 if mental_status == "良好" else 0
        )

        score_components["psychological"] = round(
            stress_score + resilience_score + status_bonus, 1
        )

        # 总分
        total_score = sum(score_components.values())

        return {
            "total_score": round(total_score, 1),
            "max_score": 100,
            "components": score_components,
            "grade": self._calculate_grade(total_score),
            "percentile": self._estimate_percentile(total_score),
            "interpretation": self._interpret_health_score(total_score),
        }

    def _calculate_grade(self, score: float) -> str:
        """计算等级"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"

    def _estimate_percentile(self, score: float) -> int:
        """估计百分位（简化版）"""
        # 基于正态分布假设
        if score >= 90:
            return 95
        elif score >= 80:
            return 85
        elif score >= 70:
            return 70
        elif score >= 60:
            return 50
        elif score >= 50:
            return 30
        else:
            return 15

    def _interpret_health_score(self, score: float) -> str:
        """解读健康评分"""
        if score >= 85:
            return "优秀：您的健康管理非常到位，请继续保持！"
        elif score >= 70:
            return "良好：整体状况不错，仍有提升空间。"
        elif score >= 55:
            return "中等：需要关注某些方面，建议制定改进计划。"
        else:
            return "需改善：建议全面审视健康管理策略，寻求专业支持。"

    def _generate_evidence_based_recommendations(
        self,
        weight_analysis: Dict,
        nutrition_analysis: Dict,
        behavior_analysis: Dict,
        psychological_analysis: Dict,
    ) -> List[Dict[str, str]]:
        """生成循证建议"""
        recommendations = []

        # 基于体重分析的建议
        if weight_analysis.get("data_available"):
            trend = weight_analysis.get("trend_analysis", {}).get("trend")
            if trend in ["上升", "轻微上升"]:
                recommendations.append(
                    {
                        "area": "体重管理",
                        "recommendation": "根据趋势分析，建议增加每日活动量200-300步或调整饮食200-300卡路里",
                        "evidence": "研究显示，每日500卡路里的能量赤字可带来每周0.5公斤的安全减重",
                        "priority": "高",
                    }
                )

        # 基于营养分析的建议
        if nutrition_analysis.get("data_available"):
            adherence = nutrition_analysis.get("calorie_analysis", {}).get(
                "adherence_percent", 0
            )
            if adherence < 70:
                recommendations.append(
                    {
                        "area": "营养管理",
                        "recommendation": "建议提高饮食计划依从性至80%以上",
                        "evidence": "研究表明，80%以上的计划依从性与更好的减重效果相关",
                        "priority": "中",
                    }
                )

        # 基于行为分析的建议
        if (
            behavior_analysis.get("behavior_change_stage", {}).get("current_stage")
            == "准备期"
        ):
            recommendations.append(
                {
                    "area": "行为建立",
                    "recommendation": "建议采用'微小习惯'策略，从每天5分钟开始",
                    "evidence": "BJ Fogg的行为模型显示，从小处开始能显著提高习惯形成成功率",
                    "priority": "高",
                }
            )

        # 基于心理分析的建议
        stress_level = psychological_analysis.get("stress_analysis", {}).get(
            "average_stress_level", 5
        )
        if stress_level >= 6:
            recommendations.append(
                {
                    "area": "压力管理",
                    "recommendation": "建议每天进行10分钟正念冥想",
                    "evidence": "元分析显示，每日正念练习可降低皮质醇水平23%，改善压力应对",
                    "priority": "高",
                }
            )

        return recommendations

    def _calculate_bmi(self, user: User) -> float:
        """计算BMI"""
        if not user.height or not user.initial_weight:
            return 0

        height_m = user.height / 100
        weight_kg = user.initial_weight / 1000

        return round(weight_kg / (height_m**2), 1)

    def _get_bmi_category(self, user: User) -> str:
        """获取BMI分类"""
        bmi = self._calculate_bmi(user)

        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 25:
            return "正常"
        elif bmi < 30:
            return "超重"
        else:
            return "肥胖"

    def _estimate_metabolic_age(self, user: User) -> Dict[str, Any]:
        """估算代谢年龄"""
        # 简化估算
        if not user.age:
            return {"estimated": None, "confidence": 0}

        bmi = self._calculate_bmi(user)
        chronological_age = user.age

        # 基于BMI的调整
        if bmi > 30:
            metabolic_adjustment = 5
        elif bmi > 25:
            metabolic_adjustment = 2
        elif bmi < 18.5:
            metabolic_adjustment = 3
        else:
            metabolic_adjustment = 0

        estimated = chronological_age + metabolic_adjustment

        return {
            "estimated": estimated,
            "chronological_age": chronological_age,
            "difference": metabolic_adjustment,
            "confidence": "中等",
            "interpretation": (
                f"您的代谢年龄约{estimated}岁，比实际年龄{'' if metabolic_adjustment <= 0 else '高'}{abs(metabolic_adjustment)}岁"
            ),
        }

    def _assess_health_risk(self, user: User) -> Dict[str, str]:
        """评估健康风险"""
        bmi = self._calculate_bmi(user)
        bmi_category = self._get_bmi_category(user)

        if bmi_category == "肥胖":
            risk_level = "高"
            risks = ["心血管疾病", "2型糖尿病", "高血压"]
        elif bmi_category == "超重":
            risk_level = "中等"
            risks = ["心血管疾病风险增加", "代谢综合征"]
        elif bmi_category == "正常":
            risk_level = "低"
            risks = []
        else:
            risk_level = "中等"
            risks = ["营养不良", "免疫力下降"]

        return {
            "risk_level": risk_level,
            "associated_risks": risks,
            "recommendation": (
                "建议积极减重"
                if risk_level == "高"
                else "保持健康生活方式"
                if risk_level == "低"
                else "关注体重变化"
            ),
        }

    def _assess_data_quality(self, user: User, days: int) -> Dict[str, Any]:
        """评估数据质量"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # 检查各类型数据的记录情况
        weight_records = (
            self.db.query(HealthRecord)
            .filter(
                and_(
                    HealthRecord.user_id == user.id,
                    HealthRecord.weight.isnot(None),
                    HealthRecord.record_date >= start_date,
                )
            )
            .count()
        )

        nutrition_records = (
            self.db.query(HealthRecord)
            .filter(
                and_(
                    HealthRecord.user_id == user.id,
                    HealthRecord.daily_calories.isnot(None),
                    HealthRecord.record_date >= start_date,
                )
            )
            .count()
        )

        expected_records = days
        weight_coverage = (weight_records / expected_records) * 100
        nutrition_coverage = (nutrition_records / expected_records) * 100

        overall_quality = (weight_coverage + nutrition_coverage) / 2

        return {
            "overall_quality": round(overall_quality, 1),
            "weight_data_coverage": round(weight_coverage, 1),
            "nutrition_data_coverage": round(nutrition_coverage, 1),
            "assessment": (
                "优秀"
                if overall_quality >= 80
                else "良好"
                if overall_quality >= 60
                else "需改进"
            ),
            "recommendations": (
                ["继续保持良好的记录习惯"]
                if overall_quality >= 80
                else ["建议增加记录频率", "设置每日提醒"]
                if overall_quality >= 60
                else ["强烈建议建立每日记录习惯", "使用自动追踪工具"]
            ),
        }

    def generate_scientific_persona_message(
        self, user: User, context: str, data: Dict
    ) -> str:
        """生成科学人设的回复消息"""
        # 基于科学数据生成专业的回复
        report = self.generate_scientific_report(user, 30)

        # 构建科学人设的语气
        greeting = "基于您的数据分析："

        # 添加上下文相关的科学解释
        if "体重" in context or "weight" in context.lower():
            weight_data = report["weight_analysis"]
            if weight_data.get("data_available"):
                message = (
                    f"{greeting}\n\n"
                    f"根据过去30天的统计分析，您的体重变化趋势为：{weight_data['trend_analysis']['trend']}。\n"
                    f"体重变异系数为{weight_data['statistics']['coefficient_of_variation']}%，"
                    f"{'显示良好的体重稳定性。' if weight_data['statistics']['coefficient_of_variation'] < 2 else '存在一定波动，建议关注饮食和水分摄入。'}\n\n"
                    f"从临床角度，您目前的体重变化具有{weight_data['clinical_significance']['clinical_significance']}。\n\n"
                    f"循证建议：{weight_data['clinical_significance']['recommended_next_steps'][0]}"
                )
            else:
                message = f"{greeting}\n\n建议开始每日体重记录，以便进行科学分析。"

        elif "营养" in context or "diet" in context.lower():
            nutrition_data = report["nutrition_analysis"]
            if nutrition_data.get("data_available"):
                score = nutrition_data["nutrition_score"]
                message = (
                    f"{greeting}\n\n"
                    f"您的营养管理综合评分为{score['overall_score']}分（等级{score['grade']}）。\n"
                    f"卡路里依从性：{nutrition_data['calorie_analysis']['adherence_percent']}%。\n\n"
                    f"根据营养学研究，保持80%以上的计划依从性与更好的健康结果相关。"
                )
            else:
                message = f"{greeting}\n\n建议开始记录每日饮食，以评估营养摄入模式。"

        elif "压力" in context or "stress" in context.lower():
            psych_data = report["psychological_analysis"]
            stress_level = psych_data["stress_analysis"]["average_stress_level"]
            message = (
                f"{greeting}\n\n"
                f"您的平均压力水平为{stress_level}/10。"
                f"{'建议实施压力管理策略。' if stress_level >= 6 else '压力管理良好。'}\n\n"
                f"基于积极心理学研究，每日正念练习可有效降低皮质醇水平。"
            )

        else:
            # 综合回复
            health_score = report["comprehensive_health_score"]
            message = (
                f"{greeting}\n\n"
                f"您的综合健康评分为{health_score['total_score']}分（{health_score['grade']}级），"
                f"超过{health_score['percentile']}%的用户。\n\n"
                f"{health_score['interpretation']}"
            )

        return message


def get_scientific_persona_service(db: Session) -> ScientificPersonaService:
    """获取科学量化人设服务实例"""
    return ScientificPersonaService(db)
