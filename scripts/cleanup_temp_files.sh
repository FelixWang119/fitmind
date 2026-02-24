#!/bin/bash
# =============================================================================
# 清理临时测试文件和废弃脚本
# =============================================================================

set -e

PROJECT_ROOT="/Users/felix/bmad"
BACKUP_DIR="$PROJECT_ROOT/_backup_before_cleanup_$(date +%Y%m%d_%H%M%S)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧹 清理临时文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 创建备份目录
echo "ℹ️  创建备份目录：$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# =============================================================================
# 临时测试文件（保留有用的）
# =============================================================================

echo ""
echo "📋 临时测试文件分类..."

# 可以安全删除的测试文件模式
TEMP_TEST_PATTERNS=(
    "test_*.py"  # 所有临时测试
)

# 需要保留的测试文件
KEEP_TESTS=(
    "test_app.py"
)

# 移动到备份目录
echo ""
echo "🗑️  移动临时测试文件到备份目录..."
cd "$PROJECT_ROOT"

# 统计
MOVED_COUNT=0
KEPT_COUNT=0

for file in test_*.py; do
    if [ -f "$file" ]; then
        # 检查是否在保留列表中
        KEEP=false
        for keep in "${KEEP_TESTS[@]}"; do
            if [ "$file" = "$keep" ]; then
                KEEP=true
                break
            fi
        done
        
        if [ "$KEEP" = true ]; then
            echo "  ✓ 保留：$file"
            ((KEPT_COUNT++)) || true
        else
            mv "$file" "$BACKUP_DIR/" 2>/dev/null && {
                echo "  → 备份：$file"
                ((MOVED_COUNT++)) || true
            }
        fi
    fi
done

# =============================================================================
# 废弃的脚本文件
# =============================================================================

echo ""
echo "📋 脚本文件分类..."

# 可以删除的旧脚本
DEPRECATED_SCRIPTS=(
    "restart_simple.sh"
    "restart_efficient.sh"
    "restart_optimized.sh"
    "debug_backend.sh"
    "debug_backend_8001.sh"
    "debug_frontend.sh"
    "debug_both.sh"
    "check_status.sh"
)

# 临时诊断脚本
TEMP_SCRIPTS=(
    "check_backend_error.py"
    "debug_schema.py"
    "diagnose_meal_issue.py"
    "fix_meal_items.py"
    "real_ai_app.py"
    "validate_infrastructure.py"
)

echo ""
echo "🗑️  移动废弃脚本到备份目录..."

for script in "${DEPRECATED_SCRIPTS[@]}"; do
    if [ -f "$PROJECT_ROOT/$script" ]; then
        mv "$PROJECT_ROOT/$script" "$BACKUP_DIR/" 2>/dev/null && {
            echo "  → 备份：$script"
            ((MOVED_COUNT++)) || true
        }
    fi
done

echo ""
echo "🗑️  移动临时脚本到备份目录..."

for script in "${TEMP_SCRIPTS[@]}"; do
    if [ -f "$PROJECT_ROOT/$script" ]; then
        mv "$PROJECT_ROOT/$script" "$BACKUP_DIR/" 2>/dev/null && {
            echo "  → 备份：$script"
            ((MOVED_COUNT++)) || true
        }
    fi
done

# =============================================================================
# Python 缓存
# =============================================================================

echo ""
echo "🗑️  清理 Python 缓存..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "  ✓ __pycache__ 目录已清理" || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null && echo "  ✓ .pyc 文件已清理" || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null && echo "  ✓ .pytest_cache 目录已清理" || true
find "$PROJECT_ROOT" -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null && echo "  ✓ .ruff_cache 目录已清理" || true
find "$PROJECT_ROOT/backend" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null && echo "  ✓ .mypy_cache 目录已清理" || true

# =============================================================================
# 其他临时文件
# =============================================================================

echo ""
echo "🗑️  清理其他临时文件..."

# 日志文件备份
LOG_FILES=(
    "backend_restart.log"
    "backend_restart.log.old"
    "backend_no_reload.log"
    "backend.pid"
)

for logfile in "${LOG_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$logfile" ]; then
        mv "$PROJECT_ROOT/$logfile" "$BACKUP_DIR/" 2>/dev/null && {
            echo "  → 备份：$logfile"
            ((MOVED_COUNT++)) || true
        }
    fi
done

# 数据库文件（测试用）
TEST_DB_FILES=(
    "test.db"
    "test_integration.db"
    "test_real.db"
    "weight_management.db"  # 注意：这个可能是生产数据库
    "lunch.jpg"
)

for dbfile in "${TEST_DB_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$dbfile" ]; then
        # 跳过可能的主数据库
        if [ "$dbfile" = "weight_management.db" ]; then
            echo "  ⚠️  跳过可能的生产数据库：$dbfile"
            continue
        fi
        mv "$dbfile" "$BACKUP_DIR/" 2>/dev/null && {
            echo "  → 备份：$dbfile"
            ((MOVED_COUNT++)) || true
        }
    fi
done

# token 文件
if [ -f "$PROJECT_ROOT/test_token.txt" ]; then
    mv "$PROJECT_ROOT/test_token.txt" "$BACKUP_DIR/" && {
        echo "  → 备份：test_token.txt"
        ((MOVED_COUNT++)) || true
    }
fi

# =============================================================================
# 总结
# =============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ 清理完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 统计:"
echo "  - 备份文件数：$MOVED_COUNT"
echo "  - 保留文件数：$KEPT_COUNT"
echo "  - 备份目录：$BACKUP_DIR"
echo ""

if [ $MOVED_COUNT -gt 0 ]; then
    echo "⚠️  注意:"
    echo "  备份目录已创建，请验证系统正常运行后再删除备份"
    echo "  删除备份命令：rm -rf $BACKUP_DIR"
    echo ""
fi

echo "📁 保留的重要文件:"
echo "  - scripts/start_backend.sh (新启动脚本)"
echo "  - test_app.py (基础测试)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
