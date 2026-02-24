# 餐次类型错乱问题修复

**问题发现日期**: 2026-02-24  
**状态**: ✅ 已修复

---

## 🐛 问题描述

用户上传晚餐照片，识别成功，但保存后：
- **名称**: "dinner 餐食" ✅
- **类型**: "lunch" ❌ (应该是 "dinner")
- **时间**: "12:00:00" ❌ (晚餐应该是 19:00)

导致前端显示混乱：
- 晚餐被归类到午餐
- 时间显示为中午 12 点
- 统计数据不准确

---

## 🔍 根本原因

**前端代码逻辑错误** (`DietTracking.tsx`):

```typescript
// ❌ 错误代码 (第 188-196 行)
const mealData = {
  name: `${selectedMealType}餐食`,        // ✅ 使用用户选择的餐次
  meal_type: photoAnalysis.meal_type,     // ❌ 使用 AI 识别的餐次
  meal_datetime: `${selectedDate}T12:00:00`, // ❌ 固定为中午 12 点
  // ...
}
```

**问题链条**:
1. 用户选择"晚餐" → `selectedMealType = 'dinner'`
2. AI 分析图片 → `photoAnalysis.meal_type = 'lunch'` (AI 可能识别错误)
3. 前端保存 → `meal_type = 'lunch'` (使用了 AI 的值)
4. 结果：名称是"dinner 餐食"，类型却是"lunch"

---

## ✅ 修复方案

### 修复 1: 使用用户选择的餐次

```typescript
// ✅ 修复后代码
const mealData = {
  name: `${selectedMealType}餐食`,
  meal_type: selectedMealType,  // ✅ 使用用户选择的餐次
  // ...
}
```

**理由**:
- 用户最清楚自己吃的是哪一餐
- AI 识别可能出错（如晚餐吃了午餐食物）
- 尊重用户的选择权

### 修复 2: 根据餐次设置合理时间

```typescript
// ✅ 添加 getMealDatetime 函数
const getMealDatetime = (mealType: string): string => {
  const hourMap: Record<string, string> = {
    'breakfast': '08',  // 早餐 8 点
    'lunch': '12',      // 午餐 12 点
    'dinner': '19',     // 晚餐 19 点
    'snack': '15'       // 加餐 15 点
  };
  const hour = hourMap[mealType] || '12';
  return `${selectedDate}T${hour}:00:00${getTimezoneOffset()}`;
};

// 使用
const mealData = {
  meal_datetime: getMealDatetime(selectedMealType), // ✅ 根据餐次设置时间
  // ...
}
```

**时间映射**:
| 餐次 | 英文 | 时间 |
|------|------|------|
| 早餐 | breakfast | 08:00 |
| 午餐 | lunch | 12:00 |
| 晚餐 | dinner | 19:00 |
| 加餐 | snack | 15:00 |

---

## 📊 修复对比

### 修复前

| 字段 | 用户选择 | AI 识别 | 实际保存 | 结果 |
|------|---------|--------|---------|------|
| 名称 | dinner | - | dinner 餐食 | ✅ |
| 类型 | dinner | lunch | **lunch** | ❌ |
| 时间 | - | - | **12:00** | ❌ |

### 修复后

| 字段 | 用户选择 | AI 识别 | 实际保存 | 结果 |
|------|---------|--------|---------|------|
| 名称 | dinner | - | dinner 餐食 | ✅ |
| 类型 | dinner | lunch | **dinner** | ✅ |
| 时间 | - | - | **19:00** | ✅ |

---

## 🧪 测试验证

### 测试场景 1: 上传晚餐照片

**步骤**:
1. 选择"晚餐"
2. 上传晚餐照片（如面条、虾仁）
3. AI 识别成功
4. 点击"确认保存"

**预期结果**:
```json
{
  "meal_type": "dinner",
  "name": "dinner 餐食",
  "meal_datetime": "2026-02-24T19:00:00+08:00",
  "calories": 560.0,
  "items": [
    {"name": "虾仁", "calories": 180.0},
    {"name": "面条", "calories": 140.0},
    // ...
  ]
}
```

### 测试场景 2: 上传早餐照片

**预期**:
- `meal_type`: "breakfast"
- `meal_datetime`: "2026-02-24T08:00:00+08:00"

### 测试场景 3: 上传加餐照片

**预期**:
- `meal_type`: "snack"
- `meal_datetime`: "2026-02-24T15:00:00+08:00"

---

## 📝 代码变更

**文件**: `frontend/src/pages/DietTracking.tsx`

**变更内容**:

1. **添加函数** (第 82-92 行):
```typescript
// 根据餐次获取合理的时间
const getMealDatetime = (mealType: string): string => {
  const hourMap: Record<string, string> = {
    'breakfast': '08',
    'lunch': '12',
    'dinner': '19',
    'snack': '15'
  };
  const hour = hourMap[mealType] || '12';
  return `${selectedDate}T${hour}:00:00${getTimezoneOffset()}`;
};
```

2. **修改保存逻辑** (第 195 行):
```typescript
// 修改前
meal_type: photoAnalysis.meal_type,
meal_datetime: `${selectedDate}T12:00:00${getTimezoneOffset()}`,

// 修改后
meal_type: selectedMealType,
meal_datetime: getMealDatetime(selectedMealType),
```

---

## 🚀 部署步骤

1. **前端重新构建**:
```bash
cd /Users/felix/bmad/frontend
npm run build
```

2. **刷新浏览器**:
- 清除缓存
- 重新加载页面

3. **测试验证**:
- 上传早餐、午餐、晚餐、加餐各一次
- 验证保存后的餐次类型和时间

---

## 📈 影响评估

### 正面影响
- ✅ 餐次分类准确
- ✅ 时间显示合理
- ✅ 统计数据正确
- ✅ 用户体验提升

### 潜在影响
- ⚠️ AI 识别的餐次信息被忽略（但这不是问题，用户选择更准确）

### 向后兼容
- ✅ 数据库 schema 无需修改
- ✅ API 接口无需修改
- ✅ 历史数据不受影响

---

## 🔗 相关问题

- **发现于**: 2026-02-24 晚餐保存问题排查
- **关联 Issue**: 饮食照片上传识别成功，保存失败
- **相关修复**: 
  - API Schema 字段不一致修复
  - Update endpoint 嵌套对象处理

---

**修复完成时间**: 2026-02-24 17:00  
**修复者**: AI Assistant  
**测试状态**: 待验证
