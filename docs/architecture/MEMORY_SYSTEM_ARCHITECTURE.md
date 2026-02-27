# 记忆系统架构设计文档

**版本**: v2.0  
**创建日期**: 2026-02-26  
**更新日期**: 2026-02-26  
**状态**: 已确认 ✅  
**主要变更**: SQLite持久化队列作为默认实现，移除内存队列选项

---

## 一、核心设计原则

### 1.1 两级记忆架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         记忆系统整体架构 (v2.0)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  短期记忆                          长期记忆                              │
│  ┌─────────────────────────────────┐  ┌────────────────┐              │
│  │ SQLitePersistentQueue           │  │ unified_memory │              │
│  │ (SQLite持久化队列，默认实现)      │  │ (pgvector)     │              │
│  │ • 嵌入式持久化，无需独立服务       │  │ (永久存储)      │              │
│  │ • 重启自动恢复，无需加载逻辑       │  │                │              │
│  │ • Redis队列 (未来扩展)            │  │                │              │
│  │ 100 条/用户                      │  │                │              │
│  └─────────────┬───────────────────┘  └────────────────┘              │
│                │ 溢出触发索引                                          │
│                ▼                                                       │
│         ┌─────────────┐                                                │
│         │ 索引服务    │                                                │
│         │ (异步)      │                                                │
│         └─────────────┘                                                │
│                │                                                       │
│                ▼                                                       │
│          写入长期记忆                                                  │
│          (无需 is_indexed 标记)                                        │
│                                                                         │
│  重启恢复策略: ✅ 队列状态自动从SQLite文件恢复，无需额外处理               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计要点

| 设计决策 | 说明 |
|----------|------|
| **短期记忆 = SQLite持久化队列** | ✅ 默认实现，嵌入式持久化，无需独立服务 |
| **队列后端** | ✅ `MEMORY_QUEUE_BACKEND=sqlite` (默认)，`redis` (未来扩展) |
| **长期记忆 = pgvector** | ✅ `unified_memory` 表，永久存储 |
| **索引触发 = 队列溢出** | ✅ 唯一的触发方式，**没有定时任务** |
| **`is_indexed` 字段** | ❌ **已移除** - SQLite队列无需此字段，队列状态自管理 |
| **重启恢复** | ✅ 队列状态自动从SQLite文件恢复，**无需数据库加载逻辑** |
| **查询数据源** | ✅ 短期=SQLite队列，长期=unified_memory 表 |

---

## 二、详细设计

### 2.1 短期记忆 (Short-Term Memory)

**实现文件**: `/backend/app/services/short_term_memory.py`

#### 数据结构

短期记忆队列基于 `MemoryQueueInterface` 接口设计，默认采用SQLite持久化队列实现：

```python
class MemoryQueueInterface:
    """队列抽象接口"""
    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """加入队列，如果溢出返回被挤出的数据"""
        raise NotImplementedError
    
    def get_all(self, user_id: int) -> List[Dict[str, Any]]:
        """获取队列所有数据（从新到旧）"""
        raise NotImplementedError
    
    def size(self, user_id: int) -> int:
        """获取队列大小"""
        raise NotImplementedError
    
    def clear(self, user_id: int) -> None:
        """清空队列"""
        raise NotImplementedError
```

**默认实现**:
- **`SQLiteQueue`** (默认): SQLite持久化队列，嵌入式持久化，无需独立服务，重启自动恢复

**未来扩展**:
- **`RedisQueue`**: Redis队列，支持分布式部署（未来需求）

#### 记忆条目格式

```python
{
    "event_id": "user123_1740556800.123",
    "user_id": 123,
    "timestamp": "2026-02-26T19:00:00",
    "event_type": "meal",              # 事件类型
    "event_source": "dinner",          # 具体来源
    "content": "记录了晚餐，摄入热量 650 千卡",  # 人类可读描述
    "metrics": {                       # 数值指标
        "calories": 650,
        "protein": 25,
        "carbs": 70,
        "fat": 20
    },
    "context": {"meal_type": "dinner"}, # 上下文
    "source_table": "meals",           # 原始数据表
    "source_id": 456                   # 原始记录 ID
}
```

#### 核心操作 (SQLite队列实现)

SQLite队列通过嵌入式数据库实现持久化FIFO队列，核心操作如下：

