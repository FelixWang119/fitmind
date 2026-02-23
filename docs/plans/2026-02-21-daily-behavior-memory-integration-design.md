# 日常行为数据（打卡）集成AI Agent记忆体系架构设计

**日期**: 2026-02-21  
**状态**: 已批准 ✅  
**版本**: 1.0

## 概述

设计一个完整的系统架构，将用户的日常行为数据（打卡）无缝集成到AI Agent的记忆体系中，实现个性化、上下文感知的体重管理支持。

## 设计目标

1. **混合数据同步**: 重要数据实时同步，普通数据批量处理
2. **分层记忆体系**: 短期记忆 + 中期记忆 + 长期记忆
3. **智能数据关联**: 自动关联相关数据，构建完整用户画像
4. **渐进式记忆构建**: 从简单到复杂，逐步完善记忆体系

## 用户需求分析

### 数据集成方式
- **混合模式**: 重要数据实时同步，普通数据批量处理

### 优先级数据（全部集成）
1. ✅ 核心健康指标（体重、体脂、血压、血糖）
2. ✅ 习惯打卡（饮食、运动、睡眠、饮水）
3. ✅ 情绪状态（压力水平、心情评分）
4. ✅ 饮食记录（具体餐食、卡路里、营养素）
5. ✅ 运动详情（类型、时长、强度）
6. ✅ 睡眠质量（时长、质量、入睡时间）

### 历史数据处理
1. ✅ 趋势分析（识别变化趋势）
2. ✅ 模式识别（发现行为模式）
3. ✅ 里程碑标记（标记重要里程碑）

## 系统架构

### 整体架构图
```
用户行为数据 → 数据收集层 → 数据处理层 → 记忆存储层 → AI记忆集成层 → AI Agent
    ↓              ↓              ↓              ↓              ↓
  打卡API      实时/批量      趋势/模式      分层存储      上下文构建
```

### 1. 数据收集层

#### 实时数据收集
- 核心健康指标（体重、血压、血糖）→ 实时同步
- 紧急情绪状态（压力>8分）→ 实时同步
- 重要里程碑（体重首次达标）→ 实时同步

#### 批量数据收集
- 日常习惯打卡 → 每日汇总
- 饮食记录详情 → 每日汇总
- 运动详情记录 → 每日汇总
- 睡眠质量数据 → 每日汇总
- 普通情绪状态 → 每日汇总

#### 数据验证与清洗
- 数据完整性检查
- 异常值检测
- 数据标准化

### 2. 数据处理层

#### 趋势分析引擎
- 体重变化趋势（7天/30天移动平均）
- 运动频率趋势
- 饮食热量趋势
- 睡眠质量趋势

#### 模式识别引擎
- 时间模式（周末vs工作日）
- 行为模式（运动后饮食、压力时睡眠）
- 习惯关联模式
- 周期性模式

#### 里程碑检测器
- 目标达成检测（体重、运动、习惯）
- 连续记录检测（打卡天数）
- 突破性进展检测
- 负面趋势预警

### 3. 记忆存储层

#### 短期记忆（对话上下文）
- 最近10条对话
- 当前会话主题
- 临时用户状态

#### 中期记忆（近期行为）
- 最近7天行为摘要
- 当前周趋势
- 正在进行的习惯

#### 长期记忆（历史数据）
- 用户画像档案
- 历史趋势数据
- 重要里程碑记录
- 行为模式库
- 个性化偏好

### 4. AI记忆集成层

#### 上下文构建器
- 实时状态注入
- 历史数据摘要
- 相关模式提取
- 个性化提示生成

#### 记忆更新器
- 增量记忆更新
- 记忆重要性评分
- 记忆衰减管理
- 记忆关联建立

#### 查询优化器
- 记忆检索优化
- 相关性排序
- 上下文裁剪
- 性能优化

## 数据库架构扩展

### 新增表结构

#### 1. 用户长期记忆表
```sql
CREATE TABLE user_long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    memory_key VARCHAR(200) NOT NULL,
    memory_value JSONB NOT NULL,
    importance_score FLOAT DEFAULT 1.0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, memory_type, memory_key)
);
```

