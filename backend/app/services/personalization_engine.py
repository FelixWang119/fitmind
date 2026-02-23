"""个性化推荐引擎服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.user import User
from app.services.milestone_detector import MilestoneDetector
from app.services.pattern_recognizer import PatternRecognizer
from app.services.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """个性化推荐引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.trend_analyzer = TrendAnalyzer(db)
        self.pattern_recognizer = PatternRecognizer(db)
        self.milestone_detector = MilestoneDetector(db)

    # ========== 饮食推荐 ==========

    async def recommend_diet(self, user_id: int) -> Dict[str, Any]:
        """个性化饮食推荐"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                return {"success": False, "error": "User not found"}

            # 获取最近趋势
            diet_trend = await self.trend_analyzer.analyze_diet_trend(user_id, days=14)
            weight_trend = await self.trend_analyzer.analyze_weight_trend(
                user_id, days=30
            )

            recommendations = []

            # 基于体重目标推荐
            if user.target_weight and user.initial_weight:
                target_weight = user.target_weight
                current_weight = user.initial_weight

                # 获取当前体重
                latest = (
                    self.db.query(HealthRecord)
                    .filter(
                        HealthRecord.user_id == user_id, HealthRecord.weight.isnot(None)
                    )
                    .order_by(HealthRecord.record_date.desc())
                    .first()
                )

                if latest:
                    current_weight = latest.weight

                if current_weight > target_weight:
                    # 减重目标
                    recommendations.append(
                        {
                            "type": "calorie_deficit",
                            "priority": "high",
                            "title": "控制卡路里摄入",
                            "description": "建议每日摄入1800-2000kcal，创造合理的热量缺口",
                            "reason": "当前体重高于目标体重",
                        }
                    )

                    # 推荐低GI食物
                    recommendations.append(
                        {
                            "type": "food_choice",
                            "priority": "medium",
                            "title": "选择低GI食物",
                            "description": "优先选择全谷物、豆类、蔬菜等低升糖指数食物",
                            "reason": "有助于稳定血糖，控制食欲",
                        }
                    )
                else:
                    # 维持或增重
                    recommendations.append(
                        {
                            "type": "maintain_weight",
                            "priority": "medium",
                            "title": "维持当前摄入",
                            "description": "保持当前饮食习惯，适量增加蛋白质摄入",
                            "reason": "体重已接近目标",
                        }
                    )

            # 基于饮食趋势推荐
            if diet_trend.get("success"):
                if diet_trend.get("trend") == "increasing":
                    recommendations.append(
                        {
                            "type": "reduce_calories",
                            "priority": "high",
                            "title": "控制饮食",
                            "description": "近期卡路里摄入有上升趋势，建议注意控制",
                            "reason": "饮食趋势分析显示摄入增加",
                        }
                    )

                # 营养素建议
                nutrition = diet_trend.get("nutrition_avg", {})
                if nutrition.get("protein", 0) < 60:
                    recommendations.append(
                        {
                            "type": "increase_protein",
                            "priority": "medium",
                            "title": "增加蛋白质摄入",
                            "description": "建议每日蛋白质摄入不低于80g",
                            "reason": "蛋白质摄入偏低",
                        }
                    )

            # 基于活动水平推荐
            activity_recommendations = self._get_activity_based_diet(
                user.activity_level
            )
            recommendations.extend(activity_recommendations)

            return {
                "success": True,
                "user_id": user_id,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"生成饮食推荐失败: {e}")
            return {"success": False, "error": str(e)}

    def _get_activity_based_diet(
        self, activity_level: Optional[str]
    ) -> List[Dict[str, Any]]:
        """基于活动水平的饮食推荐"""
        if not activity_level:
            return []

        recommendations = []

        if activity_level == "sedentary":
            recommendations.append(
                {
                    "type": "portion_control",
                    "priority": "high",
                    "title": "控制份量",
                    "description": "久坐人群建议每餐适当减少份量",
                    "reason": "活动量较低",
                }
            )
        elif activity_level == "moderate":
            recommendations.append(
                {
                    "type": "balanced_diet",
                    "priority": "medium",
                    "title": "均衡饮食",
                    "description": "保持蛋白质、碳水、脂肪的均衡摄入",
                    "reason": "适度活动水平",
                }
            )
        elif activity_level == "active":
            recommendations.append(
                {
                    "type": "increase_carbs",
                    "priority": "medium",
                    "title": "增加碳水",
                    "description": "活动量大，建议适量增加碳水化合物摄入",
                    "reason": "需要更多能量",
                }
            )

        return recommendations

    # ========== 运动推荐 ==========

    async def recommend_exercise(self, user_id: int) -> Dict[str, Any]:
        """个性化运动推荐"""
        try:
            # 获取运动趋势
            exercise_trend = await self.trend_analyzer.analyze_exercise_trend(
                user_id, days=14
            )
            habit_consistency = await self.trend_analyzer.analyze_habit_consistency(
                user_id
            )

            recommendations = []

            # 基于运动频率推荐
            if exercise_trend.get("success"):
                exercise_rate = exercise_trend.get("exercise_rate", 0)

                if exercise_rate < 30:
                    recommendations.append(
                        {
                            "type": "start_exercise",
                            "priority": "high",
                            "title": "开始运动",
                            "description": "建议每周至少3天，每次30分钟中等强度运动",
                            "reason": f"当前运动频率仅{exercise_rate}%",
                        }
                    )
                elif exercise_rate < 50:
                    recommendations.append(
                        {
                            "type": "increase_exercise",
                            "priority": "medium",
                            "title": "增加运动",
                            "description": "建议逐步增加运动频率至每周5天",
                            "reason": "运动频率有提升空间",
                        }
                    )
                else:
                    recommendations.append(
                        {
                            "type": "maintain_exercise",
                            "priority": "low",
                            "title": "保持运动习惯",
                            "description": "运动习惯很好，继续保持！",
                            "reason": "运动频率良好",
                        }
                    )

                # 趋势分析
                trend = exercise_trend.get("trend", "stable")
                if trend == "decreasing":
                    recommendations.append(
                        {
                            "type": "prevent_relapse",
                            "priority": "high",
                            "title": "防止运动减少",
                            "description": "近期运动量有下降趋势，建议保持或增加",
                            "reason": "运动趋势下降",
                        }
                    )

            # 基于习惯一致性推荐
            if habit_consistency.get("success"):
                overall = habit_consistency.get("overall_consistency", 0)

                if overall < 50:
                    recommendations.append(
                        {
                            "type": "build_habit",
                            "priority": "high",
                            "title": "建立运动习惯",
                            "description": "建议从简单运动开始，如每天散步20分钟",
                            "reason": "习惯养成需要时间",
                        }
                    )

            # 添加运动类型建议
            recommendations.extend(
                [
                    {
                        "type": "aerobic_exercise",
                        "priority": "medium",
                        "title": "有氧运动",
                        "description": "快走、跑步、游泳等，每周150分钟",
                        "reason": "有助心肺健康",
                    },
                    {
                        "type": "strength_training",
                        "priority": "medium",
                        "title": "力量训练",
                        "description": "每周2-3次，每次20-30分钟",
                        "reason": "保持肌肉量，提高基础代谢",
                    },
                ]
            )

            return {
                "success": True,
                "user_id": user_id,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"生成运动推荐失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 习惯推荐 ==========

    async def recommend_habits(self, user_id: int) -> Dict[str, Any]:
        """个性化习惯推荐"""
        try:
            # 获取当前习惯
            current_habits = (
                self.db.query(Habit)
                .filter(Habit.user_id == user_id, Habit.is_active == True)
                .all()
            )

            current_categories = {
                h.category.value if h.category else None for h in current_habits
            }

            recommendations = []

            # 缺少的习惯类型
            recommended_categories = []

            if "DIET" not in current_categories:
                recommended_categories.append(
                    {
                        "category": "DIET",
                        "suggestions": [
                            "每天喝足够的水（2L）",
                            "每餐七分饱",
                            "记录每日饮食",
                        ],
                    }
                )

            if "EXERCISE" not in current_categories:
                recommended_categories.append(
                    {
                        "category": "EXERCISE",
                        "suggestions": [
                            "每天快走30分钟",
                            "每周2次力量训练",
                            "站立办公",
                        ],
                    }
                )

            if "SLEEP" not in current_categories:
                recommended_categories.append(
                    {
                        "category": "SLEEP",
                        "suggestions": [
                            "固定时间睡觉",
                            "睡前1小时不看屏幕",
                            "保证7-8小时睡眠",
                        ],
                    }
                )

            if "MENTAL_HEALTH" not in current_categories:
                recommended_categories.append(
                    {
                        "category": "MENTAL_HEALTH",
                        "suggestions": [
                            "每天冥想10分钟",
                            "记录感恩日记",
                            "定期与朋友交流",
                        ],
                    }
                )

            for cat in recommended_categories:
                recommendations.append(
                    {
                        "type": "add_habit",
                        "priority": "high",
                        "title": f"添加{cat['category']}类习惯",
                        "description": f"建议培养以下习惯：{', '.join(cat['suggestions'])}",
                        "reason": "当前缺少该类型习惯",
                    }
                )

            # 已有习惯的改进建议
            for habit in current_habits[:3]:  # 最多3个
                if habit.streak_days and habit.streak_days < 7:
                    recommendations.append(
                        {
                            "type": "improve_habit",
                            "priority": "medium",
                            "title": f"坚持「{habit.name}」",
                            "description": f"当前连续{habit.streak_days}天，建议设定提醒保持连续性",
                            "reason": "帮助建立习惯",
                        }
                    )

            return {
                "success": True,
                "user_id": user_id,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"生成习惯推荐失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 综合推荐 ==========

    async def get_comprehensive_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取综合推荐"""
        try:
            diet = await self.recommend_diet(user_id)
            exercise = await self.recommend_exercise(user_id)
            habits = await self.recommend_habits(user_id)

            # 合并所有推荐并按优先级排序
            all_recommendations = []

            for rec in diet.get("recommendations", []):
                rec["category"] = "饮食"
                all_recommendations.append(rec)

            for rec in exercise.get("recommendations", []):
                rec["category"] = "运动"
                all_recommendations.append(rec)

            for rec in habits.get("recommendations", []):
                rec["category"] = "习惯"
                all_recommendations.append(rec)

            # 按优先级排序
            priority_order = {"high": 0, "medium": 1, "low": 2}
            all_recommendations.sort(
                key=lambda x: priority_order.get(x.get("priority", "low"), 2)
            )

            return {
                "success": True,
                "user_id": user_id,
                "total_recommendations": len(all_recommendations),
                "recommendations": all_recommendations,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"生成综合推荐失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 即时建议 ==========

    async def get_quick_tip(self, user_id: int, context: str = "general") -> str:
        """获取即时建议"""
        try:
            # 基于上下文和时间生成建议
            now = datetime.now()
            hour = now.hour

            tips = []

            # 基于时间
            if 6 <= hour < 9:
                tips.append("☀️ 早上好！建议先喝一杯温水，然后进行适度运动")
            elif 11 <= hour < 13:
                tips.append("🍽️ 午餐时间到！注意控制份量，蛋白质为主")
            elif 17 <= hour < 19:
                tips.append("🏃 下班后是运动的好时机！")
            elif 21 <= hour < 23:
                tips.append("😴 准备休息了！睡前1小时避免进食")

            # 获取今日状态
            today = date.today()
            today_start = datetime.combine(today, datetime.min.time())

            health = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date >= today_start,
                )
                .first()
            )

            if health:
                if health.calories_intake and health.calories_intake > 2000:
                    tips.append("⚠️ 今日卡路里摄入已较高，注意控制晚餐")
                if health.exercise_minutes and health.exercise_minutes < 30:
                    tips.append("🏃 今日运动量不足，建议增加活动")

            # 获取习惯完成情况
            habits = (
                self.db.query(Habit)
                .filter(Habit.user_id == user_id, Habit.is_active == True)
                .count()
            )

            completions = (
                self.db.query(HabitCompletion)
                .join(Habit)
                .filter(
                    Habit.user_id == user_id,
                    HabitCompletion.completion_date >= today_start,
                )
                .count()
            )

            if habits > 0 and completions < habits:
                tips.append(f"📝 今日习惯完成 {completions}/{habits}，还有未完成的加油！")
            elif completions == habits and habits > 0:
                tips.append("🎉 今日习惯已全部完成！太棒了！")

            return tips[0] if tips else "保持健康每一天！"

        except Exception as e:
            logger.error(f"获取即时建议失败: {e}")
            return "每天进步一点点！"


def get_personalization_engine(db: Session) -> PersonalizationEngine:
    """获取个性化引擎实例"""
    return PersonalizationEngine(db)
