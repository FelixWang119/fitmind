#!/bin/bash
# 记忆索引配置脚本 - 安装 pgvector 并创建记忆表

echo "=================================================="
echo "🧠 PostgreSQL 记忆索引配置"
echo "=================================================="
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DB_HOST="127.0.0.1"
DB_NAME="weight_ai_db"
DB_USER="weight_ai_user"
DB_PASS="weight_ai_password"

# ==================== 步骤 1: 安装 pgvector ====================
echo -e "${YELLOW}📦 步骤 1: 安装 pgvector...${NC}"
echo ""

if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1 FROM pg_extension WHERE extname='vector'" &>/dev/null; then
    echo -e "${GREEN}✅ pgvector 已经安装${NC}"
else
    echo "尝试使用 Homebrew 安装 pgvector..."
    echo "命令：brew install pgvector"
    echo ""
    read -p "是否手动执行安装？(然后按回车继续) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install pgvector
    else
        echo -e "${YELLOW}⚠️  跳过 pgvector 安装，向量搜索功能将不可用${NC}"
    fi
    
    # 尝试在数据库中启用
    echo ""
    echo "在数据库中启用 pgvector..."
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME << 'EOF'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF
    
    if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1 FROM pg_extension WHERE extname='vector'" &>/dev/null; then
        echo -e "${GREEN}✅ pgvector 启用成功${NC}"
    else
        echo -e "${RED}❌ pgvector 启用失败${NC}"
        echo "请手动执行:"
        echo "  brew install pgvector"
        echo "  PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c 'CREATE EXTENSION vector;'"
    fi
fi

echo ""

# ==================== 步骤 2: 创建记忆表 ====================
echo -e "${YELLOW}📋 步骤 2: 创建记忆系统表...${NC}"
echo ""

# 检查是否已存在
if PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1 FROM unified_memory LIMIT 1" &>/dev/null 2>&1; then
    echo -e "${GREEN}✅ 记忆表已经存在${NC}"
else
    echo "创建记忆表..."
    
    # 运行 Alembic 迁移
    cd "$(dirname "$0")/../backend"
    
    echo "运行 Alembic 迁移到最新版本..."
    alembic upgrade head 2>&1 | tail -20
    
    if PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1 FROM unified_memory LIMIT 1" &>/dev/null 2>&1; then
        echo -e "${GREEN}✅ 记忆表创建成功${NC}"
    else
        echo -e "${YELLOW}⚠️  迁移可能有问题，尝试手动创建...${NC}"
        echo "请参考文档手动执行迁移"
    fi
fi

echo ""

# ==================== 步骤 3: 验证配置 ====================
echo -e "${YELLOW}🔍 步骤 3: 验证配置...${NC}"
echo ""

echo "检查 pgvector 扩展:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT extname, extversion FROM pg_extension WHERE extname='vector';" 2>&1 | grep -E "vector|extname"

echo ""
echo "检查记忆表:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt | grep memory" 2>&1 | grep -E "memory|TableName"

echo ""
echo "检查记忆表结构:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'unified_memory' ORDER BY ordinal_position;" 2>&1 | head -20

echo ""
echo "=================================================="
echo "✅ 配置完成!"
echo "=================================================="
echo ""
echo "记忆系统功能:"
echo "  ✅ unified_memory - 统一记忆存储"
echo "  ✅ 向量索引 - 语义搜索支持"
echo "  ✅ 长期记忆 - 用户记忆持久化"
echo ""
echo "下一步:"
echo "  1. 测试记忆提取功能"
echo "  2. 测试向量相似度搜索"
echo "  3. 验证长期记忆系统"
echo ""
