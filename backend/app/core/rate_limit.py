"""速率限制工具

速率限制配置:
- 注册：5 次/分钟/IP (防止恶意注册)
- 登录：10 次/分钟/IP (防止暴力破解)
"""

import time
from typing import Dict, Optional
from fastapi import HTTPException, Request, status
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """基于 IP 的速率限制器

    配置:
        requests_per_minute: 每分钟允许的最大请求数 (默认：5)
        window_seconds: 时间窗口 (默认：60 秒)

    使用示例:
        limiter = RateLimiter(requests_per_minute=5)
        if limiter.is_rate_limited(client_ip):
            raise HTTPException(429, "Too many requests")
    """

    def __init__(self, requests_per_minute: int = 5):
        """初始化速率限制器

        Args:
            requests_per_minute: 每分钟允许的最大请求数，默认 5 次
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}

    def is_rate_limited(self, key: str) -> bool:
        """检查是否超过速率限制"""
        current_time = time.time()

        # 清理过期的请求记录
        if key in self.requests:
            self.requests[key] = [
                req_time
                for req_time in self.requests[key]
                if current_time - req_time < 60  # 保留最近60秒的记录
            ]
        else:
            self.requests[key] = []

        # 检查请求次数
        if len(self.requests[key]) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded", key=key, count=len(self.requests[key])
            )
            return True

        # 记录当前请求
        self.requests[key].append(current_time)
        return False

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求（is_rate_limited 的别名）"""
        return not self.is_rate_limited(key)

    def get_remaining_requests(self, key: str) -> int:
        """获取剩余请求次数"""
        current_time = time.time()

        if key not in self.requests:
            return self.requests_per_minute

        # 清理过期的请求记录
        self.requests[key] = [
            req_time for req_time in self.requests[key] if current_time - req_time < 60
        ]

        return max(0, self.requests_per_minute - len(self.requests[key]))


# 全局速率限制器实例
registration_limiter = RateLimiter(requests_per_minute=5)  # 每分钟最多 5 次注册请求
login_limiter = RateLimiter(
    requests_per_minute=5
)  # 每分钟最多 5 次登录请求（安全加固）


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    if request.client:
        return request.client.host
    return "unknown"


async def rate_limit_registration(request: Request):
    """注册接口速率限制依赖项"""
    client_ip = get_client_ip(request)
    key = f"registration:{client_ip}"

    if registration_limiter.is_rate_limited(key):
        remaining = registration_limiter.get_remaining_requests(key)
        retry_after = 60  # 60秒后重试

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too many registration requests",
                "message": "请稍后再试",
                "retry_after": retry_after,
                "remaining": remaining,
            },
            headers={"Retry-After": str(retry_after)},
        )


async def rate_limit_login(request: Request):
    """登录接口速率限制依赖项"""
    client_ip = get_client_ip(request)
    key = f"login:{client_ip}"

    if login_limiter.is_rate_limited(key):
        remaining = login_limiter.get_remaining_requests(key)
        retry_after = 60  # 60秒后重试

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too many login attempts",
                "message": "请稍后再试",
                "retry_after": retry_after,
                "remaining": remaining,
            },
            headers={"Retry-After": str(retry_after)},
        )


def cleanup_old_requests():
    """清理旧的请求记录（可定期调用）"""
    current_time = time.time()
    keys_to_delete = []

    for key, timestamps in registration_limiter.requests.items():
        # 清理超过5分钟的记录
        registration_limiter.requests[key] = [
            ts for ts in timestamps if current_time - ts < 300
        ]
        if not registration_limiter.requests[key]:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del registration_limiter.requests[key]

    keys_to_delete = []
    for key, timestamps in login_limiter.requests.items():
        # 清理超过5分钟的记录
        login_limiter.requests[key] = [
            ts for ts in timestamps if current_time - ts < 300
        ]
        if not login_limiter.requests[key]:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del login_limiter.requests[key]


def reset_rate_limiters():
    """重置速率限制器（用于测试）"""
    registration_limiter.requests.clear()
    login_limiter.requests.clear()
