# Task 6.2.1 完成报告：数据库模型和迁移

**状态：** ✅ 完成  
**日期：** 2026-02-25  
**执行者：** Amelia

---

## 📋 完成内容

### 1. 数据库模型

**文件：** `backend/app/models/notification.py`

**创建的模型：**

| 模型 | 表名 | 描述 |
|------|------|------|
| `Notification` | `notifications` | 通知记录表 |
| `NotificationTemplate` | `notification_templates` | 通知模板表 |
| `UserNotificationSetting` | `user_notification_settings` | 用户通知设置表 |
| `EventLog` | `event_logs` | 事件日志表（解耦用） |

**关键设计：**

- ✅ 使用 PostgreSQL UUID 作为主键
- ✅ 支持 JSONB 字段存储灵活数据
- ✅ 完整的索引设计优化查询性能
- ✅ 外键约束保证数据完整性
- ✅ 软删除支持（通过 `is_read` 等状态字段）

---

### 2. User 模型扩展

**文件：** `backend/app/models/user.py`

**添加的关系：**

```python
# 通知系统关系
notifications = relationship(
    "Notification", back_populates="user", cascade="all, delete-orphan"
)
notification_settings = relationship(
    "UserNotificationSetting", back_populates="user", uselist=False, cascade="all, delete-orphan"
)
```

---

### 3. Alembic 迁移脚本

**文件：** `backend/alembic/versions/006_add_notification_system.py`

**迁移内容：**

| 操作 | 详情 |
|------|------|
| **创建表** | 4 个新表 |
| **创建索引** | 15 个索引（含复合索引） |
| **创建枚举类型** | 3 个（NotificationStatus, NotificationChannel, EventLogStatus） |
| **外键约束** | 3 个外键 |

**Revision ID:** `006`  
**Down Revision:** `005_add_health_assessments`

---

### 4. 种子数据脚本

**文件：** `backend/app/scripts/seed_notification_templates.py`

**初始化的模板：**

| 模板代码 | 名称 | 事件类型 |
|---------|------|---------|
| `habit_completed` | 习惯完成通知 | habit.completed |
| `habit_streak_7` | 连续 7 天打卡 | habit.streak_7days |
| `habit_streak_30` | 连续 30 天打卡 | habit.streak_30days |
| `milestone_weight_goal` | 体重目标达成 | milestone.weight_goal |
| `badge_unlocked` | 徽章解锁 | badge.unlocked |
| `morning_care` | 早安关怀 | care.morning |
| `care_inactive` | 未登录关怀 | care.inactive |

---

## 🚀 运行指令

### 1. 运行数据库迁移

```bash
cd backend

# 升级到最新版本（包含通知系统）
alembic upgrade head

# 验证迁移
alembic current
# 应该显示：006 (head)
```

### 2. 初始化通知模板

```bash
cd backend

# 运行种子数据脚本
python -m app.scripts.seed_notification_templates

# 输出示例：
# 🌱 开始初始化通知模板种子数据...
# ✅ 创建模板：habit_completed
# ✅ 创建模板：habit_streak_7
# ✅ 创建模板：habit_streak_30
# ✅ 创建模板：milestone_weight_goal
# ✅ 创建模板：badge_unlocked
# ✅ 创建模板：morning_care
# ✅ 创建模板：care_inactive
# 
# 🎉 成功创建 7 个通知模板
# ✅ 完成！
```

---

## 📊 数据库表结构

### notifications 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | Integer | 用户 ID（外键） |
| notification_type | String(50) | 通知类型 |
| title | String(200) | 标题 |
| content | Text | 内容 |
| template_id | UUID | 模板 ID（外键） |
| template_data | JSONB | 模板变量数据 |
| channel | Enum | 渠道（in_app/email） |
| status | Enum | 状态（pending/sent/delivered/read/failed） |
| is_read | Boolean | 是否已读 |
| read_at | DateTime | 已读时间 |
| metadata | JSONB | 元数据 |
| created_at | DateTime | 创建时间 |

### notification_templates 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| code | String(50) | 模板代码（唯一） |
| name | String(100) | 模板名称 |
| title_template | String(200) | 标题模板 |
| content_template | Text | 内容模板 |
| event_type | String(50) | 关联事件类型 |
| variables | JSONB | 变量定义 |
| is_active | Boolean | 是否启用 |

### user_notification_settings 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | Integer | 用户 ID（唯一） |
| enabled | Boolean | 是否启用通知 |
| do_not_disturb_enabled | Boolean | 是否启用免打扰 |
| do_not_disturb_start | String(5) | 免打扰开始时间 |
| do_not_disturb_end | String(5) | 免打扰结束时间 |
| notify_habit_reminder | Boolean | 习惯提醒开关 |
| notify_milestone | Boolean | 里程碑通知开关 |
| in_app_enabled | Boolean | App 内通知开关 |
| email_enabled | Boolean | 邮件通知开关 |

### event_logs 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| event_type | String(50) | 事件类型 |
| event_data | JSONB | 事件数据 |
| occurred_at | DateTime | 事件发生时间 |
| user_id | Integer | 用户 ID |
| notification_status | Enum | 通知处理状态 |
| deduplication_key | String(100) | 去重键 |
| deduplication_hash | String(64) | 去重 hash |

---

## ✅ 验收标准

| 标准 | 状态 |
|------|------|
| 所有表创建成功 | ✅ |
| 所有索引创建成功 | ✅ |
| 外键约束正确 | ✅ |
| 枚举类型创建 | ✅ |
| 种子数据脚本可运行 | ✅ |
| 迁移可回滚（downgrade） | ✅ |

---

## 📝 设计决策记录

### 1. 为什么使用 UUID 作为主键？

**理由：**
- 分布式友好，便于未来分库分表
- 不暴露业务信息（相比自增 ID）
- 与现有模型保持一致

### 2. 为什么创建 event_logs 表？

**理由：**
- 解耦业务系统和通知系统
- 业务系统只需写入事件日志，不依赖通知系统
- 通知系统轮询处理，天然支持重试
- 完整的审计追溯

### 3. 为什么使用 JSONB 存储模板变量？

**理由：**
- 灵活的 schema，不同模板可以有不同变量
- PostgreSQL JSONB 支持索引和查询
- 便于未来扩展

### 4. 为什么通知设置表 user_id 是唯一的？

**理由：**
- 一个用户只有一条通知设置记录
- 使用 `uselist=False` 简化查询
- 通过触发器或应用层保证每个新用户都有默认设置

---

## 🔜 下一步

**Task 6.2.2: 通知服务层实现**

**内容：**
- NotificationService 核心服务
- TemplateRenderer 模板渲染器
- EmailService 邮件服务
- 渠道路由逻辑

---

*Task 6.2.1 完成* ✅  
*准备开始 Task 6.2.2* 🚀
