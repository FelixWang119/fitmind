---
storyNumber: "6.0"
storyTitle: "通知系统设计与实现"
storyType: "architecture + implementation"
priority: "P1"
status: "done"
createdDate: "2026-02-25"
lastUpdated: "2026-02-25"
architectureVersion: "v0.3"
completedDate: "2026-02-25"
---

# Story 6.0: 通知系统设计与实现

## 用户故事

作为 FitMind 用户，  
我想要及时收到重要的健康提醒和鼓励消息，  
以便我能保持动力并建立可持续的健康习惯。

---

## 背景与上下文

### 需求来源

1. **PRD 4.4.1 习惯打卡**
   - 用户设置提醒时间
   - 忘记打卡时发送提醒

2. **PRD 4.6.3 主动关怀**
   - 每天早上：天气 + 健康提醒
   - 连续 2 天未登录关怀
   - 里程碑庆祝消息
   - 生日/注册纪念日祝福

3. **PRD 游戏化系统**
   - 积分获得通知
   - 徽章解锁通知
   - 挑战完成通知

4. **用户记忆系统设计**
   - 里程碑检测 → 触发通知

### 架构决策（v0.3）

| 决策点 | 决策 | 理由 |
|--------|------|------|
| **触发机制** | 轮询而非事件系统 | 简单、易调试、适合低并发 |
| **实时通信** | 60 秒轮询而非 SSE | 不需要秒级实时、移动端兼容好 |
| **通知渠道** | Web 应用内 + 邮件 | 成本最低、前端是 Web 应用 |
| **模板系统** | 简化版 | 无国际化/A/B 测试，聚焦核心价值 |

---

## 架构设计状态

### ✅ Task 6.1: 通知系统架构设计（已完成）

**状态：** ✅ 完成  
**文档：** `_bmad_out/planning-artifacts/通知系统架构设计.md (v0.3)`  
**审阅者：** Winston（系统架构师）  
**批准状态：** ✅ 可以进入实现阶段

**核心设计：**

1. **触发机制 - 轮询方案**
   - 习惯提醒：每分钟轮询
   - 里程碑检测：每 5 分钟轮询
   - 事件日志处理：每 30 秒轮询
   - 主动关怀：每天 8:00/14:00 定时任务

2. **解耦设计 - 事件日志表**
   - 业务系统写入 `event_logs` 表
   - 通知系统轮询处理 pending 状态事件
   - 通知系统不依赖业务表结构

3. **渠道策略**
   - 所有通知：Web 应用内（通知中心 + Toast）
   - 重要通知：Web 应用内 + 邮件
   - 浏览器推送：Phase 2 可选

4. **模板系统**
   - 简化版：无国际化、无 A/B 测试
   - 支持变量替换（Jinja2）
   - 集中管理所有通知文案

---

## 任务分解

### ✅ Task 6.1: 通知系统架构设计（架构师 Winston）

**状态：** ✅ 已完成

**交付物：**
- ✅ 通知系统架构设计文档（v0.3）
- ✅ 技术选型建议
- ✅ 与记忆系统集成方案

---

### 🔄 Task 6.2: 通知系统基础实现（开发 Amelia）

**目标：** 实现通知系统核心功能

**前置条件：** Task 6.1 完成 ✅

**子任务：**

#### Subtask 6.2.1: 数据库模型和迁移

**内容：**
- [ ] 创建 `notifications` 表（通知记录）
- [ ] 创建 `notification_templates` 表（通知模板）
- [ ] 创建 `user_notification_settings` 表（用户设置）
- [ ] 创建 `event_logs` 表（事件日志，解耦用）
- [ ] Alembic 迁移脚本

**SQL 示例：**
```sql
-- 通知记录表
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    notification_type VARCHAR(50),
    title VARCHAR(200),
    content TEXT,
    channel VARCHAR(20),  -- 'in_app', 'email'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 事件日志表（解耦业务和通知）
CREATE TABLE event_logs (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB,
    user_id UUID,
    notification_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Subtask 6.2.2: 通知服务层实现

**内容：**
- [ ] `NotificationService` 核心服务
- [ ] `TemplateRenderer` 模板渲染器（Jinja2）
- [ ] `EmailService` 邮件服务（SendGrid/SMTP）
- [ ] 渠道路由逻辑（Web 应用内 + 邮件）

**核心方法：**
```python
class NotificationService:
    async def send_notification(
        user_id: UUID,
        notification_type: str,
        title: str,
        content: str,
        template_data: dict = None,
    ) -> Notification
    
    async def send_email(
        user: User,
        subject: str,
        body: str,
    ) -> bool
