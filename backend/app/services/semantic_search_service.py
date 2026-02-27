"""语义搜索服务 - 基于 pgvector 的向量相似度"""

from typing import List, Optional, Dict, Any
import logging

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.memory import UnifiedMemory
from app.services.embedding.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """语义搜索服务 - 使用 pgvector 进行数据库层面的向量搜索"""

    def __init__(self, embedding_provider: EmbeddingProvider, db_session: Session):
        self.embedding_provider = embedding_provider
        self.db = db_session

    async def search(
        self,
        user_id: int,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        语义搜索用户记忆 - 使用 pgvector 数据库层面搜索

        Args:
            user_id: 用户 ID
            query: 查询文本
            memory_types: 记忆类型过滤（可选）
            limit: 返回数量限制
            min_similarity: 最小相似度阈值 (0-1)

        Returns:
            记忆列表（按相似度排序）
        """
        try:
            # 1. 将查询文本向量化
            query_embedding = self.embedding_provider.embed(query)

            # 2. 构建 SQL 查询 - 使用 pgvector 的向量相似度操作符
            filters = [
                "user_id = :user_id",
                "is_active = true",
                "embedding IS NOT NULL",
            ]
            params = {
                "user_id": user_id,
                "query_embedding": query_embedding,
                "limit": limit,
            }

            if memory_types:
                filters.append("memory_type = ANY(:memory_types)")
                params["memory_types"] = memory_types

            where_clause = " AND ".join(filters)

            # 使用 pgvector 的 <=> 操作符计算余弦距离 (1 - 余弦相似度)
            # 1 - (embedding <=> query) = 余弦相似度
            sql = text(f"""
                SELECT 
                    id,
                    memory_type,
                    content_summary,
                    content_raw,
                    source_type,
                    source_id,
                    importance_score,
                    created_at,
                    1 - (embedding <=> :query_embedding) AS similarity
                FROM unified_memory
                WHERE {where_clause}
                ORDER BY embedding <=> :query_embedding
                LIMIT :limit
            """)

            results = self.db.execute(sql, params).fetchall()

            # 3. 转换为字典格式
            search_results = []
            for row in results:
                similarity = float(row.similarity) if row.similarity else 0.0

                # 过滤低于阈值的結果
                if similarity < min_similarity:
                    continue

                search_results.append(
                    {
                        "id": str(row.id),
                        "memory_type": row.memory_type,
                        "content_summary": row.content_summary,
                        "content_raw": row.content_raw,
                        "source_type": row.source_type,
                        "source_id": row.source_id,
                        "importance_score": float(row.importance_score)
                        if row.importance_score
                        else 0.0,
                        "similarity": similarity,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            logger.info(
                f"Semantic search completed",
                query=query[:50],
                results_count=len(search_results),
                user_id=user_id,
            )

            return search_results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}", exc_info=True)
            return []

    async def search_similar(
        self,
        memory_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        查找与指定记忆相似的其他记忆

        Args:
            memory_id: 记忆 ID
            limit: 返回数量限制

        Returns:
            相似记忆列表
        """
        try:
            from uuid import UUID

            memory_uuid = UUID(memory_id)

            # 获取指定记忆的 embedding
            sql = text("""
                SELECT embedding, user_id, memory_type
                FROM unified_memory
                WHERE id = :memory_id AND is_active = true
            """)

            result = self.db.execute(sql, {"memory_id": memory_uuid}).fetchone()

            if not result or not result.embedding:
                return []

            query_embedding = result.embedding
            user_id = result.user_id

            # 搜索相似记忆（排除自身）
            sql = text("""
                SELECT 
                    id,
                    memory_type,
                    content_summary,
                    source_type,
                    source_id,
                    importance_score,
                    created_at,
                    1 - (embedding <=> :query_embedding) AS similarity
                FROM unified_memory
                WHERE user_id = :user_id
                  AND is_active = true
                  AND embedding IS NOT NULL
                  AND id != :memory_id
                ORDER BY embedding <=> :query_embedding
                LIMIT :limit
            """)

            results = self.db.execute(
                sql,
                {
                    "user_id": user_id,
                    "query_embedding": query_embedding,
                    "memory_id": memory_uuid,
                    "limit": limit,
                },
            ).fetchall()

            # 转换为字典格式
            similar_memories = []
            for row in results:
                similar_memories.append(
                    {
                        "id": str(row.id),
                        "memory_type": row.memory_type,
                        "content_summary": row.content_summary,
                        "source_type": row.source_type,
                        "source_id": row.source_id,
                        "importance_score": float(row.importance_score)
                        if row.importance_score
                        else 0.0,
                        "similarity": float(row.similarity) if row.similarity else 0.0,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            return similar_memories

        except Exception as e:
            logger.error(f"Similar search failed: {e}", exc_info=True)
            return []

    async def get_recent_memories_with_embedding(
        self,
        user_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        获取用户最近的有 embedding 的记忆

        用于 AI 上下文构建，结合语义搜索和时间顺序
        """
        try:
            sql = text("""
                SELECT 
                    id,
                    memory_type,
                    content_summary,
                    content_raw,
                    source_type,
                    source_id,
                    importance_score,
                    created_at
                FROM unified_memory
                WHERE user_id = :user_id
                  AND is_active = true
                  AND embedding IS NOT NULL
                ORDER BY created_at DESC
                LIMIT :limit
            """)

            results = self.db.execute(
                sql, {"user_id": user_id, "limit": limit}
            ).fetchall()

            memories = []
            for row in results:
                memories.append(
                    {
                        "id": str(row.id),
                        "memory_type": row.memory_type,
                        "content_summary": row.content_summary,
                        "content_raw": row.content_raw,
                        "source_type": row.source_type,
                        "source_id": row.source_id,
                        "importance_score": float(row.importance_score)
                        if row.importance_score
                        else 0.0,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            return memories

        except Exception as e:
            logger.error(f"Get recent memories failed: {e}", exc_info=True)
            return []
