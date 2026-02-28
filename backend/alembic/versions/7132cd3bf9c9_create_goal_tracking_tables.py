"""create_goal_tracking_tables

Revision ID: 7132cd3bf9c9
Revises: e04e6a007875
Create Date: 2026-02-27 22:24:01.915460

Story 1.6: 目标数据模型
创建 3 个新表：user_goals, goal_progress, goal_history
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7132cd3bf9c9"
down_revision = "e04e6a007875"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    升级：创建目标追踪相关的 3 个表
    """
    # ========== 1. 创建 user_goals 表 ==========
    op.create_table(
        "user_goals",
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_type", sa.String(length=50), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column(
            "start_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("predicted_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True, default="active"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("goal_id"),
    )

    # 创建索引
    op.create_index("ix_user_goals_user_id", "user_goals", ["user_id"])
    op.create_index("ix_user_goals_goal_type", "user_goals", ["goal_type"])
    op.create_index("ix_user_goals_status", "user_goals", ["status"])

    # ========== 2. 创建 goal_progress 表 ==========
    op.create_table(
        "goal_progress",
        sa.Column("progress_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column(
            "recorded_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("daily_target_met", sa.Boolean(), nullable=True, default=False),
        sa.Column("streak_count", sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(
            ["goal_id"], ["user_goals.goal_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("progress_id"),
    )

    # 创建索引
    op.create_index("ix_goal_progress_goal_id", "goal_progress", ["goal_id"])
    op.create_index(
        "ix_goal_progress_recorded_date", "goal_progress", ["recorded_date"]
    )

    # ========== 3. 创建 goal_history 表 ==========
    op.create_table(
        "goal_history",
        sa.Column("history_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=50), nullable=False),
        sa.Column(
            "previous_state", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("new_state", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("ai_suggested", sa.Boolean(), nullable=True, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["goal_id"], ["user_goals.goal_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("history_id"),
    )

    # 创建索引
    op.create_index("ix_goal_history_goal_id", "goal_history", ["goal_id"])
    op.create_index("ix_goal_history_change_type", "goal_history", ["change_type"])


def downgrade() -> None:
    """
    回滚：删除目标追踪相关的 3 个表
    """
    # 删除表 (顺序与创建相反)
    op.drop_table("goal_history")
    op.drop_table("goal_progress")
    op.drop_table("user_goals")
