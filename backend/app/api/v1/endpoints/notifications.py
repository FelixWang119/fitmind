"""通知系统 API 端点"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.notification import NotificationService
from app.schemas.notification import (
    MessageResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
    UserNotificationSettingResponse,
    UserNotificationSettingUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """获取通知服务实例"""
    return NotificationService(db)


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    unread_only: bool = Query(False, description="是否只查询未读"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    获取用户通知列表

    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（1-100）
    - **unread_only**: 是否只查询未读通知
    """
    # 获取通知列表
    notifications = notification_service.get_notifications(
        user_id=current_user_id,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )

    # 获取未读数量
    unread_count = notification_service.get_unread_count(current_user_id)

    # 计算总数
    total = unread_count if unread_only else len(notifications) + (page - 1) * page_size

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user_id: int = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """获取未读通知数量"""
    count = notification_service.get_unread_count(current_user_id)
    return UnreadCountResponse(unread_count=count)


@router.put("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """标记通知为已读"""
    success = notification_service.mark_notification_as_read(
        notification_id=notification_id,
        user_id=current_user_id,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Notification not found or already read",
        )

    return MessageResponse(message="Notification marked as read")


@router.put("/read-all", response_model=MessageResponse)
async def mark_all_as_read(
    current_user_id: int = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """标记所有通知为已读"""
    count = notification_service.mark_all_as_read(current_user_id)
    return MessageResponse(message=f"Successfully marked {count} notifications as read")


@router.get("/settings", response_model=UserNotificationSettingResponse)
async def get_notification_settings(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取用户通知设置"""
    from app.models.notification import UserNotificationSetting

    settings = (
        db.query(UserNotificationSetting)
        .filter(UserNotificationSetting.user_id == current_user_id)
        .first()
    )

    if not settings:
        # 如果没有设置，创建默认设置
        settings = UserNotificationSetting(user_id=current_user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return UserNotificationSettingResponse.model_validate(settings)


@router.put("/settings", response_model=UserNotificationSettingResponse)
async def update_notification_settings(
    settings_update: UserNotificationSettingUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """更新用户通知设置"""
    from app.models.notification import UserNotificationSetting

    settings = (
        db.query(UserNotificationSetting)
        .filter(UserNotificationSetting.user_id == current_user_id)
        .first()
    )

    if not settings:
        # 如果没有设置，创建新设置
        settings = UserNotificationSetting(user_id=current_user_id)
        db.add(settings)

    # 更新字段
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)

    logger.info(f"Updated notification settings for user {current_user_id}")

    return UserNotificationSettingResponse.model_validate(settings)


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """删除通知"""
    from app.models.notification import Notification

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user_id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    db.delete(notification)
    db.commit()

    return MessageResponse(message="Notification deleted successfully")
