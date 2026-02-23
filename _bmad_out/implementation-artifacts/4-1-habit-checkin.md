---
story_id: "4.1"
story_title: "习惯打卡系统"
epic: "Epic 4: 行为习惯养成与情感支持"
status: "done"
priority: "high"
story_points: 5
created_date: "2026-02-23"
last_updated: "2026-02-23"
assigned_to: "unassigned"
related_eps:
  - "FR5: 行为习惯养成"
  - "FR7: 情感支持系统"

# Story Metadata
module: "Habit Management"
sprint: "Sprint 5"
dependencies:
  - "Story 1.7: 数据库模型设计与初始化"
  - "Story 1.5: 主仪表盘功能"

---

## Story Overview

### User Story

作为想要建立健康习惯的用户，
我想要创建和管理我的习惯，
以便我可以通过每日打卡来建立可持续的行为模式。

### Business Value

习惯打卡系统是行为习惯养成的核心功能，帮助用户建立和追踪健康行为模式。通过每日打卡和连续天数（Streak）追踪，用户可以直观地看到自己的进步，从而获得持续的动力和成就感。该系统与其他Epic紧密关联，为后续的习惯进度追踪、情感支持和游戏化激励系统提供基础数据支撑。

### Technical Context

- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **Notifications**: 定时任务系统 + 消息推送服务
- **Related Tables**: habits (习惯表), habit_logs (习惯打卡表)

---

## Functional Requirements

### FR-4.1.1: 习惯创建功能

系统应允许用户创建和管理个人习惯，包括设置习惯名称、选择频率、配置提醒时间等。

**User Interactions:**

- 用户点击"创建新习惯"按钮，系统显示习惯创建表单
- 用户填写习惯名称（必填，最多50字符）
- 用户选择习惯频率（每日、每周N次、自定义）
- 用户设置提醒时间（可选）
- 用户选择习惯分类（运动、饮食、睡眠、冥想、其他）
- 用户提交表单，系统保存习惯

**System Behaviors:**

- 表单验证：习惯名称不能为空，不能超过50字符
- 频率验证：每周次数必须在1-7之间
- 提醒时间格式验证：24小时制，格式为HH:MM
- 自动生成唯一习惯ID
- 创建习惯后自动设置当日状态为"未打卡"

**Edge Cases:**

- 用户未填写习惯名称：显示错误提示"请输入习惯名称"
- 用户选择每周N次但未指定次数：默认设为3次
- 用户设置的历史提醒时间已过：自动调整为次日提醒时间

### FR-4.1.2: 习惯模板功能

系统应提供常见习惯模板，帮助用户快速创建习惯。

**User Interactions:**

- 用户在习惯创建页面查看习惯模板列表
- 用户点击模板，系统自动填充习惯名称、频率、分类
- 用户可自定义修改模板内容后保存

**System Behaviors:**

- 提供以下默认模板：
  - "每日喝水8杯" - 每日频率，饮食分类
  - "每周运动3次" - 每周3次，运动分类
  - "每晚10点前入睡" - 每日频率，睡眠分类
  - "每日冥想10分钟" - 每日频率，冥想分类
  - "每天吃早餐" - 每日频率，饮食分类
  - "每日步行10000步" - 每日频率，运动分类

### FR-4.1.3: 每日打卡功能

系统应允许用户对习惯进行每日打卡，记录完成状态。

**User Interactions:**

- 用户在习惯列表页面查看今日待打卡习惯
- 用户点击习惯卡片上的"打卡"按钮
- 系统记录打卡时间并更新状态

**System Behaviors:**

- 打卡时自动记录当前时间戳
- 更新习惯的完成状态为"已完成"
- 同一天内重复打卡：更新打卡时间，显示"今日已打卡"
- 打卡成功后显示成功提示和鼓励消息

**Edge Cases:**

- 用户在非活跃时间打卡（如凌晨4点）：仍记录为当日打卡
- 网络中断后重试：确保打卡记录不重复
- 打卡后立即查看：状态即时更新，无需刷新页面

### FR-4.1.4: Streak连续打卡追踪

系统应计算并显示用户的连续打卡天数（Streak），激励用户持续坚持。

