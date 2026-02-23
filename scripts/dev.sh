#!/bin/bash

# 体重管理AI代理 - 开发脚本
# 简化Docker操作，提供一键启动、测试、日志查看等功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 帮助信息
show_help() {
    cat << EOF
体重管理AI代理 - 开发脚本

使用方法: ./dev.sh <命令> [参数]

命令:
  start       启动所有服务（前端、后端、数据库）
  stop        停止所有服务
  restart     重启所有服务
  logs        查看服务日志
  status      查看服务状态
  test        运行测试
  build       构建所有服务
  clean       清理所有容器和镜像
  db          数据库操作
    init      初始化数据库
    migrate   运行数据库迁移
    reset     重置数据库（删除所有数据）
  help        显示此帮助信息

示例:
  ./dev.sh start      # 启动所有服务
  ./dev.sh logs       # 查看日志
  ./dev.sh test       # 运行测试
  ./dev.sh db init    # 初始化数据库
EOF
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        echo "请先安装Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose未安装${NC}"
        echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# 启动服务
start_services() {
    echo -e "${BLUE}启动体重管理AI代理服务...${NC}"
    
    # 复制环境变量模板（如果不存在）
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        echo -e "${YELLOW}创建.env文件（从.env.example复制）${NC}"
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo -e "${YELLOW}请编辑.env文件配置您的API密钥${NC}"
    fi
    
    # 启动服务
    cd "$PROJECT_ROOT"
    docker-compose up -d
    
    echo -e "${GREEN}服务启动成功！${NC}"
    echo -e "${BLUE}访问地址:${NC}"
    echo "前端: http://localhost:3000"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}使用 './dev.sh logs' 查看日志${NC}"
    echo -e "${YELLOW}使用 './dev.sh stop' 停止服务${NC}"
}

# 停止服务
stop_services() {
    echo -e "${BLUE}停止体重管理AI代理服务...${NC}"
    cd "$PROJECT_ROOT"
    docker-compose down
    echo -e "${GREEN}服务已停止${NC}"
}

# 重启服务
restart_services() {
    echo -e "${BLUE}重启体重管理AI代理服务...${NC}"
    cd "$PROJECT_ROOT"
    docker-compose restart
    echo -e "${GREEN}服务重启完成${NC}"
}

# 查看日志
show_logs() {
    cd "$PROJECT_ROOT"
    
    if [ -z "$1" ]; then
        # 查看所有服务日志
        docker-compose logs -f
    else
        # 查看特定服务日志
        docker-compose logs -f "$1"
    fi
}

# 查看状态
show_status() {
    cd "$PROJECT_ROOT"
    echo -e "${BLUE}服务状态:${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE}容器资源使用:${NC}"
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || echo "无法获取资源使用信息"
}

# 运行测试
run_tests() {
    cd "$PROJECT_ROOT"
    
    case "$1" in
        "frontend")
            echo -e "${BLUE}运行前端测试...${NC}"
            cd frontend
            npm test
            ;;
        "backend")
            echo -e "${BLUE}运行后端测试...${NC}"
            cd backend
            python -m pytest tests/ -v
            ;;
        "e2e")
            echo -e "${BLUE}运行端到端测试...${NC}"
            cd frontend
            npm run e2e
            ;;
        *)
            echo -e "${BLUE}运行所有测试...${NC}"
            echo -e "${YELLOW}前端测试:${NC}"
            cd frontend && npm test && cd ..
            echo -e "\n${YELLOW}后端测试:${NC}"
            cd backend && python -m pytest tests/ -v && cd ..
            ;;
    esac
}

# 构建服务
build_services() {
    cd "$PROJECT_ROOT"
    echo -e "${BLUE}构建所有服务...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}构建完成${NC}"
}

# 清理
cleanup() {
    cd "$PROJECT_ROOT"
    echo -e "${BLUE}清理所有容器和镜像...${NC}"
    
    read -p "确定要删除所有容器和镜像吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        echo -e "${GREEN}清理完成${NC}"
    else
        echo -e "${YELLOW}取消清理${NC}"
    fi
}

# 数据库操作
db_operation() {
    cd "$PROJECT_ROOT"
    
    case "$1" in
        "init")
            echo -e "${BLUE}初始化数据库...${NC}"
            # 等待数据库启动
            echo "等待数据库启动..."
            sleep 5
            
            # 运行迁移
            cd backend
            python -m alembic upgrade head
            echo -e "${GREEN}数据库初始化完成${NC}"
            ;;
        "migrate")
            echo -e "${BLUE}运行数据库迁移...${NC}"
            cd backend
            python -m alembic upgrade head
            echo -e "${GREEN}数据库迁移完成${NC}"
            ;;
        "reset")
            echo -e "${RED}警告: 这将删除所有数据！${NC}"
            read -p "确定要重置数据库吗？(y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}重置数据库...${NC}"
                cd backend
                python -m alembic downgrade base
                python -m alembic upgrade head
                echo -e "${GREEN}数据库重置完成${NC}"
            else
                echo -e "${YELLOW}取消重置${NC}"
            fi
            ;;
        *)
            echo -e "${RED}未知的数据库操作: $1${NC}"
            echo "可用操作: init, migrate, reset"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    check_docker
    
    case "$1" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$2"
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests "$2"
            ;;
        "build")
            build_services
            ;;
        "clean")
            cleanup
            ;;
        "db")
            db_operation "$2"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            if [ -z "$1" ]; then
                show_help
            else
                echo -e "${RED}未知命令: $1${NC}"
                show_help
                exit 1
            fi
            ;;
    esac
}

# 运行主函数
main "$@"