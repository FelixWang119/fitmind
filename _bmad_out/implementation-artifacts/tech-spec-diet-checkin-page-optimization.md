---
title: '饮食打卡页面优化'
slug: 'diet-checkin-page-optimization'
created: '2026-02-23'
status: 'Completed'
stepsCompleted: [1, 2, 3, 4, 5, 6]
tech_stack: ['FastAPI', 'SQLAlchemy', 'Pydantic v2', '阿里云 Qwen Vision API', '本地文件存储', 'Pillow']
files_to_modify: [
  "app/core/config.py",
  "app/utils/food_image_analyzer.py",
  "app/models/nutrition.py",
  "app/schemas/meal_models.py",
  "app/api/v1/endpoints/meals.py"
]
files_to_create: [
  "app/models/calorie_goal.py",
  "app/schemas/calorie_goal.py",
  "app/api/v1/endpoints/meal_checkin.py",
  "app/services/calorie_service.py",
  "app/services/image_service.py"
]
code_patterns: [
  "API路由: app/api/v1/endpoints/",
  "Schema: app/schemas/",
  "Model: app/models/",
  "Service: app/services/",
  "使用 structlog.get_logger()",
  "重量单位: 克 (grams)"
]
test_patterns: [
  "pytest",
  "TestClient",
  "SQLite real database",
  "Fixtures in conftest.py"
]
---

# Tech-Spec: 饮食打卡页面优化

**Created:** 2026-02-23
**Status:** Ready for Development

## Overview

### Problem Statement

用户需要通过上传饮食照片进行三餐打卡，系统自动识别每餐热量并更新当日热量余额，帮助用户追踪每日饮食摄入。

### Solution

在现有餐饮记录系统基础上：
1. 添加照片上传功能（本地存储 + 定期压缩）
2. 接入阿里云 Qwen AI 进行图片识别，解析成食材和克数
3. 用户可调整食材数量，系统重新计算热量
4. 用户确认后创建打卡记录
5. 新增热量目标表存储每日目标
6. 实现热量余额自动计算和更新

### Scope

**In Scope:**
- 饮食照片上传功能（三餐：早餐、午餐、晚餐）
- 阿里云 Qwen AI 食材识别（解析成具体食材 + 克数）
- 食材数量用户可调整，调整后自动重算热量
- 用户确认后创建打卡记录
- 热量目标表设计与实现
- 热量余额计算和更新
- 每日营养摘要增强（显示目标 vs 实际）
- 热量余额可视化（颜色指示：绿/黄/红）
- 识别结果包含：热量、蛋白质、碳水、脂肪
- 照片定期压缩（不限天数）

**Out of Scope:**
- 复杂的数据分析和报表功能
- 食物库图片识别（仅识别热量）
- 多语言支持
- 离线识别功能
- 语音播报
- 家庭共享
- 照片删除功能（只压缩不删除）

## Context for Development

### Codebase Patterns

根据项目扫描结果，现有模式如下：

1. **API 约定**: 使用 FastAPI，路由位于 `app/api/v1/endpoints/`
2. **Schema 约定**: Pydantic schemas 位于 `app/schemas/`
3. **模型约定**: SQLAlchemy models 位于 `app/models/`
4. **日志约定**: 使用 `structlog.get_logger()`
5. **数据库**: 使用 SQLAlchemy ORM，会话通过 `Depends(get_db)` 注入
6. **重量单位**: 项目使用 **克 (grams)** 为单位
7. **Service 层**: 业务逻辑位于 `app/services/`

### Files to Reference

| File | Purpose | Status |
| ---- | ------- | ------ |
| `app/api/v1/endpoints/meals.py` | 现有餐饮 CRUD API | 需扩展 |
| `app/schemas/meal_models.py` | 餐饮数据模型 Schema | 需扩展 |
| `app/models/nutrition.py` | 现有营养模型 (Meal, MealItem, FoodItem) | 需扩展 |
| `app/utils/food_image_analyzer.py` | Qwen 视觉分析工具 | 需扩展支持食材识别 |
| `app/services/nutrition_service.py` | 营养计算服务 | 可复用 |
| `app/services/ai_service.py` | AI 服务 (含 Qwen) | 可复用 |
| `app/models/user.py` | 用户模型 | 参考 |
| `app/core/config.py` | 应用配置 | 需添加文件存储路径 |

### Technical Decisions

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 照片存储 | 本地文件系统 | 用户要求 |
| 照片压缩 | 定期压缩，不限天数 | 用户明确要求 |
| AI 识别 | 阿里云 Qwen Vision (qwen-vl-max) | 用户已有，复用现有工具 |
| 识别粒度 | 食材+克数（而非仅热量） | 用户明确要求 |
| 用户交互 | 先识别 → 用户调整数量 → 确认后创建 | 用户明确要求 |
| 热量目标存储 | 独立表 | 用户要求，便于管理 |
| 重量单位 | 克 (grams) | 项目规范 |
| 响应时间目标 | < 3秒 | 用户体验要求 |
| 营养成分 | 热量+蛋白质+碳水+脂肪 | 覆盖健身用户需求 |
| 余额可视化 | 颜色指示 (绿<70%/黄70-100%/红>100%) | 直观理解 |

