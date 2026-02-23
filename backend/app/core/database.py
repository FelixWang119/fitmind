from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# 创建数据库引擎
# SQLite 需要特殊配置以支持多线程测试环境
if "sqlite" in settings.DATABASE_URL:
    engine_args = {
        "url": settings.DATABASE_URL,
        "echo": settings.ENVIRONMENT == "development",
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,  # 使用静态池避免 SQLite 线程问题
        "pool_pre_ping": True,  # 启用连接健康检查
    }
else:
    engine_args = {
        "url": settings.DATABASE_URL,
        "echo": settings.ENVIRONMENT == "development",
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 30,
    }

engine = create_engine(**engine_args)

# 为SQLite添加now()函数支持
if "sqlite" in settings.DATABASE_URL:

    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        # 为SQLite添加datetime('now')函数作为now()的替代
        import sqlite3

        if isinstance(dbapi_connection, sqlite3.Connection):
            # 创建自定义的now()函数
            def sqlite_now():
                from datetime import datetime

                return datetime.now().isoformat()

            dbapi_connection.create_function("now", 0, sqlite_now)


# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖项

    使用示例：
    @app.get("/items/")
    def read_items(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库，创建所有表

    注意：在生产环境中应该使用Alembic迁移
    """
    Base.metadata.create_all(bind=engine)
