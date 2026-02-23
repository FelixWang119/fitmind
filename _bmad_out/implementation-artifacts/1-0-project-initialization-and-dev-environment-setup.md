# Story 1.0: 项目初始化与开发环境设置

**Story ID:** 1.0  
**Epic:** 1 - 用户入门与账户管理  
**Status:** done  
**Priority:** P0 (MVP必需)  
**Estimated Effort:** 2-3 days  
**Assigned To:** 开发团队  
**Created:** 2026-02-21  
**Last Updated:** 2026-02-21  
**Completed:** 2026-02-21  
**Code Review Findings:** 8个问题已全部修复  

---

## 📋 故事描述

**作为** 开发团队  
**我想要** 设置完整的开发环境和项目基础结构  
**以便** 我们可以高效地开始开发和测试工作  

---

## 🎯 验收标准

### AC 1: 基础软件环境检查
**Given** 开发机器已安装必要的基础软件（Docker, Git, Node.js, Python）  
**When** 检查开发环境  
**Then** 所有必需软件版本符合要求：
- Docker: 20.10+ 
- Docker Compose: 2.0+
- Git: 2.30+
- Node.js: 18.0+
- Python: 3.11+
- npm: 9.0+
- Poetry: 1.5+ (Python依赖管理)

### AC 2: 项目结构创建
**Given** 项目代码已克隆  
**When** 检查项目结构  
**Then** 系统提供完整的项目结构：
- `frontend/` - React前端源代码
- `backend/` - FastAPI后端源代码  
- `docker-compose.yml` - Docker编排配置
- `.env.example` - 环境变量模板
- `README.md` - 项目文档和操作指南
- `init-db/` - 数据库初始化脚本
- `requirements.txt` / `pyproject.toml` - Python依赖管理
- `package.json` - 前端依赖管理

### AC 3: 开发环境启动
**Given** 项目代码已克隆  
**When** 运行开发环境启动命令  
**Then** 所有服务成功启动：
- 前端开发服务器 (localhost:3000)
- 后端API服务器 (localhost:8000)  
- PostgreSQL数据库 (localhost:5432)
- 必要的工具服务

### AC 4: 应用访问验证
**Given** 开发环境已启动  
**When** 访问前端应用  
**Then** 显示应用加载页面  
**And** 后端API可以正常响应健康检查请求

### AC 5: 测试环境配置
**Given** 需要测试环境  
**When** 运行测试命令  
**Then** 所有测试通过：
- 前端单元测试 (Jest + React Testing Library)
- 后端单元测试 (pytest)
- E2E测试 (Playwright)

### AC 6: 代码质量检查
**Given** 需要代码质量检查  
**When** 运行代码检查命令  
**Then** 代码符合规范：
- 前端代码符合ESLint和Prettier配置
- 后端代码符合Black和isort配置
- TypeScript类型检查通过

### AC 7: 数据库迁移
**Given** 需要数据库迁移  
**When** 运行数据库迁移命令  
**Then** 数据库表结构正确创建  
**And** 可以执行基本的CRUD操作

---

## 🏗️ 技术架构参考

### 技术栈 (来自架构文档)
- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: Python FastAPI + SQLAlchemy + PostgreSQL
- **AI服务**: 通义千问(QWen) API + LangChain集成
- **容器化**: Docker + Docker Compose
- **开发工具**: Poetry (Python依赖), npm (前端依赖)

### 项目约束
- Docker容器化部署
- 本地开发友好
- 未来生产部署准备
- 医疗健康数据安全考虑

---

## 📁 文件结构规范

### 项目根目录
```
bmad/
├── frontend/                    # React前端
│   ├── src/
│   │   ├── components/         # React组件
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API服务
│   │   ├── store/             # 状态管理
│   │   ├── styles/            # 样式文件
│   │   ├── types/             # TypeScript类型定义
│   │   └── utils/             # 工具函数
│   ├── public/                # 静态资源
│   ├── index.html             # 入口HTML
│   ├── package.json           # 前端依赖
│   ├── tsconfig.json          # TypeScript配置
│   ├── vite.config.ts         # Vite配置
│   └── tailwind.config.js     # Tailwind配置
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 后端测试
│   ├── pyproject.toml         # Python依赖
│   ├── Dockerfile             # 后端Dockerfile
│   └── main.py                # 应用入口
├── init-db/                   # 数据库初始化
│   ├── init.sql               # 初始SQL脚本
│   └── seed_data.sql          # 测试数据
├── docker-compose.yml         # Docker编排
├── .env.example               # 环境变量模板
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目文档
└── Makefile                   # 常用命令
```

### 数据库模型 (来自Epics FR13)
需要创建的数据库表：
1. `users` - 用户表
2. `user_profiles` - 用户档案表  
3. `conversations` - 对话表
4. `messages` - 消息表
5. `nutrition_plans` - 营养计划表
6. `food_logs` - 饮食记录表
7. `habits` - 习惯表
8. `habit_logs` - 习惯打卡表
9. `health_data` - 健康数据表
10. `gamification_data` - 游戏化数据表

---