```python
class SQLiteQueue(MemoryQueueInterface):
    def __init__(self, max_size: int = 100, db_path: str = "./data/memory_queue.db"):
        self.max_size = max_size
        self.db_path = db_path
        self._init_database()
    
    def push(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        加入队列，如果溢出返回被挤出的最旧数据
        
        实现流程:
        1. 将记忆数据序列化为JSON，插入SQLite数据库
        2. 检查该用户的未处理记录数是否超过max_size
        3. 如果超过，查询最旧的未处理记录，标记为已处理并返回
        4. 更新内存缓存加速后续读取
        5. 返回溢出项（如有），触发长期记忆索引
        """
        # 具体实现详见 sqlite_queue.py
        pass
    
    def get_all(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取队列所有数据（从新到旧）
        
        实现流程:
        1. 优先从内存缓存读取（如果存在）
        2. 缓存未命中时，从SQLite数据库查询未处理记录
        3. 按创建时间倒序排列，返回最新数据
        4. 更新内存缓存加速后续读取
        """
        pass
    
    def size(self, user_id: int) -> int:
        """获取队列大小（未处理记录数）"""
        pass
    
    def clear(self, user_id: int) -> None:
        """清空队列（标记所有记录为已处理）"""
        pass
```

#### SQLite队列特性

**核心优势**:
- ✅ **零独立服务**: SQLite作为库嵌入应用进程，无需额外服务部署
- ✅ **重启无损**: 队列状态完全持久化，重启自动恢复，无需数据库加载逻辑
- ✅ **ACID事务**: 保证数据一致性，避免数据丢失或损坏
- ✅ **性能优化**: 内存缓存 + SQLite索引，读取速度接近内存队列
- ✅ **完全兼容**: 实现相同的 `MemoryQueueInterface` 接口，API无缝切换

**配置方式**:
```bash
# 环境变量配置 (SQLite为默认值，可省略)
export MEMORY_QUEUE_BACKEND=sqlite  # 默认值，可省略
export SQLITE_QUEUE_DB_PATH=/app/data/memory_queue.db  # 可选，默认 ./data/memory_queue.db
```

**架构简化**:
使用SQLite队列后，系统实现大幅简化：
- ❌ **移除** `short_term_memory_loader.py` 重启加载模块
- ❌ **移除** 源数据表中的 `is_indexed` 字段（队列状态自管理）
- ❌ **移除** 从数据库加载未索引记录的复杂逻辑
- ✅ **简化** 重启恢复流程：队列状态自动从SQLite文件恢复
- ✅ **简化** 数据一致性维护：队列状态独立管理，不与源数据耦合

---

### 2.2 长期记忆 (Long-Term Memory)

**实现文件**: `/backend/app/models/memory.py`

#### 表结构

```sql
CREATE TABLE unified_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    
    memory_type VARCHAR(50) NOT NULL,
    content_raw TEXT,
    content_summary TEXT NOT NULL,
    content_keywords TEXT[],
    
    embedding VECTOR(768),  -- pgvector 向量
    
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    
    importance_score FLOAT DEFAULT 5.0,
    
    is_indexed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_unified_memory_user_id ON unified_memory(user_id);
CREATE INDEX idx_unified_memory_is_indexed ON unified_memory(is_indexed);
CREATE INDEX idx_unified_memory_embedding ON unified_memory 
    USING ivfflat (embedding vector_cosine_ops);
```

#### 记忆类型

| memory_type | 说明 |
|-------------|------|
| `打卡_pattern` | 打卡行为模式 |
| `偏好_inferred` | 推断的偏好 |
| `目标_explicit` | 明确的目标 |
| `习惯_completed` | 习惯完成记录 |
| `里程碑_achieved` | 成就里程碑 |
| `趋势_insight` | 数据趋势洞察 |
| `关联_causal` | 因果关联 |

---

### 2.3 索引触发机制

**实现文件**: `/backend/app/services/memory_index_service.py`

#### 触发时机

**唯一的触发方式**: **队列溢出时实时触发**

```
用户创建新记录
      ↓
添加到短期记忆队列
      ↓
检查队列长度
      ↓
┌─────────────────┐
│ len >= 100?    │
└───────┬─────────┘
        │
   ┌────┴────┐
   │         │
  否        是
   │         │
   │         ↓
   │    overflow_item = queue.pop()  ← 最旧的数据被挤出
   │         ↓
   │    asyncio.create_task(
   │      index_memory_to_long_term(overflow_item)
   │    )
   │         ↓
   │    后台异步执行索引
   │
   ↓
完成 (数据在队列中)
```

#### 索引流程

