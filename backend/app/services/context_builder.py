"""高级上下文构建器服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import ContextSummary, HabitPattern, UserLongTermMemory
from app.models.user import User
from app.services.memory_manager import MemoryManager
from app.services.milestone_detector import MilestoneDetector
from app.services.pattern_recognizer import PatternRecognizer
from app.services.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)


class AdvancedContextBuilder:
    """高级上下文构建器"""

    def __init__(self, db: Session):
        self.db = db
        self.memory_manager = MemoryManager(db)
        self.trend_analyzer = TrendAnalyzer(db)
        self.pattern_recognizer = PatternRecognizer(db)
        self.milestone_detector = MilestoneDetector(db)

    # ========== 完整上下文构建 ==========

    async def build_full_context(
        self, user_id: int, conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建完整上下文"""
        try:
            # 1. 用户基本信息
            user_profile = await self._get_user_profile(user_id)

            # 2. 当前状态（今日数据）
            current_status = await self._get_current_status(user_id)

            # 3. 趋势分析
            trends = await self.trend_analyzer.analyze_all_trends(user_id, days=30)

            # 4. 行为模式
            patterns = await self.pattern_recognizer.detect_behavioral_patterns(user_id)

            # 5. 里程碑
            milestones = await self.milestone_detector.detect_all_milestones(user_id)

            # 6. 重要记忆
            important_memories = await self._get_important_memories(user_id)

            # 7. 近期摘要
            recent_summaries = await self.memory_manager.get_recent_summaries(
                user_id, days=7
            )

            # 8. 如果有对话上下文，加入
            if conversation_context:
                conversation_summary = await self._analyze_conversation_context(
                    user_id, conversation_context
                )
            else:
                conversation_summary = None

            # 构建最终上下文文本
            context_text = self._compile_context_text(
                user_profile=user_profile,
                current_status=current_status,
                trends=trends,
                patterns=patterns,
                milestones=milestones,
                important_memories=important_memories,
                recent_summaries=recent_summaries,
                conversation_summary=conversation_summary,
            )

            # 构建结构化上下文
            structured_context = {
                "user_id": user_id,
                "user_profile": user_profile,
                "current_status": current_status,
                "trends": trends,
                "patterns": patterns,
                "milestones": milestones,
                "important_memories": important_memories,
                "recent_summaries": [
                    {"date": s.period_start.isoformat(), "text": s.summary_text[:200]}
                    for s in recent_summaries[:3]
                ],
                "conversation_summary": conversation_summary,
                "context_text": context_text,
                "built_at": datetime.utcnow().isoformat(),
            }

            return {
                "success": True,
                "context": structured_context,
                "context_text": context_text,
            }

        except Exception as e:
            logger.error(f"构建完整上下文失败: {e}")
            return {"success": False, "error": str(e)}

    # ========== 用户画像 ==========

    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户画像"""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return {}

        return {
            "username": user.username,
            "age": user.age,
            "gender": user.gender,
            "height": user.height,
            "initial_weight": user.initial_weight / 1000
            if user.initial_weight
            else None,
            "target_weight": user.target_weight / 1000 if user.target_weight else None,
            "activity_level": user.activity_level,
            "days_since_joined": (date.today() - user.created_at.date()).days
            if user.created_at
            else 0,
        }

    # ========== 当前状态 ==========

    async def _get_current_status(self, user_id: int) -> Dict[str, Any]:
        """获取当前状态"""
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 今日健康记录
        health = (
            self.db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user_id,
                HealthRecord.record_date >= today_start,
                HealthRecord.record_date <= today_end,
            )
            .first()
        )

        # 今日习惯完成
        today_completions = (
            self.db.query(HabitCompletion)
            .join(Habit)
            .filter(
                Habit.user_id == user_id,
                HabitCompletion.completion_date >= today_start,
                HabitCompletion.completion_date <= today_end,
            )
            .all()
        )

        # 今日打卡习惯
        completed_habits = [c.habit for c in today_completions]

        # 活跃习惯总数
        total_habits = (
            self.db.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active == True)
            .count()
        )

        return {
            "date": today.isoformat(),
            "weight": health.weight / 1000 if health and health.weight else None,
            "calories": health.calories_intake
            if health and health.calories_intake
            else None,
            "exercise_minutes": health.exercise_minutes
            if health and health.exercise_minutes
            else None,
            "stress_level": health.stress_level
            if health and health.stress_level
            else None,
            "habits_completed": len(completed_habits),
            "habits_total": total_habits,
            "completion_rate": round(len(completed_habits) / total_habits * 100, 1)
            if total_habits > 0
            else 0,
        }

    # ========== 重要记忆 ==========

    async def _get_important_memories(self, user_id: int) -> List[Dict[str, Any]]:
        """获取重要记忆"""
        memories = await self.memory_manager.get_memories(user_id, min_importance=5.0)

        result = []
        for memory in memories[:10]:  # 最多10条
            try:
                value = json.loads(memory.memory_value)
            except:
                value = memory.memory_value

            result.append(
                {
                    "type": memory.memory_type,
                    "key": memory.memory_key,
                    "value": value,
                    "importance": memory.importance_score,
                    "last_accessed": memory.last_accessed.isoformat()
                    if memory.last_accessed
                    else None,
                }
            )

        return result

    # ========== 对话上下文分析 ==========

    async def _analyze_conversation_context(
        self, user_id: int, conversation_context: str
    ) -> Optional[Dict[str, Any]]:
        """分析对话上下文"""
        # 获取最近一次对话
        recent_conversation = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .first()
        )

        if not recent_conversation:
            return None

        # 获取最近消息
        recent_messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == recent_conversation.id)
            .order_by(Message.created_at.desc())
            .limit(5)
            .all()
        )

        if not recent_messages:
            return None

        # 提取关键话题
        topics = []
        for msg in recent_messages:
            if msg.role.value == "user":
                # 简单关键词提取
                keywords = self._extract_keywords(msg.content)
                topics.extend(keywords)

        return {
            "conversation_id": recent_conversation.id,
            "recent_topics": list(set(topics))[:5],
            "last_message_count": len(recent_messages),
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """简单的关键词提取"""
        keywords = []
        keyword_list = [
            "体重",
            "饮食",
            "运动",
            "睡眠",
            "压力",
            "习惯",
            "目标",
            "卡路里",
            "减肥",
            "健康",
        ]

        for keyword in keyword_list:
            if keyword in text:
                keywords.append(keyword)

        return keywords

    # ========== 上下文文本编译 ==========

    def _compile_context_text(
        self,
        user_profile: Dict,
        current_status: Dict,
        trends: Dict,
        patterns: List,
        milestones: Dict,
        important_memories: List,
        recent_summaries: List,
        conversation_summary: Optional[Dict],
    ) -> str:
        """编译上下文文本"""
        lines = []

        # 1. 用户基本信息
        lines.append("【用户基本信息】")
        if user_profile.get("username"):
            lines.append(f"  用户名: {user_profile['username']}")
        if user_profile.get("target_weight"):
            lines.append(f"  目标体重: {user_profile['target_weight']}kg")
        if user_profile.get("activity_level"):
            lines.append(f"  活动水平: {user_profile['activity_level']}")
        if user_profile.get("days_since_joined"):
            lines.append(f"  使用天数: {user_profile['days_since_joined']}天")
        lines.append("")

        # 2. 当前状态
        lines.append("【今日状态】")
        if current_status.get("weight"):
            lines.append(f"  体重: {current_status['weight']}kg")
        if current_status.get("calories"):
            lines.append(f"  摄入卡路里: {current_status['calories']}kcal")
        if current_status.get("exercise_minutes"):
            lines.append(f"  运动: {current_status['exercise_minutes']}分钟")
        if current_status.get("habits_completed"):
            lines.append(
                f"  习惯完成: {current_status['habits_completed']}/{current_status['habits_total']} ({current_status['completion_rate']}%)"
            )
        lines.append("")

        # 3. 趋势分析
        if trends.get("success") and trends.get("overall_assessment"):
            assessment = trends["overall_assessment"]
            lines.append("【健康评估】")
            lines.append(f"  总体评分: {assessment.get('overall_score', 0)}分")
            if assessment.get("recommendation"):
                lines.append(f"  建议: {assessment['recommendation']}")
            lines.append("")

        # 4. 里程碑
        if milestones.get("weight_goal") and milestones["weight_goal"].get(
            "milestones"
        ):
            lines.append("【进度里程碑】")
            for m in milestones["weight_goal"]["milestones"]:
                lines.append(f"  {m.get('title', '')}: {m.get('description', '')}")
            lines.append("")

        # 5. 重要记忆
        if important_memories:
            lines.append("【重要记录】")
            for mem in important_memories[:5]:
                lines.append(f"  [{mem['type']}] {mem['key']}")
            lines.append("")

        # 6. 近期摘要
        if recent_summaries:
            lines.append("【近期动态】")
            for summary in recent_summaries[:3]:
                lines.append(
                    f"  {summary.period_start}: {summary.summary_text[:80]}..."
                )
            lines.append("")

        return "\n".join(lines)

    # ========== AI提示生成 ==========

    async def generate_ai_prompt(
        self, user_id: int, user_message: str
    ) -> Dict[str, Any]:
        """生成AI提示"""
        try:
            # 构建完整上下文
            context_result = await self.build_full_context(user_id, user_message)

            if not context_result.get("success"):
                return {"success": False, "error": context_result.get("error")}

            context = context_result["context"]

            # 生成系统提示
            system_prompt = self._create_system_prompt(context)

            # 生成用户提示（包含上下文）
            user_prompt = self._create_user_prompt(context, user_message)

            return {
                "success": True,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "context_summary": {
                    "current_weight": context["current_status"].get("weight"),
                    "habits_completed": context["current_status"].get(
                        "habits_completed"
                    ),
                    "overall_score": context["trends"]
                    .get("overall_assessment", {})
                    .get("overall_score", 0),
                },
            }

        except Exception as e:
            logger.error(f"生成AI提示失败: {e}")
            return {"success": False, "error": str(e)}

    def _create_system_prompt(self, context: Dict) -> str:
        """创建系统提示"""
        user_profile = context.get("user_profile", {})

        prompt = f"""你是{user_profile.get("username", "用户")}的体重管理AI助手。
