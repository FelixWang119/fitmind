import enum
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.emotional_support import EmotionalState, StressLevel
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.user import User
from app.services.emotional_support_service import EmotionalSupportService
from app.services.habit_service import HabitService
from app.services.nutrition_service import NutritionService

logger = structlog.get_logger()


class ProfessionalRole(str, enum.Enum):
    """专业角色枚举"""

    NUTRITIONIST = "nutritionist"
    BEHAVIOR_COACH = "behavior_coach"
    INTEGRATED = "integrated"


class InterventionType(str, enum.Enum):
    """干预类型枚举"""

    NUTRITION_ADVICE = "nutrition_advice"
    BEHAVIOR_COACHING = "behavior_coaching"
    EMOTIONAL_SUPPORT = "emotional_support"
    INTEGRATED = "integrated"


class ProfessionalFusionService:
    """专业角色融合服务"""

    def __init__(self, db: Session):
        self.db = db
        self.nutrition_service = NutritionService(db)
        self.habit_service = HabitService(db)
        self.emotional_service = EmotionalSupportService(db)

    def assess_user_needs(self, user: User) -> Dict[str, any]:
        """评估用户需求（营养师+行为教练视角）"""
        logger.info("Assessing user needs", user_id=user.id)

        # 营养师视角评估
        nutrition_assessment = self._assess_nutrition_needs(user)

        # 行为教练视角评估
        behavior_assessment = self._assess_behavior_needs(user)

        # 情感支持视角评估
        emotional_assessment = self._assess_emotional_needs(user)

        # 综合评估
        integrated_assessment = self._integrate_assessments(
            nutrition_assessment, behavior_assessment, emotional_assessment
        )

        return {
            "nutrition_assessment": nutrition_assessment,
            "behavior_assessment": behavior_assessment,
            "emotional_assessment": emotional_assessment,
            "integrated_assessment": integrated_assessment,
            "recommended_role": self._determine_primary_role(integrated_assessment),
            "assessment_date": datetime.utcnow().isoformat(),
        }

    def _assess_nutrition_needs(self, user: User) -> Dict[str, any]:
        """营养师视角评估"""
        # 获取营养建议
        nutrition_recommendations = self.nutrition_service.get_dietary_recommendations(
            user
        )

        # 分析营养需求
        calorie_targets = self.nutrition_service.calculate_calorie_target(user)
        target_calories = calorie_targets.get("target", calorie_targets["maintenance"])

        # 获取最近的健康记录
        recent_records = (
            self.db.query(HealthRecord)
            .filter(HealthRecord.user_id == user.id)
            .order_by(HealthRecord.record_date.desc())
            .limit(7)
            .all()
        )

        # 分析饮食模式
        diet_patterns = self._analyze_diet_patterns(recent_records)

        return {
            "calorie_needs": {
                "target": target_calories,
                "maintenance": calorie_targets["maintenance"],
                "weight_loss": calorie_targets["weight_loss"],
                "weight_gain": calorie_targets["weight_gain"],
            },
            "macronutrient_needs": self.nutrition_service.calculate_macronutrients(
                user, target_calories
            ),
            "hydration_needs": self.nutrition_service._calculate_hydration_goal(user),
            "dietary_preferences": user.dietary_preferences.split(",")
            if user.dietary_preferences
            else [],
            "diet_patterns": diet_patterns,
            "supplement_needs": self.nutrition_service._get_supplement_recommendations(
                user
            ),
            "priority_level": self._calculate_nutrition_priority(user, recent_records),
        }

    def _analyze_diet_patterns(self, records: List[HealthRecord]) -> Dict[str, any]:
        """分析饮食模式"""
        if not records:
            return {"has_data": False, "message": "暂无饮食记录"}

        # 提取卡路里数据
        calorie_data = [r.daily_calories for r in records if r.daily_calories]

        if not calorie_data:
            return {"has_data": False, "message": "暂无卡路里记录"}

        avg_calories = sum(calorie_data) / len(calorie_data)
        max_calories = max(calorie_data)
        min_calories = min(calorie_data)
        variability = (
            (max_calories - min_calories) / avg_calories if avg_calories > 0 else 0
        )

        # 分析一致性
        consistency_score = 1 - min(variability, 1.0)  # 0-1分数，越高越一致

        return {
            "has_data": True,
            "avg_daily_calories": round(avg_calories, 0),
            "calorie_variability": round(variability, 2),
            "consistency_score": round(consistency_score, 2),
            "record_count": len(calorie_data),
            "consistency_level": "高"
            if consistency_score >= 0.7
            else "中"
            if consistency_score >= 0.4
            else "低",
        }

    def _calculate_nutrition_priority(
        self, user: User, records: List[HealthRecord]
    ) -> str:
        """计算营养优先级"""
        # 基于体重目标和当前进展
        weight_progress = self._calculate_weight_progress(user, records)

        if weight_progress["has_goal"]:
            percentage = weight_progress["percentage"]
            if percentage < 30:
                return "高"  # 早期阶段需要更多营养指导
            elif percentage < 70:
                return "中"  # 中期需要维持指导
            else:
                return "低"  # 接近目标，需要较少指导
        else:
            return "中"  # 没有明确目标，中等优先级

    def _calculate_weight_progress(
        self, user: User, records: List[HealthRecord]
    ) -> Dict[str, any]:
        """计算体重进展"""
        if not user.initial_weight or not user.target_weight:
            return {"has_goal": False}

        # 获取最新体重
        latest_weight = None
        for record in records:
            if record.weight:
                latest_weight = record.weight
                break

        if not latest_weight:
            latest_weight = user.initial_weight

        total_to_lose = user.initial_weight - user.target_weight
        lost_so_far = user.initial_weight - latest_weight

        if total_to_lose <= 0:
            return {"has_goal": False}

        percentage = (lost_so_far / total_to_lose) * 100 if total_to_lose > 0 else 0

        return {
            "has_goal": True,
            "current_weight": latest_weight,
            "percentage": round(percentage, 1),
            "remaining": total_to_lose - lost_so_far,
        }

    def _assess_behavior_needs(self, user: User) -> Dict[str, any]:
        """行为教练视角评估"""
        # 获取习惯统计
        habit_stats = self.habit_service.get_habit_stats(user)

        # 获取习惯完成情况
        habits = self.habit_service.get_user_habits(user, active_only=True)

        # 分析行为模式
        behavior_patterns = self._analyze_behavior_patterns(user, habits)

        # 识别行为障碍
        barriers = self._identify_behavior_barriers(user, habits)

        return {
            "habit_stats": {
                "total_habits": habit_stats.total_habits,
                "completion_rate": habit_stats.completion_rate,
                "current_streak": habit_stats.current_streak,
                "category_distribution": habit_stats.category_stats,
            },
            "behavior_patterns": behavior_patterns,
            "identified_barriers": barriers,
            "motivation_level": self._assess_motivation_level(user, habits),
            "self_efficacy": self._assess_self_efficacy(user),
            "priority_level": self._calculate_behavior_priority(
                habit_stats, behavior_patterns
            ),
        }

    def _analyze_behavior_patterns(
        self, user: User, habits: List[Habit]
    ) -> Dict[str, any]:
        """分析行为模式"""
        if not habits:
            return {"has_habits": False, "message": "暂无习惯记录"}

        # 分析习惯类别分布
        category_counts = {}
        for habit in habits:
            category = habit.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "has_habits": True,
            "category_distribution": category_counts,
            "habit_count": len(habits),
        }

    def _identify_behavior_barriers(self, user: User, habits: List[Habit]) -> List[str]:
        """识别行为障碍"""
        barriers = []

        # 分析习惯完成情况
        low_completion_habits = [h for h in habits if h.total_completions < 3]

        if low_completion_habits:
            barriers.append("新习惯建立困难")

        # 检查习惯多样性
        categories = set(h.category.value for h in habits)
        if len(categories) < 3:
            barriers.append("行为领域单一")

        return barriers

    def _assess_motivation_level(self, user: User, habits: List[Habit]) -> str:
        """评估动机水平"""
        if not habits:
            return "未知"

        # 基于习惯完成率和连续天数
        completion_rates = []
        streak_days = []

        for habit in habits:
            # 计算完成率（简化）
            days_since_creation = (
                datetime.utcnow().date() - habit.created_at.date()
            ).days
            expected_completions = (
                days_since_creation
                if habit.frequency.value == "daily"
                else days_since_creation / 7
            )
            completion_rate = (
                habit.total_completions / expected_completions
                if expected_completions > 0
                else 0
            )
            completion_rates.append(min(completion_rate, 1.0))
            streak_days.append(habit.streak_days)

        avg_completion_rate = (
            sum(completion_rates) / len(completion_rates) if completion_rates else 0
        )
        avg_streak = sum(streak_days) / len(streak_days) if streak_days else 0

        if avg_completion_rate >= 0.7 and avg_streak >= 7:
            return "高"
        elif avg_completion_rate >= 0.4 and avg_streak >= 3:
            return "中"
        else:
            return "低"

    def _assess_self_efficacy(self, user: User) -> str:
        """评估自我效能感"""
        # 基于习惯成功率和目标达成
        habits = self.habit_service.get_user_habits(user, active_only=True)

        if not habits:
            return "未知"

        successful_habits = 0
        for habit in habits:
            # 简单判断：有完成记录且连续天数>0
            if habit.total_completions > 0 and habit.streak_days > 0:
                successful_habits += 1

        success_rate = successful_habits / len(habits) if habits else 0

        if success_rate >= 0.7:
            return "高"
        elif success_rate >= 0.4:
            return "中"
        else:
            return "低"

    def _calculate_behavior_priority(self, habit_stats, behavior_patterns) -> str:
        """计算行为优先级"""
        completion_rate = habit_stats.completion_rate
        current_streak = habit_stats.current_streak

        if completion_rate < 40 or current_streak < 3:
            return "高"  # 需要行为指导
        elif completion_rate < 70 or current_streak < 7:
            return "中"  # 需要维持支持
        else:
            return "低"  # 自我管理良好

    def _assess_emotional_needs(self, user: User) -> Dict[str, any]:
        """情感支持视角评估"""
        # 获取情感洞察
        emotional_insights = self.emotional_service.get_emotional_insights(user, 7)

        # 获取压力趋势
        stress_trend = self.emotional_service.get_stress_trend(user, 7)

        # 分析情感需求
        emotional_needs = self._analyze_emotional_needs(
            emotional_insights, stress_trend
        )

        return {
            "emotional_insights": {
                "dominant_emotion": emotional_insights.dominant_emotion.value,
                "emotion_trend": emotional_insights.emotion_trend,
                "avg_stress_level": emotional_insights.avg_stress_level,
                "coping_effectiveness": emotional_insights.coping_effectiveness,
            },
            "stress_trend": stress_trend,
            "emotional_needs": emotional_needs,
            "priority_level": "高" if emotional_insights.avg_stress_level >= 7 else "中",
        }

    def _analyze_emotional_needs(self, insights, stress_trend) -> List[str]:
        """分析情感需求"""
        needs = []

        # 基于主导情感
        dominant_emotion = insights.dominant_emotion
        if dominant_emotion.value in ["sad", "anxious", "stressed"]:
            needs.append("情绪调节支持")
        elif dominant_emotion.value == "tired":
            needs.append("精力管理支持")
        elif dominant_emotion.value == "frustrated":
            needs.append("挫折应对支持")

        # 基于压力水平
        avg_stress = insights.avg_stress_level
        if avg_stress >= 7:
            needs.append("压力管理支持")
        elif avg_stress >= 5:
            needs.append("放松技巧指导")

        return needs

    def _integrate_assessments(self, nutrition, behavior, emotional) -> Dict[str, any]:
        """整合评估结果"""
        # 识别交叉领域
        cross_cutting_issues = []

        # 检查营养与行为的交叉
        if nutrition["priority_level"] == "高" and behavior["priority_level"] == "高":
            cross_cutting_issues.append("饮食行为改变困难")

        # 检查行为与情感的交叉
        if behavior["priority_level"] == "高" and emotional["priority_level"] == "高":
            cross_cutting_issues.append("情感影响行为坚持")

        # 检查营养与情感的交叉
        if nutrition["priority_level"] == "高" and emotional["priority_level"] == "高":
            cross_cutting_issues.append("情绪化饮食")

        # 确定综合优先级
        priorities = [
            nutrition["priority_level"],
            behavior["priority_level"],
            emotional["priority_level"],
        ]

        high_count = priorities.count("高")
        medium_count = priorities.count("中")
        low_count = priorities.count("低")

        if high_count >= 2:
            overall_priority = "高"
        elif high_count == 1 or medium_count >= 2:
            overall_priority = "中"
        else:
            overall_priority = "低"

        # 识别综合关注领域
        focus_areas = []
        if nutrition["priority_level"] == "高":
            focus_areas.append("营养优化")
        if behavior["priority_level"] == "高":
            focus_areas.append("行为建立")
        if emotional["priority_level"] == "高":
            focus_areas.append("情感支持")

        return {
            "cross_cutting_issues": cross_cutting_issues,
            "overall_priority": overall_priority,
            "priority_distribution": {
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
            },
            "integrated_focus_areas": focus_areas,
        }

    def _determine_primary_role(self, integrated_assessment) -> ProfessionalRole:
        """确定主要角色"""
        priority_distribution = integrated_assessment["priority_distribution"]

        if priority_distribution["high"] >= 2:
            # 多个高优先级领域，需要综合角色
            return ProfessionalRole.INTEGRATED
        elif priority_distribution["high"] == 1:
            # 单一高优先级领域
            focus_areas = integrated_assessment["integrated_focus_areas"]
            if "营养优化" in focus_areas:
                return ProfessionalRole.NUTRITIONIST
            elif "行为建立" in focus_areas:
                return ProfessionalRole.BEHAVIOR_COACH
            else:
                return ProfessionalRole.INTEGRATED
        else:
            # 没有高优先级，使用综合角色进行维持
            return ProfessionalRole.INTEGRATED

    def create_integrated_intervention(
        self, user: User, assessment: Dict
    ) -> Dict[str, any]:
        """创建综合干预计划"""
        logger.info("Creating integrated intervention", user_id=user.id)

        primary_role = assessment["recommended_role"]
        focus_areas = assessment["integrated_assessment"]["integrated_focus_areas"]

        # 基于主要角色和关注领域创建干预
        intervention_plan = {
            "primary_role": primary_role.value,
            "focus_areas": focus_areas,
            "duration_weeks": 12
            if assessment["integrated_assessment"]["overall_priority"] == "高"
            else 8
            if assessment["integrated_assessment"]["overall_priority"] == "中"
            else 4,
            "weekly_sessions": {
                "nutrition": 2
                if assessment["integrated_assessment"]["overall_priority"] == "高"
                else 1,
                "behavior": 2
                if assessment["integrated_assessment"]["overall_priority"] == "高"
                else 1,
                "emotional": 1
                if assessment["integrated_assessment"]["overall_priority"] in ["高", "中"]
                else 0,
            },
            "intervention_components": self._create_intervention_components(
                user, assessment
            ),
        }

        return intervention_plan

    def _create_intervention_components(
        self, user: User, assessment: Dict
    ) -> List[Dict]:
        """创建干预组件"""
        components = []

        # 营养组件
        if "营养优化" in assessment["integrated_assessment"]["integrated_focus_areas"]:
            components.append(
                {
                    "type": InterventionType.NUTRITION_ADVICE.value,
                    "focus": "个性化饮食计划",
                    "activities": ["卡路里目标设定", "宏量营养素分配", "餐食计划制定"],
                }
            )

        # 行为组件
        if "行为建立" in assessment["integrated_assessment"]["integrated_focus_areas"]:
            components.append(
                {
                    "type": InterventionType.BEHAVIOR_COACHING.value,
                    "focus": "习惯建立与维持",
                    "activities": ["SMART目标设定", "习惯链条建立", "奖励系统设计"],
                }
            )

        # 情感组件
        if "情感支持" in assessment["integrated_assessment"]["integrated_focus_areas"]:
            components.append(
                {
                    "type": InterventionType.EMOTIONAL_SUPPORT.value,
                    "focus": "情感调节与压力管理",
                    "activities": ["情感觉察练习", "压力应对策略", "自我同情培养"],
                }
            )

        return components


def get_professional_fusion_service(db: Session) -> ProfessionalFusionService:
    """获取专业角色融合服务实例"""
    return ProfessionalFusionService(db)
