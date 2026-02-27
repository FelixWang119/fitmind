# 短期记忆系统架构文档 (v2.0)

**版本**: v2.0  
**更新日期**: 2026-02-26  
**状态**: ✅ 已实施

---

## 概述

短期记忆系统采用 **SQLite 持久化 FIFO 队列**，实现"进入→溢出→索引→长期记忆"的完整数据流转。

### v2.0 核心变更
- ✅ **SQLite 持久化队列**: 替代内存队列，重启自动恢复
- ✅ **移除启动加载**: 不再需要从数据库加载 `is_indexed=False` 记录
- ✅ **移除 is_indexed 字段**: 队列状态由 SQLite 内部管理
- ✅ **简化架构**: 零配置部署，无需额外服务

---

## 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                     短期记忆系统 (v2.0)                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │      SQLitePersistentQueue (嵌入式持久化)            │     │
│  │  ┌───────────────────────────────────────────────┐  │     │
│  │  │ [最新] ← 数据流 ← ← ← ← [最旧]                 │  │     │
│  │  │        窗口大小：100 条/用户                    │  │     │
│  │  │        存储：./data/memory_queue.db            │  │     │
│  │  └───────────────────────────────────────────────┘  │     │
│  │           ▲                                          │     │
│  │           │ 溢出触发                                 │     │
│  └───────────┼──────────────────────────────────────────┘     │
│              │                                              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │      持久化层：UnifiedMemory (PostgreSQL + pgvector) │     │
│  │  - content_raw, content_summary, content_keywords   │     │
│  │  - source_type, source_id, importance_score         │     │
│  │  - embedding (向量)                                  │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘

重启恢复：✅ SQLite 文件自动恢复，无需手动加载
```

---

## 数据流

### 1. 新数据流程

```
用户操作 (打卡/对话)
    ↓
创建源数据记录 (meals/exercise_checkins/habits/health_records)
    ↓
ShortTermMemoryService.add_memory() 入队
    ↓
SQLiteQueue.push() 写入队列
    ↓
检查队列大小
    ↓
if > 100 条:
    ├─ 弹出最旧数据
    ├─ 触发索引 (MemoryIndexService)
    ├─ 写入 UnifiedMemory (pgvector)
    └─ 完成 (不再标记 is_indexed)
```

### 2. 重启恢复流程

```
服务器启动
    ↓
初始化 SQLiteQueue
    ↓
自动从 memory_queue.db 加载队列状态
    ↓
完成 (无需数据库查询)
```

**对比 v1.0 (已废弃)**:
```diff
- 服务器启动
-     ↓
- 查询 is_indexed = false 的记录 (最近 7 天)
-     ↓
- 加载到短期队列（每个用户最多 100 条）
-     ↓
- 等待新数据入队
```

### 3. Agent 查询

```
Agent 提问
    ↓
MemoryQueryService.get_all_memories()
    ↓
合并短期队列 (SQLite) + 长期记忆 (unified_memory 表)
    ↓
返回格式化上下文
```

---

## 核心服务

### ShortTermMemoryService

**实现文件**: `/backend/app/services/short_term_memory.py`

```python
class ShortTermMemoryService:
    """短期记忆管理服务 (v2.0)"""
    
    def __init__(self, queue: MemoryQueueInterface = None, max_size: int = 100):
        # v2.0: 默认使用 SQLiteQueue
        self.queue = queue or create_queue_instance(max_size=max_size)
        self.max_size = max_size
    
    def add_memory(self, user_id: int, event_data: Dict) -> Optional[Dict]:
        """
        添加记忆到队列
        
        Returns:
            如果队列溢出，返回被挤出的记录 (用于触发索引)
            否则返回 None
        """
        return self.queue.push(user_id, event_data)
    
    def get_recent_memories(self, user_id: int, limit: int = 20) -> List[Dict]:
        """获取用户最近的短期记忆"""
        return self.queue.get_all(user_id)[:limit]
    
    def get_queue_size(self, user_id: int) -> int:
        """获取队列当前大小"""
        return self.queue.size(user_id)
