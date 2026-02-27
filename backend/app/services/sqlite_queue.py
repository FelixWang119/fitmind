"""
SQLite持久化队列实现 - 嵌入式持久化，无需独立服务

设计要点：
1. 使用SQLite作为存储后端，数据文件与应用同进程
2. 重启后队列状态完全保留，无需从数据库重建
3. 100%兼容现有MemoryQueueInterface接口
4. 内存缓存加速读取，SQLite负责持久化
"""

import sqlite3
import json
import logging
import threading
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SQLiteQueue:
    """基于SQLite的持久化FIFO队列，兼容MemoryQueueInterface接口"""

    def __init__(self, max_size: int = 100, db_path: str = "./data/memory_queue.db"):
        """
        初始化SQLite队列

        Args:
            max_size: 每个用户队列的最大容量（默认100条）
            db_path: SQLite数据库文件路径，默认在当前目录data文件夹下
        """
        self.max_size = max_size
        self.db_path = db_path
        self._lock = threading.RLock()  # 线程安全锁
        self._memory_cache: Dict[int, List[Dict]] = {}  # 用户ID -> 内存缓存

        # 初始化数据库
        self._init_database()
        logger.info(
            f"SQLite持久化队列初始化完成，容量：{max_size}，数据文件：{db_path}"
        )

    def _init_database(self):
        """初始化SQLite数据库表结构"""
        import os

        logger.debug(f"开始初始化SQLite数据库，路径: {self.db_path}")

        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            logger.debug(f"数据库目录已创建/确认: {os.path.dirname(self.db_path)}")
        except Exception as e:
            logger.error(f"创建数据库目录失败: {e}")
            raise

        try:
            with sqlite3.connect(self.db_path) as conn:
                logger.debug("SQLite数据库连接已建立")

                # 启用WAL模式，提升并发性能
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                logger.debug("SQLite WAL模式已启用")

                # 创建队列表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        event_id TEXT NOT NULL,
                        data TEXT NOT NULL,  -- JSON格式存储完整记忆数据
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_processed BOOLEAN DEFAULT 0,
                        processed_at TIMESTAMP,
                        
                        UNIQUE(user_id, event_id)
                    )
                """)
                logger.debug("memory_queue表已创建/确认")

                # 创建索引
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_queue_user_processed 
                    ON memory_queue(user_id, is_processed, created_at)
                """)
                logger.debug("idx_memory_queue_user_processed索引已创建/确认")

                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_queue_created 
                    ON memory_queue(created_at)
                """)
                logger.debug("idx_memory_queue_created索引已创建/确认")

                conn.commit()
                logger.debug("数据库初始化事务已提交")

        except sqlite3.Error as e:
            logger.error(f"SQLite数据库初始化失败: {e}")
            raise
        except Exception as e:
            logger.error(f"数据库初始化过程中发生未知错误: {e}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接（每次操作获取新连接，SQLite处理连接池）"""
        return sqlite3.connect(self.db_path)

    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        加入队列（完全兼容MemoryQueueInterface.push接口）

        Returns:
            如果队列溢出，返回被挤出的最旧数据；否则返回None
        """
        logger.debug(f"开始push操作 - 用户ID: {user_id}, 数据keys: {list(data.keys())}")

        with self._lock:
            logger.debug(f"获取锁成功 - 用户ID: {user_id}")
            conn = self._get_connection()
            logger.debug(f"数据库连接已建立 - 用户ID: {user_id}")

            try:
                # 1. 插入新记录
                event_id = data.get(
                    "event_id", f"{user_id}_{datetime.now().timestamp()}"
                )
                logger.debug(f"生成事件ID: {event_id} - 用户ID: {user_id}")

                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memory_queue 
                    (user_id, event_id, data, created_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (user_id, event_id, json.dumps(data), datetime.now().isoformat()),
                )
                logger.debug(f"数据插入成功 - 用户ID: {user_id}, 事件ID: {event_id}")

                # 2. 检查队列大小并获取溢出项
                cursor.execute(
                    """
                    SELECT id, data 
                    FROM memory_queue 
                    WHERE user_id = ? AND is_processed = 0
                    ORDER BY created_at ASC
                    LIMIT 1
                """,
                    (user_id,),
                )

                all_records = cursor.fetchall()
                current_size = len(all_records)
                logger.debug(
                    f"当前队列大小检查 - 用户ID: {user_id}, 大小: {current_size}, 限制: {self.max_size}"
                )

                overflow_item = None
                if current_size > self.max_size:
                    # 队列溢出，获取最旧的未处理记录
                    oldest = all_records[0]
                    overflow_item = json.loads(oldest[1])
                    logger.info(
                        f"队列溢出 - 用户ID: {user_id}, 溢出事件ID: {overflow_item.get('event_id', 'unknown')}, 队列大小: {current_size}"
                    )

                    # 标记为已处理（即将被索引）
                    cursor.execute(
                        """
                        UPDATE memory_queue 
                        SET is_processed = 1, processed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """,
                        (oldest[0],),
                    )
                    logger.debug(
                        f"溢出记录标记为已处理 - 记录ID: {oldest[0]}, 用户ID: {user_id}"
                    )
                else:
                    logger.debug(
                        f"队列未溢出 - 用户ID: {user_id}, 当前大小: {current_size}"
                    )

                conn.commit()
                logger.debug(f"事务已提交 - 用户ID: {user_id}")

                # 3. 更新内存缓存
                if user_id not in self._memory_cache:
                    self._memory_cache[user_id] = []
                    logger.debug(f"初始化内存缓存 - 用户ID: {user_id}")

                self._memory_cache[user_id].insert(0, data)
                logger.debug(
                    f"数据添加到内存缓存 - 用户ID: {user_id}, 缓存大小: {len(self._memory_cache[user_id])}"
                )

                # 保持缓存大小不超过max_size
                if len(self._memory_cache[user_id]) > self.max_size:
                    self._memory_cache[user_id] = self._memory_cache[user_id][
                        : self.max_size
                    ]
                    logger.debug(
                        f"内存缓存已截断 - 用户ID: {user_id}, 新大小: {len(self._memory_cache[user_id])}"
                    )

                # 4. 定期清理已处理的旧记录（每100次操作清理一次）
                if current_size % 100 == 0:
                    logger.debug(
                        f"触发定期清理 - 用户ID: {user_id}, 操作计数: {current_size}"
                    )
                    self._cleanup_processed()

                if overflow_item:
                    logger.info(
                        f"push操作完成（有溢出）- 用户ID: {user_id}, 溢出事件类型: {overflow_item.get('event_type', 'unknown')}"
                    )
                    # 异步触发溢出索引（不阻塞当前操作）
                    self._trigger_overflow_indexing(overflow_item)
                else:
                    logger.debug(f"push操作完成（无溢出）- 用户ID: {user_id}")

                return overflow_item

            except sqlite3.Error as e:
                logger.error(f"SQLite push操作失败 - 用户ID: {user_id}, 错误: {e}")
                raise
            except json.JSONDecodeError as e:
                logger.error(
                    f"JSON解析失败 - 用户ID: {user_id}, 数据: {data}, 错误: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"push操作发生未知错误 - 用户ID: {user_id}, 错误: {e}")
                raise
            finally:
                conn.close()
                logger.debug(f"数据库连接已关闭 - 用户ID: {user_id}")

    def get_all(self, user_id: int) -> List[Dict[str, Any]]:
        """获取队列所有数据（从新到旧）"""
        logger.debug(f"开始get_all操作 - 用户ID: {user_id}")

        # 优先从内存缓存读取
        if user_id in self._memory_cache and self._memory_cache[user_id]:
            cache_size = len(self._memory_cache[user_id])
            logger.debug(f"内存缓存命中 - 用户ID: {user_id}, 缓存大小: {cache_size}")
            return self._memory_cache[user_id]

        logger.debug(f"内存缓存未命中 - 用户ID: {user_id}, 将查询数据库")

        # 缓存未命中，从数据库读取
        with self._lock:
            logger.debug(f"获取锁成功 - 用户ID: {user_id}")
            conn = self._get_connection()
            logger.debug(f"数据库连接已建立 - 用户ID: {user_id}")

            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT data 
                    FROM memory_queue 
                    WHERE user_id = ? AND is_processed = 0
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (user_id, self.max_size),
                )
                logger.debug(
                    f"数据库查询已执行 - 用户ID: {user_id}, 限制: {self.max_size}"
                )

                results = []
                row_count = 0
                for row in cursor.fetchall():
                    try:
                        data = json.loads(row[0])
                        results.append(data)
                        row_count += 1
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"JSON解析失败 - 用户ID: {user_id}, 行数据: {row[0][:100]}..., 错误: {e}"
                        )
                        # 跳过无效数据，继续处理其他行

                logger.debug(
                    f"数据库查询完成 - 用户ID: {user_id}, 获取记录数: {row_count}"
                )

                # 更新内存缓存
                self._memory_cache[user_id] = results
                logger.debug(
                    f"内存缓存已更新 - 用户ID: {user_id}, 缓存大小: {len(results)}"
                )

                return results

            except sqlite3.Error as e:
                logger.error(f"SQLite get_all操作失败 - 用户ID: {user_id}, 错误: {e}")
                raise
            except Exception as e:
                logger.error(f"get_all操作发生未知错误 - 用户ID: {user_id}, 错误: {e}")
                raise
            finally:
                conn.close()
                logger.debug(f"数据库连接已关闭 - 用户ID: {user_id}")

    def size(self, user_id: int) -> int:
        """获取队列大小"""
        logger.debug(f"开始size操作 - 用户ID: {user_id}")

        # 优先从内存缓存获取
        if user_id in self._memory_cache:
            cache_size = len(self._memory_cache[user_id])
            logger.debug(f"从内存缓存获取大小 - 用户ID: {user_id}, 大小: {cache_size}")
            return cache_size

        logger.debug(f"内存缓存未命中，查询数据库 - 用户ID: {user_id}")

        with self._lock:
            logger.debug(f"获取锁成功 - 用户ID: {user_id}")
            conn = self._get_connection()
            logger.debug(f"数据库连接已建立 - 用户ID: {user_id}")

            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM memory_queue 
                    WHERE user_id = ? AND is_processed = 0
                """,
                    (user_id,),
                )
                db_size = cursor.fetchone()[0]
                logger.debug(f"数据库查询完成 - 用户ID: {user_id}, 大小: {db_size}")
                return db_size

            except sqlite3.Error as e:
                logger.error(f"SQLite size操作失败 - 用户ID: {user_id}, 错误: {e}")
                raise
            except Exception as e:
                logger.error(f"size操作发生未知错误 - 用户ID: {user_id}, 错误: {e}")
                raise
            finally:
                conn.close()
                logger.debug(f"数据库连接已关闭 - 用户ID: {user_id}")

    def clear(self, user_id: int) -> None:
        """清空队列（主要用于测试）"""
        logger.info(f"开始clear操作 - 用户ID: {user_id}")

        with self._lock:
            logger.debug(f"获取锁成功 - 用户ID: {user_id}")
            conn = self._get_connection()
            logger.debug(f"数据库连接已建立 - 用户ID: {user_id}")

            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE memory_queue 
                    SET is_processed = 1, processed_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND is_processed = 0
                """,
                    (user_id,),
                )
                affected_rows = cursor.rowcount
                conn.commit()
                logger.info(
                    f"队列清空完成 - 用户ID: {user_id}, 影响记录数: {affected_rows}"
                )

                # 清理缓存
                if user_id in self._memory_cache:
                    del self._memory_cache[user_id]
                    logger.debug(f"内存缓存已清理 - 用户ID: {user_id}")
                else:
                    logger.debug(f"内存缓存不存在 - 用户ID: {user_id}")

            except sqlite3.Error as e:
                logger.error(f"SQLite clear操作失败 - 用户ID: {user_id}, 错误: {e}")
                raise
            except Exception as e:
                logger.error(f"clear操作发生未知错误 - 用户ID: {user_id}, 错误: {e}")
                raise
            finally:
                conn.close()
                logger.debug(f"数据库连接已关闭 - 用户ID: {user_id}")

    def _trigger_overflow_indexing(self, overflow_item: Dict[str, Any]):
        """触发溢出索引（异步处理，不阻塞当前操作）"""
        try:
            # 异步触发索引
            asyncio.create_task(self._async_index_overflow_item(overflow_item))
            logger.debug(
                f"溢出索引任务已创建 - 用户ID: {overflow_item.get('user_id')}, "
                f"事件类型: {overflow_item.get('event_type')}"
            )
        except Exception as e:
            logger.error(f"创建溢出索引任务失败: {e}")

    async def _async_index_overflow_item(self, overflow_item: Dict[str, Any]):
        """异步索引溢出项"""
        try:
            # 延迟导入以避免循环依赖
            from app.services.memory_index_service import index_memory_to_long_term
            from app.core.database import get_db

            logger.debug(
                f"开始异步索引溢出项 - 用户ID: {overflow_item.get('user_id')}, "
                f"事件类型: {overflow_item.get('event_type')}"
            )

            # 获取数据库会话并索引
            db_gen = get_db()
            db = next(db_gen)
            try:
                await index_memory_to_long_term(db=db, overflow_item=overflow_item)
                logger.info(
                    f"溢出项索引成功 - 用户ID: {overflow_item.get('user_id')}, "
                    f"事件类型: {overflow_item.get('event_type')}"
                )
            finally:
                db.close()

        except Exception as e:
            logger.error(f"溢出项索引失败: {e}", exc_info=True)

    def _cleanup_processed(self, days_to_keep: int = 7):
        """清理已处理的旧记录（保留最近7天）"""
        logger.debug(f"开始清理已处理记录 - 保留天数: {days_to_keep}")

        try:
            conn = self._get_connection()
            logger.debug("数据库连接已建立 - 清理操作")

            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM memory_queue 
                WHERE is_processed = 1 
                AND processed_at < datetime('now', ?)
            """,
                (f"-{days_to_keep} days",),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(
                    f"清理了 {deleted_count} 条已处理的旧记录 - 保留最近 {days_to_keep} 天"
                )
            else:
                logger.debug(f"没有需要清理的已处理记录 - 保留最近 {days_to_keep} 天")

        except sqlite3.Error as e:
            logger.error(f"清理已处理记录时SQLite错误: {e}")
        except Exception as e:
            logger.warning(f"清理已处理记录时出错: {e}")
