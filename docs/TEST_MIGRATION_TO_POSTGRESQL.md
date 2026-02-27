# 测试架构迁移总结：SQLite → PostgreSQL

## 迁移日期
2026-02-27

## 迁移目标
将测试架构从 SQLite 迁移到本地 PostgreSQL，解决 JSONB 类型兼容性问题。

---

## ✅ 已完成的工作

### 1. 创建独立的测试数据库环境

**数据库用户**:
- 用户名：`weight_ai_test_user`
- 密码：`weight_ai_test_password`
- 权限：独立 schema 权限

**测试数据库**:
- 数据库名：`weight_ai_db_test`
- 扩展：pgvector (向量搜索)
- Schema：public

**创建命令**:
```bash
# 创建用户
CREATE ROLE weight_ai_test_user WITH LOGIN PASSWORD 'weight_ai_test_password';

# 创建数据库
CREATE DATABASE weight_ai_db_test OWNER weight_ai_test_user;

# 授予权限
GRANT ALL ON SCHEMA public TO weight_ai_test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weight_ai_test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weight_ai_test_user;

# 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. 更新测试配置

**文件**: `backend/tests/conftest.py`

**主要变更**:
```python
# 之前 (SQLite)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
engine = create_engine(
    "sqlite:///./test_integration.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 现在 (PostgreSQL)
os.environ["DATABASE_URL"] = "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"
engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
```

### 3. 模型修复

**文件**: `backend/app/models/notification.py`

**问题**: PostgreSQL ENUM 类型不支持 `lower()` 函数

**修复**:
```python
# 之前
postgresql_where=func.lower(notification_status) == "pending"

# 修复后
postgresql_where=notification_status == "pending"
```

### 4. 创建专用测试配置

**文件**: `backend/tests/conftest_memory.py`

为 Agent Memory 测试创建专用配置，避免其他模型兼容性问题。

---

## 📋 测试运行指南

### 基本命令

```bash
cd /Users/felix/bmad/backend

# 运行 Agent Memory E2E 测试
pytest tests/e2e/test_agent_memory_e2e.py -v

# 运行日志验证测试
pytest tests/e2e/test_memory_logging.py -v

# 运行所有 memory 相关测试
pytest tests/ -k memory -v

# 运行单个测试
pytest tests/e2e/test_agent_memory_e2e.py::TestShortTermMemory::test_get_recent_memories -v
```

### 并行运行

```bash
# 使用多进程加速
pytest tests/e2e/ -v -n auto

# 指定进程数
pytest tests/e2e/ -v -n 4
```

### 生成测试报告

```bash
# HTML 报告
pytest tests/e2e/test_agent_memory_e2e.py -v --html=reports/test-report.html

# 覆盖率报告
pytest tests/e2e/test_agent_memory_e2e.py -v --cov=app --cov-report=html
```

---

## 🔍 验证步骤

### 1. 验证数据库连接

```bash
cd /Users/felix/bmad/backend
python -c "
from sqlalchemy import create_engine, text

TEST_DATABASE_URL = 'postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test'

engine = create_engine(TEST_DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT current_user, current_database()'))
    row = result.fetchone()
    print(f'✅ 连接成功：{row[0]}@{row[1]}')
"
```

**预期输出**:
```
✅ 连接成功：weight_ai_test_user@weight_ai_db_test
```

### 2. 验证 pgvector 扩展

```bash
psql -h 127.0.0.1 -U weight_ai_test_user -d weight_ai_db_test -c "\dx"
```

**预期输出**包含:
```
  Name   | Version |   Schema   | Description
---------+---------+------------+---------------------
 vector  | 0.8.1   | public     | vector data type and ivfflat index for embedding
```

### 3. 运行测试验证

```bash
pytest tests/unit/test_memory_extractor.py -v --tb=short
```

---

## ⚠️ 已知问题

### 问题 1: 系统模型外键类型不匹配

**错误**:
```
foreign key constraint "system_configs_created_by_fkey" cannot be implemented
DETAIL: Key columns "created_by" and "id" are of incompatible types: uuid and integer.
```

**影响**: `system_configs` 表无法创建

**临时解决方案**:
- 使用 `conftest_memory.py` 专用配置
- 在测试中 mock 不相关的服务

**根本解决**: 需要修复 `system_configs` 模型的外键定义

### 问题 2: 部分单元测试依赖完整数据库

某些单元测试会尝试创建所有表，导致失败。

**解决方案**:
- 使用 `@pytest.mark.unit` 标记纯单元测试
- 使用 `@pytest.mark.integration` 标记集成测试
- 在 pytest.ini 中配置标记筛选

---

## 📊 对比：SQLite vs PostgreSQL

| 特性 | SQLite (之前) | PostgreSQL (现在) |
|------|--------------|------------------|
| JSONB 支持 | ❌ | ✅ |
| pgvector | ❌ | ✅ |
| 并发写入 | ❌ | ✅ |
| 事务隔离 | 有限 | 完整 |
| 生产一致性 | 低 | 高 |
| 测试速度 | 快 | 中等 |
| 数据隔离 | 文件级 | Schema 级 |

---

## 🎯 下一步建议

### 1. 修复系统模型 (高优先级)

修复 `system_configs` 表的外键类型问题：

```python
# app/models/system_config.py
# 将 created_by 和 updated_by 改为 Integer 类型
created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
```

### 2. 添加测试标记 (中优先级)

在 `pytest.ini` 中完善标记系统：

```ini
[pytest]
markers =
    unit: 单元测试（不需要数据库）
    integration: 集成测试（需要数据库）
    e2e: 端到端测试
    memory: 记忆系统测试
    p0: P0 关键测试
    p1: P1 高优先级测试
    p2: P2 一般测试
```

### 3. CI/CD 集成 (中优先级)

更新 GitHub Actions 使用 PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: weight_ai_test_user
      POSTGRES_PASSWORD: weight_ai_test_password
      POSTGRES_DB: weight_ai_db_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

### 4. 性能优化 (低优先级)

- 使用测试数据库模板加速创建
- 实现测试数据工厂模式
- 添加数据库连接池监控

---

## 📚 相关文档

- [ADR-001: 记忆索引管道设计](../docs/architecture/decisions/ADR-001-memory-index-pipeline-design.md)
- [Agent Memory 测试总结](../_bmad_out/implementation-artifacts/tests/test-agent-memory.md)
- [PostgreSQL 本地设置](../docs/LOCAL_POSTGRES_SETUP.md)

---

## 🎉 迁移成果

✅ **测试数据库已就绪**
- 独立用户：`weight_ai_test_user`
- 独立数据库：`weight_ai_db_test`
- 扩展支持：pgvector

✅ **配置已更新**
- `conftest.py` 使用 PostgreSQL
- 数据库连接验证通过

✅ **模型修复**
- notification.py ENUM 索引修复

✅ **测试可运行**
- 基础单元测试可通过
- E2E 测试架构已就绪

---

**迁移执行者**: BMAD QA Agent  
**验证状态**: ✅ 基础功能已验证  
**文档语言**: 中文