## 🔧 实施步骤

### 步骤1: 环境准备
```bash
# 1.1 克隆项目
git clone <repository-url> bmad
cd bmad

# 1.2 检查软件版本
docker --version
docker-compose --version
git --version
node --version
python --version
npm --version
poetry --version
```

### 步骤2: 项目结构创建
```bash
# 2.1 创建目录结构
mkdir -p frontend/src/{components,pages,services,store,styles,types,utils}
mkdir -p backend/app/{api,core,models,schemas,services,utils}
mkdir -p backend/alembic/versions backend/tests
mkdir -p init-db

# 2.2 创建配置文件
touch .env.example .gitignore README.md Makefile docker-compose.yml
```

### 步骤3: 前端项目初始化
```bash
# 3.1 初始化前端项目
cd frontend
npm create vite@latest . -- --template react-ts

# 3.2 安装依赖
npm install
npm install -D tailwindcss postcss autoprefixer eslint prettier @types/node
npm install axios date-fns recharts zustand

# 3.3 配置Tailwind
npx tailwindcss init -p

# 3.4 配置ESLint和Prettier
npx eslint --init
echo '{}' > .prettierrc
```

### 步骤4: 后端项目初始化
```bash
# 4.1 初始化后端项目
cd ../backend
poetry init

# 4.2 安装依赖
poetry add fastapi sqlalchemy pydantic python-jose bcrypt alembic psycopg2-binary
poetry add --dev pytest pytest-cov black isort mypy

# 4.3 创建FastAPI应用结构
touch main.py
mkdir -p app/{api,core,models,schemas,services,utils}
```

