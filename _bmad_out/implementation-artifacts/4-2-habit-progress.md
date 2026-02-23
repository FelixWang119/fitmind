---
story_id: "4.2"
story_title: "习惯进度追踪"
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
sprint: "Sprint 6"
dependencies:
  - "Story 4.1: 习惯打卡系统"
  - "Story 1.7: 数据库模型设计与初始化"

---

## Story Overview

### User Story

作为关注习惯进展的用户，
我想要查看我的习惯完成统计和分析，
以便我可以了解我的行为改变进度和模式。

### Business Value

习惯进度追踪功能是行为习惯养成系统的重要组成部分，帮助用户从宏观和微观两个层面分析自己的习惯养成进度。通过完成率统计、详细习惯分析、行为模式识别和目标设置，用户可以科学地评估自己的行为改变效果，发现潜在问题，并获得针对性的改进建议。该功能与情感支持系统紧密关联，当用户进度不理想时，系统可以提供鼓励和调整建议。

### Technical Context

- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **Charts**: Recharts / Chart.js 数据可视化库
- **Related Tables**: habits (习惯表), habit_logs (习惯打卡表)

---

## Functional Requirements

### FR-4.2.1: 习惯完成率统计

系统应显示用户的整体习惯完成率统计，并以图表形式直观展示。

**User Interactions:**

- 用户进入习惯分析页面
- 用户查看总体完成率统计卡片
- 用户查看不同时间周期的完成率（本周、本月、本季度）

**System Behaviors:**

- 计算公式：完成率 = (实际打卡次数 / 应打卡次数) × 100%
- 显示总体完成率百分比
- 按习惯分类显示完成率（运动类、饮食类、睡眠类等）
- 按时间维度显示完成率趋势（折线图）
- 完成率 >= 80%：显示绿色高亮
- 完成率 50%-80%：显示黄色提醒
- 完成率 < 50%：显示红色警告

**Edge Cases:**

- 用户刚创建习惯无数据：显示"暂无数据，请先开始打卡"
- 所有习惯均未打卡：显示鼓励消息"开始你的第一个打卡吧！"
- 跨时区数据：使用服务器时区统一计算

### FR-4.2.2: 单个习惯详细分析

系统应提供单个习惯的详细统计数据和分析报告。

**User Interactions:**

- 用户点击具体习惯卡片
- 用户查看该习惯的详细统计页面

**System Behaviors:**

- 显示该习惯的总打卡次数
- 显示当前连续打卡天数（Current Streak）
- 显示历史最长连续打卡天数（Best Streak）
- 显示完成率趋势图（最近30天）
- 显示打卡时间分布（分析最佳打卡时间段）
- 显示每周完成模式（周一到周日完成率）
- 显示每月完成模式（1日到月末完成率）

**Edge Cases:**

- 习惯刚创建少于7天：显示"数据积累中..."
- 无完整月份数据：不显示月度统计
- 打卡时间异常（如凌晨打卡）：标记显示

### FR-4.2.3: 行为模式分析

系统应分析用户的习惯行为模式，识别习惯之间的关联和影响。

**User Interactions:**

- 用户访问行为模式分析页面
- 用户查看习惯关联性分析

**System Behaviors:**

- 分析习惯完成的时间模式：
  - 早晨型（6-10点完成最多）
  - 上午型（10-14点完成最多）
  - 下午型（14-18点完成最多）
  - 晚间型（18-24点完成最多）
- 分析习惯完成的星期模式：
  - 工作日 vs 周末完成率对比
  - 周一至周五各自完成率
- 分析习惯关联性：
  - 识别经常一起完成的习惯组合
  - 分析一个习惯完成是否促进其他习惯完成
- 显示行为洞察：
  - "你倾向于在晚间完成习惯"
  - "周末完成率比工作日高15%"

**Edge Cases:**

- 数据不足无法分析：显示"需要更多数据来分析你的行为模式"
- 只有一个习惯：显示"添加更多习惯以解锁行为分析"

### FR-4.2.4: 习惯目标设置与追踪

系统应允许用户为习惯设置目标，并追踪目标完成进度。

**User Interactions:**

- 用户点击"设置目标"按钮
- 用户选择目标类型（完成率目标、连续天数目标）
- 用户设置具体目标值
- 用户查看目标进度

**System Behaviors:**

- 支持的目标类型：
  - 完成率目标：每周/每月完成率目标（默认80%）
  - 连续天数目标：设定目标连续打卡天数
  - 总次数目标：设定每周/每月打卡总次数
- 目标进度计算：
  - 当前进度 / 目标值 × 100%
- 目标达成提醒：
  - 达成目标时显示庆祝消息
  - 未达成目标时显示鼓励消息和原因分析
- 目标历史：
  - 记录用户历史目标及达成情况
  - 显示目标达成率

