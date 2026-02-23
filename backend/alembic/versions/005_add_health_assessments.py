"""Add health_assessments table

Revision ID: 005_add_health_assessments
Revises: 004_add_habit_goals
Create Date: 2026-02-23

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "005_add_health_assessments"
down_revision = "004_add_habit_goals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create health_assessments table
    op.create_table(
        "health_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assessment_date", sa.DateTime(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("overall_grade", sa.String(20), nullable=False),
        sa.Column("nutrition_score", sa.Integer(), nullable=False),
        sa.Column(
            "nutrition_details", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "nutrition_suggestions",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("behavior_score", sa.Integer(), nullable=False),
        sa.Column(
            "behavior_details", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "behavior_suggestions",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("emotion_score", sa.Integer(), nullable=False),
        sa.Column(
            "emotion_details", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "emotion_suggestions", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "overall_suggestions", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "data_completeness", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("assessment_period_start", sa.DateTime(), nullable=True),
        sa.Column("assessment_period_end", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_health_assessments_user_id", "health_assessments", ["user_id"])
    op.create_index(
        "ix_health_assessments_assessment_date",
        "health_assessments",
        ["assessment_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_health_assessments_assessment_date", table_name="health_assessments"
    )
    op.drop_index("ix_health_assessments_user_id", table_name="health_assessments")
    op.drop_table("health_assessments")
