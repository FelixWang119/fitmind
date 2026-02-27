"""AI 提示词版本管理"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIPromptVersion(Base):
    """AI 提示词版本表"""

    __tablename__ = "ai_prompt_versions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_key = Column(String(100), nullable=False, index=True)  # 如 ai.prompt.nutritionist
    version = Column(Integer, nullable=False, default=1)
    
    # 提示词内容
    prompt_text = Column(Text, nullable=False)
    parameters = Column(JSONB, nullable=True)  # temperature, max_tokens 等
    
    # 状态
    is_active = Column(Boolean, default=False, index=True)  # 是否当前使用版本
    is_draft = Column(Boolean, default=True)  # 是否草稿
    
    # 元数据
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AIPromptVersion(key={self.prompt_key}, version={self.version})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "prompt_key": self.prompt_key,
            "version": self.version,
            "prompt_text": self.prompt_text,
            "parameters": self.parameters,
            "is_active": self.is_active,
            "is_draft": self.is_draft,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": str(self.created_by) if self.created_by else None,
        }
