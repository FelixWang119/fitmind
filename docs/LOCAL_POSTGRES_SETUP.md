# 🐘 本地 PostgreSQL 安装和使用指南

## 📋 概述

本指南帮助您在本地 macOS 系统上安装和配置 PostgreSQL，替代 Docker 容器方案。

---

## 🚀 快速开始

### 方式一：一键安装脚本（推荐）

```bash
cd /Users/felix/bmad
./scripts/setup-local-postgres.sh
```

脚本会自动完成：
1. ✅ 安装 PostgreSQL 15
2. ✅ 启动服务
3. ✅ 创建数据库和用户
4. ✅ 安装 pgvector 扩展
5. ✅ 更新项目配置
6. ✅ 运行 Alembic 迁移

### 方式二：手动安装

#### 1. 安装 PostgreSQL

```bash
brew install postgresql@15
```

#### 2. 启动服务

```bash
brew services start postgresql@15
```

#### 3. 创建数据库和用户

```bash
# 创建数据库
psql -d postgres -c "CREATE DATABASE weight_ai_db;"

# 创建用户
psql -d postgres -c "CREATE USER weight_ai_user WITH PASSWORD 'weight_ai_password';"

# 授权
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE weight_ai_db TO weight_ai_user;"
```

#### 4. 安装 pgvector 扩展

```bash
brew install pgvector
```

然后在数据库中启用：

```bash
psql -d weight_ai_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d weight_ai_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

#### 5. 更新环境配置

编辑 `.env` 和 `backend/.env`：

```bash
DATABASE_URL=postgresql://weight_ai_user:weight_ai_password@localhost:5432/weight_ai_db
```

#### 6. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

---

## 📊 数据库连接信息

| 配置项 | 值 |
|--------|-----|
| **Host** | `localhost` (或 `127.0.0.1`) |
| **Port** | `5432` |
| **Database** | `weight_ai_db` |
| **User** | `weight_ai_user` |
| **Password** | `weight_ai_password` |
| **数据目录** | `/Users/felix/pgsql_data` |

### 连接字符串

```bash
# 标准连接
postgresql://weight_ai_user:weight_ai_password@127.0.0.1:5432/weight_ai_db

# 环境变量 (.env)
DATABASE_URL=postgresql://weight_ai_user:weight_ai_password@127.0.0.1:5432/weight_ai_db
```
| **User** | `weight_ai_user` |
| **Password** | `weight_ai_password` |
| **连接字符串** | `postgresql://weight_ai_user:weight_ai_password@localhost:5432/weight_ai_db` |

---

## 🔧 常用命令

### 服务管理

```bash
# 启动 PostgreSQL
brew services start postgresql@15

# 停止 PostgreSQL
brew services stop postgresql@15

# 重启 PostgreSQL
brew services restart postgresql@15

# 查看服务状态
brew services list
```

### 数据库操作

```bash
# 连接到数据库
psql -d weight_ai_db

# 使用指定用户连接
psql -U weight_ai_user -d weight_ai_db

# 查看所有数据库
psql -l

# 查看表
psql -d weight_ai_db -c "\dt"

# 查看扩展
psql -d weight_ai_db -c "SELECT * FROM pg_extension;"
```

### 备份和恢复

```bash
# 备份数据库
pg_dump -U weight_ai_user weight_ai_db > backup.sql

# 恢复数据库
psql -U weight_ai_user weight_ai_db < backup.sql

# 备份为自定义格式
pg_dump -U weight_ai_user -Fc weight_ai_db > backup.dump

# 恢复自定义格式
pg_restore -U weight_ai_user -d weight_ai_db backup.dump
```

---

## 🔍 验证安装

### 检查 PostgreSQL 版本

```bash
psql --version
```

### 检查服务状态

```bash
brew services list | grep postgresql
```

### 测试连接

```bash
psql -h localhost -U weight_ai_user -d weight_ai_db -c "SELECT version();"
```

### 检查 pgvector

```bash
psql -d weight_ai_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

---

## 🛠️ 故障排查

### PostgreSQL 无法启动

```bash
# 查看日志
brew services info postgresql@15

# 查看 PostgreSQL 日志
ls ~/Library/Logs/homebrew/postgresql@15/

# 强制重启
brew services stop postgresql@15
brew services start postgresql@15
```

### 连接被拒绝

```bash
# 检查 PostgreSQL 是否监听正确端口
lsof -i :5432

# 检查 pg_hba.conf 配置
cat /usr/local/etc/postgresql@15/pg_hba.conf

# 确保有本地连接条目
# local   all             all                                     trust
# host    all             all             127.0.0.1/32            trust
```

### 用户权限问题

```bash
# 重置用户密码
psql -d postgres -c "ALTER USER weight_ai_user WITH PASSWORD 'weight_ai_password';"

# 重新授权
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE weight_ai_db TO weight_ai_user;"
```

### pgvector 未安装

```bash
# 检查是否安装
brew list | grep pgvector

# 安装
brew install pgvector

# 在数据库中启用
psql -d weight_ai_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 数据目录权限问题

```bash
# 修复权限
sudo chown -R $(whoami) /usr/local/var/postgresql@15
```

---

## 📝 从 SQLite 迁移数据

如果已有 SQLite 数据，可以运行迁移脚本：

```bash
# 确保 PostgreSQL 已配置好
python scripts/migrate_sqlite_to_postgres.py
```

---

## 🎯 下一步

1. ✅ 启动后端服务
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. ✅ 访问 API 文档
   ```
   http://localhost:8000/docs
   ```

3. ✅ 测试向量搜索功能
   ```bash
   # 运行测试
   pytest tests/api/test_semantic_search.py -v
   ```

---

## 💡 提示

- **开发环境**：本地 PostgreSQL 更适合日常开发调试
- **生产环境**：建议使用 Docker 或云数据库服务
- **性能优化**：可以调整 `postgresql.conf` 配置优化性能
- **数据安全**：定期备份重要数据

---

## 🔗 相关资源

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Homebrew PostgreSQL](https://formulae.brew.sh/formula/postgresql@15)

---

**最后更新**: 2026-02-26
