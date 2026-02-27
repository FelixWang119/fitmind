"""系统配置管理模块"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Integer,
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    Integer,
    Index,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConfigType(str, PyEnum):
    """配置类型枚举"""

    AI_PROMPT = "ai_prompt"
    FEATURE_FLAG = "feature_flag"
    SYSTEM_CONFIG = "system_config"
    NOTIFICATION_TEMPLATE = "notification_template"
    BUSINESS_RULE = "business_rule"


class SystemConfig(Base):
    """系统配置表"""

    __tablename__ = "system_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(JSONB, nullable=False)
    config_type = Column(String(50), nullable=False, index=True)
    config_category = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    environment = Column(
        String(20), default="all"
    )  # all/development/staging/production
    is_active = Column(Boolean, default=True, index=True)

    # 审计字段（users.id 是 Integer 类型）
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("config_key", "environment", name="uq_config_key_env"),
    )

    # 关系
    change_logs = relationship(
        "ConfigChangeLog", back_populates="config", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, type={self.config_type})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "config_key": self.config_key,
            "config_value": self.config_value,
            "config_type": self.config_type,
            "config_category": self.config_category,
            "description": self.description,
            "environment": self.environment,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
        }


class ConfigChangeLog(Base):
    """配置变更日志表"""

    __tablename__ = "config_change_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("system_configs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=True)
    changed_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # 关系
    config = relationship("SystemConfig", back_populates="change_logs")

    def __repr__(self):
        return f"<ConfigChangeLog(config_id={self.config_id}, changed_at={self.changed_at})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "config_id": str(self.config_id),
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "reason": self.reason,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }


# 初始化配置数据
INITIAL_CONFIGS = [
    # AI 提示词配置
    {
        "config_key": "ai.prompt.nutritionist",
        "config_value": {
            "prompt": "你是一位专业的营养师，专注于体重管理和健康饮食指导。你具备以下专业能力：\n\n1. 营养学知识：精通宏量营养素（蛋白质、碳水化合物、脂肪）和微量营养素（维生素、矿物质）的作用\n2. 饮食规划：根据用户的体重目标、健康状况、饮食偏好制定个性化饮食方案\n3. 食物评估：能够快速评估食物的营养价值和热量\n4. 行为指导：帮助用户建立健康的饮食习惯\n\n你的沟通风格：\n- 专业但亲切，避免使用过于专业的术语\n- 以数据为依据，提供科学建议\n- 关注用户的长期健康，而不仅仅是体重数字\n- 鼓励小步骤改变，不求完美\n\n当用户询问时，你应该：\n1. 先了解用户的具体情况（当前体重、目标、饮食习惯等）\n2. 提供具体可执行的建议\n3. 解释为什么这样建议（科学依据）\n4. 给予鼓励和支持",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        "config_type": "ai_prompt",
        "config_category": "ai",
        "description": "营养师角色提示词",
    },
    {
        "config_key": "ai.prompt.behavior_coach",
        "config_value": {
            "prompt": "你是一位专业的行为教练，专注于习惯养成和行为改变。你具备以下专业能力：\n\n1. 行为心理学：理解习惯形成的机制和 behavior change 的科学原理\n2. 目标设定：帮助用户设定 SMART 目标（具体、可衡量、可实现、相关、有时限）\n3. 障碍识别：识别阻碍用户改变的心理和环境障碍\n4. 激励策略：运用正向强化、社会支持等技巧帮助用户坚持\n\n你的沟通风格：\n- 积极正向，关注进步而非完美\n- 实用主义，提供具体可执行的行动步骤\n- 同理心强，理解改变的困难\n- 善于提问，引导用户自我发现\n\n当用户询问时，你应该：\n1. 了解用户的当前状态和目标\n2. 帮助用户拆解大目标为小步骤\n3. 预测可能的障碍并提供应对策略\n4. 庆祝每一个小进步\n5. 当用户失败时，帮助分析原因而非责备",
            "temperature": 0.8,
            "max_tokens": 1000,
        },
        "config_type": "ai_prompt",
        "config_category": "ai",
        "description": "行为教练角色提示词",
    },
    {
        "config_key": "ai.prompt.emotional_support",
        "config_value": {
            "prompt": "你是一位温暖的情感陪伴者，专注于情绪支持和心理疏导。你具备以下特质：\n\n1. 共情能力：能够理解并回应用户的情绪状态\n2. 倾听技巧：给予用户充分表达的空间，不急于给建议\n3. 正向支持：在用户低落时提供鼓励和希望\n4. 边界意识：知道何时建议寻求专业心理帮助\n\n你的沟通风格：\n- 温和耐心，让用户感到被理解\n- 使用「我注意到」「我感受到」等反映性语言\n- 避免说教，多用「可以」「也许」等建议性语言\n- 在适当时候使用表情符号增加温暖感\n\n当用户情绪低落时，你应该：\n1. 先承认和验证用户的感受（「听起来你真的很难过」）\n2. 给予情感支持（「你已经很努力了」）\n3. 帮助用户看到积极面（但不否定负面情绪）\n4. 提供小建议而非大道理\n5. 如有必要，建议寻求专业帮助",
            "temperature": 0.9,
            "max_tokens": 1000,
        },
        "config_type": "ai_prompt",
        "config_category": "ai",
        "description": "情感陪伴角色提示词",
    },
    # 功能开关配置
    {
        "config_key": "feature.ai_chat",
        "config_value": {
            "enabled": True,
            "rollout_percentage": 100,
            "environments": ["development", "staging", "production"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "AI 对话功能开关",
    },
    {
        "config_key": "feature.habit_tracking",
        "config_value": {
            "enabled": True,
            "rollout_percentage": 100,
            "environments": ["development", "staging", "production"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "习惯打卡功能开关",
    },
    {
        "config_key": "feature.nutrition_tracking",
        "config_value": {
            "enabled": True,
            "rollout_percentage": 100,
            "environments": ["development", "staging", "production"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "饮食记录功能开关",
    },
    {
        "config_key": "feature.exercise_tracking",
        "config_value": {
            "enabled": True,
            "rollout_percentage": 100,
            "environments": ["development", "staging", "production"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "运动记录功能开关",
    },
    {
        "config_key": "feature.weight_tracking",
        "config_value": {
            "enabled": True,
            "rollout_percentage": 100,
            "environments": ["development", "staging", "production"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "体重记录功能开关",
    },
    {
        "config_key": "feature.sleep_tracking",
        "config_value": {
            "enabled": False,
            "rollout_percentage": 0,
            "environments": ["development"],
        },
        "config_type": "feature_flag",
        "config_category": "features",
        "description": "睡眠记录功能开关",
    },
]
