#!/bin/bash
# =============================================================================
# BMAD 后端服务启动脚本
# =============================================================================
# 功能:
#   - 清理 Python 缓存
#   - 检查端口占用
#   - 启动/重启服务
#   - 日志管理
#
# 使用:
#   ./start_backend.sh [start|stop|restart|status|logs] [port]
#
# 示例:
#   ./start_backend.sh start 8000      # 启动到 8000 端口
#   ./start_backend.sh restart         # 重启服务（默认 8000 端口）
#   ./start_backend.sh stop            # 停止服务
#   ./start_backend.sh status          # 查看服务状态
#   ./start_backend.sh logs            # 查看实时日志
#   ./start_backend.sh logs -f         # 跟踪日志
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/backend.pid"
LOG_FILE="$LOG_DIR/backend.log"

# 默认端口
DEFAULT_PORT=8000
PORT="${2:-$DEFAULT_PORT}"

# =============================================================================
# 工具函数
# =============================================================================

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查目录是否存在
ensure_dirs() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        print_info "创建日志目录：$LOG_DIR"
    fi
}

# 检查是否在正确的项目目录
check_project_root() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_error "错误：未找到 .env 文件，请在项目根目录运行此脚本"
        exit 1
    fi
}

# =============================================================================
# 核心功能
# =============================================================================

# 获取进程 PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "$pid"
            return 0
        fi
    fi
    # 备用方案：通过端口查找
    local pid=$(lsof -ti :$PORT 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "$pid"
        return 0
    fi
    echo ""
    return 1
}

# 检查端口占用
check_port() {
    local port=$1
    local pid=$(lsof -ti :$port 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        return 0  # 端口被占用
    fi
    return 1  # 端口空闲
}

# 停止服务
stop_service() {
    print_info "正在停止服务..."
    
    local pid=$(get_pid)
    if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # 如果还在运行，强制停止
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi
        
        print_success "服务已停止 (PID: $pid)"
    else
        print_warning "未找到运行中的服务"
    fi
    
    # 清理 PID 文件
    rm -f "$PID_FILE"
    
    # 清理端口占用
    local port_pid=$(lsof -ti :$PORT 2>/dev/null | head -1)
    if [ -n "$port_pid" ]; then
        kill "$port_pid" 2>/dev/null || true
        sleep 1
        print_success "已清理端口 $PORT 的占用"
    fi
}

# 清理 Python 缓存
clean_cache() {
    print_info "清理 Python 缓存..."
    
    # 查找并删除 __pycache__ 目录
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 查找并删除 .pyc 文件
    find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # 删除其他缓存
    rm -rf "$BACKEND_DIR/.mypy_cache" 2>/dev/null || true
    rm -rf "$BACKEND_DIR/.pytest_cache" 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/.pytest_cache" 2>/dev/null || true
    
    print_success "缓存清理完成"
}

# 启动服务
start_service() {
    ensure_dirs
    check_project_root
    
    # 检查是否已经在运行
    local existing_pid=$(get_pid)
    if [ -n "$existing_pid" ]; then
        print_warning "服务已在运行 (PID: $existing_pid, 端口：$PORT)"
        echo ""
        read -p "是否先停止现有服务？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_service
        else
            print_info "保持现有服务运行"
            return 0
        fi
    fi
    
    # 检查端口占用
    if check_port "$PORT"; then
        print_warning "端口 $PORT 已被占用"
        echo "使用以下命令查看占用进程："
        echo "  lsof -i :$PORT"
        echo ""
        read -p "是否强制停止占用进程？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
            sleep 1
            print_success "端口 $PORT 已释放"
        else
            print_error "启动取消"
            exit 1
        fi
    fi
    
    # 清理缓存
    clean_cache
    
    # 启动服务
    print_info "启动服务到端口 $PORT..."
    print_info "日志文件：$LOG_FILE"
    
    cd "$BACKEND_DIR"
    
    # 使用 nohup 启动，日志输出到项目 logs 目录
    nohup python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port "$PORT" \
        --reload \
        > "$LOG_FILE" 2>&1 &
    
    local new_pid=$!
    echo "$new_pid" > "$PID_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 验证服务是否启动成功
    if ps -p "$new_pid" > /dev/null 2>&1; then
        # 检查 HTTP 响应
        local health_check=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/health 2>/dev/null || echo "000")
        
        if [ "$health_check" = "200" ]; then
            print_success "服务启动成功！"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "  🚀 服务信息"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "  PID:        $new_pid"
            echo "  端口：      $PORT"
            echo "  健康检查：  http://127.0.0.1:$PORT/health"
            echo "  API 文档：  http://127.0.0.1:$PORT/docs"
            echo "  日志文件：  $LOG_FILE"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "快捷命令:"
            echo "  查看日志：  $0 logs"
            echo "  跟踪日志：  $0 logs -f"
            echo "  停止服务：  $0 stop"
            echo "  重启服务：  $0 restart"
            echo ""
        else
            print_error "服务启动失败，请检查日志"
            echo ""
            tail -20 "$LOG_FILE"
            exit 1
        fi
    else
        print_error "服务进程未能启动"
        echo ""
        tail -20 "$LOG_FILE"
        exit 1
    fi
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 显示服务状态
show_status() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📊 服务状态"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local pid=$(get_pid)
    if [ -n "$pid" ]; then
        echo -e "  状态：      ${GREEN}运行中${NC}"
        echo "  PID:        $pid"
        echo "  端口：      $PORT"
        
        # 获取进程信息
        local proc_info=$(ps -p "$pid" -o %cpu,%mem,etime,command 2>/dev/null | tail -1)
        echo "  资源：      $proc_info"
        
        # 健康检查
        local health=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/health 2>/dev/null || echo "000")
        if [ "$health" = "200" ]; then
            echo -e "  健康状态：  ${GREEN}正常${NC}"
        else
            echo -e "  健康状态：  ${RED}异常${NC}"
        fi
    else
        echo -e "  状态：      ${RED}未运行${NC}"
    fi
    
    echo ""
    echo "  日志文件：  $LOG_FILE"
    echo "  PID 文件：   $PID_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# 查看日志
