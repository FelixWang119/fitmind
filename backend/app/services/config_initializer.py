"""配置初始化服务 - 批量初始化系统配置"""

import logging
from typing import Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig
from app.services.system_config_service import SystemConfigService

logger = logging.getLogger(__name__)


# 系统性能配置
PERFORMANCE_CONFIGS = [
    {
        "config_key": "system.performance.slow_query_threshold",
        "config_value": {
            "value": 1.0,
            "unit": "seconds",
            "description": "慢查询阈值",
            "min": 0.1,
            "max": 10.0,
        },
        "config_type": "system_config",
        "config_category": "performance",
        "description": "慢查询阈值（秒）",
    },
    {
        "config_key": "system.performance.compression_threshold_kb",
        "config_value": {
            "value": 100,
            "unit": "KB",
            "description": "响应压缩阈值",
            "min": 10,
            "max": 1000,
        },
        "config_type": "system_config",
        "config_category": "performance",
        "description": "响应压缩阈值（KB）",
    },
    {
        "config_key": "system.performance.response_cache_ttl",
        "config_value": {
            "value": 300,
            "unit": "seconds",
            "description": "响应缓存时间",
            "min": 60,
            "max": 3600,
        },
        "config_type": "system_config",
        "config_category": "performance",
        "description": "响应缓存 TTL",
    },
]

# 缓存配置
CACHE_CONFIGS = [
    {
        "config_key": "system.cache.default_ttl",
        "config_value": {
            "value": 300,
            "unit": "seconds",
            "description": "默认缓存时间",
        },
        "config_type": "system_config",
        "config_category": "cache",
        "description": "默认缓存 TTL",
    },
    {
        "config_key": "system.cache.max_size",
        "config_value": {
            "value": 1000,
            "unit": "entries",
            "description": "最大缓存条目数",
        },
        "config_type": "system_config",
        "config_category": "cache",
        "description": "缓存大小限制",
    },
    {
        "config_key": "system.cache.eviction_policy",
        "config_value": {
            "value": "LRU",
            "options": ["LRU", "LFU", "FIFO"],
            "description": "驱逐策略",
        },
        "config_type": "system_config",
        "config_category": "cache",
        "description": "缓存驱逐策略",
    },
]

# 邮件配置
EMAIL_CONFIGS = [
    {
        "config_key": "system.email.batch_size",
        "config_value": {
            "value": 100,
            "unit": "emails",
            "description": "批量发送数量",
        },
        "config_type": "system_config",
        "config_category": "email",
        "description": "邮件批量发送大小",
    },
    {
        "config_key": "system.email.retry_count",
        "config_value": {
            "value": 3,
            "unit": "times",
            "description": "重试次数",
        },
        "config_type": "system_config",
        "config_category": "email",
        "description": "邮件发送重试次数",
    },
]

# 日志配置
LOGGING_CONFIGS = [
    {
        "config_key": "system.logging.level",
        "config_value": {
            "value": "INFO",
            "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "description": "日志级别",
        },
        "config_type": "system_config",
        "config_category": "logging",
        "description": "全局日志级别",
    },
    {
        "config_key": "system.logging.slow_query_log",
        "config_value": {
            "enabled": True,
            "threshold": 1.0,
            "description": "慢查询日志",
        },
        "config_type": "system_config",
        "config_category": "logging",
        "description": "慢查询日志开关",
    },
]

# 业务规则配置
BUSINESS_RULE_CONFIGS = [
    {
        "config_key": "business.habit.streak_milestone_7",
        "config_value": {
            "value": 7,
            "unit": "days",
            "description": "7 天习惯里程碑",
        },
        "config_type": "business_rule",
        "config_category": "habits",
        "description": "习惯 7 天里程碑阈值",
    },
    {
        "config_key": "business.habit.streak_milestone_30",
        "config_value": {
            "value": 30,
            "unit": "days",
            "description": "30 天习惯里程碑",
        },
        "config_type": "business_rule",
        "config_category": "habits",
        "description": "习惯 30 天里程碑阈值",
    },
    {
        "config_key": "business.notification.max_per_day",
        "config_value": {
            "value": 20,
            "unit": "notifications",
            "description": "每日最大通知数",
        },
        "config_type": "business_rule",
        "config_category": "notifications",
        "description": "每日最大通知数",
    },
    {
        "config_key": "business.notification.min_interval_seconds",
        "config_value": {
            "value": 300,
            "unit": "seconds",
            "description": "最小通知间隔",
        },
        "config_type": "business_rule",
        "config_category": "notifications",
        "description": "通知最小间隔（秒）",
    },
]


def initialize_all_configs(db: Session, created_by: UUID = None):
    """初始化所有系统配置"""
    service = SystemConfigService(db)
    
    all_configs = (
        PERFORMANCE_CONFIGS +
        CACHE_CONFIGS +
        EMAIL_CONFIGS +
        LOGGING_CONFIGS +
        BUSINESS_RULE_CONFIGS
    )
    
    created_count = 0
    for config_data in all_configs:
        try:
            # 检查是否已存在
            existing = service.get_config(config_data["config_key"])
            if not existing:
                service.create_config(
                    config_key=config_data["config_key"],
                    config_value=config_data["config_value"],
                    config_type=config_data["config_type"],
                    config_category=config_data.get("config_category"),
                    description=config_data.get("description"),
                    created_by=created_by,
                )
                created_count += 1
                logger.info(f"Created config: {config_data['config_key']}")
            else:
                logger.debug(f"Config exists: {config_data['config_key']}")
        except Exception as e:
            logger.error(f"Failed to create config {config_data['config_key']}: {e}")
    
    logger.info(f"Initialized {created_count}/{len(all_configs)} configs")
    return created_count
