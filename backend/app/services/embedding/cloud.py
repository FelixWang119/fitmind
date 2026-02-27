"""云端 Embedding 提供商 - 预留接口"""

import logging
from typing import List

from .base import EmbeddingProvider

logger = logging.getLogger(__name__)


class CloudEmbeddingProvider(EmbeddingProvider):
    """云端 Embedding 提供商（预留接口）"""

    def __init__(self, config: dict):
        """
        初始化云端 Embedding 提供商

        Args:
            config: 配置字典
                - api_key: API 密钥
                - endpoint: API 端点
                - model: 模型名称
        """
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint")
        self.model = config.get("model", "embedding-v1")
        self._dimension = 768  # 默认维度，可根据云端模型调整

        self._client = None

    def _get_client(self):
        """获取 API 客户端"""
        if self._client is not None:
            return self._client

        # TODO: 实现云端 API 客户端
        # 例如：OpenAI, Azure OpenAI, 阿里云 DashScope 等
        raise NotImplementedError("Cloud Embedding Provider is not implemented yet")

    def embed(self, text: str) -> List[float]:
        """将单个文本转为向量"""
        try:
            client = self._get_client()
            # TODO: 实现云端调用
            raise NotImplementedError("Cloud Embedding is not implemented yet")
        except NotImplementedError:
            logger.warning("Cloud embedding not implemented, using dummy")
            return [0.0] * self._dimension
        except Exception as e:
            logger.error(f"Failed to embed text with cloud provider: {e}")
            return [0.0] * self._dimension

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转为向量"""
        try:
            client = self._get_client()
            # TODO: 实现云端批量调用
            raise NotImplementedError("Cloud Embedding is not implemented yet")
        except NotImplementedError:
            logger.warning("Cloud embedding not implemented, using dummy")
            return [[0.0] * self._dimension for _ in texts]
        except Exception as e:
            logger.error(f"Failed to embed batch with cloud provider: {e}")
            return [[0.0] * self._dimension for _ in texts]

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._dimension

    def is_available(self) -> bool:
        """检查 provider 是否可用"""
        # 由于未实现，始终返回 False
        return False