#### 2. 上下文摘要表
```sql
CREATE TABLE context_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    summary_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    summary_text TEXT NOT NULL,
    key_insights JSONB,
    data_sources JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. 习惯模式表
```sql
CREATE TABLE habit_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    first_detected DATE NOT NULL,
    last_observed DATE NOT NULL,
    observation_count INTEGER DEFAULT 1
);
```

#### 4. 数据关联表
```sql
CREATE TABLE data_associations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_id INTEGER NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER NOT NULL,
    association_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 现有表扩展

#### 1. 健康记录表扩展
```sql
ALTER TABLE health_records ADD COLUMN processed_for_memory BOOLEAN DEFAULT FALSE;
ALTER TABLE health_records ADD COLUMN memory_extracted JSONB;
```

#### 2. 习惯完成表扩展
```sql
ALTER TABLE habit_completions ADD COLUMN context_notes TEXT;
ALTER TABLE habit_completions ADD COLUMN memory_relevance_score FLOAT DEFAULT 0.0;
```

#### 3. 对话表扩展
```sql
ALTER TABLE conversations ADD COLUMN context_summary_updated BOOLEAN DEFAULT FALSE;
ALTER TABLE conversations ADD COLUMN key_topics JSONB;
```

## 服务层设计

### 核心服务模块

#### 1. MemoryManager（记忆管理器）
```python
class MemoryManager:
    async def process_daily_data(self, user_id: int, date: date):
        """处理每日数据，更新记忆体系"""
        
    async def build_context_for_ai(self, user_id: int, conversation_id: int = None):
        """为AI构建上下文"""
        
    async def detect_milestones(self, user_id: int):
        """检测里程碑事件"""
        
    async def update_memory_importance(self, user_id: int, memory_key: str, importance_delta: float):
        """更新记忆重要性"""
```

#### 2. TrendAnalyzer（趋势分析引擎）
```python
class TrendAnalyzer:
    async def analyze_weight_trend(self, user_id: int, days: int = 30):
        """分析体重趋势"""
        
    async def analyze_habit_consistency(self, user_id: int, habit_id: int = None):
        """分析习惯一致性"""
        
    async def detect_behavioral_patterns(self, user_id: int):
        """检测行为模式"""
```

#### 3. ContextBuilder（上下文构建器）
```python
class ContextBuilder:
    def build_ai_context(self, user_data: Dict, memory_data: Dict) -> str:
        """构建AI上下文提示"""
        # 包含：用户基本信息、当前状态、近期趋势、行为模式、重要里程碑、个性化提示
```

## 数据流设计

### 1. 实时数据流
```
用户打卡 → API端点 → 数据验证 → 实时处理器 → 记忆更新器 → AI上下文更新
    ↓          ↓          ↓           ↓            ↓           ↓
健康指标   情绪状态   紧急事件   重要性评分   短期记忆更新   即时响应
```

### 2. 批量数据流
```
每日数据 → 批量收集器 → 数据清洗 → 趋势分析 → 模式识别 → 记忆存储
    ↓          ↓          ↓          ↓          ↓          ↓
习惯打卡   饮食记录   运动详情   睡眠数据   情绪日志   长期记忆
```

### 3. AI交互数据流
```
用户消息 → 上下文构建 → 记忆检索 → AI调用 → 响应生成 → 记忆更新
    ↓          ↓          ↓         ↓         ↓          ↓
对话输入   状态注入   相关记忆   QWen API   个性化回复   交互记录
```

## 实施路线图

### 阶段1：基础记忆框架（1-2周）
- ✅ 数据库表结构扩展
- ✅ 基础MemoryManager服务
- ✅ 简单上下文构建
- ✅ 基础数据同步

### 阶段2：分析引擎集成（2-3周）
- 🔄 趋势分析引擎
- 🔄 模式识别引擎
- 🔄 里程碑检测器
- 🔄 记忆重要性评分

### 阶段3：智能上下文构建（2-3周）
- 🔄 高级上下文构建器
- 🔄 记忆关联系统
- 🔄 个性化提示生成
- 🔄 性能优化

