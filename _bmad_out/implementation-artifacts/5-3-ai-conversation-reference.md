# Story 5-3: AI 对话引用

**Epic**: 5 - AI 记忆集成  
**Story ID**: 5.3  
**Story Key**: `5-3-ai-conversation-reference`  
**优先级**: P1  
**故事点数**: 5 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** AI 助手  
**我想要** 在对话中引用用户记忆  
**以便** 提供更个性化、更上下文感知的回复  

---

## ✅ 验收标准 (BDD 格式)

### AC 5.3.1: 对话上下文注入

**Given** 用户与 AI 对话  
**When** 生成回复时  
**Then** 自动注入相关记忆:
- 检索最相关的 3-5 条记忆
- 格式化为上下文提示

### AC 5.3.2: 记忆引用标注

**Given** 回复包含记忆内容  
**When** 显示时  
**Then** 标注记忆来源:
- "根据您之前的目标..."
- "记得您说过..."

### AC 5.3.3: 记忆时效性判断

**Given** 检索到的记忆  
**When** 生成回复前  
**Then** 判断记忆时效性:
- 过滤过于陈旧的记忆 (>30天)
- 标记可能过时的信息

### AC 5.3.4: 隐私保护

**Given** 用户设置隐私偏好  
**When** 引用记忆时  
**Then** 遵守隐私设置:
- 排除敏感记忆
- 允许用户关闭记忆引用

---

## 🏗️ 技术需求

### 后端实现

```python
# 扩展现有 AI 服务
class MemoryAwareAIService:
    """记忆感知 AI 服务"""
    
    def generate_response_with_memory(user_id, prompt):
        """生成带记忆上下文的回复"""
        # 1. 检索相关记忆
        # 2. 格式化为上下文
        # 3. 注入 prompt
        # 4. 调用 LLM
        
    def format_memory_context(memories):
        """格式化记忆为上下文"""
        
    def is_memory_fresh(memory, max_days=30):
        """判断记忆是否新鲜"""
```

### 现有基础设施

- `memory_query_service` - 已存在
- AI Role Services - 已存在
- 对话系统 - 已存在

---

## 🔄 依赖关系

- **前置**: Story 5.2 (记忆检索增强)
- **后续**: 无 (Epic 5 完成)

---

## 🧪 测试用例

1. `test_memory_injection` - 记忆注入
2. `test_memory_freshness` - 时效性判断
3. `test_context_format` - 上下文格式化
4. `test_privacy_filter` - 隐私过滤
