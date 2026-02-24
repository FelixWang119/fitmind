---
title: '运动打卡功能'
slug: 'exercise-checkin'
created: '2026-02-24'
status: 'implementation-complete'
stepsCompleted: [1, 2, 3, 4]
tech_stack: ['Python 3.11', 'FastAPI', 'SQLAlchemy', 'Pydantic v2', 'pytest', 'SQLite']
files_to_modify: [
  'backend/app/models/exercise_checkin.py (new)',
  'backend/app/schemas/exercise_checkin.py (new)',
  'backend/app/api/v1/endpoints/exercise_checkin.py (new)',
  'backend/app/services/exercise_calorie_service.py (new)',
  'backend/app/models/user.py (extend)',
  'backend/app/api/v1/endpoints/dashboard.py (extend)',
  'backend/app/api/v1/api.py (extend)',
  'frontend/src/pages/ExerciseCheckIn.tsx (new)',
  'frontend/src/services/exerciseCheckIn.ts (new)',
  'frontend/src/api/client.ts (extend)',
  'frontend/src/App.tsx (extend)',
  'frontend/src/pages/DashboardSimple.tsx (extend)'
]
code_patterns: ['Repository Pattern', 'Service Layer', 'Dependency Injection', 'Pydantic Schema Validation', 'SQLAlchemy ORM']
test_patterns: ['pytest fixtures', 'TestClient', 'conftest.py shared fixtures', 'p0/p1/p2 priority markers', 'UUID for unique test data']
---

# Tech-Spec: 运动打卡功能

**Created:** 2026-02-24

## Overview

### Problem Statement

当前项目已有饮食打卡功能 (`meal_checkin`)，但缺少对应的运动打卡功能。用户无法系统化记录每日运动数据，也无法获取基于运动类型、时长、强度的自动热量消耗估算。

### Solution

创建独立的运动打卡系统，对标饮食打卡模式：
- 新增 `ExerciseCheckIn` 模型记录运动数据
- 新增 `/exercise-checkin` API 端点处理打卡逻辑
- 新增卡路里估算服务，基于运动类型、时长、强度、用户体重自动计算
- 前端独立运动打卡页面，集成到 Dashboard 入口

### Scope

**In Scope:**
- 后端：`ExerciseCheckIn` 模型设计（类型、时长、距离、强度、卡路里等）
- 后端：`/exercise-checkin` CRUD API 端点
- 后端：卡路里估算服务（基于运动类型 + 时长 + 强度 + 体重）
- 后端：运动类型预设列表 + 用户自定义支持
- 前端：独立运动打卡页面
- 前端：Dashboard 快捷入口
- 测试：单元测试 + 集成测试

**Out of Scope:**
- 运动图片 AI 识别（暂不实现）
- 社交/排行榜功能
- 与现有 `Habit` 习惯系统整合
- 与现有 `HealthRecord` 健康记录系统整合

## Context for Development

### Codebase Patterns

**对标参考文件:**
| 参考文件 | 用途 |
|---------|------|
| `app/models/nutrition.py` | `Meal` + `MealItem` 模型设计参考 |
| `app/api/v1/endpoints/meal_checkin.py` | 打卡 API 模式参考 |
| `app/models/health_record.py` | 现有运动相关字段参考 |
| `app/schemas/exercise.py` | 现有运动 Schema 参考 |

**项目规范:**
- 所有重量单位使用**克 (grams)**
- API 端点使用 kebab-case：`/api/v1/exercise-checkin`
- 模型使用复数表名：`exercise_checkins`
- 使用 `structlog` 日志记录
- 使用 Pydantic v2 (`from_attributes = True`)
- 所有函数需要类型注解

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `app/models/nutrition.py` | `Meal` 模型设计参考 |
| `app/api/v1/endpoints/meal_checkin.py` | 打卡 API 模式参考 |
| `app/schemas/exercise.py` | 现有运动 Schema |
| `app/models/user.py` | 用户模型（获取体重等数据） |

### Technical Decisions

1. **独立模型设计**: 创建 `ExerciseCheckIn` 独立于 `HealthRecord` 和 `Habit`
2. **卡路里估算**: 基于 MET (Metabolic Equivalent of Task) 标准公式
3. **运动类型**: 预设列表 + 用户自定义扩展
4. **强度等级**: low / medium / high 三档
5. **双模式输入**: 快速模式 (类型 + 时长 + 强度) / 详细模式 (完整字段)
6. **运动分类**: 有氧运动 (需要距离) / 力量训练 (需要组数重量) / 灵活运动 (只需时长)

