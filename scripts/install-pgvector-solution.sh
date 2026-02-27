#!/bin/bash
# pgvector 安装解决方案

echo "=================================================="
echo "🔧 pgvector 安装问题解决方案"
echo "=================================================="
echo ""

echo "问题原因："
echo "  pgvector 需要 PostgreSQL 17 或 18 来编译"
echo "  您当前安装的是 PostgreSQL 16"
echo ""

echo "解决方案："
echo ""
echo "=== 方案 1: 使用预编译的 bottle（推荐，最快）==="
echo ""
echo "尝试直接从 bottle 安装（不需要编译）："
echo "  brew install pgvector --force-bottle"
echo ""

echo "=== 方案 2: 使用 MacPorts 的 pgvector（已安装）==="
echo ""
echo "MacPorts 已经为您安装了 postgresql16-pgvector！"
echo "只需要在数据库中启用："
echo ""
echo "  sudo port install postgresql16-pgvector"
echo "  PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c 'CREATE EXTENSION vector;'"
echo ""

echo "=== 方案 3: 升级 PostgreSQL 到 17（不推荐）==="
echo ""
echo "这会升级您的 PostgreSQL，可能导致数据不兼容："
echo "  brew upgrade postgresql"
echo ""

echo "=================================================="
echo "推荐使用方案 2（MacPorts），因为您的 PostgreSQL 16 已经是 MacPorts 安装的"
echo "=================================================="
echo ""

read -p "是否使用 MacPorts 方案安装 pgvector? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在使用 MacPorts 安装 pgvector..."
    
    # 检查 MacPorts
    if ! command -v port &>/dev/null; then
        echo "❌ MacPorts 未安装"
        exit 1
    fi
    
    # 安装 pgvector
    sudo port install postgresql16-pgvector
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ pgvector 安装成功！"
        echo ""
        echo "现在在数据库中启用..."
        
        # 找到 pgvector 扩展文件位置
        PGVECTOR_PATH=$(find /opt/local -name "vector.so" 2>/dev/null | head -1)
        
        if [ -n "$PGVECTOR_PATH" ]; then
            echo "找到 pgvector: $PGVECTOR_PATH"
            
            # 复制到 PostgreSQL 16 的扩展目录
            PG16_EXT_DIR="/opt/local/var/db/postgresql16/defaultdb/extensions/"
            sudo mkdir -p "$PG16_EXT_DIR"
            sudo cp "$PGVECTOR_PATH" "$PG16_EXT_DIR/"
            
            echo "现在在数据库中启用扩展..."
            PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db << 'SQLEOF'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SQLEOF
            
            # 验证
            if PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "SELECT * FROM pg_extension WHERE extname='vector'" &>/dev/null; then
                echo ""
                echo "✅ pgvector 启用成功！"
            else
                echo ""
                echo "⚠️  pgvector 启用失败，需要手动配置"
                echo "请参考文档手动操作"
            fi
        else
            echo "❌ 未找到 pgvector 扩展文件"
        fi
    else
        echo "❌ pgvector 安装失败"
    fi
fi
