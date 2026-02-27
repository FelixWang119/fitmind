"""系统配置服务"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.system_config import ConfigChangeLog, ConfigType, SystemConfig

logger = logging.getLogger(__name__)


class SystemConfigService:
    """系统配置服务"""

    def __init__(self, db: Session):
        self.db = db
        self._cache: Dict[str, Any] = {}

    def get_config(self, config_key: str, environment: str = "all") -> Optional[Dict[str, Any]]:
        """获取配置"""
        # 先检查缓存
        cache_key = f"{config_key}:{environment}"
        if cache_key in self._cache:
            cached_value, cached_env, is_active = self._cache[cache_key]
            if is_active:
                logger.debug(f"Cache hit for config: {config_key}")
                return cached_value
        
        # 查询数据库
        config = (
            self.db.query(SystemConfig)
            .filter(
                SystemConfig.config_key == config_key,
                SystemConfig.environment.in_([environment, "all"]),
                SystemConfig.is_active == True,
            )
            .order_by(SystemConfig.environment.desc())  # 优先匹配具体环境
            .first()
        )
        
        if config:
            # 更新缓存
            self._cache[cache_key] = (config.config_value, config.environment, config.is_active)
            logger.debug(f"Loaded config from DB: {config_key}")
            return config.config_value
        
        logger.debug(f"Config not found: {config_key}")
        return None

    def update_config(
        self,
        config_key: str,
        new_value: Dict[str, Any],
        changed_by: UUID,
        reason: Optional[str] = None,
    ) -> SystemConfig:
        """更新配置"""
        config = (
            self.db.query(SystemConfig)
            .filter(SystemConfig.config_key == config_key)
            .first()
        )
        
        if not config:
            raise ValueError(f"Config not found: {config_key}")
        
        # 保存旧值
        old_value = config.config_value.copy()
        
        # 更新配置
        config.config_value = new_value
        config.updated_by = changed_by
        config.updated_at = datetime.utcnow()
        
        # 记录变更日志
        change_log = ConfigChangeLog(
            config_id=config.id,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )
        self.db.add(change_log)
        
        # 清除缓存
        self._invalidate_cache(config_key)
        
        logger.info(f"Updated config: {config_key} by {changed_by}")
        
        return config

    def create_config(
        self,
        config_key: str,
        config_value: Dict[str, Any],
        config_type: str,
        config_category: Optional[str] = None,
        description: Optional[str] = None,
        environment: str = "all",
        created_by: Optional[UUID] = None,
    ) -> SystemConfig:
        """创建配置"""
        config = SystemConfig(
            config_key=config_key,
            config_value=config_value,
            config_type=config_type,
            config_category=config_category,
            description=description,
            environment=environment,
            is_active=True,
            created_by=created_by,
        )
        self.db.add(config)
        self.db.flush()
        
        logger.info(f"Created config: {config_key}")
        
        return config

    def get_all_configs(
        self,
        config_type: Optional[str] = None,
        config_category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[SystemConfig]:
        """获取所有配置"""
        query = self.db.query(SystemConfig)
        
        if config_type:
            query = query.filter(SystemConfig.config_type == config_type)
        if config_category:
            query = query.filter(SystemConfig.config_category == config_category)
        if is_active is not None:
            query = query.filter(SystemConfig.is_active == is_active)
        
        return query.order_by(SystemConfig.config_category, SystemConfig.config_key).all()

    def get_config_history(self, config_key: str, limit: int = 20) -> List[ConfigChangeLog]:
        """获取配置变更历史"""
        config = (
            self.db.query(SystemConfig)
            .filter(SystemConfig.config_key == config_key)
            .first()
        )
        
        if not config:
            return []
        
        return (
            self.db.query(ConfigChangeLog)
            .filter(ConfigChangeLog.config_id == config.id)
            .order_by(ConfigChangeLog.changed_at.desc())
            .limit(limit)
            .all()
        )

    def is_feature_enabled(self, feature_key: str, environment: str = "all") -> bool:
        """检查功能开关是否启用"""
        config = self.get_config(feature_key, environment)
        
        if not config:
            return False
        
        return config.get("enabled", False)

    def get_ai_prompt(self, role: str) -> Optional[str]:
        """获取 AI 角色提示词"""
        config_key = f"ai.prompt.{role}"
        config = self.get_config(config_key)
        
        if not config:
            return None
        
        return config.get("prompt")

    def get_ai_config(self, role: str) -> Optional[Dict[str, Any]]:
        """获取 AI 完整配置（提示词 + 参数）"""
        config_key = f"ai.prompt.{role}"
        return self.get_config(config_key)

    def _invalidate_cache(self, config_key: str):
        """清除配置缓存"""
        keys_to_delete = [key for key in self._cache if key.startswith(f"{config_key}:")]
        for key in keys_to_delete:
            del self._cache[key]
        logger.debug(f"Invalidated cache for config: {config_key}")

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()
        logger.info("Cleared all config cache")


# 全局服务实例
config_service: Optional[SystemConfigService] = None
