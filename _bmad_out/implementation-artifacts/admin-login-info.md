# 系统管理后台 - 登录信息

**创建日期：** 2026-02-25  
**状态：** 待部署

---

## 🚀 服务启动

### 1. 启动后端服务

由于当前使用 SQLite 开发，建议切换到 PostgreSQL 进行完整测试：

```bash
# 方案 A：使用 SQLite（功能受限）
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方案 B：使用 PostgreSQL（推荐）
# 1. 配置 .env 文件
DATABASE_URL=postgresql://user:password@localhost:5432/fitmind

# 2. 运行迁移
alembic upgrade head

# 3. 启动服务
uvicorn app.main:app --reload
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

**访问地址：**
- 前端：http://localhost:3000
- 管理后台：http://localhost:3000/admin
- API 文档：http://localhost:8000/docs

---

## 👤 管理员账号

### 测试账号

| 字段 | 值 |
|------|-----|
| **邮箱** | admin@fitmind.com |
| **密码** | admin123456 |
| **用户名** | admin |
| **角色** | 超级管理员 |

### 创建管理员（PostgreSQL）

```sql
INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
VALUES (
  'admin@fitmind.com',
  'admin',
  '$2b$12$KIQWPbvPJL6Vqk5W8RjGOO9xJ5zR5QJxO8xJ5zR5QJxO8xJ5zR5QJ',
  true,
  true
);
```

### 创建管理员（SQLite）

```python
# 运行脚本
cd backend
python scripts/create_admin_simple.py
```

---

## 📋 初始化系统配置

运行配置初始化脚本：

```python
from app.services.config_initializer import initialize_all_configs
from app.core.database import SessionLocal

db = SessionLocal()
initialize_all_configs(db)
db.close()
```

**初始化配置：**
- AI 提示词（3 个）
- 功能开关（6 个）
- 性能配置（3 个）
- 缓存配置（3 个）
- 邮件配置（2 个）
- 日志配置（2 个）
- 业务规则（4 个）

---

## 🎯 管理后台功能

### 配置管理

**访问：** `/admin`

**功能：**
- ✅ 查看所有系统配置
- ✅ 编辑配置值（JSON 格式）
- ✅ 查看变更历史
- ✅ 清除缓存

### API 测试

**获取所有配置：**
```bash
curl http://localhost:8000/api/v1/admin/configs
```

**获取 AI 提示词：**
```bash
curl http://localhost:8000/api/v1/admin/ai/nutritionist/prompt
```

**检查功能开关：**
```bash
curl http://localhost:8000/api/v1/admin/feature/ai_chat/enabled
```

**更新配置：**
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/configs/feature.ai_chat?config_value={\"enabled\":false}"
```

---

## 📊 已配置的功能开关

| 功能 Key | 名称 | 默认状态 |
|---------|------|---------|
| feature.ai_chat | AI 对话 | ✅ ON |
| feature.habit_tracking | 习惯打卡 | ✅ ON |
| feature.nutrition_tracking | 饮食记录 | ✅ ON |
| feature.exercise_tracking | 运动记录 | ✅ ON |
| feature.weight_tracking | 体重记录 | ✅ ON |
| feature.sleep_tracking | 睡眠记录 | ❌ OFF |

---

## 🔧 常见问题

### 1. 数据库迁移失败

**问题：** Multiple head revisions

**解决：**
```bash
cd backend
alembic merge heads -m "merge heads"
alembic upgrade head
```

### 2. JSONB 不支持（SQLite）

**问题：** SQLite 不支持 JSONB 类型

**解决：** 使用 PostgreSQL 或修改模型为 JSON 类型

### 3. 管理员账号不存在

**解决：** 运行创建脚本
```bash
python scripts/create_admin_simple.py
```

---

## 📝 下一步

1. **启动服务**
2. **创建管理员账号**
3. **初始化配置**
4. **访问管理后台**
5. **测试配置管理功能**

---

*文档日期：2026-02-25*