```

### SQLiteQueue

**实现文件**: `/backend/app/services/sqlite_queue.py`

```python
class SQLiteQueue(MemoryQueueInterface):
    """SQLite 持久化队列实现"""
    
    def __init__(self, max_size: int = 100, db_path: str = "./data/memory_queue.db"):
        self.max_size = max_size
        self.db_path = db_path
        self._init_db()  # 初始化数据库表
    
    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        加入队列
        
        Returns:
            如果队列溢出，返回被挤出的最旧数据；否则返回 None
        """
        # 自动持久化到 SQLite 文件
```

**关键特性**:
- ✅ **自动持久化**: 每次操作自动提交到 SQLite 文件
- ✅ **重启恢复**: 实例化时自动加载已有数据
- ✅ **FIFO 顺序**: 严格保证先进先出
- ✅ **容量限制**: 每用户 100 条限制

### MemoryIndexService

**实现文件**: `/backend/app/services/memory_index_service.py`

```python
async def index_memory_to_long_term(db: Session, overflow_item: Dict) -> bool:
    """
    将溢出的短期记忆索引到长期记忆
    
    v2.0 变更:
    - 不再调用 _mark_source_as_indexed (已删除)
    - 不再标记源记录的 is_indexed 字段 (字段已删除)
    """
    # 1. 提取记忆摘要
    # 2. 生成向量嵌入
    # 3. 创建 UnifiedMemory 记录
    # 4. 完成 (不再标记 is_indexed)
```

### MemoryQueryService

**实现文件**: `/backend/app/services/memory_query_service.py`

```python
class MemoryQueryService:
    def get_all_memories(self, user_id: int, time_range: str = "today") -> Dict:
        """合并短期 + 长期记忆"""
        
    def get_today_summary(self, user_id: int) -> Dict:
        """获取今日摘要"""
        
    def get_memory_context_for_agent(self, user_id: int) -> str:
        """为 Agent 生成上下文字符串"""
```

---

## 数据格式

### 统一数据结构 (Queue 格式)

```json
{
  "event_id": "user123_1740556800.123",
  "user_id": 123,
  "timestamp": "2026-02-26T14:30:00Z",
  "event_type": "meal|exercise|habit|weight|water|conversation",
  "event_source": "breakfast|running|喝水 |...",
  "content": "记录了早餐（牛奶麦片），摄入热量约 350 千卡",
  "metrics": {
    "calories": 350,
    "protein": 15,
    "carbs": 45,
    "fat": 8
  },
  "context": {
    "meal_type": "breakfast"
  },
  "source_table": "meals",
  "source_id": 123
}
```

---

## 配置

### 环境变量

```bash
# 队列后端选择 (v2.0 默认 SQLite)
MEMORY_QUEUE_BACKEND=sqlite  # 可选：sqlite, memory, redis

# SQLite 队列文件路径 (可选)
SQLITE_QUEUE_DB_PATH=./data/memory_queue.db

# 队列容量 (可选)
MEMORY_QUEUE_MAX_SIZE=100
```

### Docker Compose 配置

```yaml
services:
  backend:
    environment:
      - MEMORY_QUEUE_BACKEND=sqlite
      - SQLITE_QUEUE_DB_PATH=/app/data/memory_queue.db
    volumes:
      - ./data:/app/data  # 持久化 SQLite 文件
```

### Kubernetes 配置

```yaml
volumeMounts:
- name: memory-queue-storage
  mountPath: /data
volumes:
- name: memory-queue-storage
  persistentVolumeClaim:
    claimName: memory-queue-pvc
```

---

## 文件列表

| 文件 | 功能 | v2.0 状态 |
|------|------|----------|
| `app/services/short_term_memory.py` | 队列工厂和服务 | ✅ 已更新 |
| `app/services/sqlite_queue.py` | SQLite 持久化队列 | ✅ 新增 |
| `app/services/memory_index_service.py` | 索引服务 | ✅ 已更新 |
| `app/services/memory_index_pipeline.py` | 批量索引 Pipeline | ❌ 已删除 (根据ADR-001) |
| `app/main.py` | 启动集成 | ✅ 已更新 |
| `app/services/short_term_memory_loader.py` | 启动加载器 | ❌ 已删除 |

---

## 性能特性

### 基准测试

| 操作 | 延迟 (P50) | 延迟 (P99) | 备注 |
|------|-----------|-----------|------|
| push (写入) | < 5ms | < 20ms | SQLite 嵌入式 |
| get_all (读取) | < 10ms | < 50ms | 100 条记录 |
| 重启恢复 | < 1s | < 2s | 1000 条记录 |

### 资源使用

| 指标 | 预期值 | 说明 |
|------|--------|------|
| SQLite 文件大小 | ~1MB/1000 条 | 取决于数据复杂度 |
| 内存占用 | < 10MB | 连接池缓存 |
| 磁盘 I/O | 低 | 嵌入式数据库 |

---

## 监控指标

### 关键指标

```python
# 推荐监控的指标
QUEUE_SIZE = "memory_queue_size"  # 队列大小
PUSH_LATENCY = "memory_queue_push_latency_ms"  # 写入延迟
GET_LATENCY = "memory_queue_get_latency_ms"  # 读取延迟
OVERFLOW_COUNT = "memory_queue_overflow_count"  # 溢出次数
FILE_SIZE = "memory_queue_file_size_bytes"  # 文件大小
```

### 告警规则

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| SQLite 文件大小 | > 100MB | ⚠️ Warning |
| 写入延迟 (P99) | > 100ms | ⚠️ Warning |
| 读取延迟 (P99) | > 200ms | ⚠️ Warning |

---

## 故障排查

### Q1: 重启后队列数据丢失？
**A**: 检查 SQLite 文件路径是否正确挂载
```bash
# 验证文件存在
ls -la ./data/memory_queue.db

# 检查文件权限
chmod 644 ./data/memory_queue.db
```

### Q2: 队列操作变慢？
**A**: 检查 SQLite 文件大小和磁盘 I/O
```bash
# 检查文件大小
du -h ./data/memory_queue.db

# 检查磁盘空间
df -h ./data
```

### Q3: 并发写入冲突？
**A**: SQLite 使用文件锁，确保单实例部署
```bash
# 检查文件锁
lsof ./data/memory_queue.db

# 多实例场景考虑使用 Redis 队列
MEMORY_QUEUE_BACKEND=redis
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-02-26 | SQLite 持久化队列，移除启动加载，删除 is_indexed 字段 |
| v1.0 | 2026-02-21 | 初始版本，内存队列 + 启动加载器 |

---

## 参考文档

- [记忆系统架构 v2.0](./architecture/MEMORY_SYSTEM_ARCHITECTURE.md)
- [实施总结](./MEMORY_SYSTEM_V2_IMPLEMENTATION_SUMMARY.md)
- [SQLite 队列实现](../backend/app/services/sqlite_queue.py)
- [数据库迁移脚本](../backend/alembic/versions/2026_02_26_v2_0_remove_is_indexed_columns.py)
