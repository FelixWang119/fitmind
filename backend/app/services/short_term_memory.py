"""
短期记忆服务 - 管理用户的短期记忆队列（FIFO 队列）

v2.0 架构变更:
- 使用 SQLite 持久化队列作为默认实现
- 队列状态由 SQLite 自动管理，重启后自动恢复
- 不再依赖源数据表的 is_indexed 字段
- 移除启动时从数据库加载的逻辑

设计要点：
1. 使用 SQLite 嵌入式数据库实现持久化 FIFO 队列
2. 每个用户队列容量限制为 100 条
3. 新数据入队时，如果队列已满，最旧的数据会被挤出
4. 挤出的数据会触发索引 Pipeline，写入 pgvector（长期记忆）
5. 重启时，SQLite 文件自动恢复队列状态，无需手动加载
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque

logger = logging.getLogger(__name__)


class MemoryQueueInterface:
    """队列抽象接口"""

    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """加入队列，如果溢出返回被挤出的数据"""
        raise NotImplementedError

    def get_all(self, user_id: int) -> List[Dict[str, Any]]:
        """获取队列所有数据（从新到旧）"""
        raise NotImplementedError

    def size(self, user_id: int) -> int:
        """获取队列大小"""
        raise NotImplementedError

    def clear(self, user_id: int) -> None:
        """清空队列"""
        raise NotImplementedError


class InMemoryQueue(MemoryQueueInterface):
    """内存队列实现"""

    def __init__(self, max_size: int = 100):
        """
        初始化内存队列

        Args:
            max_size: 每个用户队列的最大容量（默认 100 条）
        """
        self.max_size = max_size
        self._queues: Dict[int, deque] = {}
        logger.info(f"短期记忆队列初始化完成，窗口大小：{max_size}")

    def _get_queue(self, user_id: int) -> deque:
        """获取用户的队列，不存在则创建"""
        if user_id not in self._queues:
            self._queues[user_id] = deque(maxlen=self.max_size)
        return self._queues[user_id]

    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        加入队列

        Returns:
            如果队列溢出，返回被挤出的最旧数据；否则返回 None
        """
        queue = self._get_queue(user_id)

        # 检查是否即将溢出
        overflow_item = None
        if len(queue) >= self.max_size:
            # 队列已满，获取最旧的数据（即将被挤出）
            overflow_item = queue[-1]
            logger.debug(f"用户 {user_id} 短期记忆队列已满，最旧数据将被挤出")

        # 添加新数据到队首
        queue.appendleft(data)

        logger.debug(f"用户 {user_id} 添加数据到短期记忆，当前队列大小：{len(queue)}")

        return overflow_item

    def get_all(self, user_id: int) -> List[Dict[str, Any]]:
        """获取队列所有数据（从新到旧）"""
        queue = self._get_queue(user_id)
        return list(queue)

    def size(self, user_id: int) -> int:
        """获取队列大小"""
        return len(self._get_queue(user_id))

    def clear(self, user_id: int) -> None:
        """清空队列"""
        if user_id in self._queues:
            self._queues[user_id].clear()
            logger.debug(f"用户 {user_id} 的短期记忆队列已清空")


def create_queue_instance(max_size: int = 100) -> MemoryQueueInterface:
    """
    根据环境变量创建队列实例

    v2.0: 默认使用 SQLite 持久化队列

    环境变量 MEMORY_QUEUE_BACKEND 可选值:
    - 'sqlite': SQLite 持久化队列 (默认，v2.0)
    - 'memory': 内存队列 (仅用于测试)
    - 'redis': Redis 队列 (生产环境扩展，需要 REDIS_URL 配置)
    """
    backend = os.environ.get("MEMORY_QUEUE_BACKEND", "sqlite").lower()

    if backend == "sqlite":
        try:
            # 延迟导入，避免不必要的依赖
            from .sqlite_queue import SQLiteQueue

            db_path = os.environ.get("SQLITE_QUEUE_DB_PATH", "./data/memory_queue.db")
            logger.info(
                f"使用 SQLite 持久化队列，容量：{max_size}，数据文件：{db_path}"
            )
            return SQLiteQueue(max_size=max_size, db_path=db_path)
        except ImportError as e:
            logger.error(f"无法导入 SQLiteQueue，回退到内存队列：{e}")
            return InMemoryQueue(max_size=max_size)

    elif backend == "memory":
        logger.warning(f"使用内存队列（仅测试用），容量：{max_size}")
        return InMemoryQueue(max_size=max_size)

    elif backend == "redis":
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            logger.error("REDIS_URL 未配置，回退到 SQLite 队列")
            try:
                from .sqlite_queue import SQLiteQueue

                db_path = os.environ.get(
                    "SQLITE_QUEUE_DB_PATH", "./data/memory_queue.db"
                )
                return SQLiteQueue(max_size=max_size, db_path=db_path)
            except ImportError:
                return InMemoryQueue(max_size=max_size)
        try:
            # 延迟导入 Redis 队列实现
            from .redis_queue import RedisQueue  # 需要实现这个类

            logger.info(f"使用 Redis 队列，容量：{max_size}，Redis URL: {redis_url}")
            return RedisQueue(max_size=max_size, redis_url=redis_url)
        except ImportError as e:
            logger.error(f"无法导入 RedisQueue，回退到 SQLite 队列：{e}")
            try:
                from .sqlite_queue import SQLiteQueue

                db_path = os.environ.get(
                    "SQLITE_QUEUE_DB_PATH", "./data/memory_queue.db"
                )
                return SQLiteQueue(max_size=max_size, db_path=db_path)
            except ImportError:
                return InMemoryQueue(max_size=max_size)

    else:
        logger.warning(f"未知的队列后端配置：{backend}，使用 SQLite 队列")
        try:
            from .sqlite_queue import SQLiteQueue

            db_path = os.environ.get("SQLITE_QUEUE_DB_PATH", "./data/memory_queue.db")
            return SQLiteQueue(max_size=max_size, db_path=db_path)
        except ImportError:
            return InMemoryQueue(max_size=max_size)


