-- PostgreSQL 初始化脚本
-- 此脚本在 Docker 容器首次启动时自动执行

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 设置搜索路径
SET search_path TO public;

-- 创建表注释
COMMENT ON SCHEMA public IS 'Weight AI Agent Database Schema - PostgreSQL with pgvector';

-- 注意：实际表结构将由 Alembic 迁移创建
-- 此文件仅用于数据库初始化配置和扩展安装

-- 输出完成消息
SELECT 'Database extensions installed successfully!' AS message;
SELECT 'Pgvector version: ' || extversion FROM pg_extension WHERE extname = 'vector';
