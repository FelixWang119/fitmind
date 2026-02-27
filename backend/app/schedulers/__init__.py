"""定时任务调度器 - 记忆索引等定时作业"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import get_db

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = AsyncIOScheduler()


async def start_scheduler():
    """启动调度器"""
    global scheduler

    # 如果调度器未运行，则启动
    if not scheduler.running:
        scheduler.start()

        # 注意：根据ADR-001决策，已移除定期索引任务
        # 记忆索引现在通过SQLite队列溢出机制触发，无需定期调度
        logger.info("定时任务已启动（记忆索引任务已移除，使用溢出触发机制）")

        # 设置清理任务
        await setup_cleanup_job()

        # 验证任务是否已添加
        jobs = scheduler.get_jobs()
        logger.info(f"当前注册的任务数量: {len(jobs)}")


async def stop_scheduler():
    """停止调度器"""
    global scheduler

    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务已停止")


# 注意：memory_indexing_task 函数已根据ADR-001决策删除
# 记忆索引现在通过SQLite队列溢出机制触发，无需定期调度任务


async def cleanup_expired_memories_task():
    """清理过期记忆任务 - 清理超出保留期限的记忆"""
    logger.info("开始执行记忆清理任务...")

    try:
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)

        try:
            # 这里可以实现具体的清理逻辑
            # 比如清理超出 config.yaml 中设定的 retention 天数的记忆数据
            from app.models.memory import UnifiedMemory
            from app.core.config import settings
            import datetime as dt

            # 获取保留天数（如果配置）
            retention_days = getattr(settings, "MEMORY_RETENTION_DAYS", 30)

            cutoff_date = dt.datetime.utcnow() - dt.timedelta(days=retention_days)

            # 查找需要清理的记忆（这里只是占位符，实际实现可能需要更复杂的逻辑）
            expiring_memories = (
                db.query(UnifiedMemory)
                .filter(
                    UnifiedMemory.created_at < cutoff_date,
                    UnifiedMemory.is_active == True,
                )
                .limit(100)
                .all()
            )

            if expiring_memories:
                # 模拟更新这些记忆的状态
                for memory in expiring_memories:
                    memory.is_active = False  # 标记为非活跃，而不是硬删除
                    logger.debug(f"标记记忆 {memory.id} 为非活跃状态")
                    # 也可以改为软删除或归档

                db.commit()
                logger.info(f"清理了 {len(expiring_memories)} 条过期记忆")
            else:
                logger.info("没有找到过期记忆")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"记忆清理任务执行失败: {e}", exc_info=True)


# 如果要启动记忆清理任务，可在这里添加
async def setup_cleanup_job():
    """设置清理任务（可选，根据需要决定是否启用）"""
    # 获取配置确定是否启用清理
    enable_cleanup = True  # 默认启用，实际中应从配置获取

    if enable_cleanup:
        # 每天早上4点执行清理任务
        scheduler.add_job(
            cleanup_expired_memories_task,
            trigger=CronTrigger(hour=4, minute=0),  # 比索引任务晚一小时
            id="memory_cleanup",
            name="记忆清理任务",
            replace_existing=True,
        )
        logger.info("记忆清理任务已安排在每天 04:00")
