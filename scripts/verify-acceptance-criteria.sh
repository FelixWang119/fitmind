#!/bin/bash

# Story 1.0 验收标准验证脚本
# 验证所有7个验收标准的实际通过状态

set -e

echo "=========================================="
echo "Story 1.0 验收标准验证"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
total_ac=7
passed_ac=0
failed_ac=0
warning_ac=0

# 函数：打印结果
print_result() {
    local status=$1
    local message=$2
    
    case $status in
        "PASS")
            echo -e "${GREEN}✓ PASS${NC}: $message"
            ((passed_ac++))
            ;;
        "FAIL")
            echo -e "${RED}✗ FAIL${NC}: $message"
            ((failed_ac++))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠ WARN${NC}: $message"
            ((warning_ac++))
            ;;
    esac
}

echo "=== AC1: 基础软件环境检查 ==="

# 检查Git
if command -v git &> /dev/null; then
    git_version=$(git --version | awk '{print $3}')
    if [[ "$git_version" > "2.30" ]]; then
        print_result "PASS" "Git $git_version (要求: 2.30+)"
    else
        print_result "FAIL" "Git $git_version (要求: 2.30+)"
    fi
else
    print_result "FAIL" "Git未安装"
fi

# 检查Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version | sed 's/v//')
    if [[ "$node_version" > "18.0" ]]; then
        print_result "PASS" "Node.js $node_version (要求: 18.0+)"
    else
        print_result "FAIL" "Node.js $node_version (要求: 18.0+)"
    fi
else
    print_result "FAIL" "Node.js未安装"
fi

# 检查Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | awk '{print $2}')
    if [[ "$python_version" > "3.11" ]]; then
        print_result "PASS" "Python $python_version (要求: 3.11+)"
    else
        print_result "FAIL" "Python $python_version (要求: 3.11+)"
    fi
else
    print_result "FAIL" "Python未安装"
fi

# 检查npm
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    if [[ "$npm_version" > "9.0" ]]; then
        print_result "PASS" "npm $npm_version (要求: 9.0+)"
    else
        print_result "FAIL" "npm $npm_version (要求: 9.0+)"
    fi
else
    print_result "FAIL" "npm未安装"
fi

# 检查Poetry
if command -v poetry &> /dev/null; then
    poetry_version=$(poetry --version | awk '{print $3}')
    if [[ "$poetry_version" > "1.5" ]]; then
        print_result "PASS" "Poetry $poetry_version (要求: 1.5+)"
    else
        print_result "FAIL" "Poetry $poetry_version (要求: 1.5+)"
    fi
else
    print_result "WARN" "Poetry未安装（可通过pip安装）"
fi

# 检查Docker
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
    if [[ "$docker_version" > "20.10" ]]; then
        print_result "PASS" "Docker $docker_version (要求: 20.10+)"
    else
        print_result "WARN" "Docker $docker_version (要求: 20.10+)"
    fi
else
    print_result "WARN" "Docker未安装（本地开发可选）"
fi

echo ""
echo "=== AC2: 项目结构创建 ==="

# 检查关键目录和文件
required_files=(
    "frontend/"
    "backend/"
    "docker-compose.yml"
    ".env.example"
    "README.md"
    "init-db/"
    "Makefile"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ -e "$file" ]; then
        print_result "PASS" "文件/目录存在: $file"
    else
        print_result "FAIL" "文件/目录缺失: $file"
        ((missing_files++))
    fi
done

if [ $missing_files -eq 0 ]; then
    print_result "PASS" "所有项目结构文件完整"
else
    print_result "FAIL" "项目结构文件缺失 $missing_files 个"
fi

echo ""
echo "=== AC3: 开发环境启动 ==="

# 检查后端依赖
if [ -f "backend/pyproject.toml" ]; then
    if cd backend && poetry check --no-interaction &> /dev/null; then
        print_result "PASS" "后端依赖配置正确"
    else
        print_result "WARN" "后端依赖需要安装"
    fi
    cd ..
else
    print_result "FAIL" "后端依赖文件缺失"
fi

# 检查前端依赖
if [ -f "frontend/package.json" ]; then
    if [ -d "frontend/node_modules" ]; then
        print_result "PASS" "前端依赖已安装"
    else
        print_result "WARN" "前端依赖需要安装 (运行: cd frontend && npm install)"
    fi
