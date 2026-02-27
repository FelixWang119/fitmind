# 系统配置清单

**扫描日期：** 2026-02-25  
**总计配置项：** 42 个  
**状态：** 待实现

---

## 📊 配置分类总览

| 分类 | 配置项数 | 优先级 | 建议 Story |
|------|---------|--------|-----------|
| AI/LLM 配置 | 6 | P1 | Story 7.1 |
| 功能开关 | 15 | P1 | Story 7.2 |
| 通知模板 | 7 | P2 | Story 7.3 |
| 系统配置 | 8 | P2 | Story 7.4 |
| 业务规则 | 6 | P3 | Story 7.5 |

---

## 🤖 1. AI/LLM 配置（6 个）

### 1.1 角色提示词（4 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `ai.prompt.nutritionist` | 营养师提示词 | `services/ai_role_services.py:21` | 硬编码 | 专业营养师角色定义 |
| `ai.prompt.behavior_coach` | 行为教练提示词 | `services/ai_role_services.py:147` | 硬编码 | 行为教练角色定义 |
| `ai.prompt.emotional_support` | 情感陪伴提示词 | `services/ai_role_services.py:323` | 硬编码 | 情感陪伴角色定义 |
| `ai.prompt.data_analyst` | 数据分析师提示词 | `services/memory_extractor.py:41` | 硬编码 | 数据分析提示词 |