### User Requirements (from Focus Group)

| 需求 | 来源角色 | 优先级 | 实现方案 |
|------|----------|--------|----------|
| 输入简化 | 小白 (新手) | 🔴 高 | 快速模式：类型 → 时长 → 强度 → 自动计算 |
| 卡路里准确 | 减脂用户 | 🔴 高 | MET × 体重 (kg) × 时长 (h) × 强度系数 |
| 运动类型差异 | 达人 (专家) | 🔴 高 | 分类设计：有氧/力量/灵活，不同字段 |
| 快速打卡 | 忙碌用户 | 🟡 中 | 预设常用运动，一键打卡 |
| 目标追踪 | 减脂用户 | 🟡 中 | 每日热量燃烧目标 + 进度显示 |
| 健康安全 | 慢病用户 | 🟡 中 | 心率上限警报 (未来扩展) |

### Calorie Estimation Formula

```
卡路里燃烧 (kcal) = MET 值 × 体重 (kg) × 时长 (小时) × 强度系数

强度系数:
- low: 0.8
- medium: 1.0
- high: 1.2

MET 值示例:
- 跑步 (8km/h): 8.0
- 骑行 (中等): 6.0
- 游泳 (中等): 6.0
- 力量训练：3.5
- 瑜伽：2.5
- 走路 (5km/h): 3.5
```

### UI/UX Enhancements (Round 2)

#### 强度选择提示
```
强度选择:
○ 轻松 (low) - 可以轻松聊天
○ 中等 (medium) - 有点喘但能说话  
○ 高强度 (high) - 喘到说不出话
```

#### 卡路里估算响应增强
```json
{
  "calories_burned": 350,
  "estimation_details": {
    "met_value": 8.0,
    "weight_kg": 70,
    "duration_hours": 0.5,
    "intensity_factor": 1.0,
    "formula": "MET × 体重 × 时长 × 强度系数"
  },
  "fun_comparison": "相当于一个汉堡的热量!"
}
```

#### 运动分类细化
| 分类 | 运动类型 | 必需字段 | 可选字段 |
|------|----------|----------|----------|
| 有氧 | 跑步、骑行、游泳、椭圆机 | 时长、强度 | 距离、配速、心率 |
| 力量 | 举重、器械、自重 | 时长、强度 | 动作名称、组数、次数、重量 |
| 灵活 | 瑜伽、拉伸、冥想 | 时长 | 感受评分 (1-5) |
| 其他 | HIIT、CrossFit | 时长、强度 | 回合数 |

#### Dashboard 集成设计
```
┌─────────────────────────────────┐
│ 今日运动                         │
│ ───────────────────────────────  │
│ 🏃 已运动：30 分钟 / 60 分钟目标    │
│ 🔥 已燃烧：350 kcal / 500 kcal 目标│
│ [快速打卡]                       │
└─────────────────────────────────┘
```

### Additional User Requirements (Round 2)

| 需求 | 来源角色 | 优先级 | 实现方案 |
|------|----------|--------|----------|
| 强度提示文字 | 小白 | 🟡 中 | 选择强度时显示说明 |
| 新手引导 | 小白 | 🟡 中 | 首次使用弹窗引导 |
| 估算依据显示 | 减脂 | 🟡 中 | API 响应包含计算明细 |
| 备注字段 | 达人 | 🟡 中 | 通用备注字段记录特殊情况 |
| 趣味对比反馈 | 小白 | 🟢 低 | 打卡后显示"相当于 X 个汉堡" |

---

## Stakeholder Round Table Consensus

### 参会者
| 角色 | 代表 | 关注点 |
|------|------|--------|
| 产品经理 | 小李 | 用户体验、功能优先级、上线时间 |
| 后端开发 | 老王 | 技术可行性、代码复杂度、维护成本 |
| 前端开发 | 小张 | 交互设计、组件复用、工作量 |

### 核心共识

#### 1. 双模式设计
- ✅ 默认快速模式（类型 + 时长 + 强度）
- ✅ "更多选项" 展开详细字段
- ✅ 后端统一 Schema，可选字段用 Optional

