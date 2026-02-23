#!/bin/bash

echo "=== Story 1.0 验收标准快速验证 ==="
echo ""

# AC1: 基础软件环境检查
echo "AC1: 基础软件环境检查"
git --version && echo "  ✓ Git OK" || echo "  ✗ Git FAIL"
node --version && echo "  ✓ Node.js OK" || echo "  ✗ Node.js FAIL"
python3 --version && echo "  ✓ Python OK" || echo "  ✗ Python FAIL"
npm --version && echo "  ✓ npm OK" || echo "  ✗ npm FAIL"
poetry --version 2>/dev/null && echo "  ✓ Poetry OK" || echo "  ⚠ Poetry WARN"
docker --version 2>/dev/null && echo "  ⚠ Docker OK" || echo "  ⚠ Docker WARN"
echo ""

# AC2: 项目结构创建
echo "AC2: 项目结构创建"
[ -d "frontend" ] && echo "  ✓ frontend/" || echo "  ✗ frontend/"
[ -d "backend" ] && echo "  ✓ backend/" || echo "  ✗ backend/"
[ -f "docker-compose.yml" ] && echo "  ✓ docker-compose.yml" || echo "  ✗ docker-compose.yml"
[ -f ".env.example" ] && echo "  ✓ .env.example" || echo "  ✗ .env.example"
[ -f "README.md" ] && echo "  ✓ README.md" || echo "  ✗ README.md"
[ -d "init-db" ] && echo "  ✓ init-db/" || echo "  ✗ init-db/"
[ -f "Makefile" ] && echo "  ✓ Makefile" || echo "  ✗ Makefile"
echo ""

# AC3: 开发环境启动
echo "AC3: 开发环境启动"
[ -f "backend/pyproject.toml" ] && echo "  ✓ 后端依赖配置" || echo "  ✗ 后端依赖配置"
[ -f "frontend/package.json" ] && echo "  ✓ 前端依赖配置" || echo "  ✗ 前端依赖配置"
echo ""

# AC4: 应用访问验证
echo "AC4: 应用访问验证"
[ -f "backend/app/main.py" ] && echo "  ✓ 后端主文件" || echo "  ✗ 后端主文件"
[ -f "frontend/vite.config.ts" ] && echo "  ✓ 前端配置" || echo "  ✗ 前端配置"
echo ""

# AC5: 测试环境配置
echo "AC5: 测试环境配置"
[ -f "backend/pytest.ini" ] && echo "  ✓ 后端测试配置" || echo "  ✗ 后端测试配置"
[ -f "frontend/jest.config.js" ] && echo "  ✓ 前端测试配置" || echo "  ✗ 前端测试配置"
[ -d "backend/tests" ] && echo "  ✓ 后端测试目录" || echo "  ✗ 后端测试目录"
echo ""

# AC6: 代码质量检查
echo "AC6: 代码质量检查"
[ -f "backend/pyproject.toml" ] && echo "  ✓ 后端质量工具" || echo "  ✗ 后端质量工具"
[ -f "frontend/.eslintrc.cjs" ] && echo "  ✓ 前端ESLint" || echo "  ✗ 前端ESLint"
[ -f "frontend/tsconfig.json" ] && echo "  ✓ TypeScript配置" || echo "  ✗ TypeScript配置"
echo ""

# AC7: 数据库迁移
echo "AC7: 数据库迁移"
[ -f "init-db/init.sql" ] && echo "  ✓ 数据库初始化脚本" || echo "  ✗ 数据库初始化脚本"
[ -d "backend/alembic" ] && echo "  ✓ Alembic迁移" || echo "  ⚠ Alembic迁移"
echo ""

echo "=== 验证完成 ==="