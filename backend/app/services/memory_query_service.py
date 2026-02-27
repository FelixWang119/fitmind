"""
记忆查询服务 - 合并短期记忆（内存队列）和长期记忆（pgvector）
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.short_term_memory import get_short_term_memory_service
from app.models.memory import UnifiedMemory

logger = logging.getLogger(__name__)


class MemoryQueryService:
    """记忆查询服务 - 合并短期和长期记忆"""

    def __init__(self, db: Session):
        self.db = db
        self.short_term_service = get_short_term_memory_service()

    def get_all_memories_for_user(
        self,
        user_id: int,
        limit: int = 50,
        event_types: List[str] = None,
    ) -> Dict[str, Any]:
        """
        获取用户的所有记忆（短期 + 长期）
        """
        logger.debug(
            f"开始获取用户所有记忆 - 用户ID: {user_id}, 限制: {limit}, "
            f"事件类型过滤: {event_types}"
        )

        # 1. 获取短期记忆（从内存队列）
        logger.debug(f"获取短期记忆 - 用户ID: {user_id}")
        short_term_memories = self.short_term_service.get_recent_memories(
            user_id, limit=limit
        )
        logger.debug(
            f"短期记忆获取完成 - 用户ID: {user_id}, 数量: {len(short_term_memories)}"
        )

        # 2. 获取长期记忆（从 pgvector）
        logger.debug(f"获取长期记忆 - 用户ID: {user_id}")
        query = self.db.query(UnifiedMemory).filter(
            UnifiedMemory.user_id == user_id,
            UnifiedMemory.is_active == True,
        )

        if event_types:
            query = query.filter(UnifiedMemory.memory_type.in_(event_types))
            logger.debug(f"应用事件类型过滤 - 用户ID: {user_id}, 类型: {event_types}")

        long_term_memories = (
            query.order_by(UnifiedMemory.created_at.desc()).limit(limit).all()
        )
        logger.debug(
            f"长期记忆获取完成 - 用户ID: {user_id}, 数量: {len(long_term_memories)}"
        )

        # 3. 转换为字典格式
        logger.debug(f"格式化长期记忆数据 - 用户ID: {user_id}")
        long_term_data = []
        for mem in long_term_memories:
            long_term_data.append(
                {
                    "id": str(mem.id),
                    "event_type": mem.memory_type,
                    "content": mem.content_summary,
                    "content_raw": mem.content_raw,
                    "keywords": mem.content_keywords,
                    "importance": mem.importance_score,
                    "timestamp": mem.created_at.isoformat() if mem.created_at else None,
                    "source": f"{mem.source_type}:{mem.source_id}",
                }
            )
        logger.debug(
            f"长期记忆格式化完成 - 用户ID: {user_id}, 格式化数量: {len(long_term_data)}"
        )

        short_term_data = []
        logger.debug(f"格式化短期记忆数据 - 用户ID: {user_id}")
        for mem in short_term_memories:
            short_term_data.append(
                {
                    "event_type": mem.get("event_type"),
                    "content": mem.get("content"),
                    "metrics": mem.get("metrics"),
                    "context": mem.get("context"),
                    "timestamp": mem.get("timestamp"),
                    "source": f"{mem.get('source_table')}:{mem.get('source_id')}",
                }
            )
        logger.debug(
            f"短期记忆格式化完成 - 用户ID: {user_id}, 格式化数量: {len(short_term_data)}"
        )

        # 4. 生成摘要
        logger.debug(f"生成记忆摘要 - 用户ID: {user_id}")
        summary = self._generate_summary(short_term_data, long_term_data)
        logger.debug(
            f"记忆摘要生成完成 - 用户ID: {user_id}, 事件类型分布: {summary.get('event_counts', {})}"
        )

        total_memories = len(short_term_data) + len(long_term_data)
        logger.info(
            f"用户所有记忆获取完成 - 用户ID: {user_id}, "
            f"短期记忆: {len(short_term_data)}, 长期记忆: {len(long_term_data)}, "
            f"总计: {total_memories}"
        )

        return {
            "short_term": short_term_data,
            "long_term": long_term_data,
            "total": total_memories,
            "summary": summary,
        }

    def _generate_summary(
        self, short_term: List[Dict], long_term: List[Dict]
    ) -> Dict[str, Any]:
        """生成记忆摘要"""
        logger.debug(
            f"开始生成记忆摘要 - 短期记忆数：{len(short_term)}, 长期记忆数：{len(long_term)}"
        )

        event_counts = {}
        total_calories = 0
        total_exercise_duration = 0
        total_exercise_calories = 0
        recent_events = []

        all_events = short_term + long_term
        logger.debug(f"合并所有事件 - 总事件数：{len(all_events)}")

        for event in all_events:
            event_type = event.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

            # 添加到最近事件列表（用于 Agent 上下文）
            recent_events.append(event)

            metrics = event.get("metrics", {})
            if event_type == "nutrition":
                calories = metrics.get("calories", 0)
                total_calories += calories
                if calories > 0:
                    logger.debug(
                        f"营养事件 - 卡路里：{calories}, 累计：{total_calories}"
                    )
            elif event_type == "exercise":
                duration = metrics.get("duration_minutes", 0)
                calories_burned = metrics.get("calories_burned", 0)
                total_exercise_duration += duration
                total_exercise_calories += calories_burned
                if duration > 0 or calories_burned > 0:
                    logger.debug(
                        f"运动事件 - 时长：{duration}分钟，燃烧卡路里：{calories_burned}, "
                        f"累计时长：{total_exercise_duration}, 累计燃烧：{total_exercise_calories}"
                    )

        summary = {
            "event_counts": event_counts,
            "total_calories": total_calories,
            "total_exercise_duration": total_exercise_duration,
            "total_exercise_calories": total_exercise_calories,
            "total_events": len(all_events),
            "recent_events": recent_events,  # 添加最近事件列表
        }

        logger.debug(
            f"记忆摘要生成完成 - 事件类型分布：{event_counts}, "
            f"总卡路里：{total_calories}, 总运动时长：{total_exercise_duration}分钟，"
            f"最近事件数：{len(recent_events)}"
        )

        return summary

    def get_today_summary(self, user_id: int) -> Dict[str, Any]:
        """
        获取今日摘要 - 从短期记忆队列聚合

        架构原则：
        - 不再直接查询业务表（meals, exercise_checkins）
        - 所有数据从记忆队列中读取
        - 记忆队列是唯一数据源
        """
        from datetime import datetime

        # 从短期记忆队列获取今日记录
        all_memories = self.short_term_service.get_recent_memories(user_id, limit=100)

        # 过滤今日记录
        today = datetime.now().date()
        today_memories = []
        for mem in all_memories:
            timestamp = mem.get("timestamp", "")
            if timestamp:
                try:
                    mem_date = datetime.fromisoformat(timestamp).date()
                    if mem_date == today:
                        today_memories.append(mem)
                except:
                    continue

        # 聚合数据
        total_calories_intake = 0
        total_calories_burned = 0
        total_exercise_duration = 0
        meal_count = 0
        exercise_count = 0

        for mem in today_memories:
            event_type = mem.get("event_type", "")
            metrics = mem.get("metrics", {})

            # 餐食/营养记录
            if event_type in ["meal", "nutrition"]:
                meal_count += 1
                total_calories_intake += metrics.get("calories", 0)

            # 运动记录
            elif event_type in ["exercise", "exercise_record"]:
                exercise_count += 1
                total_calories_burned += metrics.get("calories_burned", 0)
                total_exercise_duration += metrics.get("duration_minutes", 0)

        return {
            "total_calories_intake": total_calories_intake,
            "total_exercise_calories_burned": total_calories_burned,
            "exercise_duration_minutes": total_exercise_duration,
            "meal_count": meal_count,
            "exercise_count": exercise_count,
            "from_memory_queue": True,  # 标记数据来源
        }


def get_memory_context_for_agent(user_id: int, db: Session) -> str:
    """为 Agent 生成记忆上下文字符串"""
    logger.debug(f"开始为Agent生成记忆上下文 - 用户ID: {user_id}")

    query_service = MemoryQueryService(db)

    # 获取今日摘要
    logger.debug(f"获取今日摘要 - 用户ID: {user_id}")
    today_summary = query_service.get_today_summary(user_id)
    logger.debug(
        f"今日摘要获取完成 - 用户ID: {user_id}, "
        f"摄入热量: {today_summary.get('total_calories_intake', 0)}千卡, "
        f"运动消耗: {today_summary.get('total_exercise_calories_burned', 0)}千卡"
    )

    # 获取最近记忆
    logger.debug(f"获取最近记忆 - 用户ID: {user_id}, 限制: 20")
    all_memories = query_service.get_all_memories_for_user(user_id, limit=20)
    logger.debug(
        f"最近记忆获取完成 - 用户ID: {user_id}, "
        f"短期记忆: {len(all_memories.get('short_term', []))}, "
        f"长期记忆: {len(all_memories.get('long_term', []))}"
    )

    # 构建上下文字符串
    logger.debug(f"构建上下文字符串 - 用户ID: {user_id}")
    context_parts = [
        "## 用户今日健康数据",
        f"- 摄入热量：{today_summary['total_calories_intake']} 千卡",
        f"- 运动消耗：{today_summary['total_exercise_calories_burned']} 千卡",
        f"- 运动时长：{today_summary['exercise_duration_minutes']} 分钟",
        f"- 记录餐食：{today_summary['meal_count']} 餐",
        f"- 运动打卡：{today_summary['exercise_count']} 次",
        "",
        "## 最近行为记录",
    ]

    recent_events = all_memories.get("summary", {}).get("recent_events", [])
    logger.debug(f"获取最近事件 - 用户ID: {user_id}, 事件数: {len(recent_events)}")

    events_added = 0
    for event in recent_events[:10]:
        event_type = event.get("event_type", "")
        content = event.get("content") or event.get("content_raw", "")
        timestamp = event.get("timestamp", "")

        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
            except Exception as e:
                logger.debug(f"时间戳解析失败 - 时间戳: {timestamp}, 错误: {e}")
                time_str = ""
        else:
            time_str = ""

        if content:
            context_parts.append(f"- [{time_str}] {content}")
            events_added += 1
            logger.debug(
                f"添加上下文事件 - 类型: {event_type}, 时间: {time_str}, 内容长度: {len(content)}"
            )

    context_text = "\n".join(context_parts)
    logger.info(
        f"Agent记忆上下文生成完成 - 用户ID: {user_id}, "
        f"上下文长度: {len(context_text)}字符, 包含事件: {events_added}个"
    )

    return context_text
