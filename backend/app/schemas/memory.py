"""记忆系统Pydantic模型"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# 基础模型
class MemoryBase(BaseModel):
    """记忆基础模型"""

    memory_type: str = Field(..., description="记忆类型")
    memory_key: str = Field(..., description="记忆键")
    memory_value: Dict[str, Any] = Field(..., description="记忆值（JSON格式）")
    importance_score: float = Field(1.0, ge=0.0, le=10.0, description="重要性评分 0-10")


class ContextSummaryBase(BaseModel):
    """上下文摘要基础模型"""

    summary_type: str = Field(..., description="摘要类型")
    period_start: date = Field(..., description="摘要开始时间")
    period_end: date = Field(..., description="摘要结束时间")
    summary_text: str = Field(..., description="摘要文本")
    key_insights: Optional[List[Dict[str, Any]]] = Field(None, description="关键洞察")
    data_sources: Optional[List[Dict[str, Any]]] = Field(None, description="数据来源")


class HabitPatternBase(BaseModel):
    """习惯模式基础模型"""

    habit_id: int = Field(..., description="习惯ID")
    pattern_type: str = Field(..., description="模式类型")
    pattern_data: Dict[str, Any] = Field(..., description="模式数据")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="置信度 0-1")
    first_detected: date = Field(..., description="首次检测时间")
    last_observed: date = Field(..., description="最后观察时间")
    observation_count: int = Field(1, ge=1, description="观察次数")


class DataAssociationBase(BaseModel):
    """数据关联基础模型"""

    source_type: str = Field(..., description="源数据类型")
    source_id: int = Field(..., description="源数据ID")
    target_type: str = Field(..., description="目标数据类型")
    target_id: int = Field(..., description="目标数据ID")
    association_type: str = Field(..., description="关联类型")
    strength: float = Field(0.0, ge=0.0, le=1.0, description="关联强度 0-1")


# 创建模型
class MemoryCreate(MemoryBase):
    """创建记忆模型"""

    pass


class ContextSummaryCreate(ContextSummaryBase):
    """创建上下文摘要模型"""

    pass


class HabitPatternCreate(HabitPatternBase):
    """创建习惯模式模型"""

    pass


class DataAssociationCreate(DataAssociationBase):
    """创建数据关联模型"""

    pass


# 更新模型
class MemoryUpdate(BaseModel):
    """更新记忆模型"""

    memory_value: Optional[Dict[str, Any]] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    last_accessed: Optional[datetime] = None


class ContextSummaryUpdate(BaseModel):
    """更新上下文摘要模型"""

    summary_text: Optional[str] = None
    key_insights: Optional[List[Dict[str, Any]]] = None
    data_sources: Optional[List[Dict[str, Any]]] = None


class HabitPatternUpdate(BaseModel):
    """更新习惯模式模型"""

    pattern_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    last_observed: Optional[date] = None
    observation_count: Optional[int] = Field(None, ge=1)


class DataAssociationUpdate(BaseModel):
    """更新数据关联模型"""

    association_type: Optional[str] = None
    strength: Optional[float] = Field(None, ge=0.0, le=1.0)


# 响应模型
class MemoryResponse(MemoryBase):
    """记忆响应模型"""

    id: int
    user_id: int
    last_accessed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContextSummaryResponse(ContextSummaryBase):
    """上下文摘要响应模型"""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HabitPatternResponse(HabitPatternBase):
    """习惯模式响应模型"""

    id: int
    user_id: int

    class Config:
        from_attributes = True


class DataAssociationResponse(DataAssociationBase):
    """数据关联响应模型"""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 查询参数
class MemoryFilter(BaseModel):
    """记忆过滤参数"""

    memory_type: Optional[str] = None
    min_importance: Optional[float] = Field(None, ge=0.0, le=10.0)
    max_importance: Optional[float] = Field(None, ge=0.0, le=10.0)
    updated_since: Optional[datetime] = None


class ContextSummaryFilter(BaseModel):
    """上下文摘要过滤参数"""

    summary_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class HabitPatternFilter(BaseModel):
    """习惯模式过滤参数"""

    habit_id: Optional[int] = None
    pattern_type: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class DataAssociationFilter(BaseModel):
    """数据关联过滤参数"""

    source_type: Optional[str] = None
    source_id: Optional[int] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    association_type: Optional[str] = None
    min_strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_strength: Optional[float] = Field(None, ge=0.0, le=1.0)


# 批量操作模型
class BatchMemoryUpdate(BaseModel):
    """批量更新记忆模型"""

    memory_keys: List[str] = Field(..., description="要更新的记忆键列表")
    importance_delta: float = Field(0.0, description="重要性变化量")


class MemoryImportanceUpdate(BaseModel):
    """记忆重要性更新模型"""

    memory_key: str = Field(..., description="记忆键")
    importance_delta: float = Field(..., description="重要性变化量")


# 上下文构建模型
class UserContext(BaseModel):
    """用户上下文模型"""

    user_id: int
    current_date: date = Field(default_factory=date.today)
    include_memories: bool = True
    include_summaries: bool = True
    include_patterns: bool = True
    include_associations: bool = True
    max_memories: int = 20
    max_summaries: int = 5
    max_patterns: int = 10
    max_associations: int = 15


class BuiltContext(BaseModel):
    """构建的上下文模型"""

    user_id: int
    context_text: str = Field(..., description="构建的上下文文本")
    memories_used: List[str] = Field(default_factory=list, description="使用的记忆键")
    summaries_used: List[int] = Field(default_factory=list, description="使用的摘要ID")
    patterns_used: List[int] = Field(default_factory=list, description="使用的模式ID")
    associations_used: List[int] = Field(default_factory=list, description="使用的关联ID")
    built_at: datetime = Field(default_factory=datetime.utcnow)


# 数据处理模型
class DailyDataProcess(BaseModel):
    """每日数据处理模型"""

    user_id: int
    process_date: date = Field(default_factory=date.today)
    force_reprocess: bool = False


class DataProcessResult(BaseModel):
    """数据处理结果模型"""

    user_id: int
    process_date: date
    memories_created: int = 0
    memories_updated: int = 0
    summaries_created: int = 0
    patterns_detected: int = 0
    associations_found: int = 0
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
