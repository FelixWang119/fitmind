# Makefile for BMAD Project
.PHONY: help start stop test lint format clean setup-db migrate

help:
	@echo "可用命令:"
	@echo "  make help      - 显示此帮助信息"
	@echo "  make start     - 启动开发环境"
	@echo "  make stop      - 停止开发环境"
	@echo "  make test      - 运行所有测试"
	@echo "  make lint      - 运行代码检查"
	@echo "  make format    - 格式化代码"
	@echo "  make clean     - 清理临时文件"
	@echo "  make setup-db  - 设置数据库"
	@echo "  make migrate   - 运行数据库迁移"

start:
	@echo "启动开发环境..."
	docker-compose up -d
	@echo "服务已启动:"
	@echo "  - 前端: http://localhost:3000"
	@echo "  - 后端API: http://localhost:8000"
	@echo "  - API文档: http://localhost:8000/docs"
	@echo "  - 数据库: localhost:5432"

stop:
	@echo "停止开发环境..."
	docker-compose down

restart: stop start

test:
	@echo "运行后端测试..."
	cd backend && poetry run pytest -v
	@echo "运行前端测试..."
	cd frontend && npm test

lint:
	@echo "检查后端代码..."
	cd backend && poetry run black --check . && poetry run isort --check .
	@echo "检查前端代码..."
	cd frontend && npm run lint

format:
	@echo "格式化后端代码..."
	cd backend && poetry run black . && poetry run isort .
	@echo "格式化前端代码..."
	cd frontend && npm run format

clean:
	@echo "清理临时文件..."
	docker-compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache backend/*.log
	rm -rf frontend/node_modules frontend/dist frontend/.next
	rm -rf *.db *.db-journal
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

setup-db:
	@echo "初始化数据库..."
	docker-compose exec postgres psql -U weight_ai_user -d weight_ai_db -f /docker-entrypoint-initdb.d/01-init.sql

migrate:
	@echo "运行数据库迁移..."
	cd backend && poetry run alembic upgrade head

logs:
	@echo "查看服务日志..."
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

status:
	@echo "服务状态:"
	docker-compose ps

build:
	@echo "构建Docker镜像..."
	docker-compose build

dev:
	@echo "启动开发模式..."
	docker-compose up

# 开发环境快速命令
up: start
down: stop
t: test
l: lint
f: format
c: clean