**Edge Cases:**

- 用户未设置目标：显示默认目标（每周80%完成率）
- 目标已过期：自动移至历史记录
- 目标设置不合理（如目标值过低）：显示建议提示

---

## UI/UX Requirements

### Layout Structure

**习惯分析主页面:**

- 顶部：页面标题"习惯分析" + 时间周期选择器（本周/本月/本季度）
- 顶部统计卡片区：
  - 总完成率百分比
  - 本周已打卡次数 / 应打卡次数
  - 当前最长连续天数
- 中部图表区：
  - 完成率趋势折线图（最近30天）
  - 分类完成率饼图/条形图
- 底部习惯列表：每个习惯的完成率概览

**单个习惯详情页面:**

- 顶部：习惯名称 + 编辑按钮
- 统计卡片区：
  - 总打卡次数
  - 当前Streak / 最佳Streak
  - 完成率
- 图表区：
  - 30天完成趋势图
  - 打卡时间分布直方图
  - 每周完成模式图
- 目标进度区：
  - 当前目标类型和目标值
  - 进度条显示
  - 达成/未达成状态

**行为模式分析页面:**

- 顶部：页面标题"行为模式"
- 时间模式区：
  - 一天中的打卡时间分布图
  - 最活跃时间段标注
- 星期模式区：
  - 一周完成率对比图
  - 工作日vs周末对比
- 习惯关联区：
  - 习惯组合展示
  - 关联洞察文字

### Visual Design

**Color Palette:**

- 主色调：#4F46E5 (indigo-600)
- 成功色：#10B981 (emerald-500)
- 警告色：#F59E0B (amber-500)
- 危险色：#EF4444 (red-500)
- 背景色：#F9FAFB (gray-50)
- 卡片背景：#FFFFFF
- 文字主色：#111827 (gray-900)
- 文字次色：#6B7280 (gray-500)

**Typography:**

- 页面标题：font-weight: 700, font-size: 24px
- 统计数字：font-weight: 700, font-size: 32px
- 卡片标题：font-weight: 600, font-size: 18px
- 正文文字：font-weight: 400, font-size: 14px

**Spacing:**

- 页面边距：16px (移动端) / 24px (平板/桌面)
- 卡片间距：16px
- 卡片内边距：20px
- 图表区域高度：200-300px

**Components:**

- 完成率统计卡片：圆角卡片，数字大号显示
- 趋势图：Recharts折线图，带数据点提示
- 进度条：圆角进度条，颜色根据进度变化
- 目标状态标签：达成(绿色)、进行中(蓝色)、未达成(灰色)

### Responsive Design

- **移动端 (< 768px)**：
  - 单列布局
  - 统计卡片垂直排列
  - 图表使用简化版本
  - 图表区域可横向滚动

- **平板 (768px - 1024px)**：
  - 双列布局
  - 统计卡片两两排列

- **桌面 (> 1024px)**：
  - 多列布局
  - 侧边栏显示快捷导航
  - 完整图表展示

---

## API Endpoints

### Backend API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/habits/stats/overview | 获取习惯统计概览 |
| GET | /api/v1/habits/stats/completion | 获取完成率统计 |
| GET | /api/v1/habits/{habit_id}/detailed-stats | 获取单个习惯详细统计 |
| GET | /api/v1/habits/stats/patterns | 获取行为模式分析 |
| GET | /api/v1/habits/goals | 获取习惯目标列表 |
| POST | /api/v1/habits/goals | 创建习惯目标 |
| PUT | /api/v1/habits/goals/{goal_id} | 更新习惯目标 |
| DELETE | /api/v1/habits/goals/{goal_id} | 删除习惯目标 |

### Data Models

**HabitStats Overview:**

```python
class HabitStatsOverview(BaseModel):
    total_habits: int
    active_habits: int
    completion_rate: float  # 0-100
    total_checkins: int
    current_longest_streak: int
    best_streak_ever: int
    weekly_checkins: int
    monthly_checkins: int
    by_category: dict  # {category: rate}
```

**HabitDetailedStats:**

```python
class HabitDetailedStats(BaseModel):
    habit_id: UUID
    total_checkins: int
    current_streak: int
    best_streak: int
    completion_rate: float
    last_30_days_trend: List[DailyStats]
    checkin_time_distribution: Dict[str, int]  # {hour: count}
    weekly_pattern: Dict[str, float]  # {day: rate}
    monthly_pattern: Dict[str, float]  # {day: rate}
```

**BehaviorPatterns:**

```python
class BehaviorPatterns(BaseModel):
    time_preference: str  # morning/afternoon/evening
    checkin_time_histogram: Dict[str, int]
    weekly_pattern: Dict[str, float]
    weekend_vs_weekday: Dict[str, float]
    habit_correlations: List[HabitCorrelation]
    insights: List[str]
```

