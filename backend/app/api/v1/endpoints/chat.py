from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.conversation import Conversation, Message, MessageRole, RoleSwitch
from app.models.user import User as UserModel
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Conversation as ConversationSchema,
    ConversationCreate,
    Message as MessageSchema,
    MessageCreate,
    RoleHistoryResponse,
    RoleSwitchRecord,
    RoleSwitchRequest,
    RoleSwitchResponse,
)
from app.services.ai_role_detection import (
    get_capability_response,
    get_role_display_name,
    suggest_role_switch,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户的对话列表"""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return conversations


@router.post(
    "/conversations",
    response_model=ConversationSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建新对话"""
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title or "新对话",
        context_summary=conversation_data.context_summary,
        current_role="general",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    logger.info(
        "Conversation created", conversation_id=conversation.id, user_id=current_user.id
    )
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定对话"""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    return conversation


@router.delete(
    "/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_conversation(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除对话"""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    db.delete(conversation)
    db.commit()

    logger.info(
        "Conversation deleted", conversation_id=conversation_id, user_id=current_user.id
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageSchema],
)
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取对话消息"""
    # 验证对话属于当前用户
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return messages


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建新消息"""
    # 验证对话属于当前用户
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    message = Message(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        ai_model=message_data.ai_model,
        tokens_used=message_data.tokens_used,
        response_time=message_data.response_time,
        message_metadata=message_data.message_metadata,
    )

    db.add(message)

    # 更新对话的更新时间
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    logger.info(
        "Message created",
        message_id=message.id,
        conversation_id=conversation_id,
        role=message.role.value,
    )

    return message


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """处理聊天请求 - 支持动态角色切换"""
    logger.info(
        "Chat request",
        user_id=current_user.id,
        conversation_id=chat_request.conversation_id,
    )

    # 如果有对话ID，验证对话属于当前用户
    if chat_request.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == chat_request.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
    else:
        # 创建新对话
        conversation = Conversation(
            user_id=current_user.id,
            title="新对话",
            current_role="general",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=chat_request.message,
    )
    db.add(user_message)
    db.commit()

    # 获取对话历史用于上下文分析
    recent_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id,
            Message.role == MessageRole.USER,
        )
        .order_by(Message.created_at.desc())
        .limit(5)
        .all()
    )
    conversation_context = [msg.content for msg in reversed(recent_messages)]

    # 确定当前角色和是否需要切换
    current_role = conversation.current_role or "general"
    previous_role = current_role
    role_switched = False
    is_fusion = False
    notification = None

    # 构建上下文
    context = {
        "conversation_id": conversation.id,
        "current_role": current_role,
        "manual_mode_override": conversation.manual_mode_override or False,
        "manual_mode_message_count": conversation.manual_mode_message_count or 0,
        "role_fusion_enabled": conversation.role_fusion_enabled or False,
    }

    # 检查是否手动指定了角色
    if chat_request.role:
        # 手动指定角色
        target_role = chat_request.role
        if target_role != current_role:
            # 记录角色切换
            role_switch = RoleSwitch(
                conversation_id=conversation.id,
                from_role=current_role,
                to_role=target_role,
                trigger_type="manual",
                switch_reason="user_manual_selection",
            )
            db.add(role_switch)

            previous_role = current_role
            current_role = target_role
            role_switched = True
            conversation.manual_mode_override = True
            conversation.manual_mode_message_count = 0
            notification = f"已切换到{get_role_display_name(target_role)}模式"

        # 增加手动模式计数
        if conversation.manual_mode_override:
            conversation.manual_mode_message_count = (
                conversation.manual_mode_message_count or 0
            ) + 1
            # 超过3条消息后允许自动切换
            if conversation.manual_mode_message_count >= 3:
                conversation.manual_mode_override = False

    else:
        # 自动角色检测
        new_role, should_switch, reason, fusion = suggest_role_switch(
            current_role=current_role,
            new_message=chat_request.message,
            context=context,
            conversation_context=conversation_context,
        )

        # 处理功能查询
        if new_role == "capability_inquiry":
            from app.services.ai_service import get_ai_response

            capability_response = get_capability_response()

            # 保存AI回复
            ai_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=capability_response,
                ai_model="role_detection",
                tokens_used=len(capability_response.split()),
                response_time=0.1,
            )
            db.add(ai_message)

            conversation.updated_at = datetime.utcnow()
            if not conversation.title or conversation.title == "新对话":
                conversation.title = chat_request.message[:50] + (
                    "..." if len(chat_request.message) > 50 else ""
                )

            db.commit()
            db.refresh(conversation)

            return ChatResponse(
                conversation_id=conversation.id,
                message=capability_response,
                conversation_title=conversation.title,
                current_role=current_role,
                role_switched=False,
                previous_role=previous_role,
                is_fusion=False,
                notification=None,
            )

        # 处理角色切换
        if should_switch and new_role != current_role:
            role_switch = RoleSwitch(
                conversation_id=conversation.id,
                from_role=current_role,
                to_role=new_role,
                trigger_type="fusion" if fusion else "automatic",
                switch_reason=reason,
            )
            db.add(role_switch)

            previous_role = current_role
            current_role = new_role
            role_switched = True

            # 设置通知消息
            if fusion:
                notification = f"让我从多个角度帮你分析..."
                conversation.role_fusion_enabled = True
                is_fusion = True
            else:
                notification = f"已切换到{get_role_display_name(new_role)}模式"
                # 关闭融合模式
                conversation.role_fusion_enabled = False

            # 重置手动模式
            conversation.manual_mode_override = False
            conversation.manual_mode_message_count = 0

    # 更新对话角色
    conversation.current_role = current_role

    # 调用AI服务生成回复
    from app.services.ai_service import get_ai_response

    # 更新上下文
    context["current_role"] = current_role
    context["role_fusion_enabled"] = is_fusion

    ai_response_data = await get_ai_response(
        message=chat_request.message,
        user_id=int(current_user.id),
        context=context,
        db=db,
    )
    ai_response = ai_response_data.response

    # 保存AI回复
    ai_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=ai_response,
        ai_model=ai_response_data.model,
        tokens_used=ai_response_data.tokens_used,
        response_time=ai_response_data.response_time,
    )
    db.add(ai_message)

    # 更新对话
    conversation.updated_at = datetime.utcnow()
    if not conversation.title or conversation.title == "新对话":
        # 根据第一条消息生成标题
        conversation.title = chat_request.message[:50] + (
            "..." if len(chat_request.message) > 50 else ""
        )

    db.commit()
    db.refresh(conversation)

    logger.info(
        "Chat response generated",
        conversation_id=conversation.id,
        response_length=len(ai_response),
        current_role=current_role,
        role_switched=role_switched,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message=ai_response,
        conversation_title=conversation.title,
        current_role=current_role,
        role_switched=role_switched,
        previous_role=previous_role if role_switched else None,
        is_fusion=is_fusion,
        fusion_roles=["nutritionist", "behavior_coach"] if is_fusion else None,
        notification=notification,
    )