**User Interactions:**

- 用户在习惯卡片上查看当前连续打卡天数
- 用户在习惯详情页面查看完整打卡历史

**System Behaviors:**

- 连续打卡天数计算规则：
  - 每日习惯：按自然日计算，中断一天则Streak重置为0
  - 每周习惯：按周计算，本周完成目标次数则Streak+1
- 显示当前连续打卡天数
- 显示历史最高连续打卡天数
- 连续打卡7天以上：显示"一周坚持"标签
- 连续打卡30天以上：显示"月度坚持"标签
- 连续打卡100天以上：显示"百日坚持"标签

**Edge Cases:**

- 习惯刚创建无打卡记录：Streak显示为0
- 跨时区用户：按服务器时区计算
- 用户修改习惯频率：重新计算Streak

### FR-4.1.5: 习惯提醒通知

系统应在用户设置的时间发送习惯打卡提醒通知。

**User Interactions:**

- 用户在创建/编辑习惯时设置提醒时间
- 用户可以开启/关闭提醒开关
- 用户可以修改提醒时间

**System Behaviors:**

- 提醒时间格式：24小时制（HH:MM）
- 提醒内容：包含习惯名称和打卡链接
- 提醒方式：应用内通知 + 推送通知（移动端）
- 同一时间多个习惯提醒：合并为一条通知
- 免打扰时段：用户可设置免打扰时段（默认22:00-08:00）

**Edge Cases:**

- 用户未设置提醒时间：默认不发送提醒
- 服务器时间与用户设备时间差异：使用服务器时间
- 提醒发送失败：记录失败日志，下次重试

### FR-4.1.6: 习惯编辑与删除

系统应允许用户编辑和删除已创建的习惯。

**User Interactions:**

- 用户点击习惯卡片上的编辑按钮
- 用户修改习惯信息并保存
- 用户点击删除按钮并确认删除

**System Behaviors:**

- 编辑时保留历史打卡记录
- 删除时提示"删除后历史记录将不可恢复"
- 删除习惯同时删除相关的打卡记录
- 编辑成功后显示成功提示

---

## UI/UX Requirements

### Layout Structure

**习惯管理主页面:**

- 顶部：页面标题"我的习惯" + "创建新习惯"按钮
- 中部：习惯卡片网格布局（每行2-3个卡片，视屏幕宽度）
- 每个习惯卡片包含：
  - 习惯图标（根据分类显示）
  - 习惯名称
  - 频率描述（如"每天"、"每周3次"）
  - 今日打卡状态（未打卡/已打卡）
  - 连续打卡天数
  - 快捷打卡按钮

**习惯创建/编辑页面:**

- 顶部：页面标题 + 保存/取消按钮
- 表单区域：
  - 习惯名称输入框
  - 习惯分类下拉选择
  - 频率选择器（单选/数字输入）
  - 提醒时间选择器
  - 提醒开关
- 底部：习惯模板快捷入口

**习惯详情/历史页面:**

- 顶部：习惯信息 + 编辑/删除按钮
- 中部：打卡日历视图（本月）
- 底部：统计信息（总打卡次数、最长Streak、当前Streak）

### Visual Design

**Color Palette:**

- 主色调：#4F46E5 (indigo-600)
- 成功色：#10B981 (emerald-500)
- 警告色：#F59E0B (amber-500)
- 背景色：#F9FAFB (gray-50)
- 卡片背景：#FFFFFF
- 文字主色：#111827 (gray-900)
- 文字次色：#6B7280 (gray-500)

**Typography:**

- 标题：font-weight: 600, font-size: 20px
- 习惯名称：font-weight: 500, font-size: 16px
- 辅助文字：font-weight: 400, font-size: 14px

**Spacing:**

- 页面边距：16px (移动端) / 24px (平板/桌面)
- 卡片间距：12px
- 卡片内边距：16px
- 元素间距：8px

**Components:**

- 打卡按钮：圆角矩形，背景色#4F46E5，文字白色
- 已打卡状态：绿色对勾图标 + "今日已完成"
- Streak显示：火焰图标 + 数字
- 习惯分类标签：圆角标签，不同颜色区分

