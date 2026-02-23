# 开发阶段
FROM python:3.11-slim AS development

# 设置安全环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装系统依赖（最小化安装）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装指定版本的Poetry（避免最新版本的不稳定性）
RUN pip install --no-cache-dir poetry==1.8.3

# 配置Poetry（不使用虚拟环境以简化Docker部署）
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装依赖（开发环境包含所有依赖）
RUN poetry install --no-interaction --no-ansi --no-root

# 复制源代码
COPY . .

# 创建非root用户（增强安全性）
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app

USER appuser

# 开发命令（启用热重载）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 生产阶段
FROM python:3.11-alpine AS production

# 设置安全环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装最小化系统依赖
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev \
    && apk add --no-cache postgresql-client libpq \
    && pip install --no-cache-dir poetry==1.8.3 \
    && apk del .build-deps

# 配置Poetry
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装仅生产依赖（排除开发依赖）
RUN poetry install --no-interaction --no-ansi --no-root --only main

# 复制源代码
COPY . .

# 创建非root用户（Alpine Linux方式）
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app

USER appuser

# 生产命令（禁用调试和热重载）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]