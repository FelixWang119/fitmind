"""
记忆索引服务 - 将短期记忆索引到长期记忆

触发方式：
队列溢出时 - 实时索引单条记忆到长期记忆存储
"""

import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


async def index_memory_to_long_term(
    db: Session,
    overflow_item: Dict[str, Any],
) -> bool:
    """
    将溢出的短期记忆索引到长期记忆

    Args:
        db: 数据库会话
        overflow_item: 被挤出的短期记忆数据

    Returns:
        是否成功索引
    """
    try:
        user_id = overflow_item.get("user_id", "unknown")
        event_type = overflow_item.get("event_type", "unknown")
        logger.debug(
            f"开始索引记忆到长期存储 - 用户ID: {user_id}, "
            f"事件类型: {event_type}, 事件ID: {overflow_item.get('event_id', 'unknown')}"
        )

        from app.services.memory_extractor import MemoryExtractor
        from app.services.ai_service import AIService
        from app.services.embedding.factory import EmbeddingProviderFactory
        from app.models.memory import UnifiedMemory

        # 1. 提取记忆摘要
        ai_service = AIService()
        extractor = MemoryExtractor(ai_service=ai_service)

        # 根据事件类型选择提取器
        event_type = overflow_item.get("event_type")
        if event_type == "meal":
            memory_data = extractor.extract_from_nutrition(overflow_item)
        elif event_type == "exercise":
            memory_data = extractor.extract_from_exercise(overflow_item)
        elif event_type == "habit":
            memory_data = extractor.extract_from_habit(overflow_item)
        elif event_type == "weight":
            memory_data = extractor.extract_from_health_record(overflow_item)
        else:
            logger.warning(f"未知的事件类型：{event_type}")
            return False

        if not memory_data:
            logger.warning("记忆提取失败")
            return False

        logger.debug(
            f"记忆提取成功 - 用户ID: {user_id}, 记忆类型: {memory_data.get('memory_type', 'unknown')}, "
            f"摘要: {memory_data.get('content_summary', '')[:50]}..."
        )

        # 2. 生成向量嵌入
        embedding_provider = EmbeddingProviderFactory.get_provider()
        embedding = embedding_provider.embed(memory_data["content_summary"])

        if not embedding:
            logger.error("向量生成失败")
            return False

        # 3. 创建长期记忆
        memory = UnifiedMemory(
            user_id=overflow_item["user_id"],
            memory_type=memory_data["memory_type"],
            content_raw=overflow_item.get("content", ""),
            content_summary=memory_data["content_summary"],
            content_keywords=memory_data.get("keywords", []),
            importance_score=memory_data["importance"],
            source_type=overflow_item.get("source_table", "unknown"),
            source_id=str(overflow_item.get("source_id", "")),
            is_indexed=True,
            is_active=True,
        )

        # 设置向量
        memory.set_embedding(embedding)

        db.add(memory)
        db.commit()
        db.refresh(memory)

        logger.info(
            f"记忆已索引到长期记忆：{memory.id}, "
            f"用户：{overflow_item['user_id']}, "
            f"类型：{memory.memory_type}"
        )

        return True

    except Exception as e:
        logger.error(f"索引记忆失败：{e}", exc_info=True)
        db.rollback()
        return False
