"""功能开关模型扩展"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeatureFlagHistory(Base):
    """功能开关变更历史"""

    __tablename__ = "feature_flag_history"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_key = Column(String(100), nullable=False, index=True)
    
    # 变更内容
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=False)
    
    # 审计
    changed_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    changed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "feature_key": self.feature_key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "reason": self.reason,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }
