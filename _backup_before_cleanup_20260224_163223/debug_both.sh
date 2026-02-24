#!/bin/bash

echo "=== 前后端服务统一调试器 ==="

echo " "
echo "启动后端服务..."
echo "==================="
sh /Users/felix/bmad/debug_backend.sh

echo " "
echo "启动前端服务..."
echo "==================="
sh /Users/felix/bmad/debug_frontend.sh

echo " "
echo "最终服务状态检查..."
echo "==================="
echo "后端服务 (端口 8000):"
if lsof -ti:8000 > /dev/null; then
    echo "✅ 运行中"
    BACKEND_STATUS=$(curl -sf http://localhost:8000/health 2>/dev/null | head -c 100)
    if [ ! -z "$BACKEND_STATUS" ]; then
        echo "   健康检查: $BACKEND_STATUS"
    fi
else
    echo "❌ 未运行"
fi

echo "前端服务 (端口 3000):"
if lsof -ti:3000 > /dev/null; then
    echo "✅ 运行中"
else
    echo "❌ 未运行"
fi

echo " "
echo "🎉 完成! 前后端服务状态:"
echo "   后端 API -> http://localhost:8000"
echo "   前端界面 -> http://localhost:3000"
echo "==============================================="