### 阶段4：高级功能（3-4周）
- 🔄 预测性分析
- 🔄 自适应学习
- 🔄 多模态记忆
- 🔄 用户反馈集成

## 技术栈

### 后端
- **框架**: FastAPI + SQLAlchemy
- **数据库**: PostgreSQL（生产），SQLite（开发）
- **AI集成**: QWen Turbo API
- **任务队列**: Celery + Redis（用于批量处理）
- **缓存**: Redis（用于记忆缓存）

### 前端
- **框架**: React + TypeScript
- **状态管理**: Zustand
- **UI库**: Ant Design / Material-UI
- **图表**: Recharts / Chart.js

### 部署
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes（可选）
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack

## 性能指标

### 响应时间
- AI响应时间: < 10秒（含记忆检索）
- 非AI交互: < 500ms
- 数据同步延迟: < 1秒（实时），< 5分钟（批量）

### 存储容量
- 短期记忆: 保留最近30天
- 中期记忆: 保留最近90天
- 长期记忆: 永久保留（可配置归档）

### 可扩展性
- 支持并发用户: 1000+
- 每日数据处理量: 10万+记录
- 记忆检索延迟: < 100ms

## 风险评估与缓解

### 技术风险
1. **AI API延迟**
   - 风险: QWen API响应时间不稳定
   - 缓解: 实现超时重试、本地缓存、降级策略

2. **数据一致性**
   - 风险: 实时与批量数据冲突
   - 缓解: 使用事务、乐观锁、冲突解决策略

3. **记忆膨胀**
   - 风险: 长期记忆数据量过大
   - 缓解: 记忆压缩、重要性衰减、定期清理

### 业务风险
1. **用户隐私**
   - 风险: 敏感健康数据泄露
   - 缓解: 数据加密、访问控制、匿名化处理

2. **系统复杂性**
   - 风险: 维护成本高
   - 缓解: 模块化设计、清晰文档、自动化测试

## 成功标准

### 技术成功标准
- ✅ 系统稳定运行率 > 99.5%
- ✅ AI响应时间 < 10秒
- ✅ 数据同步准确率 > 99.9%
- ✅ 记忆检索准确率 > 95%

### 业务成功标准
- ✅ 用户满意度 > 4.5/5.0
- ✅ 用户留存率 > 70%（30天）
- ✅ 习惯养成率提升 > 30%
- ✅ 体重管理成功率提升 > 25%

## 附录

### A. 数据优先级矩阵
| 数据类型 | 实时性要求 | 重要性 | 处理频率 |
|---------|-----------|--------|----------|
| 体重记录 | 高 | 高 | 实时 |
| 血压/血糖 | 高 | 高 | 实时 |
| 紧急情绪 | 高 | 高 | 实时 |
| 习惯打卡 | 中 | 中 | 每日 |
| 饮食记录 | 中 | 中 | 每日 |
| 运动详情 | 中 | 中 | 每日 |
| 睡眠数据 | 低 | 中 | 每日 |
| 普通情绪 | 低 | 低 | 每日 |

### B. 记忆类型定义
| 记忆类型 | 存储内容 | 保留时间 | 更新频率 |
|---------|----------|----------|----------|
| 短期记忆 | 对话上下文 | 30天 | 实时 |
| 中期记忆 | 近期行为 | 90天 | 每日 |
| 长期记忆 | 用户画像 | 永久 | 每周 |

### C. API端点设计
```
POST /api/v1/memory/process-daily-data
GET  /api/v1/memory/build-context/{user_id}
POST /api/v1/memory/update-importance
GET  /api/v1/memory/summary/{user_id}
POST /api/v1/memory/detect-milestones
```

---

**文档版本历史**
- v1.0 (2026-02-21): 初始版本，架构设计完成
- v1.1 (待更新): 实施细节补充
- v1.2 (待更新): 测试计划添加

**审批记录**
- ✅ 架构设计: 已批准
- 🔄 技术评审: 待进行
- 🔄 实施计划: 待制定