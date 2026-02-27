---
storyNumber: "7.0"
storyTitle: "系统管理后台基础框架"
storyType: "infrastructure + implementation"
priority: "P2"
status: "pending"
createdDate: "2026-02-25"
estimatedDays: "2-3"
---

# Story 7.0: 系统管理后台基础框架

## 用户故事

作为系统管理员，  
我想要一个基础的管理后台框架，  
以便我可以开始管理系统配置。

---

## 背景与上下文

这是系统管理后台的第一个 Story，目标是搭建基础框架，实现 1-2 个示例功能，为后续功能滚动开发奠定基础。

---

## 任务分解

### Task 7.0.1: 数据库设计

**内容：**
- [ ] 创建 `system_configs` 表
- [ ] 创建 `config_change_logs` 表
- [ ] 创建 `admin_users` 表（或使用现有用户表扩展）
- [ ] Alembic 迁移脚本

**SQL 示例：**
```sql
-- 系统配置表
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type VARCHAR(50) NOT NULL,
    config_category VARCHAR(50),
    description TEXT,
    environment VARCHAR(20) DEFAULT 'all',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- 配置变更日志表
CREATE TABLE config_change_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID NOT NULL REFERENCES system_configs(id),
    old_value JSONB,
    new_value JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    reason TEXT
);

-- 索引
CREATE INDEX idx_system_configs_key ON system_configs(config_key);
CREATE INDEX idx_system_configs_category ON system_configs(config_category);
CREATE INDEX idx_config_logs_config_id ON config_change_logs(config_id);
```

---

### Task 7.0.2: 后端 API 端点

**内容：**
- [ ] GET `/api/v1/admin/configs` - 获取配置列表
- [ ] GET `/api/v1/admin/configs/{key}` - 获取单个配置
- [ ] PUT `/api/v1/admin/configs/{key}` - 更新配置
- [ ] POST `/api/v1/admin/configs` - 创建配置
- [ ] GET `/api/v1/admin/configs/logs` - 获取变更历史

**API Schema：**
```python
class SystemConfig(BaseModel):
    config_key: str
    config_value: dict
    config_type: str
    config_category: str
    description: Optional[str]
    environment: str = "all"
    is_active: bool = True

class ConfigChangeLog(BaseModel):
    config_id: UUID
    old_value: dict
    new_value: dict
    changed_by: UUID
    changed_at: datetime
    reason: Optional[str]
```

---

### Task 7.0.3: 配置服务层

**内容：**
- [ ] `ConfigService` 核心服务
- [ ] 配置读取（带缓存）
- [ ] 配置更新（带审计）
- [ ] 配置验证

**核心方法：**
```python
class ConfigService:
    async def get_config(key: str) -> dict
    async def update_config(key: str, value: dict, changed_by: UUID, reason: str)
    async def get_config_history(key: str, limit: int = 20) -> List[ConfigChangeLog]
    async def invalidate_cache(key: str)
```

---

### Task 7.0.4: 管理后台 UI 框架

**内容：**
- [ ] 管理后台路由 `/admin`
- [ ] 管理员权限验证中间件
- [ ] 基础布局（侧边栏 + 内容区）
- [ ] 配置列表页面
- [ ] 配置编辑页面

**UI 组件：**
```tsx
// 配置列表
/Admin/Configs
/Admin/Configs/:key/edit
/Admin/Configs/logs

// 布局
/Admin (管理后台首页)
```

---

### Task 7.0.5: 示例功能 - AI 提示词管理

**内容：**
- [ ] 初始化 AI 提示词配置（从代码迁移到数据库）
- [ ] AI 提示词管理 UI
- [ ] 提示词实时生效机制

**示例配置：**
```json
{
  "config_key": "ai.prompt.nutritionist",
  "config_value": {
    "system_prompt": "你是一位专业的营养师...",
    "temperature": 0.7,
    "max_tokens": 500
  },
  "config_type": "ai_prompt",
  "config_category": "ai"
}
```

---

### Task 7.0.6: 示例功能 - 功能开关管理

**内容：**
- [ ] 功能开关 CRUD
- [ ] 开关状态检查中间件
- [ ] 紧急关闭功能示例（1-2 个）

**示例开关：**
```json
{
  "config_key": "feature.habit_recommendation",
  "config_value": {
    "enabled": true,
    "rollout_percentage": 100
  },
  "config_type": "feature_flag",
  "config_category": "features"
}
```

---

## 技术约束

### 缓存策略

```python
# Redis 缓存配置
CACHE_KEY = "config:{key}"
CACHE_TTL = 300  # 5 分钟

# 配置读取流程
1. 检查 Redis 缓存
2. 缓存未命中 → 查询数据库
3. 更新缓存
4. 返回配置
```

### 安全要求

- 管理员权限验证
- 配置变更审计日志
- 敏感配置加密（如 API 密钥）

### 性能要求

- 配置读取延迟 < 10ms（缓存命中）
- 配置更新后 1 分钟内生效

---

## 验收标准

### 功能标准

- [ ] 可以查看配置列表
- [ ] 可以更新配置
- [ ] 配置实时生效
- [ ] 记录变更历史
- [ ] AI 提示词可管理
- [ ] 功能开关可控制

### 技术标准

- [ ] 单元测试覆盖率 > 70%
- [ ] API 端点测试通过
- [ ] 缓存机制正常工作
- [ ] 审计日志正确记录

### 用户体验标准

- [ ] 管理后台界面简洁易用
- [ ] 配置变更有明确提示
- [ ] 变更历史可追溯

---

## 依赖关系

```
无外部依赖
    ↓
Task 7.0.1 (数据库设计)
    ↓
    ├──→ Task 7.0.2 (API 端点)
    ├──→ Task 7.0.3 (服务层)
    │
    └──→ Task 7.0.4 (UI 框架)
         ↓
         ├──→ Task 7.0.5 (AI 提示词示例)
         └──→ Task 7.0.6 (功能开关示例)
```

---

## 预计工时

| 任务 | 工时 |
|------|------|
| Task 7.0.1 数据库设计 | 0.5 天 |
| Task 7.0.2 API 端点 | 1 天 |
| Task 7.0.3 服务层 | 0.5 天 |
| Task 7.0.4 UI 框架 | 1 天 |
| Task 7.0.5 AI 提示词示例 | 0.5 天 |
| Task 7.0.6 功能开关示例 | 0.5 天 |
| **总计** | **4 天** |

---

## 下一步

Story 7.0 完成后，可以滚动开发：
- Story 7.1: AI 提示词管理（完善）
- Story 7.2: 功能开关管理（完善）
- Story 7.3: 通知模板管理

---

*文档版本：v1.0*  
*创建日期：2026-02-25*
