# 项目结构分析

## 项目概览

**项目类型**: 多部分项目 (Multi-part)
**根目录**: `/Users/felix/bmad`
**组成部分**: 2个独立部分

## 检测到的部分

### 1. 后端部分 (Backend)
- **ID**: `backend`
- **项目类型**: `backend` (Python FastAPI后端)
- **根路径**: `/Users/felix/bmad/backend`
- **技术栈**: Python, FastAPI, SQLAlchemy, Alembic
- **关键文件**: `pyproject.toml`, `requirements-test.txt`, `alembic.ini`
- **文档需求**:
  - ✅ 需要API扫描
  - ✅ 需要数据模型文档
  - ❌ 不需要状态管理文档
  - ❌ 不需要UI组件文档
  - ✅ 需要部署配置文档

### 2. 前端部分 (Frontend)
- **ID**: `frontend`
- **项目类型**: `web` (React/TypeScript前端)
- **根路径**: `/Users/felix/bmad/frontend`
- **技术栈**: TypeScript, React, Vite, Tailwind CSS
- **关键文件**: `package.json`, `tsconfig.json`, `vite.config.ts`
- **文档需求**:
  - ✅ 需要API扫描
  - ✅ 需要数据模型文档
  - ✅ 需要状态管理文档
  - ✅ 需要UI组件文档
  - ✅ 需要部署配置文档

## 目录结构

```
bmad/                              # 项目根目录
├── backend/                       # Python FastAPI后端
│   ├── app/                       # 应用代码
│   ├── tests/                     # 测试文件
│   ├── alembic/                   # 数据库迁移
│   ├── pyproject.toml             # Python依赖配置
│   └── requirements-test.txt      # 测试依赖
├── frontend/                      # React/TypeScript前端
│   ├── src/                       # 源代码
│   ├── package.json               # Node.js依赖配置
│   ├── tsconfig.json              # TypeScript配置
│   └── vite.config.ts             # 构建工具配置
├── docs/                          # 项目文档
├── scripts/                       # 工具脚本
└── tests/                         # 集成测试
```

## 架构模式

这是一个**客户端-服务器架构**，包含：
- **后端API服务**: 提供RESTful API接口
- **前端Web应用**: 用户界面和交互逻辑
- **独立部署**: 前后端可独立部署和扩展

## 集成点

前后端通过以下方式集成：
1. **REST API调用**: 前端通过HTTP请求调用后端API
2. **认证机制**: JWT令牌认证
3. **数据同步**: 实时或轮询方式同步数据

## 关键关注点

基于用户需求，需要特别关注：
1. **千问API配置**: 普通对话与图片识别的不同模型使用方式
2. **测试资源管理**: `/Users/felix/bmad/backend/tests/mealimg` 目录的测试图片资源
3. **用户认证**: 测试用户固化方案，避免每次API认证时重新注册用户
4. **前后端交互**: API调用方式、状态管理、认证机制