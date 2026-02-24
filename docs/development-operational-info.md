# 开发与运维信息

本文档提供体重管理AI代理项目的开发环境设置、运维流程、部署指南和故障排除信息。

## 目录

1. [开发环境设置](#开发环境设置)
2. [项目依赖管理](#项目依赖管理)
3. [开发工作流](#开发工作流)
4. [测试策略](#测试策略)
5. [部署流程](#部署流程)
6. [监控与日志](#监控与日志)
7. [数据库管理](#数据库管理)
8. [故障排除](#故障排除)
9. [性能优化](#性能优化)

## 开发环境设置

### 环境要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存**: 最少 2GB RAM（推荐 4GB）
- **磁盘空间**: 最少 10GB
- **网络**: 可访问互联网（用于下载镜像和AI服务）

### 快速开始

```bash
# 1. 克隆项目（如果尚未克隆）
git clone <repository-url>
cd weight-management-ai

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置（特别是 QWEN_API_KEY）

# 3. 使用开发脚本启动
chmod +x scripts/dev.sh
./scripts/dev.sh start

# 4. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 手动设置

#### 后端开发环境

```bash
cd backend

# 使用 Poetry 管理依赖
poetry install

# 激活虚拟环境
poetry shell

# 运行开发服务器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
poetry run pytest tests/ -v

# 代码格式化
poetry run black .
poetry run isort .
```

#### 前端开发环境

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test

# 代码检查
npm run lint
```

## 项目依赖管理

### 后端依赖 (Python)

**主要依赖:**
- **FastAPI**: Web框架
- **SQLAlchemy**: ORM
- **Alembic**: 数据库迁移
- **Pydantic**: 数据验证
- **python-jose**: JWT认证
- **httpx**: HTTP客户端（用于AI API调用）
- **structlog**: 结构化日志

**开发依赖:**
- **pytest**: 测试框架
- **black/isort**: 代码格式化
- **mypy**: 类型检查
- **pre-commit**: Git钩子

**依赖管理文件:**
- `backend/pyproject.toml` - Poetry配置文件
- `backend/poetry.lock` - 锁定依赖版本
- `backend/requirements-test.txt` - 测试依赖

### 前端依赖 (TypeScript/React)

**主要依赖:**
- **React 18**: UI框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Tailwind CSS**: 样式框架
- **Zustand**: 状态管理
- **React Router**: 路由
- **Axios**: HTTP客户端
- **Chart.js**: 数据可视化

**开发依赖:**
- **Jest**: 测试框架
- **ESLint**: 代码检查
- **Playwright**: E2E测试

**依赖管理文件:**
- `frontend/package.json` - npm配置文件
- `frontend/package-lock.json` - 锁定依赖版本

## 开发工作流

### 开发脚本

项目提供 `scripts/dev.sh` 脚本简化开发操作：

```bash
# 查看所有可用命令
./scripts/dev.sh help

# 常用命令
./scripts/dev.sh start      # 启动所有服务
./scripts/dev.sh stop       # 停止所有服务
./scripts/dev.sh restart    # 重启服务
./scripts/dev.sh logs       # 查看日志
./scripts/dev.sh status     # 查看服务状态
./scripts/dev.sh test       # 运行测试
./scripts/dev.sh build      # 构建所有服务

# 数据库操作
./scripts/dev.sh db init    # 初始化数据库
./scripts/dev.sh db migrate # 运行数据库迁移
./scripts/dev.sh db reset   # 重置数据库（删除所有数据）
```

### Docker Compose 配置

项目使用 Docker Compose 管理多服务环境：

**主要服务:**
- `postgres`: PostgreSQL 15 数据库
- `backend`: FastAPI 后端服务
- `frontend`: React 前端服务
- `pgadmin`: PostgreSQL 管理界面（可选）

**配置文件:**
- `docker-compose.yml` - 主配置文件
- `docker-compose.override.yml` - 开发环境覆盖配置
- `backend/Dockerfile` - 后端Dockerfile
- `frontend/Dockerfile` - 前端Dockerfile

### 环境变量配置

**关键环境变量:**

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `QWEN_API_KEY` | 是 | - | 通义千问API密钥 |
| `SECRET_KEY` | 是 | - | JWT加密密钥 |
| `DATABASE_URL` | 是 | - | 数据库连接字符串 |
| `ENVIRONMENT` | 否 | development | 环境类型 |
| `DEBUG` | 否 | true | 调试模式 |
| `VITE_API_URL` | 是 | - | 前端API地址 |

**生成安全密钥:**
```bash
# JWT Secret Key
openssl rand -hex 32

# 数据库密码
openssl rand -hex 16
```

## 测试策略

### 测试类型

1. **单元测试**: 测试单个函数或类
2. **集成测试**: 测试模块间交互
3. **API测试**: 测试REST API端点
4. **E2E测试**: 测试完整用户流程

### 后端测试

**测试框架:** pytest
**测试目录:** `backend/tests/`

```bash
# 运行所有测试
cd backend
poetry run pytest tests/ -v

# 运行特定测试文件
poetry run pytest tests/test_auth.py -v

# 运行测试并生成覆盖率报告
poetry run pytest tests/ --cov=app --cov-report=html

# 运行带标记的测试
poetry run pytest tests/ -m "not slow"
```

**测试标记:**
- `@pytest.mark.slow`: 慢速测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.api`: API测试

### 前端测试

**测试框架:** Jest + React Testing Library
**测试目录:** `frontend/src/__tests__/`

```bash
# 运行所有测试
cd frontend
npm run test

# 监视模式
npm run test:watch

# 覆盖率报告
npm run test:coverage

# E2E测试
npm run e2e
```

### 测试资源

**测试图像目录:** `backend/tests/mealimg/`
- 包含5个测试图像文件
- 总大小: ~2.3MB
- 用于图像识别测试

**测试用户:**
- 避免在每次测试中重新注册用户
- 使用固定的测试用户凭证
- 在测试前进行用户固化

## 部署流程

### 开发环境部署

```bash
# 使用Docker Compose
docker-compose up -d

# 或使用开发脚本
./scripts/dev.sh start
```

### 生产环境部署

**推荐架构:**
```
用户 → Cloudflare (CDN/SSL) → Nginx → Docker服务
                                     ↓
                               ┌─────┴─────┐
                               ↓           ↓
                           Frontend    Backend
                           (React)     (FastAPI)
                               ↓           ↓
                           静态文件    PostgreSQL
```

**部署步骤:**

1. **准备服务器**
   ```bash
   # 安装Docker和Docker Compose
   curl -fsSL https://get.docker.com | sh
   ```

2. **配置生产环境**
   ```bash
   # 创建生产环境配置文件
   cp .env.example .env.production
   # 编辑配置文件，设置生产环境值
   ```

3. **使用生产Docker Compose配置**
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
   ```

4. **部署命令**
   ```bash
   # 构建并启动
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

   # 运行数据库迁移
   docker-compose exec backend alembic upgrade head
   ```

### 持续部署

**GitHub Actions 示例:**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/weight-management-ai
            git pull origin main
            docker-compose -f docker-compose.prod.yml up -d --build
```

## 监控与日志

### 日志配置

**后端日志 (structlog):**
```python
# 配置示例
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)
```

**日志级别:**
- `DEBUG`: 详细调试信息
- `INFO`: 常规操作信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

**查看日志:**
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend

# 实时跟踪日志
docker-compose logs -f backend

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 健康检查

**后端健康端点:** `GET /health`
```bash
# 测试健康检查
curl http://localhost:8000/health
# 预期响应: {"status": "healthy"}
```

**数据库健康检查:**
```bash
# 检查数据库连接
docker-compose exec postgres pg_isready -U weight_ai_user
```

**容器健康检查配置:**
```yaml
# docker-compose.yml 示例
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 性能监控

**资源监控:**
```bash
# 查看容器资源使用
docker stats

# 查看特定容器资源
docker stats weight_ai_backend

# 查看容器详细信息
docker inspect weight_ai_backend
```

**数据库性能监控:**
```sql
-- 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- 查看连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 数据库管理

### 数据库迁移

**使用 Alembic:**
```bash
# 创建新迁移
cd backend
poetry run alembic revision --autogenerate -m "描述变更"

# 应用迁移
poetry run alembic upgrade head

# 回滚迁移
poetry run alembic downgrade -1

# 查看迁移历史
poetry run alembic history
```

**Docker环境迁移:**
```bash
# 在Docker容器中运行迁移
docker-compose exec backend alembic upgrade head

# 或使用开发脚本
./scripts/dev.sh db migrate
```

### 数据库备份

**备份脚本示例:**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="weight_management_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump \
  -U weight_ai_user \
  -d weight_ai_db \
  > $BACKUP_DIR/$FILENAME

gzip $BACKUP_DIR/$FILENAME

echo "备份创建: $BACKUP_DIR/$FILENAME.gz"
```

**自动备份 (cron):**
```bash
# 每天凌晨2点备份
0 2 * * * cd /opt/weight-management-ai && ./backup.sh
```

### 数据库恢复

```bash
# 停止应用
docker-compose down

# 恢复备份
docker-compose up -d postgres
sleep 10

gunzip -c backups/weight_management_backup_20240120_120000.sql.gz | \
  docker-compose exec -T postgres psql -U weight_ai_user -d weight_ai_db

# 重启应用
docker-compose up -d
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
sudo lsof -i :8000  # 后端端口
sudo lsof -i :3000  # 前端端口
sudo lsof -i :5432  # 数据库端口

# 杀死占用端口的进程
sudo kill -9 <PID>

# 或修改端口映射
# 编辑 docker-compose.yml 修改端口
```

#### 2. 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 检查数据库健康状态
docker-compose exec postgres pg_isready -U weight_ai_user

# 重置数据库（会丢失数据！）
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose exec backend alembic upgrade head
```

#### 3. AI服务无响应

```bash
# 检查API密钥是否正确
docker-compose logs backend | grep -i "api\|qwen\|error"

# 测试AI服务连接
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
# 检查CORS配置
grep CORS_ORIGINS .env

# 检查前端API URL
grep VITE_API_URL frontend/.env

# 检查后端是否运行
curl http://localhost:8000/health

# 检查网络连接
docker network ls
docker network inspect weight_ai_network
```

#### 5. 性能问题

```bash
# 查看资源使用
docker stats

# 查看慢查询
docker-compose exec postgres psql -U weight_ai_user -d weight_ai_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

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
docker-compose exec postgres /bin/sh
```

## 性能优化

### 后端优化

1. **数据库连接池**
   ```python
   # 配置连接池
   SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/db"
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_recycle=3600,
   )
   ```

2. **查询优化**
   - 使用索引
   - 避免N+1查询
   - 使用selectinload进行关联加载

3. **缓存策略**
   ```python
   # Redis缓存示例
   import redis
   from functools import wraps
   
   redis_client = redis.Redis.from_url(REDIS_URL)
   
   def cache_response(ttl=300):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               cache_key = f"{func.__name__}:{args}:{kwargs}"
               cached = redis_client.get(cache_key)
               if cached:
                   return json.loads(cached)
               result = await func(*args, **kwargs)
               redis_client.setex(cache_key, ttl, json.dumps(result))
               return result
           return wrapper
       return decorator
   ```

### 前端优化

1. **代码分割**
   ```javascript
   // 动态导入组件
   const Dashboard = React.lazy(() => import('./pages/Dashboard'));
   
   // 使用Suspense
   <Suspense fallback={<LoadingSpinner />}>
     <Dashboard />
   </Suspense>
   ```

2. **图片优化**
   - 使用WebP格式
   - 实现懒加载
   - 使用CDN

3. **状态管理优化**
   - 使用Zustand选择器避免不必要的重渲染
   - 实现状态持久化

### 基础设施优化

1. **CDN配置**
   - 静态资源使用CDN
   - 启用Gzip压缩
   - 配置缓存策略

2. **负载均衡**
   - 使用Nginx作为反向代理
   - 配置多个后端实例
   - 实现健康检查

3. **监控告警**
   - 设置资源使用告警
   - 监控API响应时间
   - 跟踪错误率

---

## 附录

### 开发命令速查表

| 命令 | 说明 |
|------|------|
| `./scripts/dev.sh start` | 启动所有服务 |
| `./scripts/dev.sh stop` | 停止所有服务 |
| `./scripts/dev.sh logs` | 查看服务日志 |
| `./scripts/dev.sh test` | 运行所有测试 |
| `docker-compose up -d` | Docker启动服务 |
| `docker-compose down` | Docker停止服务 |
| `docker-compose logs -f` | 实时查看日志 |
| `poetry run pytest` | 运行后端测试 |
| `npm run test` | 运行前端测试 |

### 环境变量速查表

| 变量 | 开发环境值 | 生产环境值 |
|------|------------|------------|
| `ENVIRONMENT` | `development` | `production` |
| `DEBUG` | `true` | `false` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `CORS_ORIGINS` | `*` | 特定域名 |

### 联系支持

- **GitHub Issues**: [项目问题跟踪](https://github.com/yourusername/weight-management-ai/issues)
- **文档**: [项目文档目录](/docs/)
- **紧急联系**: support@weightai.com

---

**文档版本:** 1.0.0  
**最后更新:** 2024-01-20  
**维护者:** 开发团队