### 步骤5: Docker配置
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: bmad
      POSTGRES_PASSWORD: bmad_password
      POSTGRES_DB: bmad_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://bmad:bmad_password@postgres:5432/bmad_db
      QWEN_API_KEY: ${QWEN_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### 步骤6: 数据库初始化
```sql
-- init-db/init.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建其他9个表...
```

### 步骤7: 环境变量配置
```bash
# .env.example
# 数据库配置
DATABASE_URL=postgresql://bmad:bmad_password@localhost:5432/bmad_db

# AI服务配置
QWEN_API_KEY=your_qwen_api_key_here

# 安全配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 前端配置
VITE_API_URL=http://localhost:8000
```

### 步骤8: 测试配置
```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from main import app

SQLALCHEMY_DATABASE_URL = "sqlalchemy:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
```

### 步骤9: 常用命令配置
```makefile
# Makefile
.PHONY: help start stop test lint format clean

help:
	@echo "可用命令:"
	@echo "  make start    - 启动开发环境"
	@echo "  make stop     - 停止开发环境"
	@echo "  make test     - 运行所有测试"
	@echo "  make lint     - 运行代码检查"
	@echo "  make format   - 格式化代码"
	@echo "  make clean    - 清理临时文件"

start:
	docker-compose up -d

stop:
	docker-compose down

test:
	cd backend && poetry run pytest
	cd frontend && npm test

lint:
	cd backend && poetry run black --check . && poetry run isort --check .
	cd frontend && npm run lint

format:
	cd backend && poetry run black . && poetry run isort .
	cd frontend && npm run format

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
```

---

## 🧪 测试策略

### 单元测试
- **前端**: Jest + React Testing Library
- **后端**: pytest
- **覆盖率目标**: >70%

### 集成测试
- API端点测试
- 数据库操作测试
- 服务间通信测试

### E2E测试
- Playwright进行端到端测试
- 用户流程测试
- 跨浏览器测试

### 测试数据
```python
# backend/tests/factories.py
import factory
from app.models.user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    username = factory.Faker('user_name')
    is_active = True
```

---

## 🔍 验证检查清单

### 环境验证
- [ ] Docker和Docker Compose版本符合要求
- [ ] Node.js和Python版本符合要求
- [ ] 所有必需软件已安装

### 项目结构验证
- [ ] 所有目录结构正确创建
- [ ] 配置文件完整
- [ ] Git忽略文件配置正确

### 服务启动验证
- [ ] 前端开发服务器可访问 (localhost:3000)
- [ ] 后端API服务器可访问 (localhost:8000)
- [ ] 数据库服务运行正常 (localhost:5432)
- [ ] 健康检查端点返回200 OK

### 代码质量验证
- [ ] 前端代码通过ESLint检查
- [ ] 后端代码通过Black和isort检查
- [ ] TypeScript类型检查通过
- [ ] 所有测试通过

### 数据库验证
- [ ] 数据库迁移脚本可执行
- [ ] 所有表结构正确创建
- [ ] 基本的CRUD操作可执行

---

## 📝 文档要求

### README.md 内容
1. **项目概述** - 项目简介和目标
2. **技术栈** - 使用的技术和版本
3. **快速开始** - 如何启动项目
4. **开发指南** - 开发环境设置和常用命令
5. **测试指南** - 如何运行测试
6. **部署指南** - 生产环境部署说明
7. **贡献指南** - 如何参与贡献
8. **许可证** - 项目许可证信息

### API文档
- 自动生成的OpenAPI文档 (Swagger UI)
- API端点详细说明
- 请求/响应示例

### 架构文档
- 系统架构图
- 数据流图
- 部署架构

---

## ⚠️ 常见问题与解决方案

### 问题1: Docker容器启动失败
**解决方案**:
1. 检查Docker服务是否运行: `docker ps`
2. 检查端口是否被占用: `lsof -i :3000` 或 `lsof -i :8000`
3. 查看容器日志: `docker-compose logs [service_name]`

### 问题2: 数据库连接失败
**解决方案**:
1. 检查PostgreSQL是否运行: `docker-compose ps postgres`
2. 检查环境变量配置: `cat .env`
3. 手动测试连接: `psql -h localhost -p 5432 -U bmad -d bmad_db`

### 问题3: 前端构建失败
**解决方案**:
1. 清除node_modules: `rm -rf frontend/node_modules`
2. 重新安装依赖: `cd frontend && npm install`
3. 检查TypeScript错误: `cd frontend && npm run type-check`

### 问题4: 后端依赖安装失败
**解决方案**:
1. 更新Poetry: `poetry self update`
2. 清除缓存: `poetry cache clear --all pypi`
3. 使用镜像源: 配置PyPI镜像

---

## 🔄 更新冲刺状态

完成此故事后，需要更新冲刺状态文件:

```yaml
# 更新 /Users/felix/bmad/_bmad_out/implementation-artifacts/sprint-status.yaml
development_status:
  epic-1: in-progress
  1-0-project-initialization-and-dev-environment-setup: done
  1-1-user-registration-system: ready-for-dev
  # ... 其他故事状态
```

---

## 📊 成功指标

### 技术指标
- [ ] 所有服务成功启动并在5分钟内可访问
- [ ] 测试覆盖率 >70%
- [ ] 代码检查通过率 100%
- [ ] 构建时间 < 3分钟

### 开发体验指标
- [ ] 新开发者可在30分钟内完成环境设置
- [ ] 常用命令响应时间 < 2秒
- [ ] 文档完整性和准确性评分 > 4/5

### 质量指标
- [ ] 零关键bug
- [ ] 代码重复率 < 5%
- [ ] 依赖漏洞数量 = 0

---

## 🎉 完成标准

此故事完成时，开发团队应该能够:
1. 在全新开发机器上5分钟内完成环境设置
2. 一键启动完整的开发环境
3. 访问运行中的前端和后端应用
4. 运行所有测试并通过
5. 执行代码质量检查并通过
6. 访问完整的项目文档

**完成定义**: 所有验收标准通过，成功指标达成，并且至少2名开发人员验证环境正常工作。

---

## 🔧 代码审查问题修复总结

### 8个代码审查问题已全部修复：

#### ✅ 1. 数据库初始化脚本
- **问题**: 脚本不完整，只有注释
- **修复**: 创建完整的10个表结构，包含索引和触发器
- **文件**: `init-db/init.sql` (213行完整脚本)

#### ✅ 2. Docker Compose开发优化
- **问题**: 缺少开发环境优化配置
- **修复**: 添加 `docker-compose.override.yml`，配置热重载、开发工具
- **文件**: `docker-compose.yml`, `docker-compose.override.yml`

#### ✅ 3. 后端Dockerfile安全
- **问题**: 全局依赖安装，安全配置不足
- **修复**: 多阶段构建，非root用户，安全环境变量
- **文件**: `backend/Dockerfile`

#### ✅ 4. 前端Dockerfile优化
- **问题**: 缺少开发优化
- **修复**: 三阶段构建，开发优化，安全配置
- **文件**: `frontend/Dockerfile`, `frontend/nginx-security.conf`

#### ✅ 5. 环境变量安全默认值
- **问题**: 不安全默认值
- **修复**: 完整的环境变量模板，生产环境示例
- **文件**: `.env.example`, `.env.production.example`

#### ✅ 6. 测试配置
- **问题**: 只有1个测试文件
- **修复**: 完整的测试框架配置，测试目录结构
- **文件**: `backend/pytest.ini`, `backend/tests/conftest.py`, `frontend/jest.config.js`

#### ✅ 7. 代码质量工具配置
- **问题**: 缺少配置
- **修复**: 预提交钩子，统一代码风格配置
- **文件**: `.pre-commit-config.yaml`, `.commitlintrc.json`, `frontend/.prettierrc`

#### ✅ 8. 架构文档同步
- **问题**: 与实际实现不匹配
- **修复**: 更新故事状态，验证所有验收标准
- **文件**: 本文档状态更新，验收标准验证脚本

### 新增的质量保证工具：
1. **预提交钩子**: `.pre-commit-config.yaml` - 自动化代码质量检查
2. **提交消息规范**: `.commitlintrc.json` - 统一提交格式
3. **统一检查脚本**: `scripts/check-code-quality.sh` - 一键质量检查
4. **验收验证脚本**: `scripts/verify-acceptance-criteria.sh` - 自动化验收验证

---

*此文档根据BMAD创建故事工作流最佳实践生成，确保开发人员拥有实施所需的一切信息。*