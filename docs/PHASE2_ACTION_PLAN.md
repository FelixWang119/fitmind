# Phase 2 功能行动规划

**文档创建日期**: 2026-02-28  
**讨论参与者**: Felix, John (PM Agent)  
**文档目的**: 记录产品功能讨论结论，便于下次快速启动实施

---

## 📋 功能清单总览

| 功能 | 优先级 | 预计工时 | 状态 | 快速启动命令 |
|------|--------|---------|------|-------------|
| [💧 饮水功能](#-饮水功能-phase-15) | P0 - 插队 | 0.5 天 | 📝 待实现 | `实现饮水功能` |
| [🔗 习惯自动关联引擎](#-习惯自动关联引擎-phase-2) | P1 | 2-3 天 | 📝 待实现 | `实现习惯自动关联` |
| [🚶 步数功能](#-步数功能-phase-2) | P2 | 待定 | 📝 待实现 | `实现步数功能` |

---

## 💧 饮水功能 (Phase 1.5)

### 📊 现状分析

| 模块 | 状态 | 说明 |
|------|------|------|
| 数据模型 | ✅ 已定义 | `WaterIntake` 表 (`backend/app/models/nutrition.py`) |
| Dashboard 展示 | ✅ 已实现 | `WaterIntakeCard` 组件 (`frontend/src/components/Dashboard/Cards.tsx`) |
| 数据录入 API | ❌ 未实现 | 需要创建 `water_intakes.py` 端点 |
| 数据录入 UI | ❌ 未实现 | 需要快速录入组件 |
| Dashboard 数据源 | ❌ 硬编码 | 当前显示 `1800ml` 固定值 |

### 🎯 决策结论

**优先级**: P0 - Phase 1.5（插队功能）

**原因**:
1. ✅ **门槛最低** - 比饮食/运动打卡更简单，用户容易上手
2. ✅ **高频需求** - 每天都要喝水多次，增加用户粘性
3. ✅ **成就感强** - 容易达成目标，提升用户满意度
4. ✅ **技术简单** - 已有数据模型，只需补充 API + UI
5. ✅ **产品认可** - Felix 明确表示"饮水和走路是普通人最容易做到的"

### 📋 实现计划

#### 任务清单（总计：约 3 小时）

| 任务 | 预计时间 | 文件位置 | 完成标志 |
|------|---------|---------|---------|
| **后端 API** | 30 分钟 | | |
| - Schema 定义 | 10 分钟 | `backend/app/schemas/nutrition.py` | `WaterIntakeCreate`, `WaterIntakeResponse` |
| - API 端点 | 20 分钟 | `backend/app/api/v1/endpoints/water_intakes.py` | POST/GET/DELETE 接口 |
| **Dashboard 集成** | 10 分钟 | | |
| - 修改数据源 | 10 分钟 | `backend/app/services/dashboard_service.py` | 从硬编码改为查询数据库 |
| **前端 UI** | 1.5 小时 | | |
| - 快速录入组件 | 30 分钟 | `frontend/src/components/WaterIntakeTracker.tsx` | +250ml, +500ml, 自定义 |
| - Dashboard 集成 | 30 分钟 | `frontend/src/pages/Dashboard.tsx` | 点击卡片弹出录入 |
| - API 调用 | 30 分钟 | `frontend/src/api/water.ts` | 完整 CRUD 调用 |
| **测试** | 30 分钟 | | |
| - 手动测试 | 30 分钟 | | 录入→展示→删除全流程 |

#### API 设计

```markdown
POST /api/v1/water-intakes
记录饮水
{
  "amount_ml": 250,
  "intake_datetime": "2026-02-28T10:30:00"  // 可选，默认当前时间
}

GET /api/v1/water-intakes/today
获取今日饮水记录
{
  "total_ml": 1500,
  "target_ml": 2000,
  "records": [
    {"amount_ml": 250, "time": "08:00"},
    {"amount_ml": 500, "time": "10:30"},
    {"amount_ml": 750, "time": "14:00"}
  ]
}

DELETE /api/v1/water-intakes/{id}
删除记录
```

### 🚀 快速启动

**下次开始时说**:
```
"实现饮水功能"
```

**我会自动**:
1. 创建后端 API（Schema + 端点）
2. 更新 Dashboard 数据源
3. 创建前端录入组件
4. 提供测试用例

### 📎 相关文档

- PRD 第 2.1 节 - Dashboard 功能说明
- PRD 第 4.6.1 节 - 健康数据记录
- `backend/app/models/nutrition.py` - WaterIntake 模型

---

## 🔗 习惯自动关联引擎 (Phase 2)

### 📊 现状分析

| 模块 | 状态 | 说明 |
|------|------|------|
| 饮食打卡 | ✅ 已实现 | `meals.py` - 完整的热量、营养素记录 |
| 运动打卡 | ✅ 已实现 | `exercise_checkin.py` - MET 计算、热量消耗 |
| 习惯打卡 | ✅ 已实现 | `habits.py` + `habit_service.py` |
| 自动关联规则 | ❌ 未实现 | 无 `auto_complete` 逻辑 |
| 关联字段 | ❌ 未添加 | `HabitCompletion` 缺少 `source_type`, `source_id` |

### 🎯 决策结论

**优先级**: P1 - Phase 2

**问题背景**:
- 用户记录早餐后，需要手动再去习惯页打卡"早餐不缺席"
- 用户运动后，需要手动打卡"每日运动"习惯
- **重复操作，用户体验割裂**

**解决方案**:
- 实现规则引擎，自动检测行为数据并完成关联习惯
- 例：记录早餐 → 自动完成"早餐不缺席"习惯

### 📋 实现计划

#### 任务清单（总计：2-3 天）

| 任务 | 预计时间 | 文件位置 | 完成标志 |
|------|---------|---------|---------|
| **数据库迁移** | 2 小时 | | |
| - 添加 `habits.auto_complete_rule` 字段 | 1 小时 | `alembic/versions/` | JSON 字段存储规则 |
| - 添加 `habit_completions.source_type/source_id` | 1 小时 | `alembic/versions/` | 追踪完成来源 |
| **模型扩展** | 1 小时 | | |
| - Habit 模型 | 30 分钟 | `backend/app/models/habit.py` | 添加 `auto_complete_rule` |
| - HabitCompletion 模型 | 30 分钟 | `backend/app/models/habit.py` | 添加 `source_type`, `source_id` |
| **规则引擎服务** | 1 天 | `backend/app/services/habit_auto_complete.py` | 完整规则匹配逻辑 |
| **集成到现有端点** | 4 小时 | | |
| - meals.py | 2 小时 | `backend/app/api/v1/endpoints/meals.py` | 创建餐后触发检查 |
| - exercise_checkin.py | 2 小时 | `backend/app/api/v1/endpoints/exercise_checkin.py` | 运动后触发检查 |
| **用户通知 UI** | 4 小时 | `frontend/src/components/` | 自动完成弹窗提示 |
| **设置页面** | 4 小时 | `frontend/src/pages/Settings.tsx` | 管理自动关联规则 |
| **单元测试** | 4 小时 | `backend/tests/` | 规则引擎测试 |

#### 预定义关联规则

| 习惯名称 | 触发条件 | 数据源 | 时间窗口 |
|---------|---------|-------|---------|
| 早餐不缺席 | 有早餐记录 | `meals` 表 | 06:00-10:00 |
| 午餐准时吃 | 有午餐记录 | `meals` 表 | 11:30-14:00 |
| 晚餐不超量 | 晚餐热量 < 目标值 | `meals` 表 | 17:00-21:00 |
| 每日运动 | 当日运动记录≥1 条 | `exercise_checkins` 表 | 当日 |
| 每周运动 3 次 | 本周运动记录≥3 条 | `exercise_checkins` 表聚合 | 本周一 - 周日 |
| 晨练习惯 | 07:00-09:00 有运动记录 | `exercise_checkins` 表 | 07:00-09:00 |
| 每日饮水 2000ml | 当日饮水≥2000ml | `water_intakes` 表聚合 | 当日 |

### 🚀 快速启动

**下次开始时说**:
```
"实现习惯自动关联"
```

**我会自动**:
1. 创建数据库迁移脚本
2. 扩展数据模型
3. 实现规则引擎服务
4. 集成到饮食/运动端点
5. 创建前端通知组件

### 📎 相关文档

- PRD 第 4.5.3 节 - 自动关联规则引擎（完整设计）
- `backend/app/models/habit.py` - Habit 模型
- `backend/app/services/habit_service.py` - 习惯服务

---

## 🚶 步数功能 (Phase 2)

### 📊 现状分析

| 模块 | 状态 | 说明 |
|------|------|------|
| 数据模型 | ✅ 已定义 | `HealthRecord.steps_count` 字段 |
| Dashboard 展示 | ✅ 占位符 | 显示 `0`，标注"即将上线" |
| 数据录入 API | ❌ 未实现 | 无步数记录端点 |
| 数据录入 UI | ❌ 未实现 | 无步数录入页面 |
| 设备集成 | ❌ 未实现 | 无手机/微信集成 |

### 🎯 决策结论

**优先级**: P2 - Phase 2

**原因**:
1. ⏳ **Web 应用限制** - 无法直接访问手机计步器
2. ⏳ **需要移动端配合** - App/小程序/第三方 API
3. ⏳ **可以延后** - 不影响 MVP 核心价值
4. ✅ **保持占位符** - Dashboard 显示"0 步 🚧 即将上线"，管理用户预期

### 📋 实现计划（待定）

#### 方案对比

| 方案 | 开发成本 | 用户体验 | 推荐度 | 阶段 |
|------|---------|---------|--------|------|
| 纯手动录入 | 低（1 天） | 差（繁琐） | ⭐⭐ | Phase 2 |
| 微信小程序集成 | 中（3-5 天） | 好（自动同步） | ⭐⭐⭐ | Phase 3 |
| 未来原生 App | 高（2 周+） | 最佳 | ⭐⭐⭐ | 长期 |

#### 推荐路径

1. **Phase 2** - 先实现手动录入入口（扩展 HealthRecord API）
2. **Phase 3** - 探索微信小程序步数同步（微信运动 API）
3. **长期** - 考虑第三方服务（华为健康、小米运动等）

### 🚀 快速启动

**下次开始时说**:
```
"实现步数功能"
```

**我会自动**:
1. 确认实现方案（手动/设备集成）
2. 创建后端 API
3. 创建前端录入组件
4. 更新 Dashboard 数据源

### 📎 相关文档

- PRD 第 2.1 节 - 步数功能说明
- PRD 第 4.6.1 节 - 健康数据记录表格
- `backend/app/models/health_record.py` - HealthRecord 模型
- `frontend/src/components/Dashboard/Cards.tsx` - StepCountCard 组件

---

## 📌 讨论背景与产品理念

### 讨论日期
2026-02-28

### 核心洞察

**Felix 的产品判断**:
> "饮水和走路这两个卡片还是挺有必要的。因为其实这是普通人最容易做到的。"

**产品策略**:
1. **低门槛功能优先** - 饮水 > 步数 > 饮食 > 运动
2. **用户获得感驱动** - 容易达成的功能增加粘性
3. **技术可行性约束** - Web 应用 vs 移动设备能力

### 用户增长漏斗设计

```
100 人看到产品
  ↓
80 人被"记录步数 + 饮水"吸引（门槛低）
  ↓
50 人开始尝试记录饮食（门槛升高）
  ↓
30 人坚持使用（核心价值）
```

---

## 🔖 快速索引

### 按优先级搜索
- **P0 插队**: [饮水功能](#-饮水功能-phase-15)
- **P1**: [习惯自动关联](#-习惯自动关联引擎-phase-2)
- **P2**: [步数功能](#-步数功能-phase-2)

### 按启动命令搜索
- `"实现饮水功能"` → 饮水功能实现
- `"实现习惯自动关联"` → 习惯自动关联引擎
- `"实现步数功能"` → 步数功能

### 按文档位置搜索
- **PRD 第 2.1 节** - Dashboard 功能说明
- **PRD 第 4.5.3 节** - 自动关联规则引擎
- **PRD 第 4.6.1 节** - 健康数据记录

---

## 📝 更新记录

| 日期 | 更新内容 | 更新者 |
|------|---------|--------|
| 2026-02-28 | 初始创建，记录饮水/习惯关联/步数功能讨论结论 | John (PM) |

---

**下次启动时**:
直接说快速启动命令，例如 `"实现饮水功能"`，我会立即开始实施！🚀
