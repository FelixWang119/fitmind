"""记忆系统API端点"""

import logging
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.services.context_builder import AdvancedContextBuilder
from app.services.memory_associator import MemoryAssociator
from app.services.memory_manager import MemoryManager
from app.services.milestone_detector import MilestoneDetector
from app.services.pattern_recognizer import PatternRecognizer
from app.services.personalization_engine import PersonalizationEngine
from app.services.trend_analyzer import TrendAnalyzer
from app.models.memory import UnifiedMemory

router = APIRouter(prefix="/memory", tags=["记忆系统"])


class UnifiedMemoryRequest(BaseModel):
    """统一记忆请求模型"""

    user_id: int
    memory_type: str
    content_summary: str
    content_keywords: Optional[List[str]] = None
    source_type: str
    source_id: str
    importance_score: Optional[float] = 5.0


class SearchMemoriesRequest(BaseModel):
    """搜索记忆请求模型"""

    user_id: int
    query: str
    memory_types: Optional[List[str]] = None
    limit: Optional[int] = 10


class SearchResult(BaseModel):
    """搜索结果模型"""

    id: str
    memory_type: str
    content_summary: str
    source_type: str
    source_id: str
    similarity: float
    importance_score: float
    created_at: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total: int


# ========== 记忆管理端点 ==========


@router.post("/memories")
async def create_memory(
    user_id: int,
    memory_type: str,
    memory_key: str,
    memory_value: dict,
    importance_score: float = 1.0,
    db: Session = Depends(get_db),
):
    """创建原有内存项（兼容保留）"""
    manager = MemoryManager(db)
    memory = await manager.create_memory(
        user_id=user_id,
        memory_type=memory_type,
        memory_key=memory_key,
        memory_value=memory_value,
        importance_score=importance_score,
    )

    if not memory:
        raise HTTPException(status_code=500, detail="创建记忆失败")

    return {"success": True, "memory_id": memory.id}


@router.post("/unified-memories")
async def create_unified_memory(
    request: UnifiedMemoryRequest,
    db: Session = Depends(get_db),
):
    """创建统一记忆"""
    logger.debug(
        f"开始创建统一记忆 - 用户ID: {request.user_id}, "
        f"记忆类型: {request.memory_type}, 源类型: {request.source_type}"
    )

    # 创建新的统一记忆项
    memory = UnifiedMemory(
        user_id=request.user_id,
        memory_type=request.memory_type,
        content_summary=request.content_summary,
        content_keywords=request.content_keywords or [],
        source_type=request.source_type,
        source_id=request.source_id,
        importance_score=request.importance_score,
    )

    # 生成向量嵌入
    from app.services.embedding.factory import EmbeddingProviderFactory

    try:
        provider = EmbeddingProviderFactory.get_provider()
        embedding = provider.embed(request.content_summary)
        memory.set_embedding(embedding)
        logger.debug(
            f"向量嵌入生成成功 - 记忆ID: {memory.id}, 嵌入维度: {len(embedding)}"
        )
    except Exception as e:
        logger.warning(f"向量嵌入生成失败: {e}")
        # 继续执行，没有嵌入也能创建

    db.add(memory)
    db.commit()
    db.refresh(memory)

    logger.info(
        f"统一记忆创建成功 - 记忆ID: {memory.id}, 用户ID: {request.user_id}, "
        f"记忆类型: {request.memory_type}, 重要性分数: {request.importance_score}"
    )

    return {"success": True, "memory_id": memory.id, "id": memory.id}


@router.get("/memories")
async def get_memories(
    user_id: int,
    memory_type: Optional[str] = None,
    min_importance: float = 0.0,
    db: Session = Depends(get_db),
):
    """获取记忆列表（兼容保留）"""
    logger.debug(
        f"开始获取记忆列表 - 用户ID: {user_id}, "
        f"记忆类型: {memory_type}, 最小重要性: {min_importance}"
    )

    manager = MemoryManager(db)
    memories = await manager.get_memories(user_id, memory_type, min_importance)

    logger.info(
        f"记忆列表获取成功 - 用户ID: {user_id}, "
        f"记忆数量: {len(memories)}, 记忆类型: {memory_type or '全部'}"
    )

    return {
        "success": True,
        "count": len(memories),
        "memories": [
            {
                "id": m.id,
                "memory_type": m.memory_type,
                "memory_key": m.memory_key,
                "importance_score": m.importance_score,
                "updated_at": str(m.updated_at) if m.updated_at is not None else None,
            }
            for m in memories
        ],
    }


