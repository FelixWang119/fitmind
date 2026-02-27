"""系统配置管理 API 端点"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.system_config import ConfigType, SystemConfig
from app.services.system_config_service import SystemConfigService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/configs", tags=["system-config"])


def get_config_service(db: Session = Depends(get_db)) -> SystemConfigService:
    """获取配置服务实例"""
    return SystemConfigService(db)


@router.get("")
async def get_all_configs(
    config_type: Optional[str] = Query(None, description="配置类型"),
    config_category: Optional[str] = Query(None, description="配置分类"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    service: SystemConfigService = Depends(get_config_service),
):
    """获取所有配置"""
    configs = service.get_all_configs(
        config_type=config_type,
        config_category=config_category,
        is_active=is_active,
    )
    
    return {
        "items": [config.to_dict() for config in configs],
        "total": len(configs),
    }


@router.get("/{config_key}")
async def get_config(
    config_key: str,
    environment: str = Query("all", description="环境"),
    service: SystemConfigService = Depends(get_config_service),
):
    """获取单个配置"""
    config_value = service.get_config(config_key, environment)
    
    if not config_value:
        raise HTTPException(status_code=404, detail=f"Config not found: {config_key}")
    
    return {
        "config_key": config_key,
        "config_value": config_value,
        "environment": environment,
    }


@router.put("/{config_key}")
async def update_config(
    config_key: str,
    config_value: Dict[str, Any],
    reason: Optional[str] = Query(None, description="变更原因"),
    current_user_id: UUID = Depends(get_current_user_id),
    service: SystemConfigService = Depends(get_config_service),
):
    """更新配置"""
    try:
        config = service.update_config(
            config_key=config_key,
            new_value=config_value,
            changed_by=current_user_id,
            reason=reason,
        )
        
        logger.info(f"Config updated: {config_key} by user {current_user_id}")
        
        return {
            "message": "Config updated successfully",
            "config": config.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
async def create_config(
    config_data: Dict[str, Any],
    current_user_id: UUID = Depends(get_current_user_id),
    service: SystemConfigService = Depends(get_config_service),
):
    """创建配置"""
    required_fields = ["config_key", "config_value", "config_type"]
    for field in required_fields:
        if field not in config_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:
        config = service.create_config(
            config_key=config_data["config_key"],
            config_value=config_data["config_value"],
            config_type=config_data["config_type"],
            config_category=config_data.get("config_category"),
            description=config_data.get("description"),
            environment=config_data.get("environment", "all"),
            created_by=current_user_id,
        )
        
        logger.info(f"Config created: {config.config_key} by user {current_user_id}")
        
        return {
            "message": "Config created successfully",
            "config": config.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{config_key}/history")
async def get_config_history(
    config_key: str,
    limit: int = Query(20, ge=1, le=100, description="历史记录数量"),
    service: SystemConfigService = Depends(get_config_service),
):
    """获取配置变更历史"""
    history = service.get_config_history(config_key, limit)
    
    return {
        "items": [log.to_dict() for log in history],
        "total": len(history),
    }


@router.get("/feature/{feature_key}/enabled")
async def is_feature_enabled(
    feature_key: str,
    environment: str = Query("all", description="环境"),
    service: SystemConfigService = Depends(get_config_service),
):
    """检查功能开关是否启用"""
    enabled = service.is_feature_enabled(feature_key, environment)
    
    return {
        "feature_key": feature_key,
        "enabled": enabled,
        "environment": environment,
    }


@router.get("/ai/{role}/prompt")
async def get_ai_prompt(
    role: str,
    service: SystemConfigService = Depends(get_config_service),
):
    """获取 AI 角色提示词"""
    prompt = service.get_ai_prompt(role)
    
    if not prompt:
        raise HTTPException(status_code=404, detail=f"AI prompt not found for role: {role}")
    
    return {
        "role": role,
        "prompt": prompt,
    }


@router.get("/ai/{role}/config")
async def get_ai_config(
    role: str,
    service: SystemConfigService = Depends(get_config_service),
):
    """获取 AI 完整配置"""
    config = service.get_ai_config(role)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"AI config not found for role: {role}")
    
    return {
        "role": role,
        "config": config,
    }


@router.post("/cache/clear")
async def clear_cache(
    service: SystemConfigService = Depends(get_config_service),
):
    """清除配置缓存"""
    service.clear_cache()
    
    return {"message": "Cache cleared successfully"}


@router.post("/{config_key}/rollback")
async def rollback_config(
    config_key: str,
    version_id: UUID = Query(..., description="回滚到的版本 ID"),
    reason: Optional[str] = Query(None, description="回滚原因"),
    current_user_id: UUID = Depends(get_current_user_id),
    service: SystemConfigService = Depends(get_config_service),
    db: Session = Depends(get_db),
):
    """回滚配置到指定版本"""
    from app.models.system_config import ConfigChangeLog
    
    # 获取历史版本
    history = (
        db.query(ConfigChangeLog)
        .join(SystemConfig)
        .filter(
            SystemConfig.config_key == config_key,
            ConfigChangeLog.id == version_id,
        )
        .first()
    )
    
    if not history:
        raise HTTPException(404, "Version not found")
    
    # 执行回滚
    config = service.update_config(
        config_key=config_key,
        new_value=history.old_value,
        changed_by=current_user_id,
        reason=f"Rollback: {reason or '回滚到历史版本'}",
    )
    
    logger.info(f"Config rolled back: {config_key} to version {version_id}")
    
    return {
        "message": "Config rolled back successfully",
        "config": config.to_dict(),
    }


@router.get("/audit/logs")
async def get_audit_logs(
    config_key: Optional[str] = Query(None, description="配置 Key"),
    changed_by: Optional[UUID] = Query(None, description="变更人"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="记录数量"),
    db: Session = Depends(get_db),
):
    """获取审计日志"""
    from app.models.system_config import ConfigChangeLog, SystemConfig
    
    query = db.query(ConfigChangeLog).join(SystemConfig)
    
    if config_key:
        query = query.filter(SystemConfig.config_key == config_key)
    if changed_by:
        query = query.filter(ConfigChangeLog.changed_by == changed_by)
    if start_date:
        query = query.filter(ConfigChangeLog.changed_at >= start_date)
    if end_date:
        query = query.filter(ConfigChangeLog.changed_at <= end_date)
    
    logs = query.order_by(ConfigChangeLog.changed_at.desc()).limit(limit).all()
    
    return {
        "items": [log.to_dict() for log in logs],
        "total": len(logs),
    }


@router.get("/audit/statistics")
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取审计统计"""
    from app.models.system_config import ConfigChangeLog
    from sqlalchemy import func
    
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 总变更数
    total_changes = (
        db.query(func.count(ConfigChangeLog.id))
        .filter(ConfigChangeLog.changed_at >= start_date)
        .scalar()
    )
    
    # 按类型统计
    changes_by_type = (
        db.query(SystemConfig.config_type, func.count(ConfigChangeLog.id))
        .join(SystemConfig)
        .filter(ConfigChangeLog.changed_at >= start_date)
        .group_by(SystemConfig.config_type)
        .all()
    )
    
    # 按用户统计
    changes_by_user = (
        db.query(ConfigChangeLog.changed_by, func.count(ConfigChangeLog.id))
        .filter(ConfigChangeLog.changed_at >= start_date)
        .filter(ConfigChangeLog.changed_by.isnot(None))
        .group_by(ConfigChangeLog.changed_by)
        .all()
    )
    
    return {
        "period_days": days,
        "total_changes": total_changes,
        "changes_by_type": [
            {"type": t, "count": c} for t, c in changes_by_type
        ],
        "changes_by_user": [
            {"user_id": str(u), "count": c} for u, c in changes_by_user
        ],
    }
