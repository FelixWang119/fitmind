"""缓存管理模块"""
import hashlib
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import structlog

logger = structlog.get_logger()


class SimpleCache:
    """简单内存缓存"""

    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self._ttl = default_ttl
        self._access_count = 0
        self._hit_count = 0

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        self._access_count += 1

        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                self._hit_count += 1
                return value
            else:
                # 过期，删除
                del self._cache[key]

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        expiry = time.time() + (ttl or self._ttl)
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        logger.info("Cache cleared")

    def clear_expired(self) -> int:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items() if expiry <= current_time
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_stats(self) -> dict:
        """获取缓存统计"""
        hit_rate = (
            (self._hit_count / self._access_count * 100)
            if self._access_count > 0
            else 0
        )
        return {
            "total_items": len(self._cache),
            "access_count": self._access_count,
            "hit_count": self._hit_count,
            "hit_rate": round(hit_rate, 2),
            "memory_usage_mb": len(str(self._cache)) / (1024 * 1024),
        }


# 全局缓存实例
_cache_instance = None


def get_cache() -> SimpleCache:
    """获取缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SimpleCache()
    return _cache_instance


def cached(prefix: str, ttl: int = 300):
    """缓存装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # 生成缓存键
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {prefix}")
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(prefix: str):
    """使缓存失效"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # 执行函数
            result = func(*args, **kwargs)

            # 清除相关缓存
            keys_to_delete = [
                key
                for key in cache._cache.keys()
                if key.startswith(hashlib.md5(prefix.encode()).hexdigest()[:16])
            ]
            for key in keys_to_delete:
                cache.delete(key)

            logger.debug(
                f"Invalidated {len(keys_to_delete)} cache entries for {prefix}"
            )

            return result

        return wrapper

    return decorator


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.cache = get_cache()
        self._cleanup_interval = 3600  # 1小时
        self._last_cleanup = time.time()

    def auto_cleanup(self):
        """自动清理过期缓存"""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            cleared = self.cache.clear_expired()
            self._last_cleanup = current_time
            logger.info(f"Auto-cleared {cleared} expired cache entries")

    def get_user_cache_key(self, user_id: int, data_type: str) -> str:
        """获取用户缓存键"""
        return f"user:{user_id}:{data_type}"

    def invalidate_user_cache(self, user_id: int):
        """使用户缓存失效"""
        keys_to_delete = [
            key for key in self.cache._cache.keys() if f"user:{user_id}:" in key
        ]
        for key in keys_to_delete:
            self.cache.delete(key)

        logger.info(f"Invalidated cache for user {user_id}")


# 常用数据缓存TTL配置
CACHE_TTL_CONFIG = {
    "user_profile": 600,  # 10分钟
    "dashboard": 300,  # 5分钟
    "nutrition": 600,  # 10分钟
    "habits": 300,  # 5分钟
    "emotional": 300,  # 5分钟
    "scientific_report": 1800,  # 30分钟
    "leaderboard": 3600,  # 1小时
}
