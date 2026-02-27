"""Embedding 提供商工厂"""

import logging
from typing import Optional

from .base import EmbeddingProvider, DummyEmbeddingProvider
from .local import LocalEmbeddingProvider
from .cloud import CloudEmbeddingProvider

logger = logging.getLogger(__name__)


class EmbeddingProviderFactory:
    """Embedding 提供商工厂"""

    _instance: Optional[EmbeddingProvider] = None
    _config: dict = {}

    @classmethod
    def initialize(cls, config: dict):
        """
        初始化工厂

        Args:
            config: 配置字典
                - provider: "local" 或 "cloud"
                - local: 本地配置
                - cloud: 云端配置
        """
        cls._config = config
        cls._instance = None  # 重置实例

    @classmethod
    def get_provider(cls) -> EmbeddingProvider:
        """
        获取 Embedding 提供商实例

        Returns:
            EmbeddingProvider 实例
        """
        if cls._instance is not None:
            return cls._instance

        if not cls._config:
            logger.warning("Embedding provider not configured, using dummy")
            cls._instance = DummyEmbeddingProvider()
            return cls._instance

        provider_type = cls._config.get("provider", "local")

        try:
            if provider_type == "local":
                cls._instance = LocalEmbeddingProvider(cls._config.get("local", {}))
            elif provider_type == "cloud":
                cls._instance = CloudEmbeddingProvider(cls._config.get("cloud", {}))
            else:
                logger.warning(f"Unknown provider type: {provider_type}, using dummy")
                cls._instance = DummyEmbeddingProvider()
        except Exception as e:
            logger.error(f"Failed to create embedding provider: {e}")
            cls._instance = DummyEmbeddingProvider()

        # 检查 provider 是否可用
        if not cls._instance.is_available():
            logger.warning(f"Provider {provider_type} is not available, using dummy")
            cls._instance = DummyEmbeddingProvider()

        return cls._instance

    @classmethod
    def get_dimension(cls) -> int:
        """获取向量维度"""
        return cls.get_provider().get_dimension()
