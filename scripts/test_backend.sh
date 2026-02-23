#!/bin/bash

echo "🧪 体重管理 AI 助手 - 功能测试验证"
echo "=================================="

# 清理旧进程
echo "🔄 清理旧进程..."
pkill -f "uvicorn" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
sleep 2

# 启动后端
echo "🚀 启动后端服务..."
cd backend
export DATABASE_URL="sqlite:///./weight_management.db"
export SECRET_KEY="test-secret-key-for-local-development"
export QWEN_API_KEY="mock_key_for_testing"
export USE_MOCK_AI="true"
export ENVIRONMENT="development"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

echo "⏳ 等待后端启动..."
sleep 10

# 测试后端
echo "🧪 测试后端服务..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务启动失败"
    cat backend.log
    exit 1
fi

# 测试API文档
echo "📚 测试API文档..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API文档可访问"
else
    echo "❌ API文档不可访问"
fi

# 测试API端点
echo "🔍 测试API端点..."
echo "1. 测试根路径:"
curl -s http://localhost:8000/ | python3 -m json.tool

echo ""
echo "2. 测试健康检查:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "3. 测试用户注册:"
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123456", "nickname": "测试用户"}' 2>/dev/null | python3 -m json.tool || echo "注册失败"

echo ""
echo "4. 测试用户登录:"
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123456"}' 2>/dev/null | python3 -m json.tool || echo "登录失败"

echo ""
echo "5. 测试AI对话:"
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，今天该吃什么？"}' 2>/dev/null | python3 -m json.tool || echo "AI对话失败"

echo ""
echo "=================================="
echo "✅ 后端测试完成"
echo "🛑 停止后端服务: kill $BACKEND_PID"
echo "📋 查看日志: tail -f backend/backend.log"
