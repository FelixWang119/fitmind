# Story 9.2: Dashboard 科普卡片组件

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为 **用户**，
我想要 **在首页 Dashboard 看到今日科普卡片**，
以便 **轻松学习健康知识，提升产品信任度**。

## Acceptance Criteria

1. [ ] Dashboard 展示科普卡片（小卡片形式）(AC: #1)
2. [ ] 显示标题 + 摘要（50字内）(AC: #2)
3. [ ] 点击展开查看全文 (AC: #3)
4. [ ] 底部显示："明天同一时间更新"(AC: #4)
5. [ ] 记录用户已读/未读状态 (AC: #5)
6. [ ] 支持分享功能 (AC: #6)

## Tasks / Subtasks

- [ ] Task 1: 创建科普卡片组件 DailyTipCard (AC: #1, #2)
  - [ ] Subtask 1.1: 在 frontend/src/components/Dashboard/ 创建 DailyTipCard.tsx
  - [ ] Subtask 1.2: 设计小卡片布局（标题 + 摘要 + 展开按钮）
  - [ ] Subtask 1.3: 适配 DashboardV2 样式风格
- [ ] Task 2: 获取当日科普内容 API 集成 (AC: #1, #2)
  - [ ] Subtask 2.1: 在 frontend/src/api/ 创建 dailyTip.ts API 模块
  - [ ] Subtask 2.2: 调用 GET /daily-tips/today 获取当日科普
  - [ ] Subtask 2.3: 处理无内容/加载中/错误状态
- [ ] Task 3: 实现展开/收起动画 (AC: #3)
  - [ ] Subtask 3.1: 添加展开/收起过渡动画
  - [ ] Subtask 3.2: 实现内容区域高度动画
  - [ ] Subtask 3.3: 添加"收起"按钮
- [ ] Task 4: 添加已读状态跟踪 (AC: #5)
  - [ ] Subtask: 设计 4.1已读/未读状态数据结构
  - [ ] Subtask 4.2: 实现本地存储已读状态
  - [ ] Subtask 4.3: 未读状态显示视觉提示（如小圆点）
- [ ] Task 5: 添加分享功能 (AC: #6)
  - [ ] Subtask 5.1: 实现复制链接分享
  - [ ] Subtask 5.2: 添加底部"明天同一时间更新"文案
  - [ ] Subtask 5.3: 适配移动端分享菜单
- [ ] Task 6: 集成到 DashboardV2 页面 (AC: #1)
  - [ ] Subtask 6.1: 在 DashboardV2 引入 DailyTipCard 组件
  - [ ] Subtask 6.2: 测试卡片在 Dashboard 中的展示效果
  - [ ] Subtask 6.3: 确保响应式布局适配

## Dev Notes

### 技术栈与模式

- **前端框架**: React + TypeScript
- **UI 组件库**: Ant Design + TailwindCSS
- **图标库**: Lucide React
- **状态管理**: Zustand（参考现有模式）
- **API 调用**: 现有 client.ts 模式

### 项目结构约束

1. **组件位置**: `frontend/src/components/Dashboard/DailyTipCard.tsx`
2. **API 模块**: `frontend/src/api/dailyTip.ts`
3. **类型定义**: `frontend/src/types/dailyTip.ts`（如需要）
4. **样式方案**: TailwindCSS（现有 Dashboard 组件使用）
5. **布局约束**: 适配 DashboardV2 的网格布局

### API 设计模式

参考 story 9-1 已创建的 API 端点：
- `GET /api/v1/daily-tips/today` - 获取当日科普内容
- 响应结构参考: `backend/app/schemas/daily_tip.py`

**前端 API 调用模式**（参考现有 client.ts）：
```typescript
// 现有模式
async getDailyTip() {
  const response = await this.client.get('/ux/daily-tip');
  return response.data;
}

// 新 story 应使用:
async getDailyTipToday() {
  const response = await this.client.get('/api/v1/daily-tips/today');
  return response.data;
}
```

### 组件设计模式

参考现有 Dashboard 组件结构：

**Cards.tsx 模式** - 简洁卡片：
```typescript
export const StatCard: React.FC<StatCardProps> = ({ icon, title, value, children }) => (
  <div className="bg-white rounded-xl shadow p-6">
    {/* 标题 + 图标 + 内容 */}
  </div>
);
```

**ActivityCard.tsx 模式** - 交互式卡片：
```typescript
interface ActivityCardProps {
  icon: React.ReactNode;
  title: string;
  stats: Array<{...}>;
  progress?: number;
  onClick: () => void;
}
```

**科普卡片应结合两者特点**：
- 小卡片形式（类似 StatCard 简洁风格）
- 可展开全文（类似 ActivityCard 交互）
- 底部固定文案（类似 CalorieCard 的帮助提示）

### UI/UX 设计要点

1. **卡片尺寸**: 小卡片形式，宽度自适应，建议 max-width: 400px
2. **内容布局**:
   - 顶部: 主题图标 + 标题
   - 中部: 摘要（50字内）+ "展开看全文"按钮
   - 展开后: 完整内容（300-500字）+ 医学免责声明
   - 底部: "明天同一时间更新"固定文案 + 分享按钮
3. **视觉风格**:
   - 背景: 白色或浅色渐变
   - 圆角: rounded-xl（与现有卡片一致）
   - 阴影: shadow（与现有卡片一致）
   - 主题色: 使用绿色系（与健康主题一致）
4. **交互设计**:
   - 展开动画: 200-300ms ease-in-out
   - 已读状态: 标题旁小圆点提示
   - 分享: 点击后弹出分享菜单

### 测试标准

- 单元测试覆盖组件渲染
- 组件在不同内容长度下的表现
- 展开/收起动画流畅度
- 已读状态本地存储功能
- 响应式布局适配（移动端/平板/桌面）
- API 错误处理和加载状态

### References

- [Source: _bmad_out/planning-artifacts/epic-9-daily-tip.md#Story-9.2]
- [Source: _bmad_out/implementation-artifacts/9-1-daily-tip-generation.md - 前序故事，包含 API 端点实现]
- [Source: frontend/src/components/Dashboard/Cards.tsx - Dashboard 卡片组件参考]
- [Source: frontend/src/components/Dashboard/ActivityCard.tsx - 交互式卡片参考]
- [Source: frontend/src/api/client.ts - API 调用模式参考]
- [Source: backend/app/schemas/daily_tip.py - API 响应 Schema 参考]
- [Source: backend/app/api/v1/endpoints/daily_tip.py - API 端点实现参考]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

N/A

### Completion Notes List

N/A - Implementation not yet started

### File List

New files to create:
- frontend/src/components/Dashboard/DailyTipCard.tsx
- frontend/src/api/dailyTip.ts

Modified files:
- frontend/src/pages/DashboardV2.tsx (添加科普卡片组件)
- frontend/src/api/client.ts (可选，如需扩展)

## 依赖说明

### 前置依赖 (Story 9.1)

Story 9.1 已完成以下工作，为本 story 提供基础:

1. **后端 API 端点**:
   - `GET /api/v1/daily-tips/today` - 获取当日科普
   - `GET /api/v1/daily-tips` - 获取历史科普列表
   - `POST /api/v1/daily-tips/regenerate` - 手动触发重新生成

2. **数据库模型**:
   - `DailyTip` 表结构已创建
   - 字段: id, date, topic, title, summary, content, disclaimer, is_active, created_at, updated_at

3. **数据模型 Schema**:
   - `backend/app/schemas/daily_tip.py` 定义了完整的响应结构

4. **前端 API 引用**:
   - 现有 `client.ts` 中有 `/ux/daily-tip` 端点调用
   - 建议本 story 使用 `/api/v1/daily-tips/today` 获取更完整数据

### 依赖本 story 的后续 Story

- **Story 9.3**: 通知引导 - 需要科普卡片展示完成后集成
- **Story 9.4**: 科普历史记录 - 分享功能可链接到历史页面