**配置结构建议：**
```json
{
  "prompt": "你是一位专业的...",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 0.9,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

### 1.2 LLM 参数（2 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `ai.model.temperature` | 温度参数 | `services/ai_service.py:328` | 配置文件 | 控制随机性 (0-1) |
| `ai.model.max_tokens` | 最大 Token 数 | `services/ai_service.py:329` | 1000 | 控制输出长度 |

---

## 🔘 2. 功能开关（15 个）

### 2.1 核心功能开关（6 个）

| 配置 Key | 功能名称 | 说明 | 影响范围 | 默认值 |
|---------|---------|------|---------|--------|
| `feature.ai_chat` | AI 对话功能 | 启用/禁用 AI 对话 | 核心功能 | ✅ ON |
| `feature.habit_tracking` | 习惯打卡功能 | 启用/禁用习惯打卡 | 核心功能 | ✅ ON |
| `feature.nutrition_tracking` | 饮食记录功能 | 启用/禁用饮食记录 | 核心功能 | ✅ ON |
| `feature.exercise_tracking` | 运动记录功能 | 启用/禁用运动记录 | 核心功能 | ✅ ON |
| `feature.weight_tracking` | 体重记录功能 | 启用/禁用体重记录 | 核心功能 | ✅ ON |
| `feature.sleep_tracking` | 睡眠记录功能 | 启用/禁用睡眠记录 | 核心功能 | ✅ ON |

### 2.2 AI 功能开关（4 个）

| 配置 Key | 功能名称 | 说明 | 影响范围 | 默认值 |
|---------|---------|------|---------|--------|
| `feature.ai_role_switch` | AI 角色切换 | 启用/禁用角色动态切换 | AI 对话 | ✅ ON |
| `feature.ai_nutritionist` | AI 营养师 | 启用/禁用营养师角色 | AI 对话 | ✅ ON |
| `feature.ai_behavior_coach` | AI 行为教练 | 启用/禁用行为教练角色 | AI 对话 | ✅ ON |
| `feature.ai_emotional_support` | AI 情感陪伴 | 启用/禁用情感陪伴角色 | AI 对话 | ✅ ON |

### 2.3 通知功能开关（3 个）

| 配置 Key | 功能名称 | 说明 | 影响范围 | 默认值 |
|---------|---------|------|---------|--------|
| `feature.notification_in_app` | App 内通知 | 启用/禁用 App 内通知 | 通知系统 | ✅ ON |
| `feature.notification_email` | 邮件通知 | 启用/禁用邮件通知 | 通知系统 | ✅ ON |
| `feature.notification_push` | 推送通知 | 启用/禁用推送通知 | 通知系统 | ❌ OFF |

### 2.4 游戏化功能开关（2 个）

| 配置 Key | 功能名称 | 说明 | 影响范围 | 默认值 |
|---------|---------|------|---------|--------|
| `feature.gamification_points` | 积分系统 | 启用/禁用积分系统 | 游戏化 | ⏳ TBD |
| `feature.gamification_badges` | 徽章系统 | 启用/禁用徽章系统 | 游戏化 | ⏳ TBD |

**功能开关配置结构：**
```json
{
  "enabled": true,
  "rollout_percentage": 100,
  "allowed_user_ids": [],
  "environments": ["development", "staging", "production"],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": null
}
```

---

## 🔔 3. 通知模板（7 个）

### 3.1 习惯相关（3 个）

| 配置 Key | 模板名称 | 事件类型 | 当前状态 |
|---------|---------|---------|---------|
| `notification.template.habit_completed` | 习惯完成通知 | habit.completed | ✅ 数据库 |
| `notification.template.habit_streak_7` | 连续 7 天打卡 | habit.streak_7days | ✅ 数据库 |
| `notification.template.habit_streak_30` | 连续 30 天打卡 | habit.streak_30days | ✅ 数据库 |

### 3.2 里程碑相关（1 个）

| 配置 Key | 模板名称 | 事件类型 | 当前状态 |
|---------|---------|---------|---------|
| `notification.template.milestone_weight_goal` | 体重目标达成 | milestone.weight_goal | ✅ 数据库 |

### 3.3 游戏化相关（1 个）

| 配置 Key | 模板名称 | 事件类型 | 当前状态 |
|---------|---------|---------|---------|
| `notification.template.badge_unlocked` | 徽章解锁 | badge.unlocked | ✅ 数据库 |

### 3.4 关怀相关（2 个）

| 配置 Key | 模板名称 | 事件类型 | 当前状态 |
|---------|---------|---------|---------|
| `notification.template.morning_care` | 早安关怀 | care.morning | ✅ 数据库 |
| `notification.template.care_inactive` | 未登录关怀 | care.inactive | ✅ 数据库 |

**通知模板配置结构：**
```json
{
  "title_template": "🎉 恭喜你...",
  "content_template": "你已经成功...",
  "variables": ["weight", "date"],
  "channels": ["in_app", "email"],
  "priority": 8,
  "is_active": true
}
```

---

## ⚙️ 4. 系统配置（8 个）

### 4.1 性能配置（3 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `system.performance.slow_query_threshold` | 慢查询阈值 | `core/performance.py:18` | 1.0 秒 | 慢查询判定阈值 |
| `system.performance.compression_threshold_kb` | 压缩阈值 | `core/performance.py:159` | 100 KB | 响应压缩阈值 |
| `system.performance.response_cache_ttl` | 响应缓存 TTL | `middleware/performance.py` | 300 秒 | 响应缓存时间 |

### 4.2 缓存配置（3 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `system.cache.default_ttl` | 默认缓存 TTL | `core/cache.py` | 300 秒 | 默认缓存过期时间 |
| `system.cache.max_size` | 最大缓存条目 | `core/cache.py` | 1000 条 | 内存缓存大小限制 |
| `system.cache.eviction_policy` | 驱逐策略 | `core/cache.py` | LRU | 缓存满时驱逐策略 |

### 4.3 邮件配置（2 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `system.email.smtp_host` | SMTP 服务器 | `email_service.py:21` | smtp.sendgrid.net | 邮件服务器地址 |
| `system.email.from_address` | 发件人地址 | `email_service.py:25` | noreply@fitmind.app | 默认发件人邮箱 |

**系统配置结构：**
```json
{
  "value": 300,
  "unit": "seconds",
  "min_value": 60,
  "max_value": 3600,
  "requires_restart": false
}
```

---

## 📊 5. 业务规则（6 个）

### 5.1 习惯相关（2 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `business.habit.streak_milestone_7` | 7 天里程碑 | 业务逻辑 | 7 天 | 习惯 7 天里程碑阈值 |
| `business.habit.streak_milestone_30` | 30 天里程碑 | 业务逻辑 | 30 天 | 习惯 30 天里程碑阈值 |

### 5.2 游戏化相关（2 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `business.gamification.points_per_habit` | 每次习惯积分 | 待实现 | 10 分 | 完成习惯获得积分 |
| `business.gamification.points_per_day` | 每日上限积分 | 待实现 | 100 分 | 每日积分上限 |

### 5.3 通知相关（2 个）

| 配置 Key | 配置项 | 当前位置 | 默认值 | 说明 |
|---------|--------|---------|--------|------|
| `business.notification.max_per_day` | 每日最大通知数 | 业务逻辑 | 20 条 | 防止通知骚扰 |
| `business.notification.min_interval_seconds` | 最小通知间隔 | 业务逻辑 | 300 秒 | 通知间隔控制 |

**业务规则配置结构：**
```json
{
  "value": 7,
  "description": "7 天习惯里程碑",
  "validation": {
    "type": "integer",
    "min": 1,
    "max": 365
  }
}
```

---

## 📋 实施优先级

### Story 7.0: 基础框架（2-3 天）

**实现配置：**
- ✅ AI 提示词（4 个）
- ✅ 功能开关（6 个核心功能）
- ✅ 配置表设计
- ✅ 配置 API
- ✅ 管理后台 UI

### Story 7.1: AI 提示词管理（3-4 天）

**完善配置：**
- ✅ LLM 参数（2 个）
- ✅ 提示词版本管理
- ✅ 实时生效机制

### Story 7.2: 功能开关管理（2-3 天）

**完善配置：**
- ✅ 功能开关（9 个剩余）
- ✅ 环境配置
- ✅ 紧急关闭机制

### Story 7.3: 通知模板管理（3-4 天）

**完善配置：**
- ✅ 通知模板（7 个，已有数据库）
- ✅ 模板预览
- ✅ 版本管理

### Story 7.4: 系统配置管理（3-4 天）

**完善配置：**
- ✅ 性能配置（3 个）
- ✅ 缓存配置（3 个）
- ✅ 邮件配置（2 个）

### Story 7.5: 业务规则管理（2-3 天）

**完善配置：**
- ✅ 业务规则（6 个）
- ✅ 配置历史
- ✅ 审计日志

---

## 📊 配置管理矩阵

| 配置类型 | 总数 | 已管理 | 待实现 | 完成度 |
|---------|------|--------|--------|--------|
| AI/LLM 配置 | 6 | 0 | 6 | 0% |
| 功能开关 | 15 | 0 | 15 | 0% |
| 通知模板 | 7 | 7 (数据库) | 0 (需 UI) | 100% 数据 |
| 系统配置 | 8 | 0 | 8 | 0% |
| 业务规则 | 6 | 0 | 6 | 0% |
| **总计** | **42** | **7** | **35** | **17%** |

---

*文档版本：v1.0*  
*最后更新：2026-02-25*  
*下次扫描：每次新增功能时*
