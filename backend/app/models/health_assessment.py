"""
健康评估数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HealthAssessment(Base):
    """健康评估记录表"""

    __tablename__ = "health_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assessment_date = Column(DateTime, default=func.now(), nullable=False, index=True)

    # 综合评分
    overall_score = Column(Integer, nullable=False)
    overall_grade = Column(String(20), nullable=False)  # 需改善/一般/良好/优秀

    # 营养维度
    nutrition_score = Column(Integer, nullable=False)
    nutrition_details = Column(JSON, default=dict)
    nutrition_suggestions = Column(JSON, default=list)

    # 行为维度
    behavior_score = Column(Integer, nullable=False)
    behavior_details = Column(JSON, default=dict)
    behavior_suggestions = Column(JSON, default=list)

    # 情感维度
    emotion_score = Column(Integer, nullable=False)
    emotion_details = Column(JSON, default=dict)
    emotion_suggestions = Column(JSON, default=list)

    # 评估建议
    overall_suggestions = Column(JSON, default=list)

    # 数据完整性状态
    data_completeness = Column(JSON, default=dict)

    # 评估周期
    assessment_period_start = Column(DateTime, nullable=True)
    assessment_period_end = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关联关系
    user = relationship("User", back_populates="health_assessments")

    def __repr__(self):
        return f"<HealthAssessment(id={self.id}, user_id={self.user_id}, overall_score={self.overall_score})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_date": self.assessment_date.isoformat()
            if self.assessment_date
            else None,
            "overall_score": self.overall_score,
            "overall_grade": self.overall_grade,
            "nutrition_score": self.nutrition_score,
            "nutrition_details": self.nutrition_details or {},
            "nutrition_suggestions": self.nutrition_suggestions or [],
            "behavior_score": self.behavior_score,
            "behavior_details": self.behavior_details or {},
            "behavior_suggestions": self.behavior_suggestions or [],
            "emotion_score": self.emotion_score,
            "emotion_details": self.emotion_details or {},
            "emotion_suggestions": self.emotion_suggestions or [],
            "overall_suggestions": self.overall_suggestions or [],
            "data_completeness": self.data_completeness or {},
            "assessment_period_start": self.assessment_period_start.isoformat()
            if self.assessment_period_start
            else None,
            "assessment_period_end": self.assessment_period_end.isoformat()
            if self.assessment_period_end
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
