"""性能优化中间件"""
import functools
import gzip
import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import get_cache
from app.core.performance import get_performance_monitor

logger = structlog.get_logger()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.monitor = get_performance_monitor()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 检查缓存
        cache_key = f"response:{request.url.path}:{hash(str(request.query_params))}"
        cache = get_cache()

        # 只对GET请求使用缓存
        if request.method == "GET" and not request.url.path.startswith("/api/v1/auth"):
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit: {request.url.path}")
                return Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"],
                    media_type=cached_response["media_type"],
                )

        # 执行请求
        try:
            response = await call_next(request)

            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(round(process_time, 3))

            # 记录慢请求
            if process_time > 1.0:
                logger.warning(
                    "Slow request detected",
                    path=request.url.path,
                    method=request.method,
                    duration=round(process_time, 3),
                )

            # 缓存响应
            if request.method == "GET" and response.status_code == 200:
                if not request.url.path.startswith("/api/v1/auth"):
                    cache_data = {
                        "content": response.body,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "media_type": response.media_type,
                    }
                    ttl = 300
                    if "dashboard" in request.url.path:
                        ttl = 180
                    elif "scientific-report" in request.url.path:
                        ttl = 1800

                    cache.set(cache_key, cache_data, ttl)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                path=request.url.path,
                method=request.method,
                duration=round(process_time, 3),
                error=str(e),
            )
            raise


class CompressionMiddleware(BaseHTTPMiddleware):
    """响应压缩中间件"""

    def __init__(self, app, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        accept_encoding = request.headers.get("accept-encoding", "")

        if "gzip" in accept_encoding and response.body:
            body_size = len(response.body)

            if body_size >= self.minimum_size:
                try:
                    compressed = gzip.compress(response.body)

                    if len(compressed) < body_size:
                        response.body = compressed
                        response.headers["Content-Encoding"] = "gzip"
                        response.headers["Content-Length"] = str(len(compressed))
                except Exception as e:
                    logger.error(f"Compression failed: {e}")

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """缓存控制中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        path = request.url.path

        if path.startswith("/api/v1/dashboard"):
            response.headers["Cache-Control"] = "public, max-age=180"
        elif path.startswith("/api/v1/scientific-persona/report"):
            response.headers["Cache-Control"] = "public, max-age=1800"
        elif path.startswith("/api/v1/nutrition") and request.method == "GET":
            response.headers["Cache-Control"] = "public, max-age=600"
        elif path.startswith("/api/v1/gamification"):
            response.headers["Cache-Control"] = "no-cache"
        elif path.startswith("/api/v1/auth"):
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["Cache-Control"] = "no-cache"

        return response
