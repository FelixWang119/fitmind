#!/bin/bash

# 启动脚本 - 本地测试环境

echo "🚀 启动体重管理 AI 助手测试环境..."

# 设置环境变量
export DATABASE_URL="sqlite:///./weight_management.db"
export SECRET_KEY="test-secret-key-for-local-development-only"
export ACCESS_TOKEN_EXPIRE_MINUTES=1440
export QWEN_API_KEY="mock_key_for_testing"
export USE_MOCK_AI="true"
export BACKEND_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
export ENVIRONMENT="development"

cd backend

# 初始化数据库
echo "📦 初始化数据库..."
python3 -c "
from app.db.session import engine
from app.db.base import Base
print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('✅ 数据库初始化完成')
"

# 启动后端服务
echo "🔥 启动后端服务 (http://localhost:8000)..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "⏳ 等待后端启动..."
sleep 5

# 测试后端是否运行
echo "🧪 测试后端服务..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

cd ../frontend

# 启动前端服务
echo "🎨 启动前端服务 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

echo "⏳ 等待前端启动..."
sleep 10

echo ""
echo "=========================================="
echo "✅ 所有服务已启动！"
echo ""
echo "🌐 访问地址："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🧪 测试检查清单："
echo "   ☐ 访问 http://localhost:5173 查看前端"
echo "   ☐ 注册新用户"
echo "   ☐ 登录系统"
echo "   ☐ 设置个人档案"
echo "   ☐ 与 AI 对话"
echo "   ☐ 记录饮食"
echo "   ☐ 创建习惯并打卡"
echo "   ☐ 记录体重"
echo ""
echo "🛑 停止服务：按 Ctrl+C 或运行：kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