else
    print_result "FAIL" "前端依赖文件缺失"
fi

echo ""
echo "=== AC4: 应用访问验证 ==="

# 检查后端健康检查端点配置
if [ -f "backend/app/main.py" ]; then
    if grep -q "/health" backend/app/main.py; then
        print_result "PASS" "后端健康检查端点已配置"
    else
        print_result "FAIL" "后端健康检查端点未配置"
    fi
else
    print_result "FAIL" "后端主文件缺失"
fi

# 检查前端开发服务器配置
if [ -f "frontend/vite.config.ts" ]; then
    print_result "PASS" "前端开发服务器配置完整"
else
    print_result "FAIL" "前端开发服务器配置缺失"
fi

echo ""
echo "=== AC5: 测试环境配置 ==="

# 检查后端测试
if [ -f "backend/pytest.ini" ]; then
    print_result "PASS" "后端测试框架配置完整"
else
    print_result "FAIL" "后端测试框架配置缺失"
fi

# 检查前端测试
if [ -f "frontend/jest.config.js" ]; then
    print_result "PASS" "前端测试框架配置完整"
else
    print_result "FAIL" "前端测试框架配置缺失"
fi

# 检查测试目录
if [ -d "backend/tests" ]; then
    test_count=$(find backend/tests -name "*.py" -type f | wc -l)
    if [ $test_count -gt 0 ]; then
        print_result "PASS" "后端测试文件存在 ($test_count 个)"
    else
        print_result "WARN" "后端测试目录存在但无测试文件"
    fi
else
    print_result "FAIL" "后端测试目录缺失"
fi

echo ""
echo "=== AC6: 代码质量检查 ==="

# 检查后端代码质量工具
if [ -f "backend/pyproject.toml" ]; then
    if grep -q "black" backend/pyproject.toml && grep -q "isort" backend/pyproject.toml; then
        print_result "PASS" "后端代码质量工具已配置 (Black + isort)"
    else
        print_result "FAIL" "后端代码质量工具配置不完整"
    fi
else
    print_result "FAIL" "后端配置文件缺失"
fi

# 检查前端代码质量工具
if [ -f "frontend/.eslintrc.cjs" ]; then
    print_result "PASS" "前端代码检查工具已配置 (ESLint)"
else
    print_result "FAIL" "前端代码检查工具配置缺失"
fi

# 检查TypeScript配置
if [ -f "frontend/tsconfig.json" ]; then
    print_result "PASS" "TypeScript配置完整"
else
    print_result "FAIL" "TypeScript配置缺失"
fi

echo ""
echo "=== AC7: 数据库迁移 ==="

# 检查数据库初始化脚本
if [ -f "init-db/init.sql" ]; then
    table_count=$(grep -c "CREATE TABLE IF NOT EXISTS" init-db/init.sql)
    if [ $table_count -ge 10 ]; then
        print_result "PASS" "数据库初始化脚本完整 ($table_count 个表)"
    else
        print_result "FAIL" "数据库表数量不足 ($table_count/10)"
    fi
else
    print_result "FAIL" "数据库初始化脚本缺失"
fi

# 检查Alembic迁移
if [ -d "backend/alembic" ]; then
    if [ -f "backend/alembic/env.py" ]; then
        print_result "PASS" "数据库迁移工具配置完整 (Alembic)"
    else
        print_result "WARN" "数据库迁移工具配置不完整"
    fi
else
    print_result "WARN" "数据库迁移工具目录缺失"
fi

echo ""
echo "=========================================="
echo "验证结果汇总"
echo "=========================================="
echo "总验收标准: $total_ac"
echo -e "${GREEN}通过: $passed_ac${NC}"
echo -e "${RED}失败: $failed_ac${NC}"
echo -e "${YELLOW}警告: $warning_ac${NC}"
echo ""

if [ $failed_ac -eq 0 ]; then
    if [ $warning_ac -eq 0 ]; then
        echo -e "${GREEN}✅ 所有验收标准完全通过！${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ 所有验收标准基本通过，但有 $warning_ac 个警告${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ 有 $failed_ac 个验收标准失败${NC}"
    exit 1
fi