### Responsive Design

- **移动端 (< 768px)**：
  - 单列布局
  - 习惯卡片全宽显示
  - 打卡按钮全宽
  - 底部导航固定

- **平板 (768px - 1024px)**：
  - 双列布局
  - 习惯卡片并排显示

- **桌面 (> 1024px)**：
  - 三列布局
  - 显示更多辅助信息

---

## API Endpoints

### Backend API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/habits | 创建新习惯 |
| GET | /api/v1/habits | 获取用户习惯列表 |
| GET | /api/v1/habits/{habit_id} | 获取习惯详情 |
| PUT | /api/v1/habits/{habit_id} | 更新习惯 |
| DELETE | /api/v1/habits/{habit_id} | 删除习惯 |
| POST | /api/v1/habits/{habit_id}/checkin | 打卡 |
| GET | /api/v1/habits/{habit_id}/logs | 获取打卡记录 |
| GET | /api/v1/habits/{habit_id}/stats | 获取习惯统计 |

### Data Models

**Habit Model:**

```python
class Habit(Base):
    id: UUID (Primary Key)
    user_id: UUID (Foreign Key)
    name: str (max 50)
    category: str (enum: exercise, diet, sleep, meditation, other)
    frequency_type: str (enum: daily, weekly, custom)
    frequency_value: int (1-7)
    reminder_enabled: bool
    reminder_time: Time (nullable)
    created_at: DateTime
    updated_at: DateTime
    is_active: bool
```

**HabitLog Model:**

```python
class HabitLog(Base):
    id: UUID (Primary Key)
    habit_id: UUID (Foreign Key)
    user_id: UUID (Foreign Key)
    checkin_date: Date
    checkin_time: DateTime
    created_at: DateTime
```

---

## Acceptance Criteria

### AC-4.1.1: 习惯创建

**Given** 用户进入习惯管理页面
**When** 用户点击"创建新习惯"按钮
**Then** 系统显示习惯创建表单，包含习惯名称、频率、提醒时间
**And** 提供常见习惯模板（如"每日喝水8杯"、"每周运动3次"）

### AC-4.1.2: 习惯保存

**Given** 用户创建习惯
**When** 用户填写习惯信息并保存
**Then** 系统将习惯添加到用户习惯列表
**And** 设置提醒通知（如启用）

### AC-4.1.3: 每日打卡

**Given** 用户需要打卡习惯
**When** 用户点击习惯卡片上的"打卡"按钮
**Then** 系统记录打卡时间
**And** 更新习惯完成状态

### AC-4.1.4: Streak显示

**Given** 用户查看习惯记录
**When** 用户访问习惯历史页面
**Then** 系统显示习惯完成日历
**And** 计算并显示连续打卡天数（Streak）

### AC-4.1.5: 习惯模板

**Given** 用户在创建习惯页面
**When** 用户选择习惯模板
**Then** 系统自动填充习惯名称、频率和分类
**And** 允许用户自定义修改

### AC-4.1.6: 提醒功能

**Given** 用户设置了习惯提醒
**When** 到达提醒时间
**Then** 系统发送打卡提醒通知
**And** 通知包含习惯名称和快捷打卡入口

### AC-4.1.7: 习惯编辑

**Given** 用户需要修改习惯
**When** 用户点击编辑按钮并保存
**Then** 系统更新习惯信息
**And** 保留历史打卡记录

### AC-4.1.8: 习惯删除

**Given** 用户需要删除习惯
**When** 用户确认删除
**Then** 系统删除习惯及其相关打卡记录
**And** 从习惯列表中移除

### AC-4.1.9: 性能要求

**Given** 用户加载习惯页面
**When** 用户进入习惯管理页面
**Then** 页面加载时间 < 1秒
**And** 打卡操作响应时间 < 200ms

### AC-4.1.10: 并发处理

**Given** 多个用户同时打卡
**When** 用户提交打卡请求
**Then** 系统能正确处理并发请求
**And** 不出现数据竞争或重复记录

---

## Testing Requirements

### Unit Tests

- Habit模型创建和验证测试
- 频率计算逻辑测试
- Streak计算算法测试
- 表单验证测试