@router.post(
    "/conversations/{conversation_id}/switch-role",
    response_model=RoleSwitchResponse,
)
async def switch_role(
    conversation_id: int,
    role_request: RoleSwitchRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """手动切换角色"""
    # 验证对话属于当前用户
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    # 验证角色有效
    valid_roles = ["nutritionist", "behavior_coach", "emotional_companion", "general"]
    if role_request.target_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # 记录切换
    previous_role = conversation.current_role or "general"
    if previous_role != role_request.target_role:
        role_switch = RoleSwitch(
            conversation_id=conversation.id,
            from_role=previous_role,
            to_role=role_request.target_role,
            trigger_type="manual",
            switch_reason="user_manual_selection",
        )
        db.add(role_switch)

    # 更新对话
    conversation.current_role = role_request.target_role
    conversation.manual_mode_override = True
    conversation.manual_mode_message_count = 0
    conversation.role_fusion_enabled = False

    db.commit()

    logger.info(
        "Role switched manually",
        conversation_id=conversation_id,
        previous_role=previous_role,
        new_role=role_request.target_role,
    )

    return RoleSwitchResponse(
        success=True,
        current_role=role_request.target_role,
        message=f"已切换到{get_role_display_name(role_request.target_role)}模式",
    )


@router.get(
    "/conversations/{conversation_id}/role-history",
    response_model=RoleHistoryResponse,
)
async def get_role_history(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取角色切换历史"""
    # 验证对话属于当前用户
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    # 获取角色切换记录
    switches = (
        db.query(RoleSwitch)
        .filter(RoleSwitch.conversation_id == conversation_id)
        .order_by(RoleSwitch.created_at.desc())
        .limit(50)
        .all()
    )

    return RoleHistoryResponse(
        conversation_id=conversation_id,
        current_role=conversation.current_role or "general",
        role_fusion_enabled=conversation.role_fusion_enabled or False,
        switches=[
            RoleSwitchRecord(
                id=s.id,
                conversation_id=s.conversation_id,
                from_role=s.from_role,
                to_role=s.to_role,
                trigger_type=s.trigger_type,
                switch_reason=s.switch_reason,
                created_at=s.created_at,
            )
            for s in switches
        ],
    )
