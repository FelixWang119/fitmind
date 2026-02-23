from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.conversation import MessageRole


# 角色类型枚举
class RoleType(str, Enum):
    NUTRITIONIST = "nutritionist"
    BEHAVIOR_COACH = "behavior_coach"
    EMOTIONAL_COMPANION = "emotional_companion"
    GENERAL = "general"


# 对话相关模式
class ConversationBase(BaseModel):
    title: Optional[str] = None
    context_summary: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: int
    user_id: int
    current_role: Optional[str] = "general"
    role_fusion_enabled: Optional[bool] = False
    manual_mode_override: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 消息相关模式
class MessageBase(BaseModel):
    role: MessageRole
    content: str
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    message_metadata: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 聊天请求/响应
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None
    role: Optional[str] = None  # 手动指定角色


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    conversation_title: Optional[str] = None
    current_role: Optional[str] = "general"
    role_switched: bool = False
    previous_role: Optional[str] = None
    is_fusion: bool = False
    fusion_roles: Optional[List[str]] = None
    notification: Optional[str] = None  # 角色切换通知


# 角色切换请求
class RoleSwitchRequest(BaseModel):
    target_role: str = Field(
        ..., description="目标角色: nutritionist, behavior_coach, emotional_companion"
    )


# 角色切换响应
class RoleSwitchResponse(BaseModel):
    success: bool
    current_role: str
    message: str


# 角色历史记录
class RoleSwitchRecord(BaseModel):
    id: int
    conversation_id: int
    from_role: str
    to_role: str
    trigger_type: str
    switch_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 角色历史响应
class RoleHistoryResponse(BaseModel):
    conversation_id: int
    current_role: str
    role_fusion_enabled: bool
    switches: List[RoleSwitchRecord]


# 对话列表响应
class ConversationList(BaseModel):
    conversations: List[Conversation]
    total: int
    skip: int
    limit: int


# 消息列表响应
class MessageList(BaseModel):
    messages: List[Message]
    total: int
    skip: int
    limit: int