### Integration Tests

- 习惯CRUD API测试
- 打卡功能API测试
- 习惯统计API测试

### E2E Tests

- 完整习惯创建流程
- 打卡并查看Streak流程
- 习惯编辑和删除流程

---

## Implementation Notes

### Phase 1: 基础功能

1. 创建习惯数据模型和数据库迁移
2. 实现习惯CRUD API
3. 实现打卡功能
4. 实现Streak计算逻辑

### Phase 2: UI实现

1. 习惯列表页面开发
2. 习惯创建/编辑表单开发
3. 打卡功能前端集成
4. 习惯日历视图开发

### Phase 3: 增强功能

1. 提醒通知功能开发
2. 习惯模板功能
3. 习惯统计分析页面

---

## Definition of Done

- [x] 习惯创建功能完成并测试通过
- [x] 习惯模板功能完成并测试通过
- [x] 每日打卡功能完成并测试通过
- [x] Streak追踪功能完成并测试通过
- [ ] 提醒通知功能完成并测试通过
- [x] 习惯编辑和删除功能完成并测试通过
- [x] 前端UI/UX符合设计规范
- [x] 响应式设计适配三种设备
- [ ] 代码审查通过
- [ ] 文档更新完成

---

## Tasks/Subtasks

### Phase 1: 基础功能 (Backend)
- [x] 1.1 创建习惯数据模型和数据库迁移
- [x] 1.2 实现习惯CRUD API
- [x] 1.3 实现打卡功能
- [x] 1.4 实现Streak计算逻辑

### Phase 2: UI实现 (Frontend)
- [x] 2.1 习惯列表页面开发
- [x] 2.2 习惯创建/编辑表单开发
- [x] 2.3 打卡功能前端集成
- [x] 2.4 习惯日历视图开发
- [x] 2.5 习惯模板快捷入口
- [x] 2.6 习惯编辑和删除功能

### Phase 3: 增强功能
- [ ] 3.1 提醒通知功能开发 (需要后台任务调度系统)
- [ ] 3.2 习惯统计分析页面
- [x] 3.3 习惯模板功能

---

## Dev Agent Record

### Implementation Plan

实现策略：
1. 利用现有后端Habit模型和服务（已完整实现）
2. 扩展前端Habits页面，增加：
   - 习惯创建/编辑模态框
   - 习惯模板快捷选择
   - 打卡日历视图
   - Streak徽章显示（一周坚持、月度坚持、百日坚持）
3. 添加新的API端点支持模板数据
4. 保持与现有UI设计规范一致

### Debug Log

- 修复前端TypeScript类型错误：修正target_value类型定义
- 修复未使用导入警告
- 添加HabitCompletion接口定义

### Completion Notes

已完成功能：
1. **习惯创建** - 创建习惯表单支持名称、分类、频率、目标值、提醒设置
2. **习惯模板** - 6个预设模板快速创建（喝水、运动、睡眠、冥想、饮食、步行）
3. **每日打卡** - 一键打卡，显示完成状态和鼓励消息
4. **Streak追踪** - 显示连续天数，7+/30+/100+显示特殊徽章
5. **习惯编辑** - 完整编辑功能，保留历史记录
6. **习惯删除** - 确认对话框，删除相关打卡记录
7. **日历视图** - 查看每月打卡历史，显示统计信息
8. **响应式设计** - 适配移动端/平板/桌面

待完成：
- 提醒通知功能需要后台任务调度系统（Celery/APScheduler）
- 代码审查
- 文档更新

---

## File List

Modified:
- /Users/felix/bmad/frontend/src/pages/Habits.tsx
- /Users/felix/bmad/frontend/src/api/client.ts
- /Users/felix/bmad/backend/app/api/v1/endpoints/habits.py

---

## Change Log

- 2026-02-23: 实现习惯打卡系统核心功能
  - 添加习惯创建/编辑/删除UI
  - 添加习惯模板功能
  - 添加打卡日历视图
  - 添加Streak徽章显示
  - 添加后端模板API端点
  - 完善TypeScript类型定义

---

## Status

status: review
