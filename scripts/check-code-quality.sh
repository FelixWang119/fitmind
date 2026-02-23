#!/bin/bash

# 统一代码质量检查脚本
# 运行: ./scripts/check-code-quality.sh

set -e

echo "=========================================="
echo "代码质量检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
total_checks=0
passed_checks=0
failed_checks=0

# 函数：运行检查
run_check() {
    local name=$1
    local command=$2
    local dir=${3:-.}
    
    ((total_checks++))
    
    echo -n "检查: $name ... "
    
    if cd "$dir" && eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((passed_checks++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((failed_checks++))
        return 1
    fi
}

echo "=== 后端代码质量检查 ==="

# 后端代码格式化检查
run_check "Black代码格式化" "poetry run black --check --diff ." "backend"
run_check "isort导入排序" "poetry run isort --check-only --diff ." "backend"
run_check "Flake8代码检查" "poetry run flake8" "backend"
run_check "Mypy类型检查" "poetry run mypy --ignore-missing-imports app" "backend"
run_check "Bandit安全扫描" "poetry run bandit -c pyproject.toml -r app" "backend"

echo ""
echo "=== 前端代码质量检查 ==="

# 前端代码格式化检查
run_check "ESLint代码检查" "npx eslint . --ext .ts,.tsx" "frontend"
run_check "Prettier代码格式化" "npx prettier --check ." "frontend"
run_check "TypeScript类型检查" "npx tsc --noEmit" "frontend"

echo ""
echo "=== 项目级检查 ==="

# 项目级检查
run_check "YAML文件语法" "find . -name '*.yaml' -o -name '*.yml' | xargs yamllint" "."
run_check "环境变量模板" "test -f .env.example && echo '存在'" "."
run_check "Docker Compose配置" "docker-compose config --quiet" "."

echo ""
echo "=========================================="
echo "检查结果汇总"
echo "=========================================="
echo "总检查项: $total_checks"
echo -e "${GREEN}通过: $passed_checks${NC}"
echo -e "${RED}失败: $failed_checks${NC}"
echo ""

if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}✅ 所有代码质量检查通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $failed_checks 个检查失败${NC}"
    echo ""
    echo "建议运行以下命令修复问题："
    echo "1. 后端格式化: cd backend && poetry run black . && poetry run isort ."
    echo "2. 前端格式化: cd frontend && npx prettier --write . && npx eslint . --ext .ts,.tsx --fix"
    echo "3. 重新运行检查: ./scripts/check-code-quality.sh"
    exit 1
fi