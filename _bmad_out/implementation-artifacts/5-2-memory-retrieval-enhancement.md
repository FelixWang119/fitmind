# Story 5-2: 记忆检索增强

**Epic**: 5 - AI 记忆集成  
**Story ID**: 5.2  
**Story Key**: `5-2-memory-retrieval-enhancement`  
**优先级**: P1  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** AI 助手  
**我想要** 更智能地检索用户记忆  
**以便** 提供更个性化的建议  

---

## ✅ 验收标准 (BDD 格式)

### AC 5.2.1: 语义搜索增强

**Given** AI 需要获取用户历史信息  
**When** 检索记忆时  
**Then** 支持语义向量搜索:
- 基于 pgvector 的相似度检索
- 关键词 + 向量混合检索

### AC 5.2.2: 记忆重要性排序

**Given** 检索结果  
**When** 返回记忆时  
**Then** 按重要性分数排序:
- importance_score 字段
- 最近访问时间 (last_accessed)
- 创建时间

### AC 5.2.3: 记忆类型过滤

**Given** 检索请求  
**When** 指定记忆类型时  
**Then** 只返回指定类型的记忆:
- profile_explicit
- preference_inferred
- habit_completed
- milestone_achieved

### AC 5.2.4: 时间范围过滤

**Given** 检索请求  
**When** 指定时间范围  
**Then** 只返回时间范围内的记忆

---

## 🏗️ 技术需求

### 后端实现

```python
# 扩展现有 memory_query_service.py
class EnhancedMemoryQueryService:
    """增强的记忆查询服务"""
    
    def semantic_search(user_id, query, limit=10):
        """语义向量搜索"""
        
    def hybrid_search(user_id, query, filters, limit):
        """混合搜索 (关键词 + 向量)"""
        
    def get_memories_by_type(user_id, memory_type, limit):
        """按类型获取记忆"""
        
    def get_memories_by_timerange(user_id, start_date, end_date):
        """按时间范围获取记忆"""
```

### 现有基础设施

- `UnifiedMemory` 模型 - 已支持向量存储
- `MemoryQueryService` - 已存在基础功能
- pgvector - 已配置

---

## 🔄 依赖关系

- **前置**: Story 5.1 (档案数据转入记忆)
- **后续**: Story 5.3 (AI 对话引用)

---

## 🧪 测试用例

1. `test_semantic_search` - 语义搜索
2. `test_hybrid_search` - 混合搜索
3. `test_filter_by_type` - 类型过滤
4. `test_filter_by_timerange` - 时间过滤
5. `test_importance_ranking` - 重要性排序
