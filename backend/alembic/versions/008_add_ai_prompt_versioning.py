"""add ai prompt versioning

Revision ID: 008
Revises: 007_add_system_config_management
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    # 创建 AI 提示词版本表
    op.create_table(
        "ai_prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_key", sa.String(100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=False),
        sa.Column("is_draft", sa.Boolean(), nullable=True, default=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_prompt_versions_prompt_key", "ai_prompt_versions", ["prompt_key"])
    op.create_index("ix_ai_prompt_versions_version", "ai_prompt_versions", ["version"])
    op.create_index("ix_ai_prompt_versions_is_active", "ai_prompt_versions", ["is_active"])


def downgrade():
    op.drop_table("ai_prompt_versions")
