# 记忆索引配置指南

## 📊 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| **PostgreSQL** | ✅ 运行中 | 数据库已配置 |
| **pgvector** | ❌ 未安装 | 需要安装才能支持向量索引 |
| **记忆表** | ❌ 未创建 | 迁移分支问题导致未执行 |

---

## 🎯 记忆系统核心功能

### 1. 统一记忆存储 (UnifiedMemory)

```sql
-- 核心表结构
unified_memory:
  - id (UUID)
  - user_id (Integer)
  - memory_type (String) - 记忆类型
  - content_raw (Text) - 原始内容
  - content_summary (Text) - LLM 摘要
  - content_keywords (JSON) - 关键词
  - embedding (Text) - 向量数据 ⭐
  - source_type (String) - 来源类型
  - source_id (String) - 来源 ID
  - importance_score (Float) - 重要性评分
```

### 2. 向量索引支持

```sql
-- pgvector 提供向量相似度搜索
CREATE EXTENSION vector;

-- 向量字段存储
embedding: List[float]  -- 存储为 JSON 格式

-- 相似度查询示例
SELECT * FROM unified_memory 
ORDER BY embedding <-> '[0.1,0.2,0.3,...]'::vector 
LIMIT 10;
```

### 3. 长期记忆表

- `user_long_term_memory` - 用户长期记忆
- `context_summaries` - 上下文摘要
- `habit_patterns` - 习惯模式
- `data_associations` - 数据关联

---

## 🚀 配置步骤

### 方式一：使用自动脚本（推荐）

```bash
cd /Users/felix/bmad
./scripts/setup-memory-index.sh
```

脚本会自动：
1. ✅ 安装 pgvector
2. ✅ 启用向量扩展
3. ✅ 运行 Alembic 迁移
4. ✅ 创建记忆表
5. ✅ 验证配置

### 方式二：手动配置

#### 1. 安装 pgvector

```bash
# 使用 Homebrew 安装
brew install pgvector

# 重启 PostgreSQL
./scripts/services postgres restart
```

#### 2. 启用扩展

```bash
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db << 'EOF'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF
```

#### 3. 运行迁移

```bash
cd /Users/felix/bmad/backend

# 查看当前迁移状态
alembic current

# 升级到最新版本（包含记忆表）
alembic upgrade head
```

#### 4. 验证配置

```bash
# 检查 pgvector
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "SELECT * FROM pg_extension WHERE extname='vector';"

# 检查记忆表
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "\dt" | grep memory

# 检查表结构
PGPASSWORD=weight_ai_password psql -h 127.0.0.1 -U weight_ai_user -d weight_ai_db -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'unified_memory';"
```

---

## 🧪 测试记忆功能

### 测试向量搜索

```python
# tests/test_memory_vector.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.memory import UnifiedMemory

engine = create_engine("postgresql://weight_ai_user:weight_ai_password@127.0.0.1:5432/weight_ai_db")

with Session(engine) as session:
    # 创建测试记忆
    memory = UnifiedMemory(
        user_id=1,
        memory_type="习惯打卡",
        content_summary="用户每天早上跑步 5 公里",
        source_type="habit_record",
        source_id="test_001",
        importance_score=8.0
    )
    memory.set_embedding([0.1, 0.2, 0.3, 0.4, 0.5])  # 示例向量
    session.add(memory)
    session.commit()
    
    # 测试向量相似度搜索
    query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
    results = session.execute(
        """
        SELECT id, content_summary, 
               embedding <-> :query_vector::vector AS distance
        FROM unified_memory
        ORDER BY distance
        LIMIT 5
        """,
        {"query_vector": str(query_vector)}
    )
    
    for row in results:
        print(f"记忆：{row.content_summary}, 距离：{row.distance}")
```

### 测试记忆提取

```bash
# 运行记忆系统测试
cd /Users/felix/bmad/backend
pytest tests/unit/test_memory_extractor.py -v
```

---

## 📝 记忆类型说明

| 记忆类型 | 说明 | 来源 |
|----------|------|------|
| `打卡_pattern` | 用户打卡习惯模式 | habit_record |
| `偏好_inferred` | 推断的用户偏好 | conversation |
| `目标_explicit` | 明确的目标 | conversation |
| `习惯_completed` | 完成的习惯 | habit_record |
| `里程碑_achieved` | 达成的里程碑 | health_record |
| `趋势_insight` | 数据趋势洞察 | health_record |
| `关联_causal` | 因果关系关联 | data_association |

---

## 🔍 常见问题

### Q: pgvector 安装失败？

```bash
# 尝试从源码安装
brew install postgresql
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Q: 迁移失败？

```bash
# 重置迁移状态
cd /Users/felix/bmad/backend
alembic stamp base
alembic upgrade head
```

### Q: 向量搜索不工作？

```sql
-- 检查 pgvector 是否启用
SELECT * FROM pg_extension WHERE extname='vector';

-- 检查 embedding 字段
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'unified_memory' 
AND column_name = 'embedding';
```

---

## 📚 相关文档

- [记忆系统架构](../backend/app/services/memory_extractor.py)
- [向量索引实现](../backend/app/services/embedding/)
- [记忆索引管道](../backend/app/services/memory_index_pipeline.py)

---

**创建时间**: 2026-02-26  
** PostgreSQL**: 16.12 + pgvector
