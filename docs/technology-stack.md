# 技术栈分析

## 概述

本项目采用现代全栈技术栈，包含独立的Python FastAPI后端和React/TypeScript前端。

## 后端技术栈 (Python FastAPI)

### 核心框架和库
| 类别 | 技术 | 版本 | 用途 | 关键发现 |
|------|------|------|------|----------|
| **Web框架** | FastAPI | ^0.109.0 | API开发框架 | 提供异步API支持，自动生成OpenAPI文档 |
| **服务器** | Uvicorn | ^0.24.0 | ASGI服务器 | 支持标准扩展，用于生产环境 |
| **数据库ORM** | SQLAlchemy | ^2.0.23 | 数据库操作 | 使用2.0版本，支持异步操作 |
| **数据库迁移** | Alembic | ^1.12.1 | 数据库迁移管理 | 集成到项目中，支持版本控制 |
| **数据库驱动** | psycopg2-binary | ^2.9.9 | PostgreSQL连接 | 生产环境使用PostgreSQL |
| **数据验证** | Pydantic | ^2.5.0 | 数据验证和序列化 | 使用v2版本，支持严格类型检查 |
| **配置管理** | Pydantic Settings | ^2.1.0 | 配置管理 | 支持环境变量和配置文件 |
| **认证安全** | python-jose | ^3.3.0 | JWT令牌处理 | 包含cryptography扩展 |
| **密码哈希** | passlib[bcrypt] | ^1.7.4 | 密码哈希 | 使用bcrypt算法 |
| **文件上传** | python-multipart | ^0.0.6 | 文件上传处理 | 支持multipart表单 |
| **HTTP客户端** | httpx | ^0.25.1 | 异步HTTP客户端 | 用于调用外部API（如千问API） |
| **缓存** | redis | ^5.0.1 | 缓存和会话存储 | 可选配置，支持缓存 |
| **环境变量** | python-dotenv | ^1.0.0 | 环境变量加载 | 从.env文件加载配置 |
| **日志** | structlog | ^23.2.0 | 结构化日志 | 提供结构化日志输出 |
| **监控** | prometheus-fastapi-instrumentator | ^6.1.0 | 监控指标 | 集成Prometheus监控 |

### 开发工具
| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **测试框架** | pytest | ^7.4.3 | 单元测试和集成测试 |
| **异步测试** | pytest-asyncio | ^0.21.1 | 异步测试支持 |
| **测试覆盖率** | pytest-cov | ^4.1.0 | 测试覆盖率报告 |
| **代码格式化** | black | ^23.11.0 | 代码自动格式化 |
| **导入排序** | isort | ^5.12.0 | 导入语句排序 |
| **代码检查** | flake8 | ^6.1.0 | 代码风格检查 |
| **类型检查** | mypy | ^1.7.0 | 静态类型检查 |
| **Git钩子** | pre-commit | ^3.5.0 | Git提交前检查 |
| **测试数据** | factory-boy | ^3.3.0 | 测试数据工厂 |
| **时间模拟** | freezegun | ^1.2.2 | 时间相关测试 |

### 架构模式
- **API设计**: RESTful API设计，版本控制 (`/api/v1/`)
- **认证方式**: JWT令牌认证，支持访问令牌和刷新令牌
- **数据库**: PostgreSQL（生产），SQLite（开发/测试）
- **缓存策略**: Redis可选，用于会话和缓存
- **错误处理**: 结构化错误响应，HTTP状态码规范
- **日志记录**: 结构化日志，支持上下文信息

## 前端技术栈 (React/TypeScript)

### 核心框架和库
| 类别 | 技术 | 版本 | 用途 | 关键发现 |
|------|------|------|------|----------|
| **UI框架** | React | ^18.2.0 | 用户界面开发 | 使用最新版本，支持并发特性 |
| **构建工具** | Vite | ^4.4.5 | 构建和开发服务器 | 快速构建，支持热重载 |
| **语言** | TypeScript | ^5.0.2 | 类型安全的JavaScript | 严格类型检查，提高代码质量 |
| **路由** | react-router-dom | ^6.20.0 | 客户端路由 | 支持嵌套路由和懒加载 |
| **状态管理** | zustand | ^4.4.7 | 状态管理 | 轻量级状态管理库 |
| **HTTP客户端** | axios | ^1.6.2 | HTTP请求 | 用于调用后端API |
| **样式框架** | Tailwind CSS | ^3.3.0 | 实用优先的CSS框架 | 快速UI开发，响应式设计 |
| **图标库** | lucide-react | ^0.309.0 | 图标组件 | 现代化图标集合 |
| **日期处理** | date-fns | ^2.30.0 | 日期格式化 | 轻量级日期处理库 |
| **图表** | chart.js + react-chartjs-2 | ^4.5.1 + ^5.3.1 | 数据可视化 | 图表展示，用于数据可视化 |
| **通知** | react-hot-toast | ^2.6.0 | 用户通知 | 轻量级toast通知 |
| **CSS工具** | clsx | ^2.0.0 | CSS类名组合 | 条件类名组合工具 |
| **PostCSS** | postcss + autoprefixer | ^8.4.32 + ^10.4.16 | CSS处理 | 自动添加浏览器前缀 |

