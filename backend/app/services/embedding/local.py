"""本地 Embedding 提供商 - 使用 sentence-transformers"""

import logging
import os
from typing import List

from .base import EmbeddingProvider

logger = logging.getLogger(__name__)


class LocalEmbeddingProvider(EmbeddingProvider):
    """本地 Embedding 提供商 - 使用本地模型"""

    def __init__(self, config: dict):
        """
        初始化本地 Embedding 提供商

        Args:
            config: 配置字典
                - model_path: 模型路径
                - device: 设备 (cpu/cuda)
                - batch_size: 批处理大小
        """
        self.model_path = config.get("model_path", "./models/bge-small-zh-v1.5")
        self.device = config.get("device", "cpu")
        self.batch_size = config.get("batch_size", 32)
        self._model = None
        self._dimension = 768  # bge-small-zh-v1.5 默认维度

    def _load_model(self):
        """加载模型"""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            # 检查模型路径是否存在
            if os.path.exists(self.model_path):
                logger.info(f"Loading local embedding model from {self.model_path}")
                self._model = SentenceTransformer(self.model_path, device=self.device)
            else:
                # 如果模型不存在，尝试从 HuggingFace 下载
                model_name = self.model_path.split("/")[-1]
                logger.info(
                    f"Model not found locally, downloading {model_name} from HuggingFace"
                )
                self._model = SentenceTransformer(
                    "BAAI/bge-small-zh-v1.5", device=self.device
                )

            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Local embedding model loaded, dimension: {self._dimension}")

        except ImportError:
            logger.warning("sentence-transformers not installed, using dummy provider")
            self._model = None
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {e}")
            self._model = None

    def embed(self, text: str) -> List[float]:
        """将单个文本转为向量"""
        if self._model is None:
            self._load_model()

        if self._model is None:
            # 返回零向量作为降级
            return [0.0] * self._dimension

        try:
            embedding = self._model.encode(text, device=self.device)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return [0.0] * self._dimension

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转为向量"""
        if self._model is None:
            self._load_model()

        if self._model is None:
            # 返回零向量作为降级
            return [[0.0] * self._dimension for _ in texts]

        try:
            embeddings = self._model.encode(
                texts,
                device=self.device,
                batch_size=self.batch_size,
                show_progress_bar=len(texts) > 10,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to embed batch: {e}")
            return [[0.0] * self._dimension for _ in texts]

    def get_dimension(self) -> int:
        """获取向量维度"""
        if self._model is None:
            self._load_model()
        return self._dimension

    def is_available(self) -> bool:
        """检查 provider 是否可用"""
        if self._model is None:
            self._load_model()
        return self._model is not None
