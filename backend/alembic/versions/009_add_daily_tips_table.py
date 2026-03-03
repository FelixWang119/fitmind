"""add_daily_tips_table

Revision ID: 009
Revises: 7132cd3bf9c9
Create Date: 2026-03-02

Story 9.1: 科普内容生成服务
创建每日科普内容表 daily_tips
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "009"
down_revision = "7132cd3bf9c9"
branch_labels = None
depends_on = None


def upgrade():
    # 创建每日科普内容表
    op.create_table(
        "daily_tips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("topic", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "disclaimer",
            sa.Text(),
            nullable=True,
            default="本内容仅供参考，不能替代专业医疗建议。如有健康问题，请咨询医生。",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 创建索引
    op.create_index("ix_daily_tips_id", "daily_tips", ["id"])
    op.create_index("ix_daily_tips_date", "daily_tips", ["date"], unique=True)
    op.create_index("ix_daily_tips_topic", "daily_tips", ["topic"])
    op.create_index("ix_daily_tips_is_active", "daily_tips", ["is_active"])
    op.create_index("ix_daily_tips_date_topic", "daily_tips", ["date", "topic"])
    op.create_index("ix_daily_tips_is_active_date", "daily_tips", ["is_active", "date"])


def downgrade():
    # 删除索引
    op.drop_index("ix_daily_tips_is_active_date", table_name="daily_tips")
    op.drop_index("ix_daily_tips_date_topic", table_name="daily_tips")
    op.drop_index("ix_daily_tips_is_active", table_name="daily_tips")
    op.drop_index("ix_daily_tips_topic", table_name="daily_tips")
    op.drop_index("ix_daily_tips_date", table_name="daily_tips")
    op.drop_index("ix_daily_tips_id", table_name="daily_tips")

    # 删除表
    op.drop_table("daily_tips")