### 开发工具
| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **测试框架** | Jest | ^29.6.2 | 单元测试 |
| **测试环境** | jest-environment-jsdom | ^29.6.2 | DOM测试环境 |
| **测试工具** | @testing-library/react | ^14.0.0 | React组件测试 |
| **测试工具** | @testing-library/jest-dom | ^6.1.4 | DOM断言扩展 |
| **测试工具** | @testing-library/user-event | ^14.5.1 | 用户事件模拟 |
| **E2E测试** | @playwright/test | ^1.38.0 | 端到端测试 |
| **代码检查** | ESLint | ^8.45.0 | 代码质量检查 |
| **TypeScript检查** | @typescript-eslint | ^6.0.0 | TypeScript代码检查 |
| **React插件** | @vitejs/plugin-react | ^4.0.3 | Vite React插件 |
| **CSS模拟** | identity-obj-proxy | ^3.0.0 | CSS模块测试模拟 |
| **测试报告** | jest-html-reporter | ^4.3.0 | HTML测试报告 |
| **JUnit报告** | jest-junit | ^16.0.0 | JUnit格式测试报告 |
| **TypeScript测试** | ts-jest | ^29.1.1 | TypeScript Jest转换 |

### 架构模式
- **组件架构**: 函数组件 + Hooks，支持自定义Hooks
- **状态管理**: zustand轻量级状态管理，支持持久化
- **API集成**: axios客户端，统一错误处理和拦截器
- **样式方案**: Tailwind CSS实用优先，支持暗色模式
- **路由策略**: 客户端路由，支持懒加载和代码分割
- **构建优化**: Vite构建，支持tree-shaking和代码分割

## 关键集成点

### 1. 千问API集成
- **配置位置**: `app/core/config.py` 中的 `QWEN_*` 设置
- **API密钥**: `QWEN_API_KEY` 环境变量
- **API端点**: `QWEN_API_URL` 和 `QWEN_API_BASE`
- **默认模型**: `QWEN_MODEL = "qwen-plus"`
- **实现位置**: `app/utils/food_image_analyzer.py` 和 `app/services/ai_service.py`

### 2. 测试资源管理
- **测试图片目录**: `/Users/felix/bmad/backend/tests/mealimg/`
- **包含文件**: 5个测试图片文件（lunch.jpg, meal3.png, meal4.jpg等）
- **用途**: 食品图像分析测试
- **大小**: 总共约2.3MB的测试图片

### 3. 用户认证系统
- **认证方式**: JWT令牌认证
- **实现位置**: `app/api/v1/endpoints/auth.py`
- **服务层**: `app/services/auth_service.py`
- **数据模型**: `app/models/user.py`
- **测试覆盖**: 多个认证测试文件

### 4. 数据库配置
- **生产数据库**: PostgreSQL (`DATABASE_URL`)
- **开发数据库**: SQLite (`SQLITE_DATABASE_URL`)
- **迁移工具**: Alembic (`alembic/` 目录)
- **ORM模型**: SQLAlchemy 2.0

### 5. 前后端交互
- **API基础URL**: `http://localhost:8000/api/v1` (前端配置)
- **认证头**: `Authorization: Bearer <token>`
- **错误处理**: 统一错误响应格式
- **数据格式**: JSON请求和响应

## 环境配置

### 后端环境变量
```python
# app/core/config.py 中的关键配置
PROJECT_NAME = "Weight AI Backend"
API_V1_STR = "/api/v1"
SECRET_KEY = secrets.token_urlsafe(32)  # JWT密钥
DATABASE_URL = "postgresql://..."  # PostgreSQL连接
SQLITE_DATABASE_URL = "sqlite:///./weight_management.db"  # SQLite连接
QWEN_API_KEY = None  # 千问API密钥
QWEN_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen-plus"
```

### 前端环境变量
```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api/v1
```

## 开发工作流

### 后端开发
1. **环境设置**: `poetry install` 安装依赖
2. **数据库迁移**: `alembic upgrade head` 应用迁移
3. **运行开发服务器**: `uvicorn app.main:app --reload`
4. **运行测试**: `pytest` 或 `pytest --cov`
5. **代码检查**: `black .`, `isort .`, `flake8`, `mypy`

### 前端开发
1. **环境设置**: `npm install` 安装依赖
2. **运行开发服务器**: `npm run dev`
3. **运行测试**: `npm test` 或 `npm run test:coverage`
4. **构建生产版本**: `npm run build`
5. **代码检查**: `npm run lint`

## 部署配置

### Docker配置
- **后端Dockerfile**: `backend/Dockerfile`
- **前端Dockerfile**: `frontend/Dockerfile`
- **Docker Compose**: `docker-compose.yml` 和 `docker-compose.override.yml`
- **Nginx配置**: `frontend/nginx.conf` 和 `nginx-security.conf`

### 监控和日志
- **结构化日志**: structlog提供结构化日志输出
- **性能监控**: Prometheus指标集成
- **错误追踪**: 结构化错误响应和日志记录