import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MessageRole(enum.Enum):
    """消息角色枚举"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """对话模型"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 对话标题（自动生成）
    title = Column(String(200))

    # 对话上下文
    context_summary = Column(Text)  # 对话上下文摘要

    # 角色相关字段
    current_role = Column(String(50), default="general")  # 当前活跃角色
    role_fusion_enabled = Column(Boolean, default=False)  # 是否启用角色融合
    manual_mode_override = Column(Boolean, default=False)  # 是否手动覆盖自动切换
    manual_mode_message_count = Column(Integer, default=0)  # 手动模式消息计数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    role_switches = relationship(
        "RoleSwitch", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"
        )


class Message(Base):
    """消息模型"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # 消息内容
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # AI相关字段
    ai_model = Column(String(100))  # 使用的AI模型
    tokens_used = Column(Integer)  # 使用的token数量
    response_time = Column(Float)  # 响应时间（秒）

    # 元数据
    message_metadata = Column(Text)  # JSON字符串存储额外信息

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"


class RoleSwitch(Base):
    """角色切换记录模型"""

    __tablename__ = "role_switches"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # 角色切换信息
    from_role = Column(String(50), nullable=False)  # 原角色
    to_role = Column(String(50), nullable=False)  # 新角色
    trigger_type = Column(
        String(50), nullable=False
    )  # 触发类型: 'automatic', 'manual', 'fusion'
    switch_reason = Column(Text)  # 切换原因

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    conversation = relationship("Conversation", back_populates="role_switches")

    def __repr__(self):
        return f"<RoleSwitch(id={self.id}, conversation_id={self.conversation_id}, from={self.from_role}, to={self.to_role})>"
