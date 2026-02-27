"""Embedding 服务抽象层"""

from abc import ABC, abstractmethod
from typing import List, Optional


class EmbeddingProvider(ABC):
    """Embedding 提供商抽象基类"""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        将单个文本转为向量

        Args:
            text: 输入文本

        Returns:
            向量列表
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转为向量

        Args:
            texts: 输入文本列表

        Returns:
            向量列表
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        获取向量维度

        Returns:
            向量维度
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查 provider 是否可用

        Returns:
            是否可用
        """
        pass


class DummyEmbeddingProvider(EmbeddingProvider):
    """虚拟 Embedding 提供商 - 用于测试或降级场景"""

    def __init__(self, dimension: int = 768):
        self._dimension = dimension

    def embed(self, text: str) -> List[float]:
        """返回随机向量"""
        import random

        random.seed(hash(text) % (2**32))
        return [random.random() for _ in range(self._dimension)]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量返回随机向量"""
        return [self.embed(text) for text in texts]

    def get_dimension(self) -> int:
        return self._dimension

    def is_available(self) -> bool:
        return True
