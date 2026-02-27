"""通知模板管理 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.notification import NotificationTemplate
from app.schemas.notification import NotificationTemplateCreate, NotificationTemplateUpdate

router = APIRouter(prefix="/admin/notification-templates", tags=["notification-templates"])


@router.get("")
async def get_all_templates(
    is_active: Optional[bool] = Query(None),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取所有通知模板"""
    query = db.query(NotificationTemplate)
    
    if is_active is not None:
        query = query.filter(NotificationTemplate.is_active == is_active)
    if event_type:
        query = query.filter(NotificationTemplate.event_type == event_type)
    
    templates = query.all()
    return {"items": [t.to_dict() for t in templates], "total": len(templates)}


@router.get("/{template_id}")
async def get_template(template_id: UUID, db: Session = Depends(get_db)):
    """获取单个模板"""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(404, "Template not found")
    return template.to_dict()


@router.put("/{template_id}")
async def update_template(
    template_id: UUID,
    template_data: NotificationTemplateUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """更新模板"""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(404, "Template not found")
    
    for field, value in template_data.dict(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return {"message": "Template updated", "template": template.to_dict()}
