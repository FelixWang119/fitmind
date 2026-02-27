"""add_pgvector_embedding_column

Revision ID: 3c2a37ef51de
Revises: 521bbf2caeb5
Create Date: 2026-02-26 19:26:09.025404

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "3c2a37ef51de"
down_revision = "521bbf2caeb5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """添加 pgvector 支持并迁移数据"""

    # 1. 重命名旧列：embedding -> embedding_legacy
    op.execute(
        text("ALTER TABLE unified_memory RENAME COLUMN embedding TO embedding_legacy")
    )

    # 2. 添加新的 VECTOR 类型列
    op.add_column("unified_memory", sa.Column("embedding", sa.Text(), nullable=True))

    # 3. 使用原生 SQL 修改列类型为 VECTOR 并迁移数据
    op.execute(
        text("""
        ALTER TABLE unified_memory 
        ALTER COLUMN embedding TYPE vector(768) 
        USING embedding_legacy::vector
    """)
    )

    # 4. 创建向量索引 (IVFFlat - 适合中大型数据集)
    op.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_unified_memory_embedding 
        ON unified_memory USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
    """)
    )


def downgrade() -> None:
    """回滚 pgvector 更改"""

    # 1. 删除向量索引
    op.execute(text("DROP INDEX IF EXISTS idx_unified_memory_embedding"))

    # 2. 转换回 TEXT 类型
    op.execute(
        text("""
        ALTER TABLE unified_memory 
        ALTER COLUMN embedding TYPE text 
        USING array_to_string(ARRAY(SELECT UNNEST(embedding)), ',')
    """)
    )

    # 3. 恢复旧列名
    op.execute(
        text("ALTER TABLE unified_memory RENAME COLUMN embedding TO embedding_new")
    )
    op.execute(
        text("ALTER TABLE unified_memory RENAME COLUMN embedding_legacy TO embedding")
    )
    op.drop_column("unified_memory", "embedding_new")
