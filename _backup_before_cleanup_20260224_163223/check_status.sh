#!/bin/bash

echo "=== 当前前后端服务状态 ==="

echo "后端服务 (端口 8000):"
if lsof -ti:8000 > /dev/null; then
    echo "✅ 运行中 (PID: $(lsof -ti:8000))"
    BACKEND_STATUS=$(curl -sf http://localhost:8000/health 2>/dev/null | head -c 100)
    if [ ! -z "$BACKEND_STATUS" ]; then
        echo "   健康检查: $BACKEND_STATUS"
    fi
else
    echo "❌ 未运行"
fi

echo "前端服务 (端口 3000):"
if lsof -ti:3000 > /dev/null; then
    echo "✅ 运行中 (PID: $(lsof -ti:3000))"
    RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    echo "   HTTP 状态码: $RESPONSE_CODE"
else
    echo "❌ 未运行"
fi

echo "========================================="