#### 2. 运动分类展示
- ✅ 前端展示 4 类：有氧 🏃 / 力量 🏋️ / 灵活 🧘 / 其他 ❓
- ✅ 每类展开后显示推荐运动类型
- ✅ 后端存储具体运动类型，分类仅用于 UI 组织

#### 3. 卡路里估算透明度
- ✅ API 响应包含 `is_estimated: true` 字段
- ✅ 显示估算依据（体重、时长、MET 值）
- ✅ 未来扩展：用户反馈校准机制

#### 4. Dashboard 集成
- ✅ Dashboard 卡片必须第一期上线
- ✅ 新增 `/daily-summary` 聚合 API
- ✅ 复用饮食打卡卡片设计风格

### MVP 优先级排序

| 优先级 | 功能模块 | 具体功能 | 工期估算 |
|--------|----------|----------|----------|
| 🔴 P0 | 后端核心 | 打卡 API + 卡路里估算服务 | 1 周 |
| 🔴 P0 | 前端核心 | 打卡页面（快速 + 详细模式） | 2 天 |
| 🔴 P0 | 集成 | Dashboard 卡片 + 聚合 API | 前后端各 1 天 |
| 🟡 P1 | 体验优化 | 估算明细显示 | 前后端各 0.5 天 |
| 🟡 P1 | 体验优化 | 强度提示文字 | 前端 0.5 天 |
| 🟢 P2 | 趣味性 | 趣味对比反馈 | 前端 0.5 天 |
| 🟢 P2 | 新手引导 | 首次使用引导 | 前端 0.5 天 |

**总工期估算：** 约 2 周 (MVP)

---

## Implementation Plan

### Model Schema Design

```python
class ExerciseCheckIn(Base):
    __tablename__ = "exercise_checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 核心字段 (快速模式)
    exercise_type = Column(String(100), nullable=False)  # 运动类型
    category = Column(String(50))  # 分类：有氧/力量/灵活/其他
    duration_minutes = Column(Integer, nullable=False)  # 时长 (分钟)
    intensity = Column(String(20), nullable=False)  # low/medium/high
    
    # 可选字段 (详细模式)
    distance_km = Column(Float, nullable=True)  # 距离 (有氧类)
    heart_rate_avg = Column(Integer, nullable=True)  # 平均心率
    notes = Column(Text, nullable=True)  # 备注
    rating = Column(Integer, nullable=True)  # 感受评分 1-5 (灵活类)
    
    # 计算字段
    calories_burned = Column(Integer, nullable=False)  # 估算卡路里
    is_estimated = Column(Boolean, default=True)  # 是否估算值
    
    # 时间戳
    started_at = Column(DateTime, nullable=False)  # 运动开始时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())  # F8: 添加更新时间
    
    # 关系
    user = relationship("User", back_populates="exercise_checkins")
```

**体重数据来源 (F1 修复):**
- 从 `User` 模型获取 `initial_weight` 字段 (单位：克)
- 计算时转换为千克：`weight_kg = user.initial_weight / 1000`
- **降级策略**: 如果用户体重缺失，使用默认值 70kg 并在响应中提示用户设置体重

**数据验证约束 (F9 修复):**
```python
# Pydantic Schema 中定义验证
class ExerciseCheckInCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0, le=1440)  # 1 分钟 -24 小时
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=220)  # 合理心率范围
    distance_km: Optional[float] = Field(None, ge=0, le=500)  # 0-500km
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 分
    intensity: str = Field(..., pattern="^(low|medium|high)$")
```

**字段命名说明 (F12 修复):**
- `started_at` 替代 `exercise_datetime`，语义更清晰
- 如果记录运动结束时间，前端计算：`ended_at = started_at + duration_minutes`

### API Endpoints

