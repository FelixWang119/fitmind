# Dashboard 5 行布局更新指南

**Story**: SP-3.1  
**日期**: 2026-03-01  
**状态**: 开发中

---

## 📐 新的 5 行布局

### 第 0 行：欢迎 Banner
```tsx
<header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
  <div>
    <h1>👋 早上好，Felix！新的一天，继续照顾好自己 💪</h1>
    <p>今日体重 68.5kg | 已坚持 12 天</p>
  </div>
</header>
```

### 第 1 行：热量净变化 Card（核心指标）
```tsx
<div className="bg-white rounded-xl shadow p-6">
  <h2>🔥 今日热量净变化</h2>
  <div className="text-3xl font-bold text-red-600">+350 大卡（盈余）</div>
  <p>摄入 2150 - 消耗 1800 = 盈余 350</p>
  💡 建议：今晚散步 20 分钟 或 晚餐减少 100g 米饭
</div>
```

### 第 2 行：运动打卡 + 饮食打卡
```tsx
<div className="grid grid-cols-2 gap-6">
  {/* 运动打卡 */}
  <div className="bg-white rounded-xl shadow p-6">
    <h3>🏃 运动打卡</h3>
    <p>今日运动</p>
    <p>🚶 步行 30 分钟</p>
    <p>🔥 消耗 180 大卡</p>
    <button>[+ 记录运动]</button>
  </div>
  
  {/* 饮食打卡 */}
  <div className="bg-white rounded-xl shadow p-6">
    <h3>🍽️ 饮食打卡</h3>
    <p>今日饮食</p>
    <p>🥣 早餐 450 大卡</p>
    <p>🥗 午餐 680 大卡</p>
    <p>🍜 晚餐 1020 大卡</p>
    <button>[+ 记录饮食]</button>
  </div>
</div>
```

### 第 3 行：快捷操作（4 个习惯）
```tsx
<div className="grid grid-cols-4 gap-4">
  {/* 饮水 */}
  <button onClick={() => handleQuickAction('water')} className="...">
    <div className="text-2xl">💧</div>
    <p>8 杯水</p>
    <p>5/8 杯 ✅</p>
  </button>
  
  {/* 体重 */}
  <button onClick={() => handleQuickAction('weight')} className="...">
    <div className="text-2xl">⚖️</div>
    <p>体重</p>
    <p>未记录 ⏳</p>
  </button>
  
  {/* 早睡 */}
  <button onClick={() => handleQuickAction('sleep')} className="...">
    <div className="text-2xl">🌙</div>
    <p>早睡</p>
    <p>未打卡 ❌</p>
  </button>
  
  {/* 冥想 */}
  <button onClick={() => handleQuickAction('meditation')} className="...">
    <div className="text-2xl">🧘</div>
    <p>冥想</p>
    <p>已完成 ✅</p>
  </button>
</div>
```

### 第 4 行：AI 健康顾问
```tsx
<div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl shadow p-6 text-white">
  <h3>🤖 AI 健康顾问</h3>
  <p>💡 今日观察</p>
  <ul>
    <li>你今天的热量盈余主要来自晚餐（1020 大卡）</li>
    <li>💧 喝水提醒：今天还没喝够 8 杯水哦～</li>
    <li>🌙 昨晚睡得很好，继续保持 23 点前入睡！</li>
  </ul>
  <button>[💬 和 AI 聊聊]</button>
  <button>[📊 查看详细分析]</button>
</div>
```

---

## ✅ 已完成

- [x] 更新导入（添加新图标）
- [x] 更新 handleQuickAction 函数（支持 4 个习惯）

## ⏳ 待完成

- [ ] 更新 render 部分为 5 行布局
- [ ] 移除旧的快捷操作（StepCountCard, WaterIntakeCard 等）
- [ ] 添加新的习惯快捷按钮
- [ ] 更新 AI 顾问组件
- [ ] 测试响应式布局

---

## 📝 下一步

由于 Dashboard 布局变化较大，建议：

1. **先完成核心布局**（5 行结构）
2. **再逐步完善每个组件**
3. **最后调整样式和响应式**

可以先在一个新的临时文件中实验布局，确认无误后再替换原文件。
