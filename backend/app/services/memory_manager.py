"""记忆管理器服务"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import (
    ContextSummary,
    DataAssociation,
    HabitPattern,
    UserLongTermMemory,
)
from app.models.user import User

logger = logging.getLogger(__name__)


class MemoryManager:
    """记忆管理器"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 用户长期记忆操作 ==========

    async def get_memory(
        self, user_id: int, memory_type: str, memory_key: str
    ) -> Optional[UserLongTermMemory]:
        """获取用户记忆"""
        try:
            memory = (
                self.db.query(UserLongTermMemory)
                .filter(
                    UserLongTermMemory.user_id == user_id,
                    UserLongTermMemory.memory_type == memory_type,
                    UserLongTermMemory.memory_key == memory_key,
                )
                .first()
            )

            if memory:
                memory.last_accessed = datetime.utcnow()
                self.db.commit()

            return memory
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            return None

    async def get_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[UserLongTermMemory]:
        """获取用户记忆列表"""
        try:
            query = self.db.query(UserLongTermMemory).filter(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.importance_score >= min_importance,
            )

            if memory_type:
                query = query.filter(UserLongTermMemory.memory_type == memory_type)

            return query.order_by(desc(UserLongTermMemory.importance_score)).all()
        except Exception as e:
            logger.error(f"获取记忆列表失败: {e}")
            return []

    async def create_memory(
        self,
        user_id: int,
        memory_type: str,
        memory_key: str,
        memory_value: Dict[str, Any],
        importance_score: float = 1.0,
    ) -> Optional[UserLongTermMemory]:
        """创建或更新用户记忆"""
        try:
            # 检查是否已存在
            existing = await self.get_memory(user_id, memory_type, memory_key)

            if existing:
                existing.memory_value = json.dumps(memory_value, ensure_ascii=False)
                existing.importance_score = importance_score
                existing.last_accessed = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing)
                return existing

            # 创建新记忆
            memory = UserLongTermMemory(
                user_id=user_id,
                memory_type=memory_type,
                memory_key=memory_key,
                memory_value=json.dumps(memory_value, ensure_ascii=False),
                importance_score=importance_score,
                last_accessed=datetime.utcnow(),
            )

            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)

            logger.info(
                f"创建记忆成功: user_id={user_id}, type={memory_type}, key={memory_key}"
            )
            return memory
        except Exception as e:
            logger.error(f"创建记忆失败: {e}")
            self.db.rollback()
            return None

    async def update_memory_importance(
        self, user_id: int, memory_key: str, importance_delta: float
    ) -> bool:
        """更新记忆重要性"""
        try:
            memories = (
                self.db.query(UserLongTermMemory)
                .filter(
                    UserLongTermMemory.user_id == user_id,
                    UserLongTermMemory.memory_key == memory_key,
                )
                .all()
            )

            if not memories:
                return False

            for memory in memories:
                new_importance = memory.importance_score + importance_delta
                memory.importance_score = max(0.0, min(10.0, new_importance))
                memory.last_accessed = datetime.utcnow()

            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"更新记忆重要性失败: {e}")
            self.db.rollback()
            return False

    # ========== 上下文摘要操作 ==========

    async def create_daily_summary(
        self, user_id: int, process_date: date
    ) -> Optional[ContextSummary]:
        """创建每日摘要"""
        try:
            date_start = datetime.combine(process_date, datetime.min.time())
            date_end = datetime.combine(process_date, datetime.max.time())

            # 获取当日数据
            health_records = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date >= date_start,
                    HealthRecord.record_date <= date_end,
                )
                .all()
            )

            habit_completions = (
                self.db.query(HabitCompletion)
                .join(Habit)
                .filter(
                    Habit.user_id == user_id,
                    HabitCompletion.completion_date >= date_start,
                    HabitCompletion.completion_date <= date_end,
                )
                .all()
            )

            # 生成摘要
            summary_text = self._generate_summary_text(
                health_records, habit_completions, process_date
            )
            key_insights = self._extract_insights(health_records, habit_completions)

            summary = ContextSummary(
                user_id=user_id,
                summary_type="daily",
                period_start=process_date,
                period_end=process_date,
                summary_text=summary_text,
                key_insights=json.dumps(key_insights, ensure_ascii=False),
                data_sources=json.dumps(
                    [
                        {"type": "health_records", "count": len(health_records)},
                        {"type": "habit_completions", "count": len(habit_completions)},
                    ],
                    ensure_ascii=False,
                ),
            )

            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)

            # 更新处理标记
            for record in health_records:
                record.processed_for_memory = True
                self.db.add(record)
            self.db.commit()

            logger.info(f"创建每日摘要成功: user_id={user_id}, date={process_date}")
            return summary
        except Exception as e:
            logger.error(f"创建每日摘要失败: {e}")
            self.db.rollback()
            return None

    async def get_recent_summaries(
        self, user_id: int, days: int = 7
    ) -> List[ContextSummary]:
        """获取近期摘要"""
        try:
            start_date = date.today() - timedelta(days=days)
            return (
                self.db.query(ContextSummary)
                .filter(
                    ContextSummary.user_id == user_id,
                    ContextSummary.period_start >= start_date,
                    ContextSummary.summary_type == "daily",
                )
                .order_by(desc(ContextSummary.period_start))
                .all()
            )
        except Exception as e:
            logger.error(f"获取近期摘要失败: {e}")
            return []

    # ========== 习惯模式操作 ==========

    async def create_habit_pattern(
        self,
        user_id: int,
        habit_id: int,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float = 0.5,
    ) -> Optional[HabitPattern]:
        """创建习惯模式"""
        try:
            today = date.today()
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
            self.db.refresh(pattern)

            logger.info(f"创建习惯模式成功: user_id={user_id}, habit_id={habit_id}")
            return pattern
        except Exception as e:
            logger.error(f"创建习惯模式失败: {e}")
            self.db.rollback()
            return None

    async def get_habit_patterns(
        self, user_id: int, min_confidence: float = 0.0
    ) -> List[HabitPattern]:
        """获取习惯模式列表"""
        try:
            return (
                self.db.query(HabitPattern)
                .filter(
                    HabitPattern.user_id == user_id,
                    HabitPattern.confidence_score >= min_confidence,
                )
                .order_by(desc(HabitPattern.confidence_score))
                .all()
            )
        except Exception as e:
            logger.error(f"获取习惯模式列表失败: {e}")
            return []

    # ========== 数据关联操作 ==========

    async def create_association(
        self,
        user_id: int,
        source_type: str,
        source_id: int,
        target_type: str,
        target_id: int,
        association_type: str,
        strength: float = 0.5,
    ) -> Optional[DataAssociation]:
        """创建数据关联"""
        try:
            association = DataAssociation(
                user_id=user_id,
                source_type=source_type,
                source_id=source_id,
                target_type=target_type,
                target_id=target_id,
                association_type=association_type,
                strength=strength,
            )

            self.db.add(association)
            self.db.commit()
            self.db.refresh(association)

            return association
        except Exception as e:
            logger.error(f"创建数据关联失败: {e}")
            self.db.rollback()
            return None

    async def get_associations(
        self, user_id: int, min_strength: float = 0.0
    ) -> List[DataAssociation]:
        """获取数据关联列表"""
        try:
            return (
                self.db.query(DataAssociation)
                .filter(
                    DataAssociation.user_id == user_id,
                    DataAssociation.strength >= min_strength,
                )
                .order_by(desc(DataAssociation.strength))
                .all()
            )
        except Exception as e:
            logger.error(f"获取数据关联列表失败: {e}")
            return []

    # ========== 上下文构建 ==========

    async def build_context(self, user_id: int, max_memories: int = 20) -> str:
        """构建用户上下文"""
        try:
            context_parts = []

            # 用户基本信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                context_parts.append("用户基本信息：")
                context_parts.append(f"  - 用户名：{user.username}")
                if user.height:
                    context_parts.append(f"  - 身高：{user.height}cm")
                if user.initial_weight:
                    context_parts.append(f"  - 初始体重：{user.initial_weight / 1000}kg")
                if user.target_weight:
                    context_parts.append(f"  - 目标体重：{user.target_weight / 1000}kg")
                context_parts.append("")

            # 重要记忆
            memories = await self.get_memories(user_id, min_importance=5.0)
            if memories:
                context_parts.append("重要记忆：")
                for memory in memories[:max_memories]:
                    try:
                        value = json.loads(memory.memory_value)
                        summary = value.get("summary", str(value))[:100]
                    except:
                        summary = memory.memory_value[:100]
                    context_parts.append(
                        f"  - [{memory.memory_type}] {memory.memory_key}: {summary}"
                    )
                context_parts.append("")

            # 近期摘要
            summaries = await self.get_recent_summaries(user_id)
            if summaries:
                context_parts.append("近期摘要：")
                for summary in summaries[:5]:
                    context_parts.append(
                        f"  - {summary.period_start}: {summary.summary_text[:150]}..."
                    )
                context_parts.append("")

            # 习惯模式
            patterns = await self.get_habit_patterns(user_id, min_confidence=0.7)
            if patterns:
                context_parts.append("习惯模式：")
                for pattern in patterns[:10]:
                    habit = (
                        self.db.query(Habit)
                        .filter(Habit.id == pattern.habit_id)
                        .first()
                    )
                    habit_name = habit.name if habit else f"习惯#{pattern.habit_id}"
                    context_parts.append(
                        f"  - {habit_name}: {pattern.pattern_type}模式 (置信度: {pattern.confidence_score:.2f})"
                    )
                context_parts.append("")

            # 今日状态
            today = date.today()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())

            today_health = (
                self.db.query(HealthRecord)
                .filter(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date >= today_start,
                    HealthRecord.record_date <= today_end,
                )
                .first()
            )

            if today_health:
                context_parts.append("今日状态：")
                if today_health.weight:
                    context_parts.append(f"  - 体重：{today_health.weight / 1000}kg")
                if today_health.calories_intake:
                    context_parts.append(
                        f"  - 卡路里摄入：{today_health.calories_intake}kcal"
                    )
                if today_health.exercise_minutes:
                    context_parts.append(f"  - 运动：{today_health.exercise_minutes}分钟")
                if today_health.stress_level:
                    context_parts.append(f"  - 压力水平：{today_health.stress_level}/10")
                context_parts.append("")

            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"构建上下文失败: {e}")
            return f"用户ID: {user_id}的上下文构建失败"

    # ========== 工具方法 ==========

    def _generate_summary_text(
        self,
        health_records: List[HealthRecord],
        habit_completions: List[HabitCompletion],
        process_date: date,
    ) -> str:
        """生成摘要文本"""
        parts = [f"{process_date} 的每日摘要：", ""]

        if health_records:
            parts.append("健康数据：")
            for record in health_records:
                if record.weight:
                    parts.append(f"  - 体重: {record.weight / 1000}kg")
                if record.calories_intake:
                    parts.append(f"  - 卡路里摄入: {record.calories_intake}kcal")
                if record.exercise_minutes:
                    parts.append(f"  - 运动: {record.exercise_minutes}分钟")
        else:
            parts.append("健康数据：无记录")

        parts.append("")

        if habit_completions:
            parts.append(f"习惯完成：{len(habit_completions)}项")
        else:
            parts.append("习惯完成：无记录")

        return "\n".join(parts)

    def _extract_insights(
        self,
        health_records: List[HealthRecord],
        habit_completions: List[HabitCompletion],
    ) -> List[Dict[str, Any]]:
        """提取关键洞察"""
        insights = []

        if health_records:
            weights = [r.weight for r in health_records if r.weight]
            if weights:
                insights.append(
                    {
                        "type": "weight",
                        "value": sum(weights) / len(weights),
                        "description": f"平均体重: {sum(weights) / len(weights) / 1000:.1f}kg",
                    }
                )

        if habit_completions:
            insights.append(
                {
                    "type": "habits",
                    "value": len(habit_completions),
                    "description": f"完成习惯数: {len(habit_completions)}",
                }
            )

        return insights

    async def get_memory_stats(self, user_id: int) -> Dict[str, Any]:
        """获取记忆统计"""
        try:
            memory_count = (
                self.db.query(func.count(UserLongTermMemory.id))
                .filter(UserLongTermMemory.user_id == user_id)
                .scalar()
                or 0
            )

            summary_count = (
                self.db.query(func.count(ContextSummary.id))
                .filter(ContextSummary.user_id == user_id)
                .scalar()
                or 0
            )

            pattern_count = (
                self.db.query(func.count(HabitPattern.id))
                .filter(HabitPattern.user_id == user_id)
                .scalar()
                or 0
            )

            return {
                "memory_count": memory_count,
                "summary_count": summary_count,
                "pattern_count": pattern_count,
                "total_items": memory_count + summary_count + pattern_count,
            }
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {
                "memory_count": 0,
                "summary_count": 0,
                "pattern_count": 0,
                "total_items": 0,
            }


def get_memory_manager(db: Session) -> MemoryManager:
    """获取记忆管理器实例"""
    return MemoryManager(db)
