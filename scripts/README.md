# 服务管理脚本

## 🚀 快速开始

```bash
cd /Users/felix/bmad

# 启动所有服务（前端 + 后端 + 数据库）
./scripts/services all start

# 停止所有服务
./scripts/services all stop

# 重启所有服务
./scripts/services all restart

# 查看所有服务状态
./scripts/services all status
```

## 📋 命令说明

### 启动服务

```bash
# 启动所有服务
./scripts/services all start

# 只启动前端
./scripts/services frontend start

# 只启动后端
./scripts/services backend start

# 只启动数据库
./scripts/services postgres start
```

### 停止服务

```bash
# 停止所有服务
./scripts/services all stop

# 只停止前端
./scripts/services frontend stop

# 只停止后端
./scripts/services backend stop

# 只停止数据库
./scripts/services postgres stop
```

### 重启服务

```bash
# 重启所有服务
./scripts/services all restart

# 只重启前端
./scripts/services frontend restart

# 只重启后端
./scripts/services backend restart

# 只重启数据库
./scripts/services postgres restart
```

### 查看状态

```bash
# 查看所有服务状态
./scripts/services all status
```

## 📊 服务信息

| 服务 | 端口 | 访问地址 | 日志文件 |
|------|------|----------|----------|
| **PostgreSQL** | 5432 | 127.0.0.1:5432 | /tmp/postgres.log |
| **后端 API** | 8000 | http://localhost:8000 | logs/backend.log |
| **前端** | 3000 | http://localhost:3000 | logs/frontend.log |

## 🔗 访问地址

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 💡 日常使用

```bash
# 早上启动工作
cd /Users/felix/bmad
./scripts/services all start

# 查看状态
./scripts/services all status

# 晚上停止服务
./scripts/services all stop
```

## 📁 文件结构

```
/Users/felix/bmad/
├── scripts/
│   └── services      # 主管理脚本
├── logs/             # 日志目录（自动创建）
├── frontend/         # 前端代码
└── backend/          # 后端代码
```

## 🛠️ 故障排查

### 查看所有服务状态

```bash
./scripts/services all status
```

### 查看日志

```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log

# 数据库日志
tail -f /tmp/postgres.log
```

### 手动检查端口

```bash
# 检查前端端口
lsof -i :3000

# 检查后端端口
lsof -i :8000

# 检查数据库端口
lsof -i :5432
```

### 清理卡住的进程

```bash
# 停止所有服务
./scripts/services all stop

# 如果还有残留，手动杀掉进程
pkill -f "uvicorn"
pkill -f "vite"
```

---

**创建时间**: 2026-02-26  
**更新时间**: 2026-02-26