class ShortTermMemoryService:
    """
    短期记忆服务 - 管理用户的短期记忆队列

    职责：
    1. 维护用户的 FIFO 短期记忆队列（容量 100 条）
    2. 数据入队时检查是否溢出
    3. 如果溢出，返回被挤出的数据（由调用者触发索引到长期记忆）
    """

    def __init__(
        self, queue: Optional[MemoryQueueInterface] = None, max_size: int = 100
    ):
        if queue is None:
            # 根据环境变量自动选择队列实现
            self.queue = create_queue_instance(max_size=max_size)
        else:
            self.queue = queue
        self.max_size = max_size
        logger.info(
            f"短期记忆服务初始化完成，窗口大小：{max_size}，队列类型：{type(self.queue).__name__}"
        )

    def add_memory(
        self,
        user_id: int,
        event_type: str,
        event_source: str,
        content: str,
        metrics: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        source_table: Optional[str] = None,
        source_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        添加数据到短期记忆队列

        Returns:
            如果队列溢出，返回被挤出的数据（需要触发索引到长期记忆）
            否则返回 None
        """
        logger.info(
            f"开始add_memory操作 - 用户ID: {user_id}, 事件类型: {event_type}, "
            f"事件源: {event_source}, 内容长度: {len(content)}"
        )

        # 构建记忆数据
        memory_data = {
            "event_id": f"{user_id}_{datetime.now().timestamp()}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_source": event_source,
            "content": content,
            "metrics": metrics or {},
            "context": context or {},
            "source_table": source_table,
            "source_id": source_id,
        }

        logger.info(
            f"记忆数据构建完成 - 用户ID: {user_id}, 事件ID: {memory_data['event_id']}, "
            f"源表: {source_table}, 源ID: {source_id}"
        )

        # 加入队列，检查是否溢出
        logger.info(f"调用队列push操作 - 用户ID: {user_id}")
        overflow_item = self.queue.push(user_id, memory_data)

        if overflow_item:
            logger.info(
                f"用户 {user_id} 短期记忆队列溢出 (容量{self.max_size}条)，"
                f"需要索引到长期记忆：{overflow_item.get('event_type')} - {overflow_item.get('content', '')[:50]}"
            )
            logger.info(
                f"溢出数据详情 - 用户ID: {user_id}, 事件ID: {overflow_item.get('event_id')}, "
                f"时间戳: {overflow_item.get('timestamp')}"
            )
            # 强制触发索引（不等待异步完成）
            import asyncio
            from app.services.memory_index_service import index_memory_to_long_term
            from app.core.database import get_db

            try:
                db_gen = get_db()
                db = next(db_gen)
                try:
                    asyncio.run(
                        index_memory_to_long_term(db=db, overflow_item=overflow_item)
                    )
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"强制索引失败: {e}")
        else:
            logger.info(
                f"记忆添加成功（无溢出）- 用户ID: {user_id}, 事件类型: {event_type}, "
                f"队列类型: {type(self.queue).__name__}"
            )
            # 无溢出时也尝试添加到长期记忆（用于新数据）
            self._try_add_to_long_term(user_id, memory_data)

        return overflow_item

    def get_recent_memories(
        self, user_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户最近的短期记忆"""
        logger.debug(f"开始get_recent_memories操作 - 用户ID: {user_id}, 限制: {limit}")

        all_memories = self.queue.get_all(user_id)
        result_count = min(len(all_memories), limit)

        logger.debug(
            f"获取最近记忆完成 - 用户ID: {user_id}, 总记忆数: {len(all_memories)}, "
            f"返回数量: {result_count}, 队列类型: {type(self.queue).__name__}"
        )

        if all_memories and result_count > 0:
            logger.debug(
                f"返回的记忆事件类型: {[m.get('event_type', 'unknown') for m in all_memories[: min(3, result_count)]]}"
            )

        return all_memories[:limit]

    def get_queue_size(self, user_id: int) -> int:
        """获取队列当前大小"""
        logger.debug(f"开始get_queue_size操作 - 用户ID: {user_id}")

        size = self.queue.size(user_id)

        logger.debug(
            f"队列大小查询完成 - 用户ID: {user_id}, 大小: {size}, "
            f"队列类型: {type(self.queue).__name__}"
        )

        return size

    def load_memories(self, user_id: int, memories: List[Dict[str, Any]]) -> None:
        """
        批量加载记忆到队列（用于启动时从数据库加载）

        Args:
            user_id: 用户 ID
            memories: 记忆列表（按时间从旧到新排序）
        """
        logger.info(
            f"开始load_memories操作 - 用户ID: {user_id}, 记忆数量: {len(memories)}, "
            f"队列类型: {type(self.queue).__name__}"
        )

        if not memories:
            logger.debug(f"空记忆列表，跳过加载 - 用户ID: {user_id}")
            return

        # 记录记忆类型分布
        event_types = {}
        for memory in memories:
            event_type = memory.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        logger.debug(f"记忆类型分布 - 用户ID: {user_id}, 分布: {event_types}")

        # 从旧到新依次添加，这样最新的会在队首
        loaded_count = 0
        for memory in reversed(memories):  # 反转，从最旧的开始
            try:
                self.queue.push(user_id, memory)
                loaded_count += 1
            except Exception as e:
                logger.error(
                    f"加载单个记忆失败 - 用户ID: {user_id}, 事件ID: {memory.get('event_id', 'unknown')}, "
                    f"错误: {e}"
                )

                # 继续加载其他记忆，不中断整个流程
                continue

        logger.info(
            f"记忆加载完成 - 用户ID: {user_id}, 尝试加载: {len(memories)}, "
            f"成功加载: {loaded_count}, 失败: {len(memories) - loaded_count}"
        )

    def _try_add_to_long_term(self, user_id: int, memory_data: Dict[str, Any]) -> bool:
        """
        尝试将记忆添加到长期记忆（非阻塞）

        Args:
            user_id: 用户ID
            memory_data: 记忆数据

        Returns:
            是否成功添加
        """
        try:
            # 异步触发索引
            import asyncio
            from app.services.memory_index_service import index_memory_to_long_term
            from app.core.database import get_db

            # 异步调用，不阻塞当前操作
            asyncio.create_task(self._async_index_single_memory(user_id, memory_data))
            logger.debug(
                f"已创建长期记忆索引任务 - 用户ID: {user_id}, 事件类型: {memory_data.get('event_type')}"
            )
            return True
        except Exception as e:
            logger.error(f"创建长期记忆索引任务失败: {e}")
            return False

    async def _async_index_single_memory(
        self, user_id: int, memory_data: Dict[str, Any]
    ):
        """异步索引单条记忆到长期记忆"""
        try:
            from app.services.memory_index_service import index_memory_to_long_term
            from app.core.database import get_db

            # 获取数据库会话并索引
            db_gen = get_db()
            db = next(db_gen)
            try:
                # 将短期记忆转换为溢出格式
                overflow_item = {
                    **memory_data,
                    "user_id": user_id,
                }
                await index_memory_to_long_term(db=db, overflow_item=overflow_item)
                logger.info(
                    f"单条记忆索引成功 - 用户ID: {user_id}, 事件类型: {memory_data.get('event_type')}"
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"单条记忆索引失败: {e}", exc_info=True)


# 全局单例
_short_term_memory_service: Optional[ShortTermMemoryService] = None


def get_short_term_memory_service() -> ShortTermMemoryService:
    """获取短期记忆服务单例"""
    global _short_term_memory_service
    if _short_term_memory_service is None:
        _short_term_memory_service = ShortTermMemoryService(max_size=100)
    return _short_term_memory_service


def init_short_term_memory_service(max_size: int = 100) -> ShortTermMemoryService:
    """初始化短期记忆服务（用于启动时）"""
    global _short_term_memory_service
    _short_term_memory_service = ShortTermMemoryService(max_size=max_size)
    return _short_term_memory_service
