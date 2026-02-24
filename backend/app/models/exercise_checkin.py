from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExerciseCheckIn(Base):
    """运动打卡模型"""

    __tablename__ = "exercise_checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 核心字段 (快速模式)
    exercise_type = Column(String(100), nullable=False)  # 运动类型
    category = Column(String(50))  # 分类：有氧/力量/灵活/其他
    duration_minutes = Column(Integer, nullable=False)  # 时长 (分钟)
    intensity = Column(String(20), nullable=False)  # low/medium/high

    # 可选字段 (详细模式)
    distance_km = Column(Float, nullable=True)  # 距离 (有氧类)
    heart_rate_avg = Column(Integer, nullable=True)  # 平均心率
    notes = Column(Text, nullable=True)  # 备注
    rating = Column(Integer, nullable=True)  # 感受评分 1-5 (灵活类)

    # 计算字段
    calories_burned = Column(Integer, nullable=False)  # 估算卡路里
    is_estimated = Column(Boolean, default=True)  # 是否估算值

    # 时间戳
    started_at = Column(DateTime, nullable=False)  # 运动开始时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())  # 更新时间
    deleted_at = Column(DateTime, nullable=True)  # 软删除标记

    # 关系
    user = relationship("User", back_populates="exercise_checkins")

    def __repr__(self):
        return f"<ExerciseCheckIn(id={self.id}, user_id={self.user_id}, type={self.exercise_type}, duration={self.duration_minutes})>"