```python
async def index_memory_to_long_term(
    db: Session,
    overflow_item: Dict[str, Any],
) -> bool:
    """
    将溢出的短期记忆索引到长期记忆
    
    步骤:
    1. MemoryExtractor 提取摘要
    2. Embedding 生成向量
    3. 写入 unified_memory 表
    4. 标记 is_indexed=True
    """
    
    # 1. 提取记忆摘要
    ai_service = AIService()
    extractor = MemoryExtractor(ai_service=ai_service)
    
    event_type = overflow_item.get('event_type')
    if event_type == 'meal':
        memory_data = extractor.extract_from_nutrition(overflow_item)
    elif event_type == 'exercise':
        memory_data = extractor.extract_from_exercise(overflow_item)
    # ...
    
    # 2. 生成向量嵌入
    embedding_provider = EmbeddingProviderFactory.get_provider()
    embedding = embedding_provider.embed(memory_data['content_summary'])
    
    # 3. 创建长期记忆
    memory = UnifiedMemory(
        user_id=overflow_item['user_id'],
        memory_type=memory_data['memory_type'],
        content_raw=overflow_item.get('content', ''),
        content_summary=memory_data['content_summary'],
        content_keywords=memory_data.get('keywords', []),
        importance_score=memory_data['importance'],
        source_type=overflow_item.get('source_table', 'unknown'),
        source_id=str(overflow_item.get('source_id', '')),
        is_indexed=True,
        is_active=True,
    )
    memory.set_embedding(embedding)
    
    db.add(memory)
    db.commit()
    
    # 4. 更新原始记录的索引状态
    _mark_source_as_indexed(db, overflow_item)
    
    return True
```

---

### 2.4 自动恢复机制 (SQLite队列)

**架构变更**: 采用SQLite持久化队列后，**无需独立的重启恢复逻辑**

#### SQLite队列的自动恢复特性

SQLite队列通过嵌入式数据库实现数据持久化，系统重启时自动恢复队列状态：

1. **数据持久化**: 所有队列操作自动写入SQLite数据库文件
2. **自动恢复**: 应用启动时，队列自动从SQLite文件加载未处理记录
3. **状态一致**: 队列计数、内容和顺序完全恢复，与重启前一致
4. **零配置**: 无需额外代码或配置，自动工作

#### 与传统内存队列的对比

| 特性 | 内存队列 (旧架构) | SQLite队列 (新架构) |
|------|------------------|-------------------|
| **数据持久性** | ❌ 重启丢失 | ✅ 持久化保存 |
| **重启恢复** | ⚠️ 需从数据库加载`is_indexed=False`记录 | ✅ 自动从SQLite文件恢复 |
| **恢复复杂度** | ⚠️ 复杂加载逻辑，多表查询 | ✅ 零代码，自动恢复 |
| **依赖关系** | ⚠️ 依赖源数据表的`is_indexed`字段 | ✅ 独立存储，无外部依赖 |
| **启动速度** | ⚠️ 需加载N条记录，速度慢 | ✅ 瞬间恢复，速度快 |

#### 已移除的组件

使用SQLite队列后，以下组件**已不再需要**：

1. **`short_term_memory_loader.py`** - 重启加载模块 ❌ 移除
2. **源数据表的`is_indexed`字段** - 队列状态标记 ❌ 移除（可优化）
3. **数据库查询逻辑** - 加载未索引记录 ❌ 移除
4. **批量加载逻辑** - `load_memories()`方法 ❌ 移除

#### 简化后的启动流程

```python
# /backend/app/main.py (简化后)
@app.on_event("startup")
async def startup_event():
    # ... 数据库连接 ...
    
    # ✅ SQLite队列自动恢复，无需额外代码
    logger.info("SQLite持久化队列已自动恢复")
    
    # ❌ 不再需要以下代码:
    # from app.services.short_term_memory_loader import load_pending_memories_on_startup
    # loaded_count = load_pending_memories_on_startup(db)
```

**关键优势**:
- ✅ **启动速度提升**: 无需查询数据库和加载记录
- ✅ **代码简化**: 移除复杂重启恢复逻辑
- ✅ **维护性提升**: 队列状态独立管理，不与业务数据耦合
- ✅ **可靠性增强**: SQLite ACID事务保证数据一致性

---

### 2.5 查询服务

**实现文件**: `/backend/app/services/memory_query_service.py`

#### 记忆查询服务

