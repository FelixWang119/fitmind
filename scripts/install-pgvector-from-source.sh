#!/bin/bash
# 从源码安装 pgvector 到 PostgreSQL 16

echo "=================================================="
echo "🔧 从源码安装 pgvector"
echo "=================================================="
echo ""

# 配置
PG_CONFIG="/opt/local/lib/postgresql16/bin/pg_config"
PGVECTOR_VERSION="0.8.1"

# 检查 pg_config
if [ ! -f "$PG_CONFIG" ]; then
    echo "❌ 找不到 pg_config: $PG_CONFIG"
    exit 1
fi

echo "✅ 找到 pg_config: $PG_CONFIG"
echo ""

# 下载 pgvector 源码
echo "📥 下载 pgvector v$PGVECTOR_VERSION..."
cd /tmp
rm -rf pgvector
git clone --branch v$PGVECTOR_VERSION --depth 1 https://github.com/pgvector/pgvector.git

if [ ! -d "/tmp/pgvector" ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "✅ 下载完成"
echo ""

# 编译
echo "🔨 编译 pgvector..."
cd /tmp/pgvector
make

if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi

echo "✅ 编译完成"
echo ""

# 安装（需要 sudo）
echo "📦 安装 pgvector..."
echo "需要管理员密码..."
sudo make install

if [ $? -ne 0 ]; then
    echo "❌ 安装失败"
    exit 1
fi

echo "✅ 安装完成"
echo ""

# 验证安装
echo "🔍 验证安装..."
echo "查找安装的扩展文件..."
find /opt/local -name "vector*" -type f 2>/dev/null | head -10

echo ""
echo "=================================================="
echo "✅ pgvector 安装完成！"
echo "=================================================="
echo ""
echo "现在需要在数据库中启用扩展："
echo ""
echo "  PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db << 'SQLEOF'"
echo "  CREATE EXTENSION IF NOT EXISTS vector;"
echo "  CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
echo "  SQLEOF"
echo ""
