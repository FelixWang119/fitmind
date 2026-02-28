# Story 5-1: 档案数据转入记忆

**Epic**: 5 - AI 记忆集成  
**Story ID**: 5.1  
**Story Key**: `5-1-profile-data-to-memory`  
**优先级**: P1  
**故事点数**: 5 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 系统  
**我想要** 将用户档案数据自动转入记忆系统  
**以便** AI 可以利用历史档案数据进行个性化建议  

---

## ✅ 验收标准 (BDD 格式)

### AC 5.1.1: 档案数据提取

**Given** 用户完善个人档案  
**When** 档案变更时  
**Then** 自动提取关键信息存入统一记忆:
- 身体数据 (身高、体重、BMI、体脂率)
- 健康目标 (目标体重、减重目标)
- 偏好设置 (饮食偏好、运动偏好)

### AC 5.1.2: 记忆类型标记

**Given** 档案数据转入记忆  
**When** 存储时  
**Then** 标记正确的记忆类型:
- `profile_explicit` - 显式档案数据
- `preference_inferred` - 推断的偏好

### AC 5.1.3: 历史数据批量迁移

**Given** 已有用户档案  
**When** 首次启用记忆功能  
**Then** 批量迁移历史档案数据到记忆系统

---

## 🏗️ 技术需求

### 后端实现

```python
# 新建服务: profile_memory_service.py
class ProfileMemoryService:
    """档案记忆服务"""
    
    def sync_profile_to_memory(user_id: int):
        """同步用户档案到记忆"""
        # 1. 获取用户档案
        # 2. 提取关键信息
        # 3. 存入统一记忆 (UnifiedMemory)
        
    def batch_migrate_existing_profiles():
        """批量迁移现有用户档案"""
```

### 现有基础设施

- `UnifiedMemory` 模型 - 已支持
- `memory_index_service` - 已存在
- `ShortTermMemoryService` - 已存在

---

## 🔄 依赖关系

- **前置**: Epic 1 (Profile) - 已完成 ✅
- **后续**: Story 5.2 (记忆检索增强)

---

## 🧪 测试用例

1. `test_profile_sync_on_update` - 档案更新时同步
2. `test_memory_type_correct` - 记忆类型正确
3. `test_batch_migration` - 批量迁移