**HabitGoal:**

```python
class HabitGoal(BaseModel):
    id: UUID
    habit_id: UUID
    goal_type: str  # completion_rate/streak/total_count
    target_value: float
    period: str  # weekly/monthly
    start_date: Date
    end_date: Date
    is_active: bool
    current_progress: float
    is_achieved: bool
```

---

## Acceptance Criteria

### AC-4.2.1: 习惯完成率统计显示

**Given** 用户进入习惯分析页面
**When** 用户查看习惯统计
**Then** 系统显示习惯完成率图表
**And** 显示不同习惯的完成情况对比

### AC-4.2.2: 单个习惯详细分析

**Given** 用户需要详细分析
**When** 用户点击具体习惯
**Then** 系统显示该习惯的详细统计
**And** 提供完成模式分析（如最佳打卡时间）

### AC-4.2.3: 行为模式分析

**Given** 用户查看行为模式
**When** 用户访问行为模式页面
**Then** 系统分析习惯关联性
**And** 显示习惯之间的相互影响（如运动后饮食更健康）

### AC-4.2.4: 习惯目标设置

**Given** 用户设置习惯目标
**When** 用户设定习惯完成目标（如每月完成80%）
**Then** 系统追踪目标进度
**And** 提供改进建议

### AC-4.2.5: 时间周期选择

**Given** 用户查看习惯统计
**When** 用户选择不同时间周期
**Then** 系统更新统计数据显示
**And** 图表随时间变化

### AC-4.2.6: 目标达成通知

**Given** 用户设置的习惯目标达成
**When** 目标完成时
**Then** 系统显示庆祝消息
**And** 记录目标达成历史

### AC-4.2.7: 性能要求

**Given** 用户加载习惯分析页面
**When** 页面加载
**Then** 统计计算响应时间 < 1秒
**And** 图表渲染时间 < 500ms

### AC-4.2.8: 数据可视化

**Given** 用户查看分析图表
**When** 图表数据加载完成
**Then** 图表清晰展示数据趋势
**And** 支持数据点悬停查看详情

---

## Testing Requirements

### Unit Tests

- 完成率计算逻辑测试
- Streak计算算法测试
- 行为模式分析算法测试
- 目标进度计算测试

### Integration Tests

- 习惯统计API测试
- 行为模式API测试
- 目标管理API测试

### E2E Tests

- 查看习惯统计流程
- 查看单个习惯详情流程
- 设置和追踪目标流程
- 查看行为模式分析流程

---

## Implementation Notes

### Phase 1: 后端API开发

1. 创建习惯统计API端点
2. 实现完成率计算逻辑
3. 实现行为模式分析算法
4. 实现目标管理CRUD

### Phase 2: 前端UI开发

1. 习惯分析主页面开发
2. 单个习惯详情页开发
3. 行为模式分析页开发
4. 目标设置组件开发

### Phase 3: 数据可视化

1. 完成率趋势图
2. 打卡时间分布图
3. 行为模式图表
4. 目标进度可视化

---

## Definition of Done

- [ ] 习惯完成率统计功能完成并测试通过
- [ ] 单个习惯详细分析功能完成并测试通过
- [ ] 行为模式分析功能完成并测试通过
- [ ] 习惯目标设置与追踪功能完成并测试通过
- [ ] 前端UI/UX符合设计规范
- [ ] 响应式设计适配三种设备
- [ ] 数据可视化图表清晰易读
- [ ] 代码审查通过
- [ ] 文档更新完成

---

## Tasks/Subtasks

### Phase 1: 后端API开发
- [ ] 1.1 创建习惯统计API端点
- [ ] 1.2 实现完成率计算逻辑
- [ ] 1.3 实现行为模式分析算法
- [ ] 1.4 实现目标管理CRUD API

### Phase 2: 前端UI开发
- [ ] 2.1 习惯分析主页面开发
- [ ] 2.2 单个习惯详情页开发
- [ ] 2.3 行为模式分析页开发
- [ ] 2.4 目标设置组件开发

### Phase 3: 数据可视化
- [ ] 3.1 完成率趋势图
- [ ] 3.2 打卡时间分布图
- [ ] 3.3 行为模式图表
- [ ] 3.4 目标进度可视化

---

## File List

New:
- /Users/felix/bmad/frontend/src/pages/HabitStats.tsx
- /Users/felix/bmad/frontend/src/pages/HabitDetail.tsx
- /Users/felix/bmad/frontend/src/pages/BehaviorPatterns.tsx
- /Users/felix/bmad/backend/app/api/v1/endpoints/habit_stats.py

Modified:
- /Users/felix/bmad/frontend/src/App.tsx (添加路由)
- /Users/felix/bmad/frontend/src/api/client.ts

---

## Status

status: ready-for-dev
