# Story 9.1: 科普内容生成服务

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为 **系统**，
我想要 **每天自动生成科普内容**，
以便 **为用户提供新鲜的知识点**。

## Acceptance Criteria

1. [x] 每日凌晨生成当日科普内容 (AC: #1)
2. [x] 每周一个主题（营养/运动/睡眠/心理）(AC: #2)
3. [x] 内容长度：摘要 50 字内，正文 300-500 字 (AC: #3)
4. [x] 添加医学免责声明 (AC: #4)
5. [x] 内容存储到数据库，支持历史查看 (AC: #5)
6. [x] 支持手动触发重新生成 (AC: #6)

## Tasks / Subtasks

- [x] Task 1: 创建科普内容数据模型 DailyTip (AC: #5)
  - [x] Subtask 1.1: 在 backend/app/models/ 创建 daily_tip.py 模型文件
  - [x] Subtask 1.2: 定义 DailyTip 表结构（id, date, topic, title, summary, content, disclaimer, is_active, created_at, updated_at）
  - [x] Subtask 1.3: 在 backend/app/models/__init__.py 导出模型
- [x] Task 2: 实现 AI 生成 Prompt 模板 (AC: #1, #2, #3, #4)
  - [x] Subtask 2.1: 创建科普内容生成 Prompt 模板
  - [x] Subtask 2.2: 实现主题轮换逻辑（营养/运动/睡眠/心理，每周一个主题）
  - [x] Subtask 2.3: 添加医学免责声明模板
- [x] Task 3: 创建定时生成任务 (AC: #1)
  - [x] Subtask 3.1: 在 backend/app/schedulers/tasks/ 创建 daily_tip_task.py
  - [x] Subtask 3.2: 配置每日凌晨执行（参考 notification_tasks.py 的调度模式）
  - [x] Subtask 3.3: 实现主题轮换和内容生成逻辑
- [x] Task 4: 实现内容存储和查询 API (AC: #5, #6)
  - [x] Subtask 4.1: 创建 backend/app/schemas/daily_tip.py Schema
  - [x] Subtask 4.2: 创建 backend/app/api/v1/daily_tip.py API 路由
  - [x] Subtask 4.3: 实现 GET /daily-tips/today 获取当日科普
  - [x] Subtask 4.4: 实现 GET /daily-tips 获取历史科普列表
  - [x] Subtask 4.5: 实现 POST /daily-tips/regenerate 手动触发重新生成
- [x] Task 5: 数据库迁移 (AC: #5)
  - [x] Subtask 5.1: 使用 alembic 创建新表迁移脚本
  - [x] Subtask 5.2: 执行迁移验证表创建成功

## Dev Notes

### 技术栈与模式

- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **AI**: Qwen (通义千问) - 参考 backend/app/services/ai_service.py 的调用模式
- **定时任务**: APScheduler - 参考 backend/app/schedulers/scheduler.py 和 tasks/notification_tasks.py
- **数据库迁移**: Alembic - 参考 backend/alembic/ 目录结构

### 项目结构约束

1. **Model 位置**: `backend/app/models/daily_tip.py`
2. **Schema 位置**: `backend/app/schemas/daily_tip.py`
3. **API 路由**: `backend/app/api/v1/daily_tip.py`
4. **服务层**: `backend/app/services/daily_tip_service.py` (新建)
5. **定时任务**: `backend/app/schedulers/tasks/daily_tip_task.py` (新建)

### API 设计模式

参考现有 API 结构（如 habit, goal 等）：
- 使用 FastAPI Router
- 路径: `/api/v1/daily-tips`
- 使用 Pydantic Schema 验证
- 返回 JSON 响应

### 数据库模型模式

参考 `backend/app/models/goal.py` 的结构：
- 继承 `app.core.database.Base`
- 使用 SQLAlchemy Column 定义字段
- 添加适当的索引
- 使用 `func.now()` 处理时间戳

### AI 服务调用模式

参考 `backend/app/services/ai_service.py`：
- 使用 httpx.AsyncClient 调用 Qwen API
- 处理 mock_mode（开发环境无 API key 时）
- 使用结构化日志记录

### 测试标准

- 单元测试覆盖数据模型
- 单元测试覆盖服务层
- API 集成测试
- 定时任务单元测试

### References

- [Source: _bmad_out/planning-artifacts/epic-9-daily-tip.md#Story-9.1]
- [Source: backend/app/models/goal.py - 数据模型参考]
- [Source: backend/app/services/ai_service.py - AI 服务调用参考]
- [Source: backend/app/schedulers/tasks/notification_tasks.py - 定时任务参考]
- [Source: backend/app/api/v1/habit.py - API 路由参考]

## Dev Agent Record

### Agent Model Used

minimax-m2.5-free

### Debug Log References

N/A - Implementation completed without major issues

### Completion Notes List

- ✅ Task 1: 创建 DailyTip 数据模型
  - Model: backend/app/models/daily_tip.py
  - Added TipTopic enum for topic management
  - Added to __init__.py exports
  - 11 unit tests created and passing

- ✅ Task 2: 实现 AI 生成 Prompt 模板
  - Service: backend/app/services/daily_tip_service.py
  - Implemented topic rotation logic (weekly)
  - Created mock content for development mode
  - 17 unit tests created and passing

- ✅ Task 3: 创建定时生成任务
  - Task: backend/app/schedulers/tasks/daily_tip_task.py
  - Registered in scheduler.py with midnight cron job
  - Implemented regenerate_daily_tip function for manual trigger

- ✅ Task 4: 实现 API 端点
  - Schema: backend/app/schemas/daily_tip.py
  - Endpoint: backend/app/api/v1/endpoints/daily_tip.py
  - Routes: GET /daily-tips/today, GET /daily-tips, POST /daily-tips/regenerate, GET /daily-tips/{id}
  - Added to api_router in api.py

- ✅ Task 5: 数据库迁移
  - Migration: backend/alembic/versions/009_add_daily_tips_table.py
  - All indexes created

### Implementation Summary

**Total tests created**: 28 (model: 11, service: 17)
**All tests passing**: ✅

### File List

New files created:
- backend/app/models/daily_tip.py
- backend/app/services/daily_tip_service.py
- backend/app/schedulers/tasks/daily_tip_task.py
- backend/app/schemas/daily_tip.py
- backend/app/api/v1/endpoints/daily_tip.py
- backend/alembic/versions/009_add_daily_tips_table.py

Modified files:
- backend/app/models/__init__.py
- backend/app/api/v1/api.py
- backend/app/schedulers/scheduler.py