@router.get("/unified-memories")
async def get_unified_memories(
    user_id: int,
    memory_type: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取统一记忆列表"""
    query = db.query(UnifiedMemory).filter(UnifiedMemory.user_id == user_id)

    if memory_type:
        query = query.filter(UnifiedMemory.memory_type == memory_type)
    if source_type:
        query = query.filter(UnifiedMemory.source_type == source_type)

    # 按重要性和创建时间排序
    query = query.order_by(UnifiedMemory.importance_score.desc()).order_by(
        UnifiedMemory.created_at.desc()
    )

    memories = query.offset(offset).limit(limit).all()

    return {
        "success": True,
        "count": len(memories),
        "memories": [
            {
                "id": str(m.id),
                "memory_type": m.memory_type,
                "content_summary": m.content_summary,
                "content_keywords": m.get_keywords(),
                "source_type": m.source_type,
                "source_id": m.source_id,
                "importance_score": m.importance_score,
                "created_at": m.created_at.isoformat()
                if m.created_at is not None
                else None,
                "has_embedding": m.get_embedding() is not None,
            }
            for m in memories
        ],
    }


@router.get("/memories/stats")
async def get_memory_stats(user_id: int, db: Session = Depends(get_db)):
    """获取记忆统计"""
    manager = MemoryManager(db)
    stats = await manager.get_memory_stats(user_id)

    return {"success": True, "stats": stats}


# ========== 语义搜索端点 ==========


@router.post("/search")
async def search_memories(
    request: SearchMemoriesRequest,
    db: Session = Depends(get_db),
):
    """语义搜索记忆"""
    logger.debug(
        f"开始语义搜索记忆 - 用户ID: {request.user_id}, "
        f"查询: {request.query[:50]}..., 限制: {request.limit}"
    )

    from app.services.semantic_search_service import SemanticSearchService

    service = SemanticSearchService(
        embedding_provider=EmbeddingProviderFactory.get_provider(), db_session=db
    )

    results = await service.search(
        user_id=request.user_id,
        query=request.query,
        memory_types=request.memory_types,
        limit=request.limit,
    )

    logger.info(
        f"语义搜索完成 - 用户ID: {request.user_id}, "
        f"查询: {request.query[:30]}..., 结果数量: {len(results)}"
    )

    return {
        "results": [
            SearchResult(
                id=str(r.id),
                memory_type=r.memory_type,
                content_summary=r.content_summary,
                source_type=r.source_type,
                source_id=r.source_id,
                similarity=1 - r.similarity,  # 相似度计算中距离越小越相似
                importance_score=float(r.importance_score),
                created_at=str(r.created_at) if r.created_at is not None else None,
            ).dict()
            for r in results
        ],
        "query": request.query,
        "total": len(results),
    }


# ========== 趋势分析端点 ==========


@router.get("/trends/weight")
async def get_weight_trend(
    user_id: int, days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)
):
    """获取体重趋势"""
    analyzer = TrendAnalyzer(db)
    trend = await analyzer.analyze_weight_trend(user_id, days)

    return {"success": True, "trend": trend}


@router.get("/trends/exercise")
async def get_exercise_trend(
    user_id: int, days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)
):
    """获取运动趋势"""
    analyzer = TrendAnalyzer(db)
    trend = await analyzer.analyze_exercise_trend(user_id, days)

    return {"success": True, "trend": trend}


@router.get("/trends/diet")
async def get_diet_trend(
    user_id: int, days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)
):
    """获取饮食趋势"""
    analyzer = TrendAnalyzer(db)
    trend = await analyzer.analyze_diet_trend(user_id, days)

    return {"success": True, "trend": trend}


@router.get("/trends/all")
async def get_all_trends(
    user_id: int, days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)
):
    """获取所有趋势"""
    analyzer = TrendAnalyzer(db)
    trends = await analyzer.analyze_all_trends(user_id, days)

    return {"success": True, "trends": trends}


@router.get("/habits/consistency")
async def get_habit_consistency(
    user_id: int, habit_id: Optional[int] = None, db: Session = Depends(get_db)
):
    """获取习惯一致性分析"""
    analyzer = TrendAnalyzer(db)
    consistency = await analyzer.analyze_habit_consistency(user_id, habit_id)

    return {"success": True, "consistency": consistency}


# ========== 里程碑端点 ==========


@router.get("/milestones")
async def get_milestones(user_id: int, db: Session = Depends(get_db)):
    """获取所有里程碑"""
    detector = MilestoneDetector(db)
    milestones = await detector.detect_all_milestones(user_id)

    return {"success": True, "milestones": milestones}


@router.get("/milestones/weight-goal")
async def get_weight_goal_milestone(user_id: int, db: Session = Depends(get_db)):
    """获取体重目标里程碑"""
    detector = MilestoneDetector(db)
    milestone = await detector.check_weight_goal(user_id)

    return {"success": True, "milestone": milestone}


@router.get("/milestones/streaks")
async def get_streak_milestones(user_id: int, db: Session = Depends(get_db)):
    """获取连续记录里程碑"""
    detector = MilestoneDetector(db)
    milestones = await detector.check_streak_milestones(user_id)

    return {"success": True, "milestones": milestones}


@router.get("/milestones/warnings")
async def get_warning_signs(user_id: int, db: Session = Depends(get_db)):
    """获取预警信号"""
    detector = MilestoneDetector(db)
    warnings = await detector.check_warning_signs(user_id)

    return {"success": True, "warnings": warnings}


# ========== 上下文端点 ==========


@router.get("/context")
async def get_context(user_id: int, db: Session = Depends(get_db)):
    """获取完整上下文"""
    builder = AdvancedContextBuilder(db)
    result = await builder.build_full_context(user_id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.get("/context/quick")
async def get_quick_context(user_id: int, db: Session = Depends(get_db)):
    """获取快速上下文"""
    builder = AdvancedContextBuilder(db)
    context = await builder.build_quick_context(user_id)

    return {"success": True, "context": context}


@router.get("/ai-prompt")
async def get_ai_prompt(
    user_id: int, user_message: str = "", db: Session = Depends(get_db)
):
    """获取AI提示"""
    builder = AdvancedContextBuilder(db)
    result = await builder.generate_ai_prompt(user_id, user_message)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


# ========== 关联端点 ==========


@router.get("/associations")
async def get_associations(
    user_id: int,
    min_strength: float = Query(0.3, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """获取数据关联"""
    associator = MemoryAssociator(db)
    associations = await associator.get_all_associations(user_id, min_strength)

    return {"success": True, "associations": associations}


@router.post("/associations/detect")
async def detect_associations(user_id: int, db: Session = Depends(get_db)):
    """检测所有关联"""
    associator = MemoryAssociator(db)
    result = await associator.detect_all_associations(user_id)

    return result


# ========== 推荐端点 ==========


@router.get("/recommendations")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """获取综合推荐"""
    engine = PersonalizationEngine(db)
    recommendations = await engine.get_comprehensive_recommendations(user_id)

    return recommendations


@router.get("/recommendations/diet")
async def get_diet_recommendations(user_id: int, db: Session = Depends(get_db)):
    """获取饮食推荐"""
    engine = PersonalizationEngine(db)
    recommendations = await engine.recommend_diet(user_id)

    return recommendations


@router.get("/recommendations/exercise")
async def get_exercise_recommendations(user_id: int, db: Session = Depends(get_db)):
    """获取运动推荐"""
    engine = PersonalizationEngine(db)
    recommendations = await engine.recommend_exercise(user_id)

    return recommendations


@router.get("/recommendations/habits")
async def get_habit_recommendations(user_id: int, db: Session = Depends(get_db)):
    """获取习惯推荐"""
    engine = PersonalizationEngine(db)
    recommendations = await engine.recommend_habits(user_id)

    return recommendations


@router.get("/quick-tip")
async def get_quick_tip(
    user_id: int, context: str = "general", db: Session = Depends(get_db)
):
    """获取即时建议"""
    engine = PersonalizationEngine(db)
    tip = await engine.get_quick_tip(user_id, context)

    return {"success": True, "tip": tip}


# ========== 每日数据处理端点 ==========


@router.post("/process-daily")
async def process_daily_data(
    user_id: int,
    process_date: Optional[date] = None,
    force: bool = False,
    db: Session = Depends(get_db),
):
    """处理每日数据"""
    if process_date is None:
        process_date = date.today()

    manager = MemoryManager(db)
    result = await manager.create_daily_summary(user_id, process_date)

    if not result:
        raise HTTPException(status_code=500, detail="处理每日数据失败")

    return {"success": True, "summary_id": result.id}


# ========== 摘要端点 ==========


@router.get("/summaries")
async def get_summaries(
    user_id: int, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)
):
    """获取近期摘要"""
    manager = MemoryManager(db)
    summaries = await manager.get_recent_summaries(user_id, days)

    return {
        "success": True,
        "count": len(summaries),
        "summaries": [
            {
                "id": s.id,
                "period_start": s.period_start.isoformat(),
                "summary_text": s.summary_text[:200],
            }
            for s in summaries
        ],
    }