### 现有功能调研结果

#### ✅ 已实现 (可复用):
1. **食物图片分析** (`app/utils/food_image_analyzer.py`)
   - 使用 `qwen-vl-max` 模型
   - ⚠️ 需扩展：当前只返回总热量，需改为返回食材列表（名称+克数+营养）
   
2. **营养计算服务** (`app/services/nutrition_service.py`)
   - `calculate_calorie_target()` - 计算每日热量目标
   - `calculate_tdee()` - 计算每日总能量消耗
   
3. **每日营养摘要 API** (`app/api/v1/endpoints/meals.py`)
   - `GET /daily-nutrition-summary` - 获取当日营养汇总

4. **餐饮记录 CRUD** - 完整的 Meal/MealItem API

#### 🔄 需要新增/修改:
1. **食物图片分析扩展** - 返回食材列表而非仅热量
2. **热量目标表** (`app/models/calorie_goal.py`)
3. **照片上传 API** + 本地存储
4. **打卡流程 API** - 上传 → 识别 → 返回食材列表 → 用户调整 → 确认 → 创建记录
5. **图片压缩服务** - 定期压缩旧照片

### 项目结构

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── meals.py          # 现有餐饮API
│   │   └── meal_checkin.py   # [新建] 打卡API
│   ├── core/
│   │   ├── config.py         # [修改] 添加文件存储路径
│   │   └── database.py
│   ├── models/
│   │   ├── nutrition.py      # [修改] 可能需要扩展
│   │   └── calorie_goal.py   # [新建] 热量目标模型
│   ├── schemas/
│   │   ├── meal_models.py    # [修改] 添加食材识别结果Schema
│   │   └── calorie_goal.py   # [新建]
│   ├── services/
│   │   ├── nutrition_service.py   # [复用]
│   │   ├── calorie_service.py     # [新建] 热量计算服务
│   │   └── image_service.py       # [新建] 图片处理+压缩服务
│   └── utils/
│       └── food_image_analyzer.py  # [修改] 扩展为食材识别
└── tests/
    └── test_*.py
