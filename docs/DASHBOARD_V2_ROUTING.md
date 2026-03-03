# Dashboard V2 路由配置说明

**文件**: `/Users/felix/bmad/frontend/src/pages/DashboardV2.tsx`  
**状态**: ✅ 已完成开发  
**下一步**: 测试 + 路由配置

---

## 📐 5 行布局实现

### ✅ 已完成

| 行 | 内容 | 状态 |
|----|------|------|
| 第 0 行 | 欢迎 Banner | ✅ 完成 |
| 第 1 行 | 热量净变化 Card | ✅ 完成 |
| 第 2 行 | 运动打卡 + 饮食打卡 | ✅ 完成 |
| 第 3 行 | 4 个习惯快捷入口 | ✅ 完成 |
| 第 4 行 | AI 健康顾问 | ✅ 完成 |

---

## 🔗 路由配置

### 方案 A：替换现有 Dashboard（推荐用于测试）

1. **临时修改 App.tsx**
```tsx
// 原代码
<Route path="/" element={<Layout><Navigate to="/dashboard" replace /></Layout>} />
<Route path="/dashboard" element={<DashboardSimple />} />

// 修改为
<Route path="/" element={<Layout><Navigate to="/dashboard-v2" replace /></Layout>} />
<Route path="/dashboard-v2" element={<DashboardV2 />} />
```

2. **访问测试**
```
http://localhost:3000/dashboard-v2
```

### 方案 B：并行运行两个版本

保留 `DashboardSimple.tsx`，同时测试 `DashboardV2.tsx`：

```tsx
<Route path="/dashboard" element={<DashboardSimple />} />
<Route path="/dashboard-v2" element={<DashboardV2 />} />
```

---

## ⚠️ TODO: 待完成

### 1. 习惯打卡页面跳转

当前 4 个习惯按钮都跳转到 `/habits`，需要更新为独立页面：

```tsx
// DashboardV2.tsx line ~60
case 'water':
  navigate('/habits/water'); // TODO: 创建饮水打卡页
  break;
case 'weight':
  navigate('/habits/weight'); // TODO: 创建体重打卡页
  break;
case 'sleep':
  navigate('/habits/sleep'); // TODO: 创建早睡打卡页
  break;
case 'meditation':
  navigate('/habits/meditation'); // TODO: 创建冥想打卡页
  break;
```

### 2. 习惯状态数据

当前习惯状态是硬编码的，需要从后端获取：

```tsx
// 需要从 API 获取
const [habitStatus, setHabitStatus] = useState<HabitStatus>({
  water: { completed: 0, target: 8 }, // TODO: 从 API 获取
  weight: { recorded: false },
  sleep: { completed: false },
  meditation: { completed: false }
});
```

### 3. AI 建议数据

当前 AI 建议是硬编码的，需要调用 AI API：

```tsx
// TODO: 调用 AI API 获取个性化建议
const aiSuggestions = await api.getAIHealthSuggestions();
```

---

## 🧪 测试清单

- [ ] Dashboard V2 正常加载
- [ ] 5 行布局正确显示
- [ ] 热量计算正确
- [ ] 运动/饮食数据正确显示
- [ ] 4 个习惯按钮点击跳转正常
- [ ] AI 顾问区域正常显示
- [ ] 响应式布局正常（移动端/桌面端）
- [ ] 无 TypeScript 错误
- [ ] 无控制台错误

---

## 📊 对比

| 特性 | Dashboard V1 | Dashboard V2 |
|------|-------------|-------------|
| 布局 | 卡片网格 | 5 行结构 |
| 习惯快捷 | "完成习惯"按钮 | 4 个独立按钮 |
| 热量展示 | 单一数值 | 详细计算过程 |
| AI 顾问 | 简单入口 | 智能建议展示 |
| 欢迎 Banner | 简单问候 | 体重 + 坚持天数 |

---

**状态**: ✅ 开发完成，等待测试和路由配置
