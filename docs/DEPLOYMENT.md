# 部署指南

本文档介绍如何将体重管理 AI 助手部署到不同环境。

---

## 目录

1. [环境要求](#环境要求)
2. [开发环境部署](#开发环境部署)
3. [生产环境部署](#生产环境部署)
4. [环境配置](#环境配置)
5. [数据库管理](#数据库管理)
6. [监控与日志](#监控与日志)
7. [备份与恢复](#备份与恢复)
8. [故障排查](#故障排查)

---

## 环境要求

### 基础要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存**: 最少 2GB RAM（推荐 4GB）
- **磁盘**: 最少 10GB 可用空间
- **网络**: 可访问互联网（下载镜像和AI服务）

### 可选工具

- **Git**: 用于版本控制
- **Make**: 用于运行快捷命令
- **Nginx**: 生产环境反向代理
- **PostgreSQL客户端**: 用于数据库管理

---

## 开发环境部署

### 快速开始

最简单的方式是使用 Docker Compose：

```bash
# 1. 克隆代码（如果在本地已有时跳过）
git clone <repository-url>
cd weight-management-ai

# 2. 复制环境变量文件
cp .env.example .env

# 3. 编辑 .env 文件，填入必要的配置
# 特别是 QWEN_API_KEY
nano .env

# 4. 启动所有服务
docker-compose up -d

# 5. 等待服务启动（约30秒）
sleep 30

# 6. 查看日志确认启动成功
docker-compose logs -f backend

# 7. 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 分步部署

#### 1. 准备环境

```bash
# 创建项目目录
mkdir -p ~/projects/weight-management-ai
cd ~/projects/weight-management-ai

# 确保 Docker 已安装并运行
docker --version
docker-compose --version
```

#### 2. 配置环境变量

```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件
# 必填项：
# - QWEN_API_KEY: 你的通义千问 API Key
# - SECRET_KEY: JWT密钥，建议随机生成
# - POSTGRES_PASSWORD: 数据库密码

cat > .env << EOF
# AI Configuration
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo

# Security
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=weight_management
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/weight_management

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Backend
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF
```

#### 3. 构建镜像

```bash
# 构建所有镜像
docker-compose build

# 或者分别构建
docker-compose build backend
docker-compose build frontend
```

#### 4. 初始化数据库

```bash
# 启动数据库
docker-compose up -d db

# 等待数据库就绪（约10秒）
sleep 10

# 运行迁移
docker-compose run --rm backend alembic upgrade head

# 创建初始数据（可选）
docker-compose run --rm backend python scripts/init_data.py
```

#### 5. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 6. 验证部署

```bash
# 测试后端API
curl http://localhost:8000/health

# 预期输出：{"status": "healthy"}

# 测试API文档
curl http://localhost:8000/docs

# 应该返回 Swagger UI HTML
```

---

## 生产环境部署

### 架构建议

生产环境建议使用以下架构：

```
用户 → Cloudflare (CDN/SSL) → Nginx (反向代理) → Docker 服务
                                          ↓
                                    ┌─────┴─────┐
                                    ↓           ↓
                                Frontend    Backend
                                (React)     (FastAPI)
                                    ↓           ↓
                                静态文件    PostgreSQL
```

### 部署步骤

#### 1. 准备服务器

```bash
# 更新系统（Ubuntu示例）
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建应用目录
sudo mkdir -p /opt/weight-management-ai
sudo chown $USER:$USER /opt/weight-management-ai
```

#### 2. 上传代码

```bash
cd /opt/weight-management-ai

# 方法1：通过 Git
git clone https://github.com/yourusername/weight-management-ai.git .

# 方法2：通过 SCP
# 本地执行：scp -r . user@server:/opt/weight-management-ai/

# 方法3：通过 GitHub Actions 自动部署（推荐）
```

#### 3. 配置生产环境

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - app_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - backend_logs:/app/logs
    networks:
      - app_network
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_BASE_URL=/api/v1
    networks:
      - app_network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - frontend_dist:/usr/share/nginx/html
    networks:
      - app_network
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  backend_logs:
  frontend_dist:

networks:
  app_network:
    driver: bridge
```

#### 4. 配置 Nginx

创建 `nginx/nginx.prod.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    # 前端静态文件
    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            expires 1d;
        }

        # API 代理
        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 86400;
        }

        # WebSocket 支持（用于流式AI响应）
        location /ws/ {
            proxy_pass http://backend:8000/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }
    }
}
```

#### 5. 获取 SSL 证书

```bash
# 使用 Let's Encrypt
cd /opt/weight-management-ai

# 安装 Certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 创建证书目录
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /opt/weight-management-ai/nginx/ssl/" | sudo crontab -
```

#### 6. 启动生产环境

```bash
cd /opt/weight-management-ai

# 拉取最新代码
git pull origin main

# 构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 运行数据库迁移
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 检查状态
docker-compose -f docker-compose.prod.yml ps
```

---

## 环境配置

### 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|-------|------|--------|------|
| `QWEN_API_KEY` | 是 | - | 通义千问 API Key |
| `QWEN_BASE_URL` | 否 | dashscope | API 基础 URL |
| `QWEN_MODEL` | 否 | qwen-turbo | AI 模型名称 |
| `SECRET_KEY` | 是 | - | JWT 加密密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | 1440 | Token 过期时间（分钟） |
| `DATABASE_URL` | 是 | - | PostgreSQL 连接字符串 |
| `POSTGRES_USER` | 是 | postgres | 数据库用户名 |
| `POSTGRES_PASSWORD` | 是 | - | 数据库密码 |
| `POSTGRES_DB` | 否 | weight_management | 数据库名 |
| `VITE_API_BASE_URL` | 是 | - | 前端 API 地址 |
| `BACKEND_CORS_ORIGINS` | 否 | - | 允许的跨域来源 |

### 生成安全密钥

```bash
# JWT Secret Key
openssl rand -hex 32

# 数据库密码
openssl rand -hex 16
```

### 配置 AI 服务

如果使用 QWen（通义千问）：

1. 访问 https://dashscope.aliyun.com/
2. 注册并获取 API Key
3. 在 .env 中设置 `QWEN_API_KEY`

如果使用其他兼容 OpenAI 格式的服务：

```bash
QWEN_API_KEY=your_api_key
QWEN_BASE_URL=https://api.your-provider.com/v1
QWEN_MODEL=gpt-3.5-turbo
```

---

## 数据库管理

### 备份数据库

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="weight_management_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump \
  -U postgres \
  -d weight_management \
  > $BACKUP_DIR/$FILENAME

gzip $BACKUP_DIR/$FILENAME

echo "Backup created: $BACKUP_DIR/$FILENAME.gz"
EOF

chmod +x backup.sh

# 手动执行
./backup.sh

# 设置自动备份（每天凌晨2点）
crontab -l > mycron
echo "0 2 * * * cd /opt/weight-management-ai && ./backup.sh" >> mycron
crontab mycron
rm mycron
```

### 恢复数据库

```bash
# 停止应用
docker-compose down

# 恢复备份
docker-compose up -d db
sleep 10

gunzip -c backups/weight_management_backup_20240120_120000.sql.gz | \
  docker-compose exec -T db psql -U postgres -d weight_management

# 重启应用
docker-compose up -d
```

### 数据库迁移

```bash
# 查看迁移历史
docker-compose run --rm backend alembic history

# 升级到最新版本
docker-compose run --rm backend alembic upgrade head

# 降级到特定版本
docker-compose run --rm backend alembic downgrade <revision>

# 创建新迁移（修改模型后）
docker-compose run --rm backend alembic revision --autogenerate -m "描述"
```

---

## 监控与日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 实时跟踪日志
docker-compose logs -f backend

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 日志轮转

创建 `backend/logging.conf`：

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 数据库健康检查
docker-compose exec db pg_isready -U postgres

# 完整系统检查
./scripts/health_check.sh
```

---

## 备份与恢复

### 完整备份

```bash
#!/bin/bash
# backup-full.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/$DATE"
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T db pg_dump -U postgres weight_management > $BACKUP_DIR/database.sql

# 备份环境配置
cp .env $BACKUP_DIR/

# 备份上传的文件（如果有）
cp -r uploads $BACKUP_DIR/ 2>/dev/null || true

# 打包
tar -czf /opt/backups/backup_$DATE.tar.gz -C /opt/backups $DATE

# 清理临时文件
rm -rf $BACKUP_DIR

# 保留最近30天的备份
find /opt/backups -name "backup_*.tar.gz" -mtime +30 -delete

echo "Full backup created: /opt/backups/backup_$DATE.tar.gz"
```

### 完整恢复

```bash
#!/bin/bash
# restore-full.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 停止服务
docker-compose down

# 解压备份
tar -xzf $BACKUP_FILE -C /tmp/
BACKUP_DIR=$(ls /tmp/ | grep -E '^[0-9]{8}_[0-9]{6}$' | head -1)

# 恢复数据库
docker-compose up -d db
sleep 10
cat /tmp/$BACKUP_DIR/database.sql | docker-compose exec -T db psql -U postgres

# 恢复环境配置
cp /tmp/$BACKUP_DIR/.env .env

# 恢复上传的文件
if [ -d "/tmp/$BACKUP_DIR/uploads" ]; then
    cp -r /tmp/$BACKUP_DIR/uploads .
fi

# 清理临时文件
rm -rf /tmp/$BACKUP_DIR

# 启动服务
docker-compose up -d

echo "Restore completed from: $BACKUP_FILE"
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
sudo lsof -i :8000
sudo lsof -i :5173
sudo lsof -i :5432

# 杀死占用端口的进程
sudo kill -9 <PID>

# 或者修改端口映射
docker-compose down
# 编辑 docker-compose.yml 修改端口
docker-compose up -d
```

#### 2. 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 检查数据库健康状态
docker-compose exec db pg_isready -U postgres

# 重置数据库（会丢失数据！）
docker-compose down -v
docker-compose up -d db
sleep 10
docker-compose run --rm backend alembic upgrade head
```

#### 3. AI 服务无响应

```bash
# 检查 API Key 是否正确
docker-compose logs backend | grep -i "api\|qwen\|error"

# 测试 AI 服务连接
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $QWEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

#### 4. 前端无法连接后端

```bash
# 检查 CORS 配置
grep BACKEND_CORS_ORIGINS .env

# 检查前端 API URL
grep VITE_API_BASE_URL frontend/.env

# 检查后端是否运行
curl http://localhost:8000/health

# 检查网络连接
docker network ls
docker network inspect weight-management-ai_default
```

#### 5. 性能问题

```bash
# 查看资源使用
docker stats

# 查看慢查询（在数据库中）
docker-compose exec db psql -U postgres -d weight_management -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# 重启服务
docker-compose restart backend
```

### 调试模式

```bash
# 启用后端调试
docker-compose exec backend python -m pdb -c continue app/main.py

# 查看详细日志
docker-compose logs -f backend | grep -i "error\|exception\|traceback"

# 进入容器调试
docker-compose exec backend /bin/sh
docker-compose exec db /bin/sh
```

### 获取帮助

如果问题仍无法解决：

1. 查看详细日志：`docker-compose logs --tail=500 <service>`
2. 检查 GitHub Issues：https://github.com/yourusername/weight-management-ai/issues
3. 联系开发团队

---

## 更新部署

### 滚动更新

```bash
cd /opt/weight-management-ai

# 1. 拉取最新代码
git pull origin main

# 2. 备份数据库
./backup.sh

# 3. 构建新镜像
docker-compose -f docker-compose.prod.yml build

# 4. 运行数据库迁移
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 5. 滚动更新（零停机）
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend

# 6. 更新前端
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# 7. 验证
curl http://localhost:8000/health
```

### 回滚

```bash
# 回滚代码
git reset --hard <previous-commit>

# 重新部署
docker-compose -f docker-compose.prod.yml up -d --build

# 或者回滚数据库迁移
docker-compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1
```

---

**文档结束**

如有问题，请参考 [README.md](../README.md) 或联系开发团队。