```

#### Subtask 6.2.3: 通知轮询任务

**内容：**
- [ ] 习惯提醒轮询任务（每分钟）
- [ ] 里程碑检测轮询任务（每 5 分钟）
- [ ] 事件日志处理任务（每 30 秒）
- [ ] 主动关怀定时任务（每天 8:00/14:00）

**APScheduler 配置：**
```python
@scheduler.scheduled_job('cron', second=0)
async def habit_reminder_task():
    # 查询当前时间需要提醒的习惯
    # 发送通知

@scheduler.scheduled_job('interval', minutes=5)
async def milestone_detection_task():
    # 检测用户达成的里程碑
    # 发送通知
```

#### Subtask 6.2.4: 通知 API 端点

**API 列表：**

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/notifications` | 获取通知列表（支持分页） |
| GET | `/api/v1/notifications/unread-count` | 获取未读数量（红点） |
| PUT | `/api/v1/notifications/{id}/read` | 标记为已读 |
| PUT | `/api/v1/notifications/read-all` | 全部标记已读 |
| GET | `/api/v1/notifications/settings` | 获取通知设置 |
| PUT | `/api/v1/notifications/settings` | 更新通知设置 |

#### Subtask 6.2.5: 通知前端组件（React）

**组件列表：**

| 组件 | 描述 |
|------|------|
| `NotificationCenter` | 通知中心（红点 + 列表 + 抽屉） |
| `NotificationBadge` | 未读数量红点 |
| `ToastNotification` | Toast 弹窗（基于 react-hot-toast） |
| `NotificationSettings` | 通知设置页面 |

**轮询逻辑：**
```typescript
// 60 秒轮询未读数量
useEffect(() => {
    const timer = setInterval(async () => {
        const count = await getUnreadCount();
        setUnreadCount(count);
    }, 60000);
    return () => clearInterval(timer);
}, []);
```

**验收标准：**
- [ ] 所有 API 端点正常工作
- [ ] 前端通知中心可以查看历史通知
- [ ] 红点实时更新未读数量
- [ ] 单元测试覆盖率 > 70%
- [ ] 所有测试通过

---

### 🔄 Task 6.3: 习惯提醒通知实现

**目标：** 实现习惯打卡提醒功能

**前置条件：** Task 6.2 完成

**子任务：**

#### Subtask 6.3.1: 习惯提醒轮询

**内容：**
- [ ] 查询待发送的习惯提醒
- [ ] 去重逻辑（避免重复发送）
- [ ] 发送通知

#### Subtask 6.3.2: 前端提醒设置

**内容：**
- [ ] 习惯创建/编辑页面添加提醒时间设置
- [ ] 时间选择器组件

**验收标准：**
- [ ] 用户设置提醒时间后能准时收到通知
- [ ] 支持多个习惯的不同提醒时间
- [ ] 用户可以关闭提醒

---

### 🔄 Task 6.4: 里程碑通知实现

**目标：** 实现里程碑检测和通知

**前置条件：** Task 6.2 完成，记忆系统已实现

**子任务：**

#### Subtask 6.4.1: 里程碑事件写入

**内容：**
- [ ] 记忆系统在达成里程碑时写入 `event_logs` 表
- [ ] 事件类型：`milestone.achieved`

#### Subtask 6.4.2: 里程碑通知处理

**内容：**
- [ ] 轮询 `event_logs` 表 pending 状态事件
- [ ] 调用 `NotificationService` 发送通知
- [ ] 更新事件状态为 `sent`

#### Subtask 6.4.3: 重要通知邮件

**内容：**
- [ ] 连续 30 天打卡 → 发送邮件
- [ ] 体重目标达成 → 发送邮件
- [ ] 邮件模板设计和实现

**验收标准：**
- [ ] 达成里程碑时自动发送通知
- [ ] 重要里程碑同时发送邮件
- [ ] 通知内容个性化（模板变量）

---

### 🔄 Task 6.5: 主动关怀通知实现

**目标：** 实现主动关怀功能

**前置条件：** Task 6.2 完成

**子任务：**

#### Subtask 6.5.1: 早安关怀

**内容：**
- [ ] 每天 8:00 定时任务
- [ ] 查询活跃用户
- [ ] 发送早安通知

#### Subtask 6.5.2: 未登录关怀

**内容：**
- [ ] 每天 14:00 定时任务
- [ ] 查询连续 2 天未登录用户
- [ ] 发送关怀通知

**验收标准：**
- [ ] 早安提醒准时发送
- [ ] 连续 2 天未登录触发关怀
- [ ] 测试通过

---

## 技术约束

### 后端
- 框架：FastAPI
- 数据库：PostgreSQL
- 任务调度：APScheduler
- 邮件服务：SendGrid / SMTP
- 模板引擎：Jinja2

### 前端
- React + TypeScript
- UI 库：Ant Design / MUI
- 状态管理：Zustand
- Toast：react-hot-toast（已有）

