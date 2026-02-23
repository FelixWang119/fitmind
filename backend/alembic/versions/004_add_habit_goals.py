"""Add habit_goals table

Revision ID: 004_add_habit_goals
Revises:
Create Date: 2026-02-23

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_add_habit_goals"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create habit_goals table
    op.create_table(
        "habit_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("habit_id", sa.Integer(), nullable=False),
        sa.Column("goal_type", sa.String(length=50), nullable=False),
        sa.Column("target_value", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("is_achieved", sa.Boolean(), nullable=True, default=False),
        sa.Column("current_progress", sa.Integer(), nullable=True, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index for faster queries
    op.create_index("ix_habit_goals_user_id", "habit_goals", ["user_id"])
    op.create_index("ix_habit_goals_habit_id", "habit_goals", ["habit_id"])
    op.create_index("ix_habit_goals_is_active", "habit_goals", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_habit_goals_is_active", table_name="habit_goals")
    op.drop_index("ix_habit_goals_habit_id", table_name="habit_goals")
    op.drop_index("ix_habit_goals_user_id", table_name="habit_goals")
    op.drop_table("habit_goals")
