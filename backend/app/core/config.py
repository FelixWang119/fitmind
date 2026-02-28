import secrets
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "Weight AI Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # API配置
    API_V1_STR: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置 (本地 PostgreSQL)
    DATABASE_URL: str = (
        "postgresql://weight_ai_user:weight_ai_password@127.0.0.1:5432/weight_ai_db"
    )

    # SQLite配置（用于本地测试）
    SQLITE_DATABASE_URL: str = "sqlite:///./backend/weight_management.db"

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = []

    # 主机配置
    ALLOWED_HOSTS: List[str] = ["*"]

    # AI服务配置
    QWEN_API_KEY: Optional[str] = None
    QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_URL: str = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
    QWEN_TEXT_MODEL: str = "qwen-turbo"  # 文本模型
    QWEN_VISION_MODEL: str = "qwen-vl-max"  # 视觉模型

    # Redis配置（用于缓存和会话）
    REDIS_URL: Optional[str] = None

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads/meal_photos"
    IMAGE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    IMAGE_COMPRESS_QUALITY: int = 70

    # 日志配置
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env file
    )


settings = Settings()