### 通知渠道
| 渠道 | Phase | 说明 |
|------|-------|------|
| **Web 应用内** | Phase 1 | 通知中心 + Toast |
| **邮件** | Phase 1 | 仅重要通知 |
| **浏览器推送** | Phase 2 可选 | Web Push API |

---

## 依赖关系

```
Task 6.1 (架构设计) ✅
    ↓
Task 6.2 (基础实现) 🔄
    ↓
    ├──→ Task 6.3 (习惯提醒) 🔄
    ├──→ Task 6.4 (里程碑通知) 🔄
    └──→ Task 6.5 (主动关怀) 🔄
```

**外部依赖：**
- ✅ 记忆系统里程碑检测功能
- ✅ 习惯打卡功能

---

## 优先级和工时估算

| 任务 | 优先级 | 预计工时 | 状态 |
|------|--------|---------|------|
| Task 6.1 架构设计 | P0 | 已完成 | ✅ |
| Task 6.2.1 数据库模型 | P0 | 0.5 天 | 🔄 |
| Task 6.2.2 通知服务 | P0 | 1 天 | 🔄 |
| Task 6.2.3 轮询任务 | P0 | 1 天 | 🔄 |
| Task 6.2.4 API 端点 | P0 | 1 天 | 🔄 |
| Task 6.2.5 前端组件 | P0 | 1-2 天 | 🔄 |
| Task 6.3 习惯提醒 | P1 | 1 天 | 🔄 |
| Task 6.4 里程碑通知 | P1 | 1-2 天 | 🔄 |
| Task 6.5 主动关怀 | P2 | 0.5 天 | 🔄 |

**总计：** 约 7-9 个工作日

---

## 成功标准

### 功能标准
- [ ] 用户可以查看通知历史
- [ ] 习惯提醒准时发送
- [ ] 里程碑达成时自动发送通知
- [ ] 重要里程碑发送邮件
- [ ] 用户可以标记通知已读
- [ ] 免打扰时间不发送通知

### 技术标准
- [ ] 通知发送延迟 < 5 秒
- [ ] 通知发送成功率 > 99%
- [ ] 单元测试覆盖率 > 70%
- [ ] 所有测试通过
- [ ] 无内存泄漏（轮询任务正确清理）

### 用户体验标准
- [ ] 通知中心易于使用
- [ ] 红点准确反映未读数量
- [ ] 通知内容个性化
- [ ] 不打扰用户（遵守免打扰设置）

---

## 重要通知定义

以下通知类型会**额外发送邮件**：

```python
IMPORTANT_NOTIFICATIONS = {
    "habit.streak_30days",      # 连续 30 天打卡
    "milestone.weight_goal",    # 体重目标达成
    "milestone.streak_master",  # 习惯大师
    "report.weekly",            # 周报
    "report.monthly",           # 月报
}
```

---

## 通知模板（Phase 1）

| 模板代码 | 事件类型 | 标题 | 内容 |
|---------|---------|------|------|
| `habit_completed` | habit.completed | `💪 {{habit_name}} 完成！` | `你已经连续 {{streak_days}} 天完成{{habit_name}}，保持这个好习惯！` |
| `habit_streak_7` | habit.streak_7days | `🔥 连续打卡 7 天！` | `你已经连续 7 天完成{{habit_name}}，一周的坚持值得庆祝！` |
| `habit_streak_30` | habit.streak_30days | `🏆 连续打卡 30 天！` | `太棒了！你已连续 30 天完成{{habit_name}}，这是真正的习惯养成！` |
| `milestone_weight_goal` | milestone.weight_goal | `🎉 恭喜你达成体重目标！` | `你已经成功减重{{weight}}kg，继续加油！` |
| `badge_unlocked` | badge.unlocked | `🎖️ 新徽章解锁！` | `恭喜你获得"{{badge_name}}"徽章！` |
| `morning_care` | care.morning | `☀️ 早安！` | `新的一天开始了，今天也要加油哦～` |
| `care_inactive` | care.inactive | `💙 想你啦！` | `{{days}}天没见到你了，一切还好吗？` |

---

## 备注

**与记忆系统集成：**
- 记忆系统检测里程碑 → 写入 `event_logs` 表
- 通知系统轮询 `event_logs` 表 → 发送通知
- 通过事件日志表解耦，互不依赖

**轮询方案优势：**
- 简单易懂，易于调试
- 不依赖 Redis 等中间件
- 数据库记录可追溯
- 天然支持重试（pending 状态）

**未来扩展（Phase 2）：**
- 浏览器推送（Web Push API）
- 通知聚合（免打扰期间摘要）
- 智能发送时间优化

---

*文档版本：v2.0（基于架构设计 v0.3 更新）*  
*最后更新：2026-02-25*  
*状态：✅ 可以开始实现*
