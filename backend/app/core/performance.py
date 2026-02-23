"""性能监控和优化模块"""
import functools
import time
from contextlib import contextmanager
from typing import Any, Callable

import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = structlog.get_logger()


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self._slow_query_threshold = 1.0  # 慢查询阈值（秒）
        self._query_stats = {}

    @contextmanager
    def monitor_db_query(self, query_name: str):
        """监控数据库查询"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time

            # 记录查询统计
            if query_name not in self._query_stats:
                self._query_stats[query_name] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "max_time": 0,
                    "slow_queries": 0,
                }

            stats = self._query_stats[query_name]
            stats["count"] += 1
            stats["total_time"] += duration
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["max_time"] = max(stats["max_time"], duration)

            if duration > self._slow_query_threshold:
                stats["slow_queries"] += 1
                logger.warning(
                    f"Slow query detected: {query_name}",
                    duration=round(duration, 3),
                    threshold=self._slow_query_threshold,
                )

    def get_stats(self) -> dict:
        """获取性能统计"""
        return {
            "query_stats": self._query_stats,
            "total_queries": sum(s["count"] for s in self._query_stats.values()),
            "slow_query_threshold": self._slow_query_threshold,
        }

    def reset_stats(self):
        """重置统计"""
        self._query_stats.clear()


# 全局性能监控实例
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def timer_decorator(func_name: str = None):
    """计时装饰器"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or func.__name__

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if duration > 0.5:  # 记录超过500ms的操作
                    logger.info(
                        f"Slow operation: {name}",
                        duration=round(duration, 3),
                    )

        return wrapper

    return decorator


class QueryOptimizer:
    """查询优化器"""

    @staticmethod
    def add_pagination(query, skip: int = 0, limit: int = 100):
        """添加分页"""
        return query.offset(skip).limit(limit)

    @staticmethod
    def optimize_count_query(db: Session, model, filters=None):
        """优化计数查询"""
        query = db.query(func.count(model.id))

        if filters:
            query = query.filter(*filters)

        return query.scalar()

    @staticmethod
    def batch_query(db: Session, query, batch_size: int = 1000):
        """批量查询"""
        offset = 0
        while True:
            batch = query.offset(offset).limit(batch_size).all()
            if not batch:
                break
            yield batch
            offset += batch_size

    @staticmethod
    def select_related(db: Session, query, *relations):
        """添加预加载"""
        from sqlalchemy.orm import joinedload

        for relation in relations:
            query = query.options(joinedload(relation))

        return query


class ResponseOptimizer:
    """响应优化器"""

    @staticmethod
    def paginate_response(items: list, total: int, skip: int, limit: int) -> dict:
        """生成分页响应"""
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + len(items)) < total,
        }

    @staticmethod
    def compress_large_response(data: dict, threshold_kb: int = 100) -> dict:
        """压缩大响应"""
        import json

        size_kb = len(json.dumps(data)) / 1024

        if size_kb > threshold_kb:
            # 对于大数据，只保留关键字段
            if "items" in data and len(data["items"]) > 100:
                data["items"] = data["items"][:100]
                data["_truncated"] = True
                data["_total_items"] = len(data.get("items", []))

        return data

    @staticmethod
    def add_cache_headers(response, max_age: int = 300):
        """添加缓存头"""
        response.headers["Cache-Control"] = f"max-age={max_age}"
        response.headers["X-Cache"] = "HIT"
        return response


class BulkOperations:
    """批量操作工具"""

    @staticmethod
    def bulk_insert(db: Session, model, items: list, batch_size: int = 1000):
        """批量插入"""
        from sqlalchemy.dialects.postgresql import insert

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            db.bulk_insert_mappings(model, batch)
            db.commit()

    @staticmethod
    def bulk_update(db: Session, model, updates: list, batch_size: int = 1000):
        """批量更新"""
        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]
            db.bulk_update_mappings(model, batch)
            db.commit()

    @staticmethod
    def bulk_delete(db: Session, model, ids: list, batch_size: int = 1000):
        """批量删除"""
        for i in range(0, len(ids), batch_size):
            batch = ids[i : i + batch_size]
            db.query(model).filter(model.id.in_(batch)).delete(
                synchronize_session=False
            )
            db.commit()


# 数据库连接池优化配置
DATABASE_OPTIMIZATION = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}

# API响应优化配置
API_OPTIMIZATION = {
    "default_page_size": 50,
    "max_page_size": 200,
    "compression_threshold_kb": 100,
    "response_timeout_seconds": 30,
}

# 缓存策略配置
CACHE_STRATEGY = {
    "user_data": {
        "ttl": 300,
        "invalidate_on_update": True,
    },
    "dashboard": {
        "ttl": 180,
        "invalidate_on_update": True,
    },
    "reports": {
        "ttl": 1800,
        "invalidate_on_update": False,
    },
    "static_data": {
        "ttl": 3600,
        "invalidate_on_update": False,
    },
}


@contextmanager
def measure_execution_time(operation_name: str):
    """测量执行时间"""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.debug(f"{operation_name} took {duration:.3f}s")


class AsyncTaskQueue:
    """异步任务队列（简化版）"""

    def __init__(self):
        self._tasks = []

    def add_task(self, task: Callable, *args, **kwargs):
        """添加任务"""
        self._tasks.append((task, args, kwargs))

    def execute_all(self):
        """执行所有任务"""
        results = []
        for task, args, kwargs in self._tasks:
            try:
                result = task(*args, **kwargs)
                results.append(("success", result))
            except Exception as e:
                logger.error(f"Task failed: {e}")
                results.append(("error", str(e)))

        self._tasks.clear()
        return results


def optimize_query_for_user_data(db: Session, user_id: int, days: int = 30):
    """优化用户数据查询"""
    from datetime import datetime, timedelta

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # 使用索引优化查询
    query = text(
        """
        SELECT * FROM health_records 
        WHERE user_id = :user_id 
        AND record_date >= :start_date 
        AND record_date <= :end_date
        ORDER BY record_date DESC
    """
    )

    result = db.execute(
        query,
        {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return result.fetchall()