```python
class MemoryQueryService:
    """合并短期记忆和长期记忆的查询服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.short_term_service = get_short_term_memory_service()
    
    def get_all_memories_for_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """获取用户的所有记忆（短期 + 长期）"""
        
        # 1. 短期记忆 = 从内存队列读取
        short_term_memories = self.short_term_service.get_recent_memories(
            user_id, limit=limit
        )
        
        # 2. 长期记忆 = 从 unified_memory 读取
        long_term_memories = (
            self.db.query(UnifiedMemory)
            .filter(
                UnifiedMemory.user_id == user_id,
                UnifiedMemory.is_active == True,
            )
            .order_by(UnifiedMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return {
            "short_term": short_term_data,
            "long_term": long_term_data,
            "total": len(short_term_data) + len(long_term_data),
            "summary": self._generate_summary(short_term_data, long_term_data),
        }
```

#### AI 上下文生成

```python
def get_memory_context_for_agent(user_id: int, db: Session) -> str:
    """
    为 Agent 生成记忆上下文字符串
    
    AI 聊天时调用的主要接口
    """
    query_service = MemoryQueryService(db)
    
    # 1. 获取今日摘要
    today_summary = query_service.get_today_summary(user_id)
    
    # 2. 获取所有记忆（短期 + 长期）
    all_memories = query_service.get_all_memories_for_user(user_id, limit=20)
    
    # 3. 构建上下文字符串
    context_parts = [
        "## 用户今日健康数据",
        f"- 摄入热量：{today_summary['total_calories_intake']} 千卡",
        f"- 运动消耗：{today_summary['total_exercise_calories_burned']} 千卡",
        f"- 运动时长：{today_summary['exercise_duration_minutes']} 分钟",
        "",
        "## 最近行为记录",
    ]
    
    for event in all_memories['summary']['recent_events'][:10]:
        context_parts.append(f"- {event['content']}")
    
    return "\n".join(context_parts)
```

---

## 三、业务层集成

### 3.1 餐食记录集成

**文件**: `/backend/app/api/v1/endpoints/meals.py`

```python
@router.post("", response_model=Meal)
async def create_meal(
    meal_data: MealCreate,
    current_user: User,
    db: Session
):
    # 1. 创建餐食记录
    meal = Meal(
        user_id=current_user.id,
        meal_type=meal_data.meal_type,
        name=meal_data.name,
        calories=meal_data.calories,
        is_indexed=False,  # 初始为 False
    )
    db.add(meal)
    db.commit()
    
    # 2. 添加到短期记忆队列
    meal_type_map = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "加餐"}
    content = f"记录了{meal_type_map.get(meal.meal_type)}，摄入热量{meal.calories}千卡"
    
    overflow_item = get_short_term_memory_service().add_memory(
        user_id=int(current_user.id),
        event_type="meal",
        event_source=meal.meal_type,
        content=content,
        metrics={
            "calories": meal.calories,
            "protein": meal.protein,
            "carbs": meal.carbs,
            "fat": meal.fat,
        },
        context={"meal_type": meal.meal_type},
        source_table="meals",
        source_id=meal.id,
    )
    
    # 3. 如果队列溢出，触发索引
    if overflow_item:
        logger.info(f"短期记忆队列溢出，将索引到长期记忆：{overflow_item.get('event_type')}")
        
        # 异步触发索引 Pipeline（不阻塞请求）
        from app.core.database import get_db
        from app.services.memory_index_service import index_memory_to_long_term
        
        asyncio.create_task(
            index_memory_to_long_term(
                db=next(get_db()),
                overflow_item=overflow_item,
            )
        )
    
    return meal
```

### 3.2 运动打卡集成

**文件**: `/backend/app/api/v1/endpoints/exercise_checkin.py`

```python
@router.post("", response_model=ExerciseCheckIn)
async def create_exercise_checkin(
    checkin_data: ExerciseCheckInCreate,
    current_user: User,
    db: Session
):
    # 1. 创建运动记录
    checkin = ExerciseCheckIn(
        user_id=current_user.id,
        exercise_type=checkin_data.exercise_type,
        duration_minutes=checkin_data.duration_minutes,
        calories_burned=checkin_data.calories_burned,
        is_indexed=False,
    )
    db.add(checkin)
    db.commit()
    
    # 2. 添加到短期记忆队列
    content = f"进行了{checkin.exercise_type}运动"
    if checkin.duration_minutes:
        content += f"时长{checkin.duration_minutes}分钟"
    if checkin.calories_burned:
        content += f"，消耗{checkin.calories_burned}千卡"
    
    overflow_item = get_short_term_memory_service().add_memory(
        user_id=int(current_user.id),
        event_type="exercise",
        event_source=checkin.exercise_type,
        content=content,
        metrics={
            "duration": checkin.duration_minutes,
            "calories": checkin.calories_burned,
            "distance": checkin.distance_km,
        },
        context={
            "category": checkin.category,
            "intensity": checkin.intensity,
        },
        source_table="exercise_checkins",
        source_id=checkin.id,
    )
    
    # 3. 如果队列溢出，触发索引
    if overflow_item:
        logger.info(f"短期记忆队列溢出，将索引到长期记忆")
        
        asyncio.create_task(
            index_memory_to_long_term(
                db=next(get_db()),
                overflow_item=overflow_item,
            )
        )
    
    return checkin
```

