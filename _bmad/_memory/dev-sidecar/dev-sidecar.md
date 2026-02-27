# Dev Agent Memory - 服务管理规范

## 🚨 CRITICAL RULE - 服务管理

### 规则：必须使用项目 scripts/services 脚本

> 当用户要求启动、停止或重启服务时，**必须**使用项目提供的 `scripts/services` 脚本，**禁止**使用自定义命令。

---

## 正确做法 ✅

```bash
# 使用项目脚本
cd /Users/felix/bmad

# 重启所有服务
./scripts/services all restart

# 只重启后端
./scripts/services backend restart

# 只重启前端
./scripts/services frontend start

# 查看状态
./scripts/services all status

# 停止所有服务
./scripts/services all stop
```

---

## 错误做法 ❌

```bash
# 禁止这样做
pkill -f uvicorn
nohup uvicorn app.main:app ... &
npm run dev &
python -m uvicorn ...
tail -f /tmp/backend.log
```

---

## 原因

1. **一致性** - 所有服务管理操作统一使用一个脚本
2. **可维护性** - 脚本集中管理，日志统一
3. **可靠性** - 经过测试的启动/停止流程
4. **日志统一** - 日志集中到 `/logs` 目录

---

## 脚本位置

- **路径**: `/Users/felix/bmad/scripts/services`
- **使用**: 在项目根目录执行 `./scripts/services <服务> <操作>`

---

## 服务列表

| 服务名 | 说明 |
|--------|------|
| `all` | 所有服务（前端+后端+数据库） |
| `frontend` | 前端服务 (端口 3000) |
| `backend` | 后端服务 (端口 8000) |
| `postgres` | PostgreSQL 数据库 |

---

## 操作列表

| 操作 | 说明 |
|------|------|
| `start` | 启动服务 |
| `stop` | 停止服务 |
| `restart` | 重启服务 |
| `status` | 查看状态 |

---

## 示例场景

### 场景 1: 用户说"重启服务"
```bash
./scripts/services all restart
```

### 场景 2: 用户说"重启后端"
```bash
./scripts/services backend restart
```

### 场景 3: 用户说"看看服务状态"
```bash
./scripts/services all status
```

---

**生效日期**: 2026-02-26  
**优先级**: CRITICAL - 必须遵守
