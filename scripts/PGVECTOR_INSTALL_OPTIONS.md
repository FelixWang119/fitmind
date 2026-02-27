# pgvector 安装方案

## 问题

- ❌ MacPorts 没有 pgvector 包
- ❌ Homebrew 编译需要 PostgreSQL 17
- ✅ 当前使用 PostgreSQL 16 (MacPorts)

---

## 方案 1: 从源码编译（推荐 ⭐）

最简单直接的方案，直接编译到您的 PostgreSQL 16。

### 执行脚本

```bash
cd /Users/felix/bmad
./scripts/install-pgvector-from-source.sh
```

### 或手动执行

```bash
# 1. 下载源码
cd /tmp
git clone --branch v0.8.1 --depth 1 https://github.com/pgvector/pgvector.git
cd pgvector

# 2. 编译
make

# 3. 安装（需要密码）
sudo make install

# 4. 启用扩展
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db \
  -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# 5. 验证
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db \
  -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

**优点：**
- ✅ 直接安装到您的 PostgreSQL 16
- ✅ 不需要升级数据库
- ✅ 过程透明可控

**缺点：**
- ⚠️ 需要编译（约 2-5 分钟）
- ⚠️ 需要 Xcode 命令行工具

---

## 方案 2: 尝试 Homebrew bottle

```bash
# 尝试强制使用预编译包
brew install pgvector --force-bottle --build-from-source
```

**可能失败**，因为需要 PostgreSQL 17 的库文件。

---

## 方案 3: 使用 Docker PostgreSQL（完全独立）

如果您不想折腾编译，可以使用 Docker 运行带 pgvector 的 PostgreSQL：

```bash
# 使用带 pgvector 的 PostgreSQL 镜像
docker run -d \
  --name weight_ai_postgres \
  -e POSTGRES_DB=weight_ai_db \
  -e POSTGRES_USER=weight_ai_user \
  -e POSTGRES_PASSWORD=weight_ai_password \
  -p 5433:5432 \
  -v weight_ai_pgdata:/var/lib/postgresql/data \
  pgvector/pgvector:16

# 然后更新 .env 中的 DATABASE_URL 端口为 5433
```

**优点：**
- ✅ 开箱即用
- ✅ 不干扰现有 PostgreSQL

**缺点：**
- ⚠️ 需要 Docker
- ⚠️ 数据在另一个数据库

---

## 🎯 推荐执行方案 1

```bash
cd /Users/felix/bmad
./scripts/install-pgvector-from-source.sh
```

这个脚本会：
1. ✅ 下载 pgvector 源码
2. ✅ 编译到您的 PostgreSQL 16
3. ✅ 安装扩展文件
4. ✅ 提供启用命令

---

## 📝 检查 Xcode 命令行工具

源码编译需要 Xcode 命令行工具：

```bash
# 检查是否安装
xcode-select --version

# 如果未安装，执行：
xcode-select --install
```

---

**创建时间**: 2026-02-26
