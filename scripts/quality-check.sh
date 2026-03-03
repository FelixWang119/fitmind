#!/bin/bash
# Sprint 质量检查脚本
# 检查前端页面中的占位符、TODO、后续版本等未完成内容

echo "=================================="
echo "Sprint 质量检查报告"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# 检查文件中的占位符内容
check_file() {
    local file=$1
    local filename=$(basename "$file")
    
    # 检查占位符文本
    if grep -q "后续版本\|todo\|TODO\|placeholder\|待实现\|简化版\|coming soon\|Coming Soon" "$file" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  $filename${NC} - 发现占位符内容"
        grep -n "后续版本\|todo\|TODO\|待实现\|简化版\|coming soon\|Coming Soon" "$file" | head -5
        ((ISSUES_FOUND++))
    fi
}

# 检查所有前端页面
echo "📋 检查前端页面..."
echo ""

for file in frontend/src/pages/*.tsx; do
    check_file "$file"
done

echo ""
echo "📋 检查前端组件..."
for file in frontend/src/components/**/*.tsx; do
    check_file "$file"
done

echo ""
echo "📋 检查后端 API 端点..."
for file in backend/app/api/v1/endpoints/*.py; do
    if grep -q "TODO\|FIXME\|待实现\|placeholder" "$file" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  $(basename $file)${NC} - 发现 TODO/FIXME"
        grep -n "TODO\|FIXME\|待实现" "$file" | head -3
        ((ISSUES_FOUND++))
    fi
done

echo ""
echo "=================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ 没有发现占位符内容${NC}"
else
    echo -e "${RED}❌ 发现 $ISSUES_FOUND 个问题${NC}"
fi
echo "=================================="