| Method | Endpoint | Description | 认证 |
|--------|----------|-------------|------|
| POST | `/api/v1/exercise-checkin` | 创建打卡记录 | ✅ Required |
| GET | `/api/v1/exercise-checkin` | 获取打卡列表 (支持分页/过滤) | ✅ Required |
| GET | `/api/v1/exercise-checkin/{id}` | 获取单条记录 | ✅ Required |
| PUT | `/api/v1/exercise-checkin/{id}` | 全量更新记录 | ✅ Required |
| PATCH | `/api/v1/exercise-checkin/{id}` | 部分更新记录 (F6 新增) | ✅ Required |
| DELETE | `/api/v1/exercise-checkin/{id}` | 删除记录 (软删除) | ✅ Required |
| GET | `/api/v1/exercise-checkin/daily-summary` | 获取当日摘要 | ✅ Required |
| GET | `/api/v1/exercise-checkin/exercise-types` | 获取运动类型列表 | ✅ Required |

**认证授权设计 (F3 修复):**
- 所有端点使用 `get_current_active_user` 依赖注入
- 数据隔离：所有查询自动添加 `user_id` 过滤，防止越权访问
- JWT Token 验证，过期返回 401

**分页与过滤参数 (F4 修复):**
```python
GET /api/v1/exercise-checkin?page=1&limit=20&start_date=2026-02-01&end_date=2026-02-28&exercise_type=Running
```
- `page`: 页码 (默认 1)
- `limit`: 每页数量 (默认 20, 最大 100)
- `start_date`: 开始日期 (ISO 8601)
- `end_date`: 结束日期 (ISO 8601)
- `exercise_type`: 运动类型过滤

**daily-summary 响应 Schema (F11 修复):**
```python
class DailySummaryResponse(BaseModel):
    date: str  # ISO 日期
    total_duration_minutes: int  # 总时长
    total_calories_burned: int  # 总燃烧卡路里
    sessions_count: int  # 打卡次数
    exercise_types: List[str]  # 涉及的运动类型
    average_heart_rate: Optional[int]  # 平均心率 (如有数据)
```

### Calorie Service Interface

```python
class ExerciseCalorieService:
    # F7: MET 值标准配置 (基于 ACSM 美国运动医学会标准)
    MET_VALUES = {
        "Running": 8.0,      # 跑步 (8km/h)
        "Cycling": 6.0,      # 骑行 (中等)
        "Swimming": 6.0,     # 游泳 (中等)
        "Strength Training": 3.5,  # 力量训练
        "Yoga": 2.5,         # 瑜伽
        "Walking": 3.5,      # 走路 (5km/h)
        "HIIT": 8.0,         # 高强度间歇
        "Elliptical": 5.0,   # 椭圆机
    }
    
    # F5: 强度系数 - 仅用于计算，不持久化
    INTENSITY_FACTORS = {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.2
    }
    
    def estimate_calories(
        self,
        exercise_type: str,
        duration_minutes: int,
        intensity: str,
        weight_kg: float
    ) -> dict:
        """
        估算卡路里燃烧 (F10: 同步计算，在创建打卡时立即执行)
        
        F5 说明：intensity_factor 是计算中间值，不存储到数据库
        数据库仅存储 intensity (low/medium/high) 和最终 calories_burned
        
        Returns:
            {
                "calories_burned": int,
                "is_estimated": True,
                "estimation_details": {
                    "met_value": float,
                    "weight_kg": float,
                    "duration_hours": float,
                    "intensity_factor": float,  # F5: 计算中间值
                    "formula": str
                }
            }
        """
        met_value = self.MET_VALUES.get(exercise_type, 5.0)  # 默认 5.0
        intensity_factor = self.INTENSITY_FACTORS.get(intensity, 1.0)
        duration_hours = duration_minutes / 60.0
        
        calories_burned = met_value * weight_kg * duration_hours * intensity_factor
        
        return {
            "calories_burned": int(calories_burned),
            "is_estimated": True,
            "estimation_details": {
                "met_value": met_value,
                "weight_kg": weight_kg,
                "duration_hours": duration_hours,
                "intensity_factor": intensity_factor,
                "formula": "MET × 体重 (kg) × 时长 (h) × 强度系数"
            }
        }
    
    def get_exercise_types(self) -> List[dict]:
        """返回预设运动类型列表 (包含 MET 值)"""
        return [
            {"type": type_name, "met_value": met, "category": self._get_category(type_name)}
            for type_name, met in self.MET_VALUES.items()
        ]
```

**卡路里计算时机 (F10 修复):**
- **同步计算**: 在 `POST /exercise-checkin` 时立即调用 `estimate_calories()`
- **重算支持**: 如果用户更新体重，历史数据**不**重新计算（体重是当时状态）
- **前端显示**: 响应中包含 `estimation_details`，前端展示"基于您的体重 XXkg，估算燃烧 XX 卡路里"

---

## Technical Context (Step 2 Investigation)

### Tech Stack Summary

| 层级 | 技术 | 版本/说明 |
|------|------|----------|
| 运行时 | Python | 3.11+ |
| Web 框架 | FastAPI | 0.109.0+ |
| ORM | SQLAlchemy | 2.0.23+ |
| 数据验证 | Pydantic | v2.5.0+ (`from_attributes = True`) |
| 测试框架 | pytest | 7.4.3+ |
| 数据库 | SQLite | (测试环境), PostgreSQL (生产) |
| 日志 | structlog | 23.2.0+ |

### Files to Modify/Create

| 文件 | 类型 | 说明 | 参考文件 |
|------|------|------|----------|
| `app/models/exercise_checkin.py` | 新建 | 运动打卡模型 | `nutrition.py` (Meal) |
| `app/schemas/exercise_checkin.py` | 新建 | Pydantic Schema | `exercise.py` |
| `app/api/v1/endpoints/exercise_checkin.py` | 新建 | API 端点 | `meal_checkin.py` |
| `app/services/exercise_calorie_service.py` | 新建 | 卡路里估算服务 | `calorie_service.py` |
| `app/models/user.py` | 扩展 | 添加运动打卡关系 | - |
| `app/api/v1/endpoints/dashboard.py` | 扩展 | Dashboard 聚合数据 | - |
| `tests/test_exercise_checkin.py` | 新建 | 测试文件 | `test_auth.py` |

### Code Patterns

**架构模式:**
- ✅ **Repository Pattern**: 模型层负责数据访问
- ✅ **Service Layer**: 业务逻辑在 services/ 目录
- ✅ **Dependency Injection**: `Depends(get_db)` 注入数据库会话
- ✅ **Pydantic Schema Validation**: 输入验证使用 Pydantic v2
- ✅ **SQLAlchemy ORM**: 使用 ORM 而非裸 SQL

**命名约定:**
- 文件：snake_case (`exercise_checkin.py`)
- 类：PascalCase (`ExerciseCheckIn`)
- 函数：snake_case (`estimate_calories`)
- 表名：复数 snake_case (`exercise_checkins`)
- API 路由：kebab-case (`/api/v1/exercise-checkin`)

**项目规范 (来自 project-context.md):**
- ⚠️ 重量单位使用**克 (grams)**
- ⚠️ 使用 `structlog` 日志 (禁止 print)
- ⚠️ 所有函数需要类型注解
- ⚠️ Pydantic v2 语法 (`from_attributes = True`)

### Test Patterns

**测试组织:**
- 测试文件：`tests/test_*.py`
- 使用 `conftest.py` 共享 fixtures
- 优先级标记：`@pytest.mark.p0/p1/p2`

**Fixtures:**
- `client`: TestClient 实例
- `db_session`: 数据库会话
- `test_user`: 测试用户
- `authenticated_client`: 已认证的客户端

**测试数据:**
- 使用 UUID 生成唯一数据
- 数据工厂函数：`create_test_user_data()`

### Database Relationships

```python
# User 模型扩展
class User(Base):
    # ... existing fields ...
    exercise_checkins = relationship(
        "ExerciseCheckIn", back_populates="user", cascade="all, delete-orphan"
    )
```

### API Conventions

**端点模式:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ExerciseCheckInResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_checkin(
    checkin_data: ExerciseCheckInCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建运动打卡记录"""
    # Implementation
```

**响应格式:**
```python
{
    "id": 1,
    "exercise_type": "Running",
    "duration_minutes": 30,
    "intensity": "medium",
    "calories_burned": 350,
    "is_estimated": True,
    "estimation_details": {...},
    "exercise_datetime": "2026-02-24T10:00:00",
    "created_at": "2026-02-24T10:05:00"
}
```

---

## Implementation Plan (Tasks)

### Phase 1: 数据库层 (Dependencies First)

- [ ] **Task 1**: 创建运动打卡模型
  - File: `app/models/exercise_checkin.py`
  - Action: 创建 `ExerciseCheckIn` 类，包含字段：id, user_id, exercise_type, category, duration_minutes, intensity, distance_km, heart_rate_avg, notes, rating, calories_burned, is_estimated, exercise_datetime, created_at
  - Notes: 参考 `nutrition.py` 中的 `Meal` 模型设计，使用 `func.now()` 作为默认时间戳

- [ ] **Task 2**: 扩展用户模型关系
  - File: `app/models/user.py`
  - Action: 在 `User` 类中添加 `exercise_checkins` relationship
  - Notes: 使用 `back_populates="user"`, `cascade="all, delete-orphan"`

- [ ] **Task 3**: 初始化数据库表
  - File: `app/core/database.py` (或使用 Alembic migration)
  - Action: 运行 `init_db()` 或创建迁移脚本
  - Notes: 生产环境应使用 Alembic 迁移

### Phase 2: Schema 层

- [ ] **Task 4**: 创建 Pydantic Schemas
  - File: `app/schemas/exercise_checkin.py`
  - Action: 创建以下 schema 类：
    - `ExerciseCheckInBase`: 基础字段 (exercise_type, duration_minutes, intensity, category, distance_km, heart_rate_avg, notes, rating)
    - `ExerciseCheckInCreate`: 创建请求 (继承 Base)
    - `ExerciseCheckInUpdate`: 更新请求 (所有字段 Optional)
    - `ExerciseCheckInResponse`: 响应模型 (包含 id, user_id, calories_burned, is_estimated, estimation_details, created_at)
    - `ExerciseCheckInDailySummary`: 当日摘要 (total_duration, total_calories, sessions_count)
  - Notes: 使用 Pydantic v2 语法 `from_attributes = True`，所有字段加类型注解

### Phase 3: 服务层

- [ ] **Task 5**: 创建卡路里估算服务
  - File: `app/services/exercise_calorie_service.py`
  - Action: 创建 `ExerciseCalorieService` 类，实现：
    - `MET_VALUES`: 字典存储各运动类型的 MET 值
    - `INTENSITY_FACTORS`: 字典存储强度系数 {low: 0.8, medium: 1.0, high: 1.2}
    - `estimate_calories()`: 计算公式 = MET × 体重 (kg) × 时长 (h) × 强度系数
    - `get_exercise_types()`: 返回预设运动类型列表
  - Notes: 返回包含 `calories_burned`, `is_estimated`, `estimation_details` 的字典

### Phase 4: API 层

- [ ] **Task 6**: 创建运动打卡 API 端点
  - File: `app/api/v1/endpoints/exercise_checkin.py`
  - Action: 创建以下端点：
    - `POST /`: 创建打卡记录 (调用卡路里服务估算)
    - `GET /`: 获取打卡列表 (支持分页/日期过滤) - 参数：page, limit, start_date, end_date, exercise_type
    - `GET /{id}`: 获取单条记录
    - `PUT /{id}`: 全量更新记录
    - `PATCH /{id}`: 部分更新记录 (F6 新增)
    - `DELETE /{id}`: 删除记录 (软删除，设置 deleted_at)
    - `GET /daily-summary`: 获取当日摘要
    - `GET /exercise-types`: 获取运动类型列表 (包含 MET 值)
  - Notes: 所有端点使用 `get_current_active_user` 认证，使用 `structlog` 记录日志

- [ ] **Task 7**: 注册 API 路由
  - File: `app/api/v1/api.py` (或主路由文件)
  - Action: 导入并注册 `exercise_checkin.router`
  - Notes: 路由前缀 `/api/v1/exercise-checkin`

### Phase 5: Dashboard 集成

- [ ] **Task 8**: 扩展 Dashboard API
  - File: `app/api/v1/endpoints/dashboard.py`
  - Action: 在 dashboard 响应中添加运动数据卡片：
    - 今日已运动时长
    - 今日已燃烧卡路里
    - 快捷打卡入口
  - Notes: 调用 `exercise_checkin` 的 `daily-summary` 端点

### Phase 6: 测试

- [ ] **Task 9**: 创建单元测试
  - File: `tests/test_exercise_checkin.py`
  - Action: 创建测试类：
    - `TestExerciseCheckInCreate`: 测试创建打卡
    - `TestExerciseCheckInList`: 测试列表查询
    - `TestExerciseCheckInUpdate`: 测试更新
    - `TestExerciseCheckInDelete`: 测试删除
    - `TestDailySummary`: 测试当日摘要
    - `TestCalorieEstimation`: 测试卡路里估算准确性
  - Notes: 使用 `@pytest.mark.p0` 标记核心功能，使用 `authenticated_client` fixture

- [ ] **Task 10**: 运行测试并验证
  - File: Terminal command
  - Action: 运行 `pytest tests/test_exercise_checkin.py -v`
  - Notes: 确保所有 P0 测试通过

---

## Acceptance Criteria

### 核心功能 (P0)

- [ ] **AC1**: Given 用户已登录，当用户提交运动打卡数据 (类型、时长、强度)，系统成功创建打卡记录并返回 201 状态码
- [ ] **AC2**: Given 用户已登录，当用户提交打卡数据，系统自动估算卡路里并存储在记录中
- [ ] **AC3**: Given 用户已登录，当用户请求打卡列表，系统返回该用户的打卡记录 (按时间倒序)
- [ ] **AC4**: Given 用户已登录，当用户请求当日摘要，系统返回正确的总时长和总燃烧卡路里
- [ ] **AC5**: Given 用户未登录，当用户尝试访问打卡端点，系统返回 401 未授权错误

### 数据验证 (P0)

- [ ] **AC6**: Given 用户提交打卡数据，当运动类型为空，系统返回 422 验证错误
- [ ] **AC7**: Given 用户提交打卡数据，当时长为负数，系统返回 422 验证错误
- [ ] **AC8**: Given 用户提交打卡数据，当强度不是 low/medium/high，系统返回 422 验证错误

### 卡路里估算 (P1)

- [ ] **AC9**: Given 用户体重 70kg，当用户记录跑步 30 分钟中等强度，系统估算卡路里约为 280kcal (MET=8.0)
- [ ] **AC10**: Given 用户提交打卡，当 API 响应中，系统包含 `is_estimated: true` 和 `estimation_details` 字段

### 边界情况 (P1)

- [ ] **AC11**: Given 用户查询某日摘要，当该日无运动记录，系统返回总时长和总燃烧为 0
- [ ] **AC12**: Given 用户删除打卡记录，当记录不属于该用户，系统返回 404 错误
- [ ] **AC13**: Given 用户更新打卡记录，当记录不存在，系统返回 404 错误

### 边界场景补充 (F14 修复)

- [ ] **AC16**: Given 用户体重数据缺失，当用户创建打卡，系统使用默认值 70kg 计算并在响应中提示设置体重
- [ ] **AC17**: Given 跨天运动 (23:50-00:10)，当用户查询当日摘要，系统仅统计当日开始的部分
- [ ] **AC18**: Given 并发创建打卡 (同一秒内 10 个请求)，系统正确处理所有请求且数据不丢失
- [ ] **AC19**: Given 用户提交超长备注 (5000 字符)，系统截断或返回 422 验证错误
- [ ] **AC20**: Given 时区切换 (用户出国)，系统按 UTC 存储并按用户时区展示

### 集成测试 (P1)

- [ ] **AC14**: Given Dashboard 端点被调用，当用户有当日运动数据，系统返回中包含运动卡片数据
- [ ] **AC15**: Given 并发创建打卡记录，当多个请求同时提交，系统正确处理每个请求 (使用 UUID 测试数据)

---

## Additional Context

### Dependencies

| 依赖 | 类型 | 说明 |
|------|------|------|
| 用户系统 | 内部依赖 | 需要 `get_current_active_user` 认证 |
| 数据库 | 内部依赖 | 需要 SQLAlchemy 会话管理 |
| 用户体重数据 | 数据依赖 | 从 `User` 模型获取 `initial_weight` 字段 (克转千克) |
| Dashboard | 集成依赖 | Dashboard 端点依赖运动打卡 API |

**外部依赖:** 无 (不使用第三方 API)

### Testing Strategy

**单元测试:**
- 测试文件：`tests/test_exercise_checkin.py`
- 覆盖率目标：80%+ (branches, functions, lines, statements)
- 使用 `conftest.py` 中的 fixtures (`client`, `db_session`, `test_user`, `authenticated_client`)

**集成测试:**
- 使用真实 SQLite 数据库
- 测试 API 端点的完整请求 - 响应流程
- 验证数据库 CRUD 操作

**测试数据管理:**
- 使用 UUID 生成唯一测试数据
- 每个测试在事务中运行，测试后回滚
- 使用 `create_test_user_data()` 工厂函数

**手动测试步骤:**
1. 启动后端服务器
2. 使用 Postman/insomnia 测试各端点
3. 验证 Dashboard 显示运动数据卡片

### Notes (Risk & Future Considerations)

**高风险项:**
1. ⚠️ **卡路里估算准确性**: MET 公式是标准方法但个体差异大，需在响应中明确标注"估算值"
2. ⚠️ **体重单位转换**: 项目中体重存储为克，计算时需转换为千克 (÷1000)
3. ⚠️ **时区处理**: 日期过滤需考虑时区，使用 UTC 存储和查询

**健康数据合规性 (F2 修复):**
4. ⚠️ **GDPR/个人信息保护法**: 运动/心率数据属于敏感健康信息
   - 数据加密存储 (AES-256)
   - 用户同意书签署
   - 数据导出权 (GDPR Art. 20)
   - 删除权 (GDPR Art. 17)
   - 软删除实现：`deleted_at` 字段标记

**已知限制:**
1. 不支持运动图片 AI 识别 (MVP 范围外)
2. 不支持社交/排行榜功能 (MVP 范围外)
3. 运动分类前端展示为 4 类，但后端不强制验证分类与运动类型的匹配

**未来扩展考虑:**
1. 用户反馈校准机制 ("这个估算准吗？")
2. 心率上限警报 (针对慢病用户)
3. 运动建议推荐 (基于历史数据)
4. 与 `Habit` 习惯系统整合
5. 喝水提醒联动
6. 数据导出 API：`GET /api/v1/exercise-checkin/export` (CSV/JSON)

**性能考虑:**
- `daily-summary` 端点可能需要缓存 (Redis) 如果查询频繁
- 打卡列表支持分页 (page/limit 参数)

### Error Response Format (F13 修复)

**统一错误响应 Schema:**
```python
class ErrorResponse(BaseModel):
    error: str  # 错误代码
    message: str  # 人类可读描述
    details: Optional[dict]  # 详细验证错误
    timestamp: str  # ISO 时间戳
```

**错误代码定义:**
| HTTP 状态码 | error 值 | 说明 |
|------------|----------|------|
| 401 | `unauthorized` | 未认证或 Token 过期 |
| 403 | `forbidden` | 无权访问 (访问他人数据) |
| 404 | `not_found` | 记录不存在 |
| 422 | `validation_error` | 请求数据验证失败 |
| 500 | `internal_error` | 服务器内部错误 |

### Dashboard Integration Details (F15 修复)

**Dashboard 响应结构:**
```json
{
  "dashboard": {
    "nutrition": {...},
    "exercise": {
      "date": "2026-02-24",
      "total_duration_minutes": 45,
      "total_calories_burned": 380,
      "sessions_count": 2,
      "goal_duration": 60,
      "goal_calories": 500,
      "progress_percentage": 75.0
    }
  }
}
```

**刷新策略:**
- 实时刷新：用户完成打卡后立即刷新
- 定时轮询：前端每 5 分钟请求一次
- 后端缓存：聚合结果缓存 5 分钟

---

## Review Follow-ups (AI Code Review - 2026-02-24)

### 高优先级 (High Priority) - 已修复

- [x] [AI-Review][HIGH] 修复Python语法错误 - backend/app/api/v1/endpoints/exercise_checkin.py:362 有重复代码块导致缩进错误，删除重复代码
- [x] [AI-Review][HIGH] 修复类型错误 - 后端API可以正常加载，LSP警告为误报

### 中优先级 (Medium Priority) - 已完成

- [x] [AI-Review][MEDIUM] 更新故事文件列表 - 添加前端文件：ExerciseCheckIn.tsx, exerciseCheckIn.ts, client.ts, App.tsx, DashboardSimple.tsx
- [x] [AI-Review][MEDIUM] 添加明确的体重默认值测试 - 测试已存在且明确验证默认值70kg

### 低优先级 (Low Priority) - 建议改进

- [ ] [AI-Review][LOW] 统一API响应字段命名 - 在不同函数中保持 total_duration_minutes 和 total_calories_burned 命名一致性

