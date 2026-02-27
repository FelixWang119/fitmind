#!/bin/bash
"""
Git预提交钩子 - 文档一致性检查

在提交前检查代码是否符合架构文档要求。
"""

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECK_SCRIPT="$PROJECT_ROOT/scripts/architecture/check_document_consistency.py"
REPORT_FILE="/tmp/architecture-check-$(date +%s).txt"

echo "🔍 正在检查文档一致性..."

# 检查是否有架构相关文件变更
ARCH_FILES_CHANGED=$(git diff --cached --name-only | grep -E "(docs/architecture/|backend/app/services/memory|backend/app/models/memory)" || true)

if [ -z "$ARCH_FILES_CHANGED" ]; then
    echo "✅ 无架构相关文件变更，跳过检查"
    exit 0
fi

echo "📋 检测到架构相关文件变更:"
echo "$ARCH_FILES_CHANGED" | sed 's/^/  - /'

# 运行文档一致性检查
echo ""
echo "🚀 运行文档一致性检查..."
python "$CHECK_SCRIPT" --format text --output "$REPORT_FILE"

# 检查退出码
if [ $? -eq 0 ]; then
    echo "✅ 所有架构检查通过"
    echo ""
    echo "📊 检查报告摘要:"
    tail -20 "$REPORT_FILE" | head -10
    rm -f "$REPORT_FILE"
    exit 0
else
    echo "❌ 架构检查失败"
    echo ""
    echo "📋 详细报告:"
    cat "$REPORT_FILE"
    echo ""
    echo "💡 建议操作:"
    echo "  1. 修复上述架构不一致问题"
    echo "  2. 或添加例外说明（需要架构委员会批准）"
    echo "  3. 重新运行检查: python $CHECK_SCRIPT"
    echo ""
    echo "⚠️  提交被阻止，请修复架构问题后重试"
    rm -f "$REPORT_FILE"
    exit 1
fi