```

## Implementation Plan

### Tasks

#### Phase 1: 基础设施 (配置与模型)

- [x] **Task 1: 添加配置文件**
  - File: `app/core/config.py`
  - Action: 添加 `UPLOAD_DIR` 配置项（照片存储目录），`IMAGE_MAX_SIZE` (10MB)，`IMAGE_COMPRESS_QUALITY` (70)
  - Notes: 默认值 `./uploads/meal_photos`

- [x] **Task 2: 创建热量目标模型**
  - File: `app/models/calorie_goal.py`
  - Action: 新建 `CalorieGoal` 模型，包含字段：user_id, date, target_calories, target_protein, target_carbs, target_fat, is_auto_calculated
  - Notes: 使用 `user_id + date` 唯一索引

- [x] **Task 3: 创建热量目标 Schema**
  - File: `app/schemas/calorie_goal.py`
  - Action: 新建 `CalorieGoalCreate`, `CalorieGoalResponse` Schema

#### Phase 2: 图片识别服务

- [x] **Task 4: 扩展食材识别功能**
  - File: `app/utils/food_image_analyzer.py`
  - Action: 修改 `analyze_food_with_qwen_vision` 返回食材列表格式：
    ```json
    {
      "meal_type": "lunch",
      "items": [
        {"name": "米饭", "grams": 150, "calories": 174, "protein": 3, "carbs": 38, "fat": 0.5},
        {"name": "红烧肉", "grams": 100, "calories": 350, "protein": 12, "carbs": 8, "fat": 30}
      ],
      "total_calories": 524,
      "total_protein": 15,
      "total_carbs": 46,
      "total_fat": 30.5
    }
    ```
  - Notes: 修改 prompt 要求返回食材名称和克数

- [x] **Task 5: 创建图片处理服务**
  - File: `app/services/image_service.py`
  - Action: 新建 `ImageService` 类
    - `save_image(user_id, file) -> str` 保存照片到 `{UPLOAD_DIR}/{user_id}/{filename}`
    - `compress_image(image_path)` 压缩超过1MB的图片
    - `get_image_path(user_id, filename)` 获取照片访问路径
  - Notes: 使用 Pillow 库，照片按用户ID隔离存储

#### Phase 3: 打卡 API

- [x] **Task 6: 创建打卡 API 端点**
  - File: `app/api/v1/endpoints/meal_checkin.py`
  - Action: 新建以下端点：
    - `POST /meal-checkin/upload` - 上传照片，返回识别结果（食材列表）
    - `POST /meal-checkin/confirm` - 用户确认后创建 Meal 记录，更新热量余额
    - `POST /meal-checkin/recalculate` - 用户调整食材数量后重新计算热量
  - Notes: 使用 `UploadFile` 处理文件上传

- [x] **Task 7: 创建热量计算服务**
  - File: `app/services/calorie_service.py`
  - Action: 新建 `CalorieService` 类
    - `calculate_daily_balance(user_id, date)` - 计算当日热量余额
    - `get_calorie_goal(user_id, date)` - 获取当日目标（支持自动计算或自定义）
    - `set_calorie_goal(user_id, goal_data)` - 设置热量目标
    - `recalculate_from_items(items)` - 根据食材列表重新计算营养总量

#### Phase 4: 集成与扩展

- [ ] **Task 8: 扩展每日营养摘要 API**
  - File: `app/api/v1/endpoints/meals.py`
  - Action: 修改 `/daily-nutrition-summary` 端点，返回中增加：
    - `calorie_goal` - 当日目标
    - `calorie_balance` - 热量余额 (target - actual)
    - `balance_status` - 余额状态 (green/yellow/red)

- [ ] **Task 9: 扩展 Meal Schema**
  - File: `app/schemas/meal_models.py`
  - Action: 添加 `MealWithPhoto` Schema，包含 `photo_url` 字段

- [x] **Task 10: 扩展 Meal 模型**
  - File: `app/models/nutrition.py`
  - Action: 在 `Meal` 模型中添加 `photo_url` 字段 (String, nullable)

#### Phase 5: 定期压缩任务

- [x] **Task 11: 创建图片压缩定时任务**
  - File: `app/services/image_service.py` (添加方法)
  - Action: 添加 `compress_old_images()` 方法
    - 查找超过1MB的图片
    - 压缩到 70% 质量
    - 记录压缩日志
  - Notes: 可通过 Celery 或 cron 调用

### Acceptance Criteria

#### 功能验收

- [ ] **AC 1**: Given用户上传了一张食物照片，when调用 `/meal-checkin/upload`，then返回识别结果，包含食材名称、克数、热量、蛋白质、碳水、脂肪

- [ ] **AC 2**: Given用户收到识别结果，when调整某个食材的数量（如从150g改为200g），then调用 `/meal-checkin/recalculate`，then返回更新后的营养总计

- [ ] **AC 3**: Given用户确认识别结果，when调用 `/meal-checkin/confirm`，then创建 Meal 记录，包含所有食材（MealItem），并返回创建结果

- [ ] **AC 4**: Given用户已设置热量目标，when调用 `/daily-nutrition-summary`，then返回包含 `calorie_balance` 和 `balance_status` (green/yellow/red)

- [ ] **AC 5**: Given照片文件，when保存到本地，then存储路径为 `{UPLOAD_DIR}/{user_id}/{year}/{month}/{filename}`

#### 错误处理验收

- [ ] **AC 6**: Given调用 `/meal-checkin/upload` 传入无效图片文件，then返回 400 错误，提示"不支持的图片格式"

- [ ] **AC 7**: Given调用 `/meal-checkin/upload` 传入超过10MB的文件，then返回 400 错误，提示"文件大小超过限制"

- [ ] **AC 8**: Given Qwen API 调用超时，then返回错误信息，提示"识别服务暂时不可用，请稍后重试"

#### 边界情况验收

- [ ] **AC 9**: Given用户第一次使用没有设置热量目标，when调用 `/daily-nutrition-summary`，then自动计算并返回默认目标（基于 TDEE）

- [ ] **AC 10**: Given用户同日多次打卡，then每次打卡的热量正确累加到当日总计

#### 照片存储验收

- [ ] **AC 11**: Given图片超过1MB，when保存后，then自动压缩到1MB以下

- [ ] **AC 12**: Given不同用户的照片，when分别上传，then存储在不同的用户目录下（隔离存储）

## Additional Context

### Dependencies

- **外部库**:
  - `Pillow` - 图像处理和压缩
  - `python-multipart` - 文件上传支持（FastAPI）
- **已配置服务**:
  - 阿里云 Qwen Vision API (`QWEN_API_KEY`)

### Testing Strategy

- **单元测试**:
  - `test_calorie_service.py` - 测试热量计算逻辑
  - `test_image_service.py` - 测试图片保存和压缩

- **API 测试**:
  - `test_meal_checkin.py` - 测试打卡流程 API
  - 使用 `TestClient` 和 SQLite 数据库

- **集成测试**:
  - 完整流程测试：上传 → 识别 → 调整 → 确认 → 查询余额

### Notes

- **风险提示**:
  - Qwen API 识别准确性依赖模型能力，建议添加置信度提示
  - 照片存储需定期清理压缩后的旧文件
  - 热量目标建议使用数据库存储而非每次重新计算

- **已知限制**:
  - 食材识别准确性取决于图片质量
  - 当前仅支持 jpg/png/webp 格式

- **未来考虑**:
  - 可扩展为离线识别（使用本地模型）
  - 可添加食材历史记录快速选择
  - 可添加家庭成员共享功能

## Review Notes

- Adversarial review completed
- Findings: 5 total, 5 fixed (F1-F5), 0 skipped
- Resolution approach: auto-fix
- Issues fixed:
  - F1/F4: image_service.py import io 位置修复
  - F2: meal_checkin 路由已在 api.py 中注册
  - F3: 文件类型验证已在 meal_checkin.py 中实现