show_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_error "日志文件不存在：$LOG_FILE"
        exit 1
    fi
    
    if [ "$2" = "-f" ]; then
        print_info "跟踪日志 (Ctrl+C 停止)..."
        tail -f "$LOG_FILE"
    else
        print_info "最近 50 行日志:"
        tail -50 "$LOG_FILE"
    fi
}

# 清理所有 Python 进程
cleanup_all() {
    print_warning "此操作将停止所有 Python/uvicorn 进程"
    read -p "确定继续？(y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "uvicorn app.main:app" 2>/dev/null || true
        pkill -f "python.*backend" 2>/dev/null || true
        rm -f "$PID_FILE"
        print_success "已清理所有相关进程"
    fi
}

# =============================================================================
# 主程序
# =============================================================================

show_help() {
    echo ""
    echo "BMAD 后端服务管理脚本"
    echo ""
    echo "用法：$0 <命令> [端口]"
    echo ""
    echo "命令:"
    echo "  start       启动服务（默认端口：$DEFAULT_PORT）"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      显示服务状态"
    echo "  logs [-f]   查看日志（-f 跟踪模式）"
    echo "  clean       清理 Python 缓存"
    echo "  cleanup     清理所有 Python 进程（强制）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start 8000      # 启动到 8000 端口"
    echo "  $0 restart         # 重启服务（默认 8000 端口）"
    echo "  $0 logs -f         # 跟踪日志输出"
    echo "  $0 status          # 查看服务状态"
    echo ""
}

main() {
    local command="${1:-help}"
    
    case "$command" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        clean)
            clean_cache
            ;;
        cleanup)
            cleanup_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"
