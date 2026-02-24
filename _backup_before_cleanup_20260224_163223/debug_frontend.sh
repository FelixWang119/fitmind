#!/bin/bash

PORT=3000
PROCESS_NAME="node"

echo "=== 前端服务调试器启动 ==="

# 检查端口是否已被占用
if lsof -ti:$PORT > /dev/null; then
    echo "发现端口 $PORT 已被占用，正在停止服务..."
    
    # 获取端口占用进程ID
    PIDS=$(lsof -ti:$PORT)
    
    # 杀死所有占用端口的进程  
    for pid in $PIDS; do
        echo "停止进程 PID: $pid"
        kill $pid
        
        # 使用更积极的方式终止
        while kill -0 $pid 2>/dev/null; do
            sleep 0.5
            # 如果正常 kill 不成功，尝试强制杀死
            kill -9 $pid 2>/dev/null
        done
    done
    
    echo "端口 $PORT 已清理完毕"
else
    echo "端口 $PORT 未被占用"
fi

echo "启动前端服务..."

# 切换到 frontend 目录并启动服务
cd /Users/felix/bmad/frontend

# 以后台模式启动服务（npm run dev）
npm run dev &

SERVER_PID=$!

echo "前端服务已在端口 $PORT 启动，进程PID: $SERVER_PID"

# 等待几秒让服务充分启动
sleep 3

# 检查服务是否成功启动
if lsof -ti:$PORT > /dev/null; then
    echo "✅ 前端服务正常运行在 http://localhost:$PORT"
    
    # 尝试简单HTTP请求检测
    if curl -f -s http://localhost:$PORT > /dev/null; then
        echo "📊 前端服务响应正常"
    else
        echo "🔍 提示: 服务可能仍在启动过程中，请稍等片刻"
    fi
else
    echo "❌ 未检测到服务在端口 $PORT 启动"
    echo "🔍 检查端口 3000 是否在正确端口上被 Node.js 占用:"
    lsof -i :3000
fi

echo "=============================================="