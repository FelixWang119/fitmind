"""add system config management

Revision ID: 007
Revises: 006_add_notification_system
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建系统配置表
    op.create_table(
        "system_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("config_key", sa.String(100), nullable=False),
        sa.Column("config_value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("config_type", sa.String(50), nullable=False),
        sa.Column("config_category", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("environment", sa.String(20), nullable=True, default="all"),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_key", "environment", name="uq_config_key_env"),
    )
    op.create_index("ix_system_configs_config_key", "system_configs", ["config_key"])
    op.create_index("ix_system_configs_config_type", "system_configs", ["config_type"])
    op.create_index("ix_system_configs_config_category", "system_configs", ["config_category"])
    op.create_index("ix_system_configs_is_active", "system_configs", ["is_active"])

    # 2. 创建配置变更日志表
    op.create_table(
        "config_change_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("config_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["config_id"], ["system_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_config_change_logs_config_id", "config_change_logs", ["config_id"])
    op.create_index("ix_config_change_logs_changed_at", "config_change_logs", ["changed_at"])

    # 3. 插入初始配置数据
    insert_initial_configs()


def downgrade():
    op.drop_table("config_change_logs")
    op.drop_table("system_configs")


def insert_initial_configs():
    """插入初始配置数据"""
    from sqlalchemy import text
    
    # AI 提示词配置
    configs = [
        (
            "ai.prompt.nutritionist",
            '{"prompt": "你是一位专业的营养师，专注于体重管理和健康饮食指导。", "temperature": 0.7, "max_tokens": 1000}',
            "ai_prompt",
            "ai",
            "营养师角色提示词",
        ),
        (
            "ai.prompt.behavior_coach",
            '{"prompt": "你是一位专业的行为教练，专注于习惯养成和行为改变。", "temperature": 0.8, "max_tokens": 1000}',
            "ai_prompt",
            "ai",
            "行为教练角色提示词",
        ),
        (
            "ai.prompt.emotional_support",
            '{"prompt": "你是一位温暖的情感陪伴者，专注于情绪支持和心理疏导。", "temperature": 0.9, "max_tokens": 1000}',
            "ai_prompt",
            "ai",
            "情感陪伴角色提示词",
        ),
        # 功能开关配置
        (
            "feature.ai_chat",
            '{"enabled": true, "rollout_percentage": 100}',
            "feature_flag",
            "features",
            "AI 对话功能开关",
        ),
        (
            "feature.habit_tracking",
            '{"enabled": true, "rollout_percentage": 100}',
            "feature_flag",
            "features",
            "习惯打卡功能开关",
        ),
        (
            "feature.nutrition_tracking",
            '{"enabled": true, "rollout_percentage": 100}',
            "feature_flag",
            "features",
            "饮食记录功能开关",
        ),
        (
            "feature.exercise_tracking",
            '{"enabled": true, "rollout_percentage": 100}',
            "feature_flag",
            "features",
            "运动记录功能开关",
        ),
        (
            "feature.weight_tracking",
            '{"enabled": true, "rollout_percentage": 100}',
            "feature_flag",
            "features",
            "体重记录功能开关",
        ),
        (
            "feature.sleep_tracking",
            '{"enabled": false, "rollout_percentage": 0}',
            "feature_flag",
            "features",
            "睡眠记录功能开关",
        ),
    ]
    
    for config_key, config_value, config_type, config_category, description in configs:
        op.execute(
            text("""
                INSERT INTO system_configs (
                    id, config_key, config_value, config_type, config_category, description,
                    environment, is_active, created_at
                ) VALUES (
                    gen_random_uuid(), :config_key, :config_value::jsonb, :config_type, :config_category, :description,
                    'all', true, NOW()
                )
            """),
            {
                "config_key": config_key,
                "config_value": config_value,
                "config_type": config_type,
                "config_category": config_category,
                "description": description,
            }
        )
