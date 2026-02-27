"""remove is_indexed columns from source tables

Revision ID: v2_0_remove_is_indexed
Revises: 3c2a37ef51de
Create Date: 2026-02-26

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "v2_0_remove_is_indexed"
down_revision: Union[str, None] = "3c2a37ef51de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    删除所有源数据表的 is_indexed 列

    记忆系统架构 v2.0 变更：
    - SQLite 持久化队列自动管理状态，不再需要 is_indexed 标记
    - 重启恢复由 SQLite 文件自动处理，无需从数据库加载
    """
    from sqlalchemy import inspect
    from app.core.database import engine

    # 检查 water_intakes 表是否存在
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # 1. 删除 meals 表的 is_indexed 列
    op.drop_column("meals", "is_indexed")
    print("✓ 已删除 meals.is_indexed 列")

    # 2. 删除 exercise_checkins 表的 is_indexed 列
    op.drop_column("exercise_checkins", "is_indexed")
    print("✓ 已删除 exercise_checkins.is_indexed 列")

    # 3. 删除 habits 表的 is_indexed 列
    op.drop_column("habits", "is_indexed")
    print("✓ 已删除 habits.is_indexed 列")

    # 4. 删除 health_records 表的 is_indexed 列
    op.drop_column("health_records", "is_indexed")
    print("✓ 已删除 health_records.is_indexed 列")

    # 5. 删除 water_intakes 表的 is_indexed 列（如果表存在）
    if "water_intakes" in tables:
        op.drop_column("water_intakes", "is_indexed")
        print("✓ 已删除 water_intakes.is_indexed 列")
    else:
        print("⚠ water_intakes 表不存在，跳过")

    print("\n✅ v2.0 迁移完成：所有 is_indexed 列已删除")
    print("💡 提示：SQLite 持久化队列现在自动管理记忆状态")


def downgrade() -> None:
    """
    恢复所有源数据表的 is_indexed 列

    注意：回滚后需要手动重置所有记录的 is_indexed=False
    """

    # 1. 恢复 meals 表的 is_indexed 列
    op.add_column(
        "meals",
        sa.Column("is_indexed", sa.Boolean(), nullable=False, server_default="false"),
    )
    print("✓ 已恢复 meals.is_indexed 列")

    # 2. 恢复 exercise_checkins 表的 is_indexed 列
    op.add_column(
        "exercise_checkins",
        sa.Column("is_indexed", sa.Boolean(), nullable=False, server_default="false"),
    )
    print("✓ 已恢复 exercise_checkins.is_indexed 列")

    # 3. 恢复 habits 表的 is_indexed 列
    op.add_column(
        "habits",
        sa.Column("is_indexed", sa.Boolean(), nullable=False, server_default="false"),
    )
    print("✓ 已恢复 habits.is_indexed 列")

    # 4. 恢复 health_records 表的 is_indexed 列
    op.add_column(
        "health_records",
        sa.Column("is_indexed", sa.Boolean(), nullable=False, server_default="false"),
    )
    print("✓ 已恢复 health_records.is_indexed 列")

    # 5. 恢复 water_intakes 表的 is_indexed 列（如果表存在）
    try:
        op.add_column(
            "water_intakes",
            sa.Column(
                "is_indexed", sa.Boolean(), nullable=False, server_default="false"
            ),
        )
        print("✓ 已恢复 water_intakes.is_indexed 列")
    except Exception as e:
        print(f"⚠ water_intakes 表不存在，跳过：{e}")

    print("\n✅ 回滚完成：所有 is_indexed 列已恢复")
    print("⚠️  警告：所有记录的 is_indexed=False，需要重新运行索引 Pipeline")
