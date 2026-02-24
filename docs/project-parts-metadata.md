# 项目部分元数据

## 概述

此文档包含项目各部分的详细元数据，用于指导文档生成和项目分析。

## 后端部分 (backend)

### 基本信息
- **部分ID**: `backend`
- **项目类型ID**: `backend`
- **显示名称**: Python FastAPI Backend
- **根路径**: `/Users/felix/bmad/backend`
- **检测方法**: 关键文件模式匹配 (`requirements.txt`, `pyproject.toml`)

### 文档需求 (来自 documentation-requirements.csv)
| 需求类型 | 是否必需 | 说明 |
|---------|---------|------|
| API扫描 | ✅ 是 | 需要扫描API路由和端点 |
| 数据模型 | ✅ 是 | 需要扫描数据模型和数据库模式 |
| 状态管理 | ❌ 否 | 不需要状态管理文档 |
| UI组件 | ❌ 否 | 不需要UI组件文档 |
| 部署配置 | ✅ 是 | 需要扫描部署配置 |

### 扫描模式
- **关键目录**: `src/`, `api/`, `services/`, `models/`, `routes/`, `controllers/`, `middleware/`, `handlers/`, `repositories/`, `domain/`
- **集成扫描模式**: `*client.ts`, `*repository.ts`, `*service.ts`, `*connector*.ts`, `*adapter*.ts`
- **测试文件模式**: `*.test.ts`, `*.spec.ts`, `*_test.go`, `test_*.py`, `*Test.java`, `*_test.rs`
- **配置文件模式**: `.env*`, `config/*`, `*.config.*`, `application*.yml`, `application*.yaml`, `appsettings*.json`, `settings.py`
- **认证安全模式**: `*auth*.ts`, `*session*.ts`, `*authenticat*`, `*authorization*`, `middleware/auth*`, `guards/`, `*jwt*`, `*oauth*`
- **模式迁移模式**: `migrations/**`, `alembic/**`, `flyway/**`, `liquibase/**`, `prisma/**`, `*.prisma`, `*migration*.sql`, `*migration*.ts`, `db/migrate`
- **入口点模式**: `main.ts`, `index.ts`, `server.ts`, `app.ts`, `main.go`, `main.py`, `Program.cs`, `__init__.py`
- **共享代码模式**: `shared/**`, `common/**`, `utils/**`, `lib/**`, `core/**`, `@*/**`, `pkg/**`
- **异步事件模式**: `*event*.ts`, `*queue*.ts`, `*subscriber*.ts`, `*consumer*.ts`, `*producer*.ts`, `*worker*.ts`, `*handler*.ts`, `jobs/**`, `workers/**`
- **CI/CD模式**: `.github/workflows/**`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/**`, `azure-pipelines.yml`, `.drone.yml`
- **协议模式**: `*.proto`, `*.graphql`, `graphql/**`, `*.avro`, `*.thrift`, `openapi.*`, `swagger.*`, `schema/**`

## 前端部分 (frontend)

### 基本信息
- **部分ID**: `frontend`
- **项目类型ID**: `web`
- **显示名称**: React/TypeScript Frontend
- **根路径**: `/Users/felix/bmad/frontend`
- **检测方法**: 关键文件模式匹配 (`package.json`, `tsconfig.json`, `vite.config.ts`)

### 文档需求 (来自 documentation-requirements.csv)
| 需求类型 | 是否必需 | 说明 |
|---------|---------|------|
| API扫描 | ✅ 是 | 需要扫描API客户端和服务 |
| 数据模型 | ✅ 是 | 需要扫描数据模型和类型定义 |
| 状态管理 | ✅ 是 | 需要扫描状态管理实现 |
| UI组件 | ✅ 是 | 需要扫描UI组件库 |
| 部署配置 | ✅ 是 | 需要扫描部署配置 |

### 扫描模式
- **关键目录**: `src/`, `app/`, `pages/`, `components/`, `api/`, `lib/`, `styles/`, `public/`, `static/`
- **集成扫描模式**: `*client.ts`, `*service.ts`, `*api.ts`, `fetch*.ts`, `axios*.ts`, `*http*.ts`
- **测试文件模式**: `*.test.ts`, `*.spec.ts`, `*.test.tsx`, `*.spec.tsx`, `**/__tests__/**`, `**/*.test.*`, `**/*.spec.*`
- **配置文件模式**: `.env*`, `config/*`, `*.config.*`, `.config/`, `settings/`
- **认证安全模式**: `*auth*.ts`, `*session*.ts`, `middleware/auth*`, `*.guard.ts`, `*authenticat*`, `*permission*`, `guards/`
- **模式迁移模式**: `migrations/**`, `prisma/**`, `*.prisma`, `alembic/**`, `knex/**`, `*migration*.sql`, `*migration*.ts`
- **入口点模式**: `main.ts`, `index.ts`, `app.ts`, `server.ts`, `_app.tsx`, `_app.ts`, `layout.tsx`
- **共享代码模式**: `shared/**`, `common/**`, `utils/**`, `lib/**`, `helpers/**`, `@*/**`, `packages/**`
- **Monorepo工作区模式**: `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `workspace.json`, `rush.json`
- **异步事件模式**: `*event*.ts`, `*queue*.ts`, `*subscriber*.ts`, `*consumer*.ts`, `*producer*.ts`, `*worker*.ts`, `jobs/**`
- **CI/CD模式**: `.github/workflows/**`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/**`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, `.drone.yml`
- **资源模式**: `public/**`, `static/**`, `assets/**`, `images/**`, `media/**`
- **协议模式**: `*.proto`, `*.graphql`, `graphql/**`, `schema.graphql`, `*.avro`, `openapi.*`, `swagger.*`
- **本地化模式**: `i18n/**`, `locales/**`, `lang/**`, `translations/**`, `messages/**`, `*.po`, `*.pot`

## 用户特别关注点

基于用户需求，需要特别关注以下方面：

### 1. 千问API配置
- **普通对话模型**: 需要识别使用的模型名称和配置方式
- **图片识别模型**: 需要识别不同的模型使用方式和API密钥配置
- **API密钥管理**: 同一套API密钥在不同模型中的使用方式

### 2. 测试资源位置
- **测试图片目录**: `/Users/felix/bmad/backend/tests/mealimg`
- **资源管理**: 测试图片的组织方式和使用模式
- **测试数据**: 测试用户数据和测试用例的组织

### 3. 用户认证和测试用户固化
- **认证机制**: JWT令牌认证的实现方式
- **测试用户**: 避免每次API认证时重新注册用户的方案
- **用户固化**: 测试用户的持久化和管理方式

### 4. 前后端交互
- **API调用方式**: 前端的API客户端实现
- **状态管理**: 前端的状态管理方案（Redux、Context API等）
- **认证机制**: 前后端的认证流程和令牌管理

### 5. 数据库结构
- **数据模型**: 主要的数据库表和关系
- **迁移管理**: Alembic迁移的使用方式
- **ORM配置**: SQLAlchemy模型定义和配置