### 3.3 AI 聊天集成

**文件**: `/backend/app/services/ai_service.py`

```python
async def send_message(self, message: str, conversation_id: str = None):
    # 1. 获取记忆上下文
    from app.services.memory_query_service import get_memory_context_for_agent
    
    memory_context = get_memory_context_for_agent(self.user_id, self.db)
    # 返回字符串，包含：
    # - 今日健康数据摘要
    # - 短期记忆（最近 100 条行为）
    # - 长期记忆（unified_memory 中的向量化记忆）
    
    # 2. 构建系统提示
    system_prompt = f"""
    你是一个健康管理助手。
    
    {memory_context}
    
    请根据用户的记忆上下文，提供个性化的建议。
    """
    
    # 3. 调用 AI
    response = await self.qwen_client.chat(
        system_prompt=system_prompt,
        user_message=message
    )
    
    return response
```

---

## 四、完整数据流示例

### 场景：用户创建第 101 条餐食记录

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 步骤 1: 用户创建餐食                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ POST /api/v1/meals                                                       │
│ { "meal_type": "dinner", "name": "红烧肉米饭", "calories": 650 }         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 步骤 2: 保存到数据库                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ INSERT INTO meals (user_id, meal_type, name, calories, is_indexed)      │
│ VALUES (123, 'dinner', '红烧肉米饭', 650, False)                         │
│ → meal.id = 456                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 步骤 3: 添加到短期记忆队列                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ short_term_service.add_memory(...)                                      │
│                                                                          │
│ 当前队列大小：100 → 101 (溢出!)                                         │
│ 返回：overflow_item (第 1 条记忆，最旧的)                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 步骤 4: 触发索引 Pipeline（异步）                                          │
├─────────────────────────────────────────────────────────────────────────┤
│ asyncio.create_task(                                                    │
│   index_memory_to_long_term(db, overflow_item)                          │
│ )                                                                       │
│                                                                          │
│ 后台执行:                                                                │
│   1. extractor.extract_from_meal(overflow_item)                         │
│      → summary: "用户习惯食用高热量晚餐"                                   │
│      → keywords: ["晚餐", "高热量", "红烧肉"]                             │
│      → importance: 7.5                                                  │
│                                                                          │
│   2. embedding_provider.embed(summary)                                  │
│      → [0.123, -0.456, 0.789, ...] (768 维向量)                           │
│                                                                          │
│   3. INSERT INTO unified_memory (...)                                   │
│      → memory.id = uuid-xxx                                             │
│      → is_indexed = True                                                │
│                                                                          │
│   4. UPDATE meals SET is_indexed=True WHERE id=1                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 步骤 5: AI 查询时                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ GET /api/v1/ai/chat                                                     │
│ { "message": "我今天吃了什么？" }                                        │
│                                                                          │
│ ↓                                                                        │
│                                                                          │
│ get_memory_context_for_agent(user_id=123)                               │
│   ↓                                                                      │
│   1. 从短期记忆队列获取最近 100 条 (内存，快速)                               │
│   2. 从 unified_memory 获取长期记忆 (pgvector，向量化)                     │
│   3. 合并生成上下文                                                       │
│                                                                          │
│ ↓                                                                        │
│                                                                          │
│ AI 回复："您今天记录了 3 餐，摄入总热量 1850 千卡。晚餐吃了红烧肉米饭..."          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 五、配置说明

### 5.1 配置项

