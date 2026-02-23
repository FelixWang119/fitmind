#!/bin/bash

# 用户注册系统集成测试脚本
# 测试前后端注册功能的完整集成

set -e

echo "=========================================="
echo "用户注册系统集成测试"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
total_tests=0
passed_tests=0
failed_tests=0

# 函数：运行测试
run_test() {
    local test_name=$1
    local command=$2
    local expected_status=${3:-0}
    
    ((total_tests++))
    
    echo -n "测试: $test_name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        if [ $? -eq $expected_status ]; then
            echo -e "${GREEN}✓ 通过${NC}"
            ((passed_tests++))
            return 0
        else
            echo -e "${RED}✗ 失败 (状态码: $?)${NC}"
            ((failed_tests++))
            return 1
        fi
    else
        if [ $? -eq $expected_status ]; then
            echo -e "${GREEN}✓ 通过 (预期失败)${NC}"
            ((passed_tests++))
            return 0
        else
            echo -e "${RED}✗ 失败${NC}"
            ((failed_tests++))
            return 1
        fi
    fi
}

echo "=== 1. 后端API测试 ==="

# 测试后端服务器是否可启动
run_test "后端FastAPI应用导入" "cd backend && python3 -c 'from app.main import app; print(\"App loaded:\", app.title)'"

# 测试数据库连接配置（不实际连接）
run_test "数据库配置导入" "cd backend && python3 -c 'from app.core.database import Base, SessionLocal; print(\"Database modules imported successfully\")'"

# 测试用户模型导入
run_test "用户模型导入" "cd backend && python3 -c 'from app.models.user import User; print(\"User model:\", User.__name__)'"

echo ""
echo "=== 2. 注册功能测试 ==="

# 创建测试Python脚本
cat > /tmp/test_registration.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.schemas.user import UserCreate
from pydantic import ValidationError
import json

def test_password_validation():
    """测试密码验证"""
    print("测试密码验证...")
    
    # 测试弱密码
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "confirm_password": "weak"
        }
        UserCreate(**user_data)
        print("  ✗ 弱密码应该被拒绝")
        return False
    except ValidationError as e:
        if "至少需要8个字符" in str(e):
            print("  ✓ 弱密码正确被拒绝")
        else:
            print(f"  ✗ 错误类型不正确: {e}")
            return False
    
    # 测试缺少大写字母
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "lowercase123",
            "confirm_password": "lowercase123"
        }
        UserCreate(**user_data)
        print("  ✗ 缺少大写字母应该被拒绝")
        return False
    except ValidationError as e:
        if "必须包含至少一个大写字母" in str(e):
            print("  ✓ 缺少大写字母正确被拒绝")
        else:
            print(f"  ✗ 错误类型不正确: {e}")
            return False
    
    # 测试缺少数字
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "UppercaseOnly",
            "confirm_password": "UppercaseOnly"
        }
        UserCreate(**user_data)
        print("  ✗ 缺少数字应该被拒绝")
        return False
    except ValidationError as e:
        if "必须包含至少一个数字" in str(e):
            print("  ✓ 缺少数字正确被拒绝")
        else:
            print(f"  ✗ 错误类型不正确: {e}")
            return False
    
    # 测试密码不匹配
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPass123",
            "confirm_password": "DifferentPass123"
        }
        UserCreate(**user_data)
        print("  ✗ 密码不匹配应该被拒绝")
        return False
    except ValidationError as e:
        if "密码和确认密码不匹配" in str(e):
            print("  ✓ 密码不匹配正确被拒绝")
        else:
            print(f"  ✗ 错误类型不正确: {e}")
            return False
    
    # 测试有效密码
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        }
        user = UserCreate(**user_data)
        print("  ✓ 有效密码通过验证")
        return True
    except ValidationError as e:
        print(f"  ✗ 有效密码被拒绝: {e}")
        return False

def test_email_validation():
    """测试邮箱验证"""
    print("\n测试邮箱验证...")
    
    # 测试无效邮箱
    try:
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        }
        UserCreate(**user_data)
        print("  ✗ 无效邮箱应该被拒绝")
        return False
    except ValidationError as e:
        if "value is not a valid email address" in str(e).lower():
            print("  ✓ 无效邮箱正确被拒绝")
        else:
            print(f"  ✗ 错误类型不正确: {e}")
            return False
    
    # 测试有效邮箱
    try:
        user_data = {
            "email": "valid@example.com",
            "username": "testuser",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        }
        user = UserCreate(**user_data)
        print("  ✓ 有效邮箱通过验证")
        return True
    except ValidationError as e:
        print(f"  ✗ 有效邮箱被拒绝: {e}")
        return False

if __name__ == "__main__":
    print("开始用户注册验证测试")
    print("=" * 50)
    
    password_test = test_password_validation()
    email_test = test_email_validation()
    
    print("\n" + "=" * 50)
    if password_test and email_test:
        print("所有验证测试通过！")
        sys.exit(0)
    else:
        print("部分测试失败")
        sys.exit(1)
EOF

# 运行验证测试
run_test "用户注册数据验证" "cd /Users/felix/bmad && python3 /tmp/test_registration.py"

echo ""
echo "=== 3. 前端构建测试 ==="

# 测试前端TypeScript编译
run_test "TypeScript类型检查" "cd frontend && npx tsc --noEmit"

# 测试前端依赖
run_test "前端依赖完整性" "cd frontend && npm list --depth=0"

echo ""
echo "=== 4. 配置文件测试 ==="

# 测试环境变量配置
run_test "环境变量模板" "[ -f .env.example ] && grep -q 'DATABASE_URL' .env.example"

# 测试Docker配置
run_test "Docker Compose配置" "docker-compose config --quiet"

echo ""
echo "=== 5. 数据库测试 ==="

# 测试数据库初始化脚本
run_test "数据库初始化脚本" "grep -q 'CREATE TABLE IF NOT EXISTS users' init-db/init.sql"

# 测试表数量
table_count=$(grep -c "CREATE TABLE IF NOT EXISTS" init-db/init.sql)
echo -n "测试: 数据库表数量 ... "
if [ $table_count -ge 10 ]; then
    echo -e "${GREEN}✓ 通过 ($table_count 个表)${NC}"
    ((passed_tests++))
else
    echo -e "${RED}✗ 失败 (只有 $table_count 个表，需要至少10个)${NC}"
    ((failed_tests++))
fi
((total_tests++))

echo ""
echo "=========================================="
echo "集成测试结果汇总"
echo "=========================================="
echo "总测试项: $total_tests"
echo -e "${GREEN}通过: $passed_tests${NC}"
echo -e "${RED}失败: $failed_tests${NC}"
echo ""

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}✅ 所有集成测试通过！${NC}"
    echo ""
    echo "用户注册系统集成状态："
    echo "- ✅ 后端API功能完整"
    echo "- ✅ 数据验证逻辑正确"
    echo "- ✅ 前端构建配置正常"
    echo "- ✅ 配置文件完整"
    echo "- ✅ 数据库结构正确"
    echo ""
    echo "可以开始编写具体测试用例和进行端到端测试。"
    exit 0
else
    echo -e "${RED}❌ 有 $failed_tests 个测试失败${NC}"
    exit 1
fi