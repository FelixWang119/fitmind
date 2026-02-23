"""Add role switching tables

Revision ID: 003
Revises: 002
Create Date: 2026-02-23 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role columns to conversations table
    op.add_column(
        "conversations",
        sa.Column(
            "current_role",
            sa.String(length=50),
            nullable=True,
            server_default="general",
        ),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "role_fusion_enabled",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "manual_mode_override",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "manual_mode_message_count",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
    )

    # Create role_switches table
    op.create_table(
        "role_switches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_role", sa.String(length=50), nullable=False),
        sa.Column("to_role", sa.String(length=50), nullable=False),
        sa.Column(
            "trigger_type",
            sa.String(length=50),
            nullable=False,
        ),  # 'automatic', 'manual', 'fusion'
        sa.Column("switch_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_switches_id"), "role_switches", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_role_switches_id"), table_name="role_switches")
    op.drop_table("role_switches")
    op.drop_column("conversations", "manual_mode_message_count")
    op.drop_column("conversations", "manual_mode_override")
    op.drop_column("conversations", "role_fusion_enabled")
    op.drop_column("conversations", "current_role")