你的角色融合了：
1. 专业营养师 - 提供科学的饮食建议
2. 行为教练 - 帮助养成健康习惯
3. 情感支持者 - 提供心理支持和鼓励

请根据以下用户信息，提供个性化、温暖、专业的建议。

"""

        # 添加当前状态
        current = context.get("current_status", {})
        if current.get("weight"):
            prompt += f"用户今日体重: {current['weight']}kg\n"
        if current.get("habits_completed"):
            prompt += f"今日习惯完成: {current['habits_completed']}/{current['habits_total']} ({current['completion_rate']}%)\n"

        # 添加评估
        assessment = context.get("trends", {}).get("overall_assessment", {})
        if assessment.get("overall_score"):
            prompt += f"健康评分: {assessment['overall_score']}分\n"

        # 添加建议
        if assessment.get("recommendation"):
            prompt += f"建议: {assessment['recommendation']}\n"

        prompt += "\n请用温暖、专业的方式回复用户的问题。"

        return prompt

    def _create_user_prompt(self, context: Dict, user_message: str) -> str:
        """创建用户提示"""
        # 包含简要上下文
        prompt = f"""【用户消息】
{user_message}

"""

        # 添加相关上下文
        recent = context.get("recent_summaries", [])
        if recent:
            prompt += "【近期动态】\n"
            for s in recent:
                prompt += f"- {s.get('date', '')}: {s.get('text', '')[:100]}...\n"

        return prompt

    # ========== 快速上下文 ==========

    async def build_quick_context(self, user_id: int) -> str:
        """构建快速上下文（用于简单查询）"""
        try:
            # 只获取核心信息
            user_profile = await self._get_user_profile(user_id)
            current_status = await self._get_current_status(user_id)

            lines = []

            if user_profile.get("target_weight"):
                lines.append(f"目标: {user_profile['target_weight']}kg")

            if current_status.get("weight"):
                lines.append(f"当前: {current_status['weight']}kg")

            if current_status.get("habits_completed"):
                lines.append(
                    f"今日习惯: {current_status['habits_completed']}/{current_status['habits_total']}"
                )

            return " | ".join(lines) if lines else "暂无数据"

        except Exception as e:
            logger.error(f"构建快速上下文失败: {e}")
            return "数据加载中..."


def get_advanced_context_builder(db: Session) -> AdvancedContextBuilder:
    """获取高级上下文构建器实例"""
    return AdvancedContextBuilder(db)
