"""
科普内容 Schema
Story 9.1: 科普内容生成服务
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DailyTipBase(BaseModel):
    """科普内容基础字段"""

    topic: str = Field(..., description="主题")
    title: str = Field(..., max_length=200, description="标题")
    summary: str = Field(..., max_length=100, description="摘要")
    content: str = Field(..., description="正文")


class DailyTipCreate(DailyTipBase):
    """创建科普内容"""

    disclaimer: Optional[str] = Field(None, description="免责声明")


class DailyTipUpdate(BaseModel):
    """更新科普内容"""

    title: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    is_active: Optional[bool] = None


class DailyTipInDB(DailyTipBase):
    """数据库中的科普内容"""

    id: int
    date: datetime
    disclaimer: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyTipResponse(DailyTipInDB):
    """API 响应的科普内容"""

    pass


class DailyTipListResponse(BaseModel):
    """科普内容列表响应"""

    total: int
    items: List[DailyTipInDB]
