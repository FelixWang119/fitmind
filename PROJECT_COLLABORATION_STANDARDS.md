# 项目协作规范

**版本:** 1.0  
**创建日期:** 2026-02-26  
**目的:** 确保所有协作 Agent 使用统一的操作规范

---

## 🚀 服务管理规范

### 核心原则

> **所有服务管理操作必须使用项目提供的 `scripts/services` 脚本，禁止自定义脚本启动/停止服务。**

### 原因

1. ✅ **一致性** - 统一的服务管理方式
2. ✅ **可维护性** - 脚本集中管理，易于更新
3. ✅ **可靠性** - 经过测试的服务管理流程
4. ✅ **日志统一** - 日志集中到 `/logs` 目录

### 正确做法

```bash
# ✅ 使用项目脚本
./scripts/services all restart
./scripts/services backend restart
./scripts/services frontend start
```

### 错误做法

```bash
# ❌ 禁止这样做
pkill -f uvicorn
nohup uvicorn app.main:app ... &
npm run dev &
```

### 可用命令

| 命令 | 说明 |
|------|------|
| `./scripts/services all start` | 启动所有服务 |
| `./scripts/services all stop` | 停止所有服务 |
| `./scripts/services all restart` | 重启所有服务 |
| `./scripts/services all status` | 查看所有服务状态 |
| `./scripts/services frontend start` | 启动前端 |
| `./scripts/services backend start` | 启动后端 |
| `./scripts/services postgres start` | 启动数据库 |

---

## 📝 Agent 协作规范

### 当用户要求重启服务时

**Agent 应该：**
1. ✅ 使用 `./scripts/services all restart` 或指定服务
2. ✅ 检查服务状态确认启动成功
3. ✅ 告知用户访问地址

**Agent 不应该：**
1. ❌ 写自定义的启动/停止脚本
2. ❌ 使用 `pkill` / `nohup` 等原始命令
3. ❌ 假设服务端口和日志路径

### 当需要查看服务日志时

```bash
# ✅ 使用项目脚本查看日志
tail -f logs/backend.log
tail -f logs/frontend.log

# ❌ 不要这样做
tail -f /tmp/backend.log  # 错误路径
```

### 当需要排查服务问题时

1. ✅ 使用 `./scripts/services all status` 查看状态
2. ✅ 检查 `logs/` 目录下的日志文件
3. ✅ 使用项目文档 `/docs/DEPLOYMENT.md` 查找解决方案

---

## 📚 相关文档

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - 部署指南
- [scripts/services](./services) - 服务管理脚本

---

**维护声明:**  
此规范适用于所有参与本项目的 AI Agent 和开发者。任何例外需要经过项目负责人批准。

**更新记录:**
- 2026-02-26: 初始版本
