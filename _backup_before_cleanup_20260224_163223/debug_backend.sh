#!/bin/bash

PORT=8000
PROCESS_NAME="uvicorn"
APP_MODULE="app.main:app"

echo "=== 后端服务调试器启动 ==="

# 检查端口是否已被占用
if lsof -ti:$PORT > /dev/null; then
    echo "发现端口 $PORT 已被占用，正在停止服务..."
    
    # 获取端口占用进程ID
    PIDS=$(lsof -ti:$PORT)
    
    # 杀死所有占用端口的进程  
    for pid in $PIDS; do
        echo "停止进程 PID: $pid"
        kill $pid
        
        # 等待进程退出
        while kill -0 $pid 2>/dev/null; do
            sleep 0.5
        done
    done
    
    echo "端口 $PORT 已清理完毕"
else
    echo "端口 $PORT 未被占用"
fi

echo "启动后端服务..."

# 切换到 backend 目录并启动服务
cd /Users/felix/bmad/backend

# 以后台模式启动服务
uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT --reload &

SERVER_PID=$!

echo "后端服务已在端口 $PORT 启动，进程ID: $SERVER_PID"

# 等待几秒让服务充分启动
sleep 2

# 检查服务是否成功启动
if lsof -ti:$PORT > /dev/null; then
    echo "✅ 后端服务正常运行在 http://localhost:$PORT"
    
    # 尝试发送健康检查请求
    if curl -f -s http://localhost:$PORT/health > /dev/null; then
        HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health)
        echo "📊 健康检查响应: $HEALTH_RESPONSE"
    else
        echo "🔍 提示: 服务可能已启动但在准备阶段"
    fi
else
    echo "❌ 注意: 未检测到服务在端口 $PORT 启动"
fi

echo "==========================================="