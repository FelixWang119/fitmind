"""
增强的记忆查询服务 - Story 5.2: 记忆检索增强
提供语义搜索、混合搜索、类型过滤、时间范围过滤等功能
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.memory import UnifiedMemory

logger = logging.getLogger(__name__)


class EnhancedMemoryQueryService:
    """增强的记忆查询服务"""

    def __init__(self, db: Session):
        self.db = db

    def semantic_search(
        self,
        user_id: int,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        语义向量搜索

        Args:
            user_id: 用户ID
            query: 搜索查询
            limit: 返回数量限制
            memory_types: 可选的记忆类型过滤

        Returns:
            记忆列表，按相似度排序
        """
        logger.info(
            "Semantic search",
            user_id=user_id,
            query=query[:50],
            limit=limit,
        )

        try:
            # 1. 生成查询向量
            from app.services.embedding.factory import EmbeddingProviderFactory

            embedding_provider = EmbeddingProviderFactory.get_provider()
            query_embedding = embedding_provider.embed(query)

            if not query_embedding:
                logger.warning("Failed to generate embedding for query")
                return self._fallback_keyword_search(
                    user_id, query, limit, memory_types
                )

            # 2. 构建查询
            base_query = self.db.query(UnifiedMemory).filter(
                UnifiedMemory.user_id == user_id,
                UnifiedMemory.is_active == True,
                UnifiedMemory.embedding.isnot(None),
            )

            if memory_types:
                base_query = base_query.filter(
                    UnifiedMemory.memory_type.in_(memory_types)
                )

            # 3. 执行向量相似度搜索 (使用余弦相似度)
            # 注意: pgvector 的 cosine_distance 越小越相似
            memories = (
                base_query.order_by(
                    UnifiedMemory.embedding.cosine_distance(query_embedding).asc()
                )
                .limit(limit)
                .all()
            )

            # 4. 格式化结果
            results = []
            for mem in memories:
                results.append(self._format_memory(mem))

            logger.info(
                "Semantic search completed",
                user_id=user_id,
                results_count=len(results),
            )

            return results

        except Exception as e:
            logger.error(
                "Semantic search failed, falling back to keyword search",
                user_id=user_id,
                error=str(e),
            )
            return self._fallback_keyword_search(user_id, query, limit, memory_types)

    def _fallback_keyword_search(
        self,
        user_id: int,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """关键词搜索回退方案"""
        logger.info("Using fallback keyword search", user_id=user_id, query=query[:50])

        keywords = query.lower().split()

        base_query = self.db.query(UnifiedMemory).filter(
            UnifiedMemory.user_id == user_id,
            UnifiedMemory.is_active == True,
        )

        if memory_types:
            base_query = base_query.filter(UnifiedMemory.memory_type.in_(memory_types))

        # 关键词过滤
        conditions = []
        for keyword in keywords:
            keyword = keyword.strip()
            if keyword:
                conditions.append(
                    or_(
                        UnifiedMemory.content_summary.ilike(f"%{keyword}%"),
                        UnifiedMemory.content_keywords.ilike(f'%"{keyword}"%'),
                    )
                )

        if conditions:
            base_query = base_query.filter(or_(*conditions))

        memories = (
            base_query.order_by(
                UnifiedMemory.importance_score.desc(),
                UnifiedMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

        return [self._format_memory(mem) for mem in memories]

    def hybrid_search(
        self,
        user_id: int,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        keyword_weight: float = 0.3,
        vector_weight: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        混合搜索 (关键词 + 向量)

        Args:
            user_id: 用户ID
            query: 搜索查询
            filters: 过滤条件
            limit: 返回数量限制
            keyword_weight: 关键词权重
            vector_weight: 向量权重

        Returns:
            记忆列表，按综合得分排序
        """
        logger.info(
            "Hybrid search",
            user_id=user_id,
            query=query[:50],
            limit=limit,
            filters=filters,
        )

        # 1. 关键词搜索
        keyword_results = self._fallback_keyword_search(
            user_id, query, limit * 2, filters.get("memory_types") if filters else None
        )
        keyword_ids = {mem["id"]: mem for mem in keyword_results}

        # 2. 向量搜索
        try:
            vector_results = self.semantic_search(
                user_id,
                query,
                limit * 2,
                filters.get("memory_types") if filters else None,
            )
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            vector_results = []
        vector_ids = {mem["id"]: mem for mem in vector_results}

        # 3. 合并结果并计算综合得分
        all_ids = set(keyword_ids.keys()) | set(vector_ids.keys())
        scored_results = []

        for mem_id in all_ids:
            mem = keyword_ids.get(mem_id) or vector_results[0]
            keyword_score = 0
            vector_score = 0

            if mem_id in keyword_ids:
                # 关键词匹配得分 (基于排名)
                keyword_rank = list(keyword_ids.keys()).index(mem_id)
                keyword_score = 1 - (keyword_rank / len(keyword_ids))

            if mem_id in vector_ids:
                # 向量相似度得分
                vector_score = 1  # 简化处理

            # 综合得分
            combined_score = (
                keyword_score * keyword_weight + vector_score * vector_weight
            )

            mem["combined_score"] = combined_score
            scored_results.append(mem)

        # 4. 排序并应用额外过滤
        scored_results.sort(key=lambda x: x["combined_score"], reverse=True)

        # 应用时间范围过滤
        if filters and filters.get("start_date"):
            scored_results = self._filter_by_time_range(
                scored_results,
                filters.get("start_date"),
                filters.get("end_date"),
            )

        return scored_results[:limit]

    def get_memories_by_type(
        self,
        user_id: int,
        memory_type: str,
        limit: int = 20,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        按记忆类型获取记忆

        Args:
            user_id: 用户ID
            memory_type: 记忆类型
            limit: 返回数量限制
            include_inactive: 是否包含非活跃记忆

        Returns:
            记忆列表
        """
        logger.info(
            "Get memories by type",
            user_id=user_id,
            memory_type=memory_type,
            limit=limit,
        )

        query = self.db.query(UnifiedMemory).filter(
            UnifiedMemory.user_id == user_id,
            UnifiedMemory.memory_type == memory_type,
        )

        if not include_inactive:
            query = query.filter(UnifiedMemory.is_active == True)

        memories = (
            query.order_by(
                UnifiedMemory.importance_score.desc(),
                UnifiedMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

        return [self._format_memory(mem) for mem in memories]

    def get_memories_by_timerange(
        self,
        user_id: int,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        memory_types: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        按时间范围获取记忆

        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期 (默认为现在)
            memory_types: 可选的记忆类型过滤
            limit: 返回数量限制

        Returns:
            记忆列表
        """
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            "Get memories by time range",
            user_id=user_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            limit=limit,
        )

        query = self.db.query(UnifiedMemory).filter(
            UnifiedMemory.user_id == user_id,
            UnifiedMemory.created_at >= start_date,
            UnifiedMemory.created_at <= end_date,
            UnifiedMemory.is_active == True,
        )

        if memory_types:
            query = query.filter(UnifiedMemory.memory_type.in_(memory_types))

        memories = query.order_by(UnifiedMemory.created_at.desc()).limit(limit).all()

        return [self._format_memory(mem) for mem in memories]

    def get_memories_with_importance_ranking(
        self,
        user_id: int,
        limit: int = 20,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取按重要性排序的记忆

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            memory_types: 可选的记忆类型过滤

        Returns:
            记忆列表，按重要性排序
        """
        logger.info(
            "Get memories with importance ranking",
            user_id=user_id,
            limit=limit,
        )

        query = self.db.query(UnifiedMemory).filter(
            UnifiedMemory.user_id == user_id,
            UnifiedMemory.is_active == True,
        )

        if memory_types:
            query = query.filter(UnifiedMemory.memory_type.in_(memory_types))

        # 综合排序: 重要性分数 > 最近访问 > 创建时间
        memories = (
            query.order_by(
                UnifiedMemory.importance_score.desc(),
                UnifiedMemory.last_accessed.desc().nullslast(),
                UnifiedMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

        return [self._format_memory(mem) for mem in memories]

    def _filter_by_time_range(
        self,
        memories: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """按时间范围过滤记忆"""
        filtered = []

        for mem in memories:
            mem_time = mem.get("created_at")
            if not mem_time:
                continue

            if isinstance(mem_time, str):
                try:
                    mem_time = datetime.fromisoformat(mem_time.replace("Z", "+00:00"))
                except:
                    continue

            if start_date and mem_time < start_date:
                continue

            if end_date and mem_time > end_date:
                continue

            filtered.append(mem)

        return filtered

    def _format_memory(self, mem: UnifiedMemory) -> Dict[str, Any]:
        """格式化记忆为字典"""
        return {
            "id": str(mem.id),
            "user_id": mem.user_id,
            "memory_type": mem.memory_type,
            "content_summary": mem.content_summary,
            "content_raw": mem.content_raw,
            "content_keywords": mem.content_keywords,
            "source_type": mem.source_type,
            "source_id": mem.source_id,
            "importance_score": mem.importance_score,
            "created_at": mem.created_at.isoformat() if mem.created_at else None,
            "updated_at": mem.updated_at.isoformat() if mem.updated_at else None,
            "last_accessed": mem.last_accessed.isoformat()
            if mem.last_accessed
            else None,
            "is_active": mem.is_active,
        }

    def is_memory_fresh(self, memory: Dict[str, Any], max_days: int = 30) -> bool:
        """
        判断记忆是否新鲜

        Args:
            memory: 记忆字典
            max_days: 最大天数

        Returns:
            是否新鲜
        """
        created_at = memory.get("created_at")
        if not created_at:
            return False

        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                return False

        age_days = (datetime.utcnow() - created_at).days
        return age_days <= max_days


def get_enhanced_memory_query_service(db: Session) -> EnhancedMemoryQueryService:
    """获取增强的记忆查询服务实例"""
    return EnhancedMemoryQueryService(db)
