"""Pytest configuration and fixtures for backend tests."""

import os
import uuid
import pytest
from typing import Generator, TYPE_CHECKING
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
# 使用 PostgreSQL 测试数据库（独立于生产数据库）
os.environ["DATABASE_URL"] = (
    "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"
)
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["ALGORITHM"] = "HS256"

from app.main import app
from app.core.database import Base, get_db

# Import User model for type hints
if TYPE_CHECKING:
    from app.models.user import User


# =============================================================================
# Data Factory Functions
# =============================================================================


def create_test_user_data(overrides: dict = None) -> dict:
    """
    数据工厂：为测试生成唯一的用户数据

    使用 UUID 确保并发测试时不会发生数据冲突
    """
    unique_id = str(uuid.uuid4())[:8]

    base_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "hashed_password": None,  # Will be set by fixture
        "is_active": True,
        "full_name": f"Test User {unique_id}",
    }

    if overrides:
        base_data.update(overrides)

    return base_data


def create_test_habit_data(user_id: int, overrides: dict = None) -> dict:
    """数据工厂：为测试生成唯一的习惯数据"""
    unique_id = str(uuid.uuid4())[:8]

    base_data = {
        "user_id": user_id,
        "name": f"Test Habit {unique_id}",
        "description": f"Test description {unique_id}",
        "category": "health",
        "frequency": "daily",
        "target_count": 1,
        "is_active": True,
    }

    if overrides:
        base_data.update(overrides)

    return base_data


def create_test_health_record_data(user_id: int, overrides: dict = None) -> dict:
    """数据工厂：为测试生成唯一的健康记录数据"""
    from datetime import datetime

    unique_id = str(uuid.uuid4())[:8]

    base_data = {
        "user_id": user_id,
        "weight": 70000 + (hash(unique_id) % 10000),  # 70kg +/- 10kg
        "height": 170,
        "record_date": datetime.utcnow().date(),
        "heart_rate": 70 + (hash(unique_id) % 20),
        "blood_pressure_systolic": 120 + (hash(unique_id) % 20),
        "blood_pressure_diastolic": 80 + (hash(unique_id) % 10),
        "sleep_hours": 7.0 + (hash(unique_id) % 3),
    }

    if overrides:
        base_data.update(overrides)

    return base_data


# =============================================================================
# Test Database Setup (PostgreSQL)
# =============================================================================

# PostgreSQL 测试数据库连接
TEST_DATABASE_URL = "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"
engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,  # 关闭 SQL 日志以提高性能
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """在测试会话开始时创建数据库表"""
    # 先启用必要的扩展
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("\n✅ pgvector 扩展已启用")
        except Exception as e:
            print(f"\n⚠️  pgvector 扩展可能已存在：{e}")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 验证表已创建
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        table_count = result.scalar()
        print(f"\n✅ 测试数据库已初始化，共创建 {table_count} 张表")

    yield

    # 测试结束后清理所有数据（保留表结构）
    with engine.connect() as conn:
        # 使用事务回滚来清理
        transaction = conn.begin()
        try:
            # 删除所有表数据
            conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
            transaction.commit()
            print("\n✅ 测试数据已清理")
        except Exception:
            transaction.rollback()
            print("\n⚠️  数据清理跳过（表可能为空）")


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """为每个测试创建独立的数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # 回滚事务，清理测试数据
    try:
        transaction.rollback()
        session.close()
        connection.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """创建测试客户端，注入数据库会话"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session) -> "User":
    """创建测试用户，返回 User 对象 - 使用集中式测试用户管理系统"""
    from app.models.user import User
    from app.core.test_users import test_user_manager

    # 使用集中式测试用户管理系统获取或创建测试用户
    user_data = test_user_manager.get_or_create_test_user(db_session, "default")

    # 从数据库获取用户对象
    user = db_session.query(User).filter(User.id == user_data["id"]).first()

    if not user:
        # 如果用户不存在（不应该发生），回退到原始创建逻辑
        from app.services.auth_service import get_password_hash
        from datetime import datetime

        user_data_fallback = create_test_user_data()
        user = User(
            email=user_data_fallback["email"],
            username=user_data_fallback["username"],
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=user_data_fallback["is_active"],
            full_name=user_data_fallback["full_name"],
            created_at=datetime.utcnow(),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user, db_session) -> tuple:
    """创建已认证的测试客户端 - 使用集中式测试用户管理系统获取令牌"""
    from app.core.test_users import test_user_manager

    # 使用集中式测试用户管理系统获取令牌
    token = test_user_manager.get_test_user_token(db_session, "default")

    if not token:
        # 如果无法获取令牌，回退到原始创建逻辑
        from app.services.auth_service import create_access_token
        from datetime import timedelta

        access_token_expires = timedelta(minutes=30)
        token = create_access_token(
            data={
                "sub": str(test_user.id),
                "email": test_user.email,
                "user_id": test_user.id,
            },
            expires_delta=access_token_expires,
        )

    # 设置认证头
    headers = {"Authorization": f"Bearer {token}"}
    client.headers.update(headers)

    return client, headers, test_user