```yaml
# config.yaml
memory:
  # 队列后端配置（短期记忆）
  queue_backend: "memory"       # memory (默认) / sqlite / redis
  
  # 队列容量（短期记忆）
  queue_capacity: 100           # 每用户队列容量（条）
  
  # SQLite队列配置
  sqlite:
    db_path: "./data/memory_queue.db"  # SQLite数据库文件路径
  
  # 长期记忆保留策略
  long_term_retention_days: 0   # 0=永久保留
  
  # 向量嵌入配置
  embedding:
    provider: "local"           # local 或 cloud
    model: "bge-small-zh-v1.5"
    dimension: 768
```

### 5.2 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `MEMORY_QUEUE_BACKEND` | 短期记忆队列后端 (`memory`/`sqlite`/`redis`) | `memory` |
| `SQLITE_QUEUE_DB_PATH` | SQLite队列数据库文件路径 | `./data/memory_queue.db` |
| `REDIS_URL` | Redis连接URL (用于Redis队列) | 无 |
| `EMBEDDING_MODEL_PATH` | 本地模型路径 | `./models/bge-small-zh-v1.5` |
| `EMBEDDING_DEVICE` | 设备 (cpu/cuda) | `cpu` |

---

## 六、文件结构

```
backend/app/
├── services/
│   ├── short_term_memory.py          # 短期记忆队列服务
│   ├── sqlite_queue.py              # SQLite持久化队列实现
│   ├── short_term_memory_loader.py   # 启动加载器
│   ├── memory_query_service.py       # 记忆查询服务
│   ├── memory_index_service.py       # 索引服务（实时触发）
│   ├── memory_index_pipeline.py      # 索引 Pipeline（仅定时任务用，待删除）
│   ├── memory_extractor.py           # 记忆提取器
│   └── embedding/
│       ├── factory.py                # Embedding 工厂
│       └── providers/
│           ├── local.py              # 本地 Embedding
│           └── cloud.py              # 云端 Embedding（预留）
│
├── models/
│   └── memory.py                     # 统一记忆模型
│
├── api/v1/endpoints/
│   ├── meals.py                      # 餐食 API（集成短期记忆）
│   ├── exercise_checkin.py           # 运动 API（集成短期记忆）
│   └── ai.py                         # AI 聊天 API（使用记忆上下文）
│
└── schedulers/
    └── __init__.py                   # 定时任务（记忆索引任务待删除）
```

---

## 七、重要说明

### 7.1 不需要的组件

| 组件 | 状态 | 原因 |
|------|------|------|
| **定时索引任务** | ❌ 删除 | 队列溢出时实时触发，不需要定时 |
| **MemoryIndexPipeline** | ❌ 删除 | 批量处理逻辑不需要 |
| **short_term_days 配置** | ❌ 删除 | 由队列容量控制，不需要时间维度 |

### 7.2 关键设计决策

1. **为什么短期记忆是内存队列？**
   - 快速写入和读取（微秒级）
   - 自动溢出机制（FIFO）
   - 简单可靠

2. **为什么队列容量是 100 条？**
   - 平衡性能和存储
   - 覆盖用户最近的行为（约 3-7 天）
   - 可配置调整

3. **为什么重启后要加载队列？**
   - 保证计数正确
   - 否则新写入时无法正确判断是否溢出
   - `is_indexed=False` = 还在队列中

4. **为什么没有定时任务？**
   - 队列溢出是唯一的触发方式
   - 实时索引，不需要延迟
    - 定时任务会导致重复索引

5. **为什么需要SQLite持久化队列？**
   - 单实例部署时，无需独立服务即可实现持久化
   - 重启后队列状态自动恢复，无需从数据库加载
   - 保持内存队列的简单性，同时获得持久化能力
   - 未来可平滑迁移到Redis队列，支持分布式部署

---

## 八、测试验收标准

### 8.1 功能测试

| 测试项 | 预期结果 |
|--------|----------|
| 创建前 100 条记录 | `is_indexed=False`，不触发索引 |
| 创建第 101 条记录 | 第 1 条被挤出，触发索引，`is_indexed=True` |
| 重启后查询 | 短期记忆队列正确恢复 |
| AI 聊天 | 能回答用户最近的行为记录 |

### 8.2 性能测试

| 测试项 | 预期结果 |
|--------|----------|
| 写入延迟 | < 10ms（不包含索引） |
| 索引延迟 | < 5 秒（异步，不阻塞） |
| 查询延迟 | < 100ms（内存队列） |
| 重启加载 | < 1 秒（100 条） |

---

## 九、变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.1 | 2026-02-26 | 新增SQLite持久化队列设计，支持可配置队列后端 | - |
| v1.0 | 2026-02-26 | 初始版本，确认完整设计 | - |

---

*文档结束*
