"""add notification system tables

Revision ID: 006
Revises: 005_add_health_assessments
Create Date: 2026-02-25

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005_add_health_assessments"
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建通知模板表
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("title_template", sa.String(200), nullable=False),
        sa.Column("content_template", sa.Text(), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=True),
        sa.Column("variables", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notification_templates_code",
        "notification_templates",
        ["code"],
        unique=True,
    )
    op.create_index(
        "ix_notification_templates_event_type", "notification_templates", ["event_type"]
    )
    op.create_index(
        "ix_notification_templates_is_active", "notification_templates", ["is_active"]
    )

    # 2. 创建用户通知设置表
    op.create_table(
        "user_notification_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=True, default=True),
        sa.Column("do_not_disturb_enabled", sa.Boolean(), nullable=True, default=True),
        sa.Column("do_not_disturb_start", sa.String(5), nullable=True, default="22:00"),
        sa.Column("do_not_disturb_end", sa.String(5), nullable=True, default="08:00"),
        sa.Column("notify_habit_reminder", sa.Boolean(), nullable=True, default=True),
        sa.Column("notify_milestone", sa.Boolean(), nullable=True, default=True),
        sa.Column("notify_care", sa.Boolean(), nullable=True, default=True),
        sa.Column("notify_system", sa.Boolean(), nullable=True, default=True),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=True, default=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=True, default=False),
        sa.Column("max_notifications_per_day", sa.Integer(), nullable=True, default=20),
        sa.Column(
            "min_notification_interval", sa.Integer(), nullable=True, default=300
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_notification_settings_user_id",
        "user_notification_settings",
        ["user_id"],
        unique=True,
    )

    # 3. 创建通知记录表
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "template_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "channel",
            sa.Enum("IN_APP", "EMAIL", name="notificationchannel"),
            nullable=False,
            default="IN_APP",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "SENT",
                "DELIVERED",
                "READ",
                "FAILED",
                name="notificationstatus",
            ),
            nullable=True,
            default="PENDING",
        ),
        sa.Column("is_read", sa.Boolean(), nullable=True, default=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column(
            "metadata_",
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text())),
            nullable=True,
        ),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["notification_templates.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "ix_notifications_notification_type", "notifications", ["notification_type"]
    )
    op.create_index("ix_notifications_status", "notifications", ["status"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index(
        "ix_notifications_user_status", "notifications", ["user_id", "status"]
    )
    op.create_index(
        "ix_notifications_user_created", "notifications", ["user_id", "created_at"]
    )

    # 4. 创建事件日志表
    op.create_table(
        "event_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column(
            "event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("business_type", sa.String(50), nullable=True),
        sa.Column("business_id", sa.String(100), nullable=True),
        sa.Column(
            "notification_status",
            sa.Enum("PENDING", "SENT", "SKIPPED", "FAILED", name="eventlogstatus"),
            nullable=True,
            default="PENDING",
        ),
        sa.Column("notification_sent_at", sa.DateTime(), nullable=True),
        sa.Column("notification_error", sa.Text(), nullable=True),
        sa.Column("deduplication_key", sa.String(100), nullable=True),
        sa.Column("deduplication_hash", sa.String(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_logs_event_type", "event_logs", ["event_type"])
    op.create_index("ix_event_logs_occurred_at", "event_logs", ["occurred_at"])
    op.create_index("ix_event_logs_user_id", "event_logs", ["user_id"])
    op.create_index(
        "ix_event_logs_notification_status", "event_logs", ["notification_status"]
    )
    op.create_index(
        "ix_event_logs_deduplication_key", "event_logs", ["deduplication_key"]
    )


def downgrade():
    # 删除表的顺序要与创建时相反（先删除有外键依赖的表）
    op.drop_table("event_logs")
    op.drop_table("notifications")
    op.drop_table("user_notification_settings")
    op.drop_table("notification_templates")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS notificationstatus")
    op.execute("DROP TYPE IF EXISTS notificationchannel")
    op.execute("DROP TYPE IF EXISTS eventlogstatus")
