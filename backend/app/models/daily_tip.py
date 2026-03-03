"""
科普内容数据模型
Story 9.1: 科普内容生成服务
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class TipTopic(str, Enum):
    """科普主题枚举"""

    NUTRITION = "nutrition"  # 营养
    EXERCISE = "exercise"  # 运动
    SLEEP = "sleep"  # 睡眠
    PSYCHOLOGY = "psychology"  # 心理


class DailyTip(Base):
    """
    每日科普内容模型
    存储每日生成的科普内容，支持主题轮换
    """

    __tablename__ = "daily_tips"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 日期（唯一索引，每天一条）
    date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)

    # 主题
    topic = Column(String(20), nullable=False, index=True)  # TipTopic

    # 内容
    title = Column(String(200), nullable=False)
    summary = Column(String(100), nullable=False)  # 摘要 50 字内
    content = Column(Text, nullable=False)  # 正文 300-500 字

    # 免责声明
    disclaimer = Column(
        Text,
        nullable=False,
        default="本内容仅供参考，不能替代专业医疗建议。如有健康问题，请咨询医生。",
    )

    # 状态
    is_active = Column(Boolean, default=True, index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index("ix_daily_tips_date_topic", "date", "topic"),
        Index("ix_daily_tips_is_active_date", "is_active", "date"),
    )

    def __repr__(self):
        return f"<DailyTip(id={self.id}, date={self.date}, topic={self.topic}, title={self.title})>"
