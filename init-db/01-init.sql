-- 初始化数据库脚本
-- 创建扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgvector";

-- 设置搜索路径
SET search_path TO public;

-- 创建表注释
COMMENT ON SCHEMA public IS 'Weight AI Agent Database Schema';

-- 注意：实际表结构将由Alembic迁移创建
-- 此文件仅用于数据库初始化配置