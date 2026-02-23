# 🏋️ 体重管理AI代理

一个专业的、AI驱动的体重管理系统，融合营养师和行为教练的专业知识，提供科学量化的健康管理方案。

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)](https://www.postgresql.org/)

## 📋 目录

- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [API文档](#-api文档)
- [开发指南](#-开发指南)
- [部署](#-部署)
- [贡献](#-贡献)

## ✨ 功能特性

### 🎯 核心功能

- **👤 用户管理** - JWT认证、用户配置、个人资料
- **💬 AI对话** - 基于QWen的智能对话系统
- **📊 健康追踪** - 体重、BMI、体脂率记录和趋势分析
- **🥗 营养管理** - BMR/TDEE计算、卡路里目标、宏量营养素建议
- **✅ 习惯养成** - 习惯创建、完成追踪、连续天数统计
- **💝 情感支持** - 情感状态跟踪、正念练习、压力管理
- **🎮 游戏化** - 徽章系统、积分奖励、等级提升、成就解锁
- **📈 科学分析** - 循证医学建议、统计报告、健康风险评估
- **👨‍⚕️ 专业融合** - 营养师+行为教练的双重专业视角

### 🚀 特色亮点

- **科学量化** - 基于循证医学的健康评估和建议
- **专业融合** - 自动识别用户需求，动态切换营养师/行为教练/综合顾问角色
- **情感智能** - 识别用户情感状态，提供个性化心理支持
- **游戏化激励** - 24种徽章、等级系统、连续记录、挑战任务
- **全栈Docker** - 一键启动完整的开发环境

## 🛠 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **路由**: React Router DOM
- **图表**: Chart.js
- **HTTP**: Axios
- **图标**: Lucide React

### 后端
- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **迁移**: Alembic
- **认证**: JWT (python-jose)
- **日志**: Structlog
- **测试**: Pytest

### AI集成
- **大模型**: 通义千问 (QWen)
- **框架**: LangChain (可选)

### 基础设施
- **容器**: Docker + Docker Compose
- **反向代理**: Nginx
- **包管理**: Poetry (Python), npm (Node.js)

## 🚀 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM (推荐)
- 10GB 磁盘空间

### 1. 克隆项目

```bash
git clone <repository-url>
cd weight-management-ai-agent
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置必要的环境变量
# 特别注意：修改 SECRET_KEY 和数据库密码
```

### 3. 启动开发环境

```bash
# 使用开发脚本（推荐）
chmod +x scripts/dev.sh
./scripts/dev.sh start

# 或者使用 Docker Compose 直接启动
docker-compose up -d
```

### 4. 访问应用

- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432

### 5. 初始化数据库

```bash
# 运行数据库迁移
./scripts/dev.sh migrate

# 创建管理员用户（可选）
./scripts/dev.sh create-admin
```

## 📁 项目结构

```
.
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由和端点
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── dashboard.py
│   │   │       │   ├── emotional_support.py
│   │   │       │   ├── gamification.py
│   │   │       │   ├── habit.py
│   │   │       │   ├── health.py
│   │   │       │   ├── nutrition.py
│   │   │       │   ├── professional_fusion.py
│   │   │       │   └── scientific_persona.py
│   │   │       └── api.py
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── cache.py
│   │   │   └── performance.py
│   │   ├── middleware/        # 中间件
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模型
│   │   └── services/          # 业务逻辑服务
│   ├── alembic/               # 数据库迁移
│   └── tests/                 # 测试文件
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/              # API客户端
│   │   ├── components/       # React组件
│   │   │   ├── layout/
│   │   │   └── ui/
│   │   ├── pages/            # 页面组件
│   │   ├── store/            # 状态管理
│   │   └── types/            # TypeScript类型
│   └── public/
│
├── scripts/                    # 开发脚本
│   ├── dev.sh
│   └── setup.sh
│
├── docker-compose.yml          # Docker编排
├── .env.example               # 环境变量模板
└── README.md                  # 本文件
```

## 📚 API文档

### 主要API端点

| 模块 | 端点 | 描述 |
|------|------|------|
| **认证** | `/api/v1/auth/login` | 用户登录 |
| | `/api/v1/auth/register` | 用户注册 |
| | `/api/v1/auth/me` | 获取当前用户 |
| **仪表板** | `/api/v1/dashboard/overview` | 获取仪表板数据 |
| | `/api/v1/dashboard/quick-stats` | 快速统计 |
| **健康** | `/api/v1/health/records` | 健康记录CRUD |
| **习惯** | `/api/v1/habits/` | 习惯管理 |
| | `/api/v1/habits/daily-checklist` | 每日清单 |
| **营养** | `/api/v1/nutrition/recommendations` | 营养建议 |
| | `/api/v1/nutrition/calorie-target` | 卡路里目标 |
| **情感** | `/api/v1/emotional-support/check-in` | 情感签到 |
| | `/api/v1/emotional-support/emotional-states` | 情感状态 |
| **游戏化** | `/api/v1/gamification/overview` | 游戏化概览 |
| | `/api/v1/gamification/badges` | 徽章列表 |
| **科学分析** | `/api/v1/scientific-persona/scientific-report` | 科学报告 |
| | `/api/v1/scientific-persona/bmi` | BMI计算 |

### 完整API文档

启动后端服务后，访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 💻 开发指南

### 开发环境

```bash
# 查看所有可用命令
./scripts/dev.sh help

# 常用命令
./scripts/dev.sh start      # 启动所有服务
./scripts/dev.sh stop       # 停止所有服务
./scripts/dev.sh restart    # 重启服务
./scripts/dev.sh logs       # 查看日志
./scripts/dev.sh migrate    # 运行数据库迁移
./scripts/dev.sh shell      # 进入后端容器
./scripts/dev.sh test       # 运行测试
./scripts/dev.sh lint       # 代码检查
```

### 前端开发

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

### 后端开发

```bash
cd backend

# 使用 Poetry 管理依赖
poetry install

# 激活虚拟环境
poetry shell

# 运行开发服务器
poetry run uvicorn app.main:app --reload

# 运行测试
poetry run pytest

# 代码格式化
poetry run black .
poetry run isort .
```

### 数据库迁移

```bash
# 创建新的迁移
./scripts/dev.sh makemigrations "添加新表"

# 应用迁移
./scripts/dev.sh migrate

# 回滚迁移
./scripts/dev.sh downgrade
```

## 🚀 部署

### 生产环境部署

```bash
# 1. 配置生产环境变量
cp .env.example .env
# 编辑 .env，设置生产环境配置

# 2. 使用生产配置启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. 运行数据库迁移
docker-compose exec backend alembic upgrade head
```

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | JWT密钥 | 必须修改 |
| `DATABASE_URL` | 数据库连接 | `postgresql://...` |
| `QWEN_API_KEY` | 通义千问API密钥 | 可选 |
| `REDIS_URL` | Redis连接 | 可选 |

## 🧪 测试

### 运行测试

```bash
# 后端测试
./scripts/dev.sh test

# 前端测试
cd frontend && npm run test

# E2E测试
cd frontend && npm run e2e
```

### 测试覆盖率

```bash
# 后端覆盖率
./scripts/dev.sh test --cov

# 前端覆盖率
cd frontend && npm run test:coverage
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- Python: 使用 Black 格式化，遵循 PEP 8
- TypeScript: 使用 ESLint 和 Prettier
- 提交信息: 遵循 [Conventional Commits](https://www.conventionalcommits.org/)

## 📝 使用手册

### 新用户入门

1. **注册账号** - 访问 `/register` 创建账号
2. **完善资料** - 设置身高、体重目标等基本信息
3. **创建习惯** - 添加想要养成的健康习惯
4. **开始追踪** - 每日记录体重、饮食、情感状态
5. **查看报告** - 定期查看科学分析报告

### 核心工作流

```
每日流程:
1. 记录体重 (早上起床后)
2. 完成习惯打卡
3. 记录饮食 (三餐)
4. 情感签到
5. 与AI助手对话获取建议

每周流程:
1. 查看周度总结报告
2. 调整下周目标
3. 领取每周奖励
```

## 🔧 故障排除

### 常见问题

**Q: 数据库连接失败**
```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重置数据库（会清空数据）
docker-compose down -v
docker-compose up -d db
```

**Q: 前端无法连接后端**
```bash
# 检查后端服务状态
./scripts/dev.sh status

# 确保环境变量配置正确
cat .env | grep API_URL
```

**Q: 数据库迁移失败**
```bash
# 删除迁移历史并重新开始
rm -rf backend/alembic/versions/*
./scripts/dev.sh makemigrations "init"
./scripts/dev.sh migrate
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [React](https://reactjs.org/) - 用于构建用户界面的JavaScript库
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [通义千问](https://tongyi.aliyun.com/) - 阿里云大语言模型

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: support@example.com

---

<p align="center">用 ❤️ 和 🥗 构建</p>