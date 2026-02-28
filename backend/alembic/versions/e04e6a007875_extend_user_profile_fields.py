"""extend_user_profile_fields

Revision ID: e04e6a007875
Revises: v2_0_remove_is_indexed
Create Date: 2026-02-27 22:03:49.945894

扩展用户档案字段：从 6 字段到 17 字段
Story 1.1: 数据库模型扩展
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e04e6a007875"
down_revision = "v2_0_remove_is_indexed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    升级：添加 11 个新字段到 users 表
    所有字段 nullable=True 保证向后兼容性
    """
    # 添加体重相关字段
    op.add_column(
        "users",
        sa.Column(
            "current_weight", sa.Integer(), nullable=True, comment="当前体重 (单位：克)"
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "waist_circumference",
            sa.Integer(),
            nullable=True,
            comment="腰围 (单位：厘米)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "hip_circumference",
            sa.Integer(),
            nullable=True,
            comment="臀围 (单位：厘米)",
        ),
    )

    # 添加体成分字段
    op.add_column(
        "users",
        sa.Column(
            "body_fat_percentage",
            sa.Float(),
            nullable=True,
            comment="体脂率 (单位：百分比)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "muscle_mass", sa.Integer(), nullable=True, comment="肌肉量 (单位：克)"
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "bone_density",
            sa.Float(),
            nullable=True,
            comment="骨密度 (单位：克/平方厘米)",
        ),
    )

    # 添加代谢字段
    op.add_column(
        "users",
        sa.Column(
            "metabolism_rate",
            sa.Integer(),
            nullable=True,
            comment="基础代谢率 (单位：kcal/day)",
        ),
    )

    # 添加健康信息字段 (JSON)
    op.add_column(
        "users",
        sa.Column(
            "health_conditions",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment="健康状况 (JSON 格式)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "medications",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment="用药情况 (JSON 格式)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "allergies",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment="过敏信息 (JSON 格式)",
        ),
    )

    # 添加生活质量字段
    op.add_column(
        "users",
        sa.Column(
            "sleep_quality", sa.Integer(), nullable=True, comment="睡眠质量 (1-10 分)"
        ),
    )


def downgrade() -> None:
    """
    回滚：删除所有新增字段
    顺序与升级相反
    """
    # 删除字段 (顺序与 upgrade 相反)
    op.drop_column("users", "sleep_quality")
    op.drop_column("users", "allergies")
    op.drop_column("users", "medications")
    op.drop_column("users", "health_conditions")
    op.drop_column("users", "metabolism_rate")
    op.drop_column("users", "bone_density")
    op.drop_column("users", "muscle_mass")
    op.drop_column("users", "body_fat_percentage")
    op.drop_column("users", "hip_circumference")
    op.drop_column("users", "waist_circumference")
    op.drop_column("users", "current_weight")
