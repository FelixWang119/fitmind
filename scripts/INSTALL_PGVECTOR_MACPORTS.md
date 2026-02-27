# 使用 MacPorts 安装 pgvector

## 🚀 安装步骤

### 1. 安装 pgvector（需要密码）

在终端执行以下命令：

```bash
sudo port install postgresql16-pgvector
```

**输入您的 macOS 密码**（密码不会显示）

### 2. 启用扩展

安装完成后，执行：

```bash
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db << 'SQLEOF'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SQLEOF
```

### 3. 验证安装

```bash
# 检查扩展是否启用
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "SELECT extname, extversion FROM pg_extension WHERE extname='vector';"
```

应该输出：
```
 extname | extversion 
---------+------------
 vector  | 0.8.1
```

### 4. 创建记忆表

```bash
cd /Users/felix/bmad/backend
alembic upgrade head
```

### 5. 验证记忆表

```bash
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "\dt | grep memory"
```

---

## 📝 一行命令完成

如果您想一次性完成所有操作：

```bash
# 1. 安装 pgvector
sudo port install postgresql16-pgvector

# 2. 启用扩展
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# 3. 验证
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

---

## ✅ 完成后

所有记忆索引功能将正常工作：
- ✅ 向量相似度搜索
- ✅ 长期记忆存储
- ✅ 语义检索
- ✅ 记忆提取和索引

---

## 🛠️ 故障排查

### 如果 MacPorts 安装失败

```bash
# 更新 MacPorts
sudo port selfupdate
sudo port update outdated

# 重试安装
sudo port install postgresql16-pgvector
```

### 如果扩展创建失败

```bash
# 检查 PostgreSQL 日志
tail -f /tmp/postgres.log

# 手动查找 pgvector 扩展文件
find /opt/local -name "vector*" -type f 2>/dev/null
```

---

**创建时间**: 2026-02-26
