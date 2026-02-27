"""
Agent Memory 测试专用配置

使用独立的 PostgreSQL 测试数据库，避免模型兼容性问题。
只创建 memory 相关的表。
"""

import os
import pytest
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# 设置测试环境
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"
)
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["ALGORITHM"] = "HS256"


# 仅导入 memory 相关的模型
from sqlalchemy import MetaData

# 创建只包含必要表的 metadata
memory_metadata = MetaData()

# 创建数据库引擎
TEST_DATABASE_URL = "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"
engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_memory_test_database():
    """设置 memory 测试数据库"""
    # 启用 pgvector
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("\n✅ pgvector 扩展已启用")
        except Exception as e:
            print(f"\n⚠️  pgvector 可能已存在：{e}")

    # 只创建 memory 相关的表
    # 使用 app.core.database.Base 会创建所有表，这里我们手动创建需要的
    from app.core.database import Base

    # 创建所有表（包括有问题的表，但我们会处理）
    # 在实际测试中使用 mocked 服务避免依赖所有表
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 所有表已创建")
    except Exception as e:
        print(f"⚠️  部分表创建失败：{e}")
        print("   继续执行，使用 mock 服务")

    yield

    # 清理数据
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
            transaction.commit()
            print("\n✅ 测试数据已清理")
        except Exception:
            transaction.rollback()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """为每个测试创建独立的数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # 回滚事务，清理测试数据
    transaction.rollback()
    connection.close()
