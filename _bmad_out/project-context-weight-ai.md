# 体重管理 AI 助手 - 项目上下文文档

> **文档类型**: Brownfield 项目上下文分析  
> **生成日期**: 2026-02-27  
> **分析范围**: 后端 (FastAPI + PostgreSQL) + 前端 (React + TypeScript)  
> **目标读者**: LLM Agent、开发人员  
> **用途**: 为 Epic/Story 拆解和后续开发提供依据

---

## 📋 文档导航

1. [项目概览](#项目概览)
2. [技术架构](#技术架构)
3. [数据模型结构](#数据模型结构)
4. [API 端点组织](#api-端点组织)
5. [前端组件结构](#前端组件结构)
6. [测试框架与覆盖率](#测试框架与覆盖率)
7. [代码规范与约定](#代码规范与约定)
8. [实现约束与注意事项](#实现约束与注意事项)
9. [技术债务与风险点](#技术债务与风险点)
10. [Epic/Story 拆解建议](#epicstory-拆解建议)

---

## 项目概览

### 产品定位
体重管理 AI 助手 = AI 营养师 + 行为教练

### 核心功能模块
| 模块 | 状态 | 说明 |
|------|------|------|
| 用户系统 | ✅ 已实现 | 注册、登录、JWT 认证、密码重置 |
| AI 对话 | ✅ 已实现 | 基于 Qwen 的 AI 聊天、角色切换 |
| 营养管理 | ✅ 已实现 | 饮食记录、卡路里追踪、营养分析 |
| 运动打卡 | ✅ 已实现 | 运动记录、卡路里消耗计算 |
| 习惯追踪 | ✅ 已实现 | 习惯创建、打卡、连续记录 |
| 健康评估 | ✅ 已实现 | 多维度健康评分、评估报告 |
| 游戏化系统 | ✅ 已实现 | 积分、徽章、等级、成就、挑战 |
| 记忆系统 | ✅ 已实现 | 统一记忆、语义搜索、上下文摘要 |

### 本次优化重点
1. **个人档案扩展**: 6 字段 → 17 字段
2. **目标系统新增**: 4 维度目标追踪
3. **饮食/运动成就系统**: 游戏化扩展
4. **AI 记忆集成**: 增强个性化推荐
5. **Onboarding 引导流程**: 5 步新手引导

---

## 技术架构

### 后端技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 运行时 | Python | ^3.11 | 后端运行时 |
| Web 框架 | FastAPI | ^0.109.0 | RESTful API |
| ORM | SQLAlchemy | ^2.0.23 | 数据库操作 |
| 数据验证 | Pydantic | ^2.5.0 | Schema 验证 |
| 数据库 | PostgreSQL | 15+ | 主数据库 |
| 向量搜索 | pgvector | ^0.2.4 | 语义搜索 |
| 认证 | python-jose + passlib | ^3.3.0 / ^1.7.4 | JWT + bcrypt |
| 日志 | structlog | ^23.2.0 | 结构化日志 |
| 缓存 | Redis | ^5.0.1 | 缓存层 |
| 迁移 | Alembic | ^1.12.1 | 数据库迁移 |
| 调度器 | APScheduler | - | 定时任务 |

### 前端技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | React | ^18.2.0 | UI 框架 |
| 语言 | TypeScript | ^5.0.2 | 类型系统 |
| 路由 | React Router | ^6.20.0 | 客户端路由 |
| 状态管理 | Zustand | ^4.4.7 | 全局状态 |
| UI 库 | Ant Design | ^6.3.1 | 组件库 |
| 样式 | TailwindCSS | ^3.3.0 | 原子化 CSS |
| 图表 | Chart.js + react-chartjs-2 | ^4.5.1 | 数据可视化 |
| 图标 | lucide-react | ^0.309.0 | 图标库 |
| HTTP 客户端 | Axios | ^1.6.2 | API 调用 |
| 日期处理 | date-fns / dayjs | ^2.30.0 / ^1.11.19 | 日期格式化 |
| 通知 | react-hot-toast | ^2.6.0 | Toast 通知 |

### 测试技术栈

| 类型 | 工具 | 配置 |
|------|------|------|
| 后端单元测试 | pytest | ^7.4.3 |
| 后端集成测试 | pytest + TestClient | 真实 PostgreSQL |
| 前端单元测试 | Jest + Testing Library | ^29.6.2 |
| E2E 测试 | Playwright | ^1.38.0 |
| 覆盖率工具 | pytest-cov / Istanbul | 80% 目标 |

### 项目结构

```
bmad/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── api.py              # 路由聚合
│   │   │   └── endpoints/          # 端点实现 (30+ 文件)
│   │   ├── core/
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── database.py         # 数据库连接
│   │   │   ├── middleware.py       # 中间件
│   │   │   └── test_users.py       # 测试用户管理
│   │   ├── models/                 # SQLAlchemy 模型 (17 个)
│   │   ├── schemas/                # Pydantic Schema (24 个)
│   │   ├── services/               # 业务逻辑 (20+ 服务)
│   │   └── schedulers/             # 定时任务
│   ├── alembic/
│   │   └── versions/               # 数据库迁移 (12 个)
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── factories.py            # 数据工厂
│   │   ├── mocks.py                # Mock 对象
│   │   ├── unit/                   # 单元测试
│   │   ├── api/                    # API 测试
│   │   └── e2e/                    # E2E 测试
│   ├── pyproject.toml
│   └── start_server.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts           # API 客户端封装
│   │   ├── components/
│   │   │   ├── Dashboard/          # Dashboard 组件
│   │   │   ├── NotificationCenter/ # 通知中心
│   │   │   └── layout/             # 布局组件
│   │   ├── pages/                  # 页面组件 (15+)
│   │   ├── services/               # 服务层
│   │   ├── store/
│   │   │   └── authStore.ts        # Zustand store
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript 类型定义
│   │   ├── utils/                  # 工具函数
│   │   └── App.tsx                 # 应用入口
│   ├── tests/
│   │   ├── unit/                   # 单元测试
│   │   ├── api/                    # API 测试
│   │   └── e2e/                    # E2E 测试
│   ├── package.json
│   └── playwright.config.ts
├── _bmad/                          # BMAD 框架
├── _bmad_out/                      # 输出产物
└── docker-compose.override.yml     # Docker 配置
```

---

## 数据模型结构

### 核心模型清单

| 模型 | 表名 | 字段数 | 说明 |
|------|------|--------|------|
| User | users | 17 | 用户主表 |
| HealthRecord | health_records | 21 | 健康记录 |
| Habit | habits | 16 | 习惯定义 |
| HabitCompletion | habit_completions | 8 | 习惯打卡 |
| HabitGoal | habit_goals | 12 | 习惯目标 |
| Meal | meals | - | 餐饮记录 |
| ExerciseCheckIn | exercise_checkins | - | 运动打卡 |
| HealthAssessment | health_assessments | 18 | 健康评估 |
| UserPoints | user_points | 11 | 用户积分 |
| UserBadge | user_badges | 13 | 用户徽章 |
| Achievement | achievements | 13 | 成就系统 |
| Challenge | challenges | 15 | 挑战系统 |
| UnifiedMemory | unified_memory | 15 | 统一记忆 |
| ContextSummary | context_summaries | 10 | 上下文摘要 |

### User 模型详解

**文件位置**: `backend/app/models/user.py`

```python
class User(Base):
    __tablename__ = "users"

    # 核心身份 (5 字段)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)

    # 账户状态 (2 字段)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 个人档案 - 当前 6 字段 ⚠️ 需扩展到 17 字段
    age = Column(Integer)
    gender = Column(String(10))  # male, female, other
    height = Column(Integer)  # 厘米
    initial_weight = Column(Integer)  # 克 ⚠️
    target_weight = Column(Integer)  # 克 ⚠️
    activity_level = Column(String(50))  # sedentary, light, moderate, active, very_active
    dietary_preferences = Column(Text)  # JSON 字符串

    # 时间戳 (3 字段)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # 关系 (15+ 关联)
    health_records = relationship("HealthRecord", ...)
    conversations = relationship("Conversation", ...)
    habits = relationship("Habit", ...)
    # ... 更多关系
```

### User Schema 详解

**文件位置**: `backend/app/schemas/user.py`

```python
# 当前字段 (6 个)
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[int] = Field(None, ge=50, le=250)
    initial_weight: Optional[int] = Field(None, ge=20000, le=300000)  # 克
    target_weight: Optional[int] = Field(None, ge=20000, le=300000)  # 克
    activity_level: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None
```

### ⚠️ 关键注意事项：重量单位

```
🚨 CRITICAL: 所有重量字段使用克 (grams)，不是千克！

- initial_weight: 70000 = 70kg
- target_weight: 65000 = 65kg
- weight (HealthRecord): 69500 = 69.5kg

前端展示时需转换：weight_g / 1000 = weight_kg
```

### 记忆系统模型

**文件位置**: `backend/app/models/memory.py`

```python
class UnifiedMemory(Base):
    """统一记忆 - 长期记忆核心存储"""
    __tablename__ = "unified_memory"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 记忆类型
    memory_type = Column(String(50), nullable=False, index=True)
    # 类型枚举：'打卡_pattern', '偏好_inferred', '目标_explicit', 
    #          '习惯_completed', '里程碑_achieved', '趋势_insight', '关联_causal'

    # 记忆内容
    content_raw = Column(Text)  # 原始内容
    content_summary = Column(Text, nullable=False)  # LLM 摘要
    content_keywords = Column(JsonType, default=list)  # 关键词

    # 向量存储 (pgvector)
    embedding = Column(Vector(768), nullable=True)  # pgvector 类型
    embedding_legacy = Column(Text, nullable=True)  # 旧字段兼容

    # 来源追溯
    source_type = Column(String(50), nullable=False, index=True)
    # 类型：'habit_record', 'conversation', 'health_record', 'meal_record', 'exercise_record'
    source_id = Column(String(100), nullable=False)

    # 元数据
    importance_score = Column(Float, default=5.0)  # 0-10
    is_active = Column(Boolean, default=True, index=True)
    is_indexed = Column(Boolean, default=False, index=True)
```

### 游戏化模型

**文件位置**: `backend/app/models/gamification.py`

```python
# 徽章类别
class BadgeCategory(str, enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    HABIT_MASTERY = "habit_mastery"
    NUTRITION = "nutrition"
    EMOTIONAL_WELLNESS = "emotional_wellness"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SOCIAL = "social"
    SPECIAL = "special"

# 徽章等级
class BadgeLevel(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
```

---

## API 端点组织

### 路由聚合结构

**文件位置**: `backend/app/api/v1/api.py`

```python
api_router = APIRouter()

# 核心认证
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# 核心业务
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

# 饮食管理
api_router.include_router(meals.router, prefix="/meals", tags=["meals"])
api_router.include_router(meal_checkin.router, prefix="/meal-checkin", tags=["meal-checkin"])

# 运动管理
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(exercise_checkin.router, prefix="/exercise-checkin", tags=["exercise-checkin"])

# 记忆系统
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])

# 游戏化
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])
api_router.include_router(reward_analytics.router, prefix="/reward-analytics", tags=["reward-analytics"])

# 健康评估
api_router.include_router(health_assessment.router, prefix="/health-assessment", tags=["health-assessment"])
api_router.include_router(health_reports.router, prefix="/health-reports", tags=["health-reports"])
api_router.include_router(health_score.router, prefix="/health-score", tags=["health-score"])

# 系统管理
api_router.include_router(system_config.router, prefix="/admin", tags=["system-config"])
```

### 端点清单 (30+)

| 端点 | 前缀 | 主要功能 |
|------|------|----------|
| auth | `/api/v1/auth` | 注册、登录、登出、密码重置 |
| users | `/api/v1/users` | 用户 CRUD、个人资料 |
| health | `/api/v1/health` | 健康记录 CRUD |
| habits | `/api/v1/habits` | 习惯 CRUD、打卡 |
| habit_stats | `/api/v1/habits` | 习惯统计、分析 |
| meals | `/api/v1/meals` | 餐饮记录、照片分析 |
| meal_checkin | `/api/v1/meal-checkin` | 饮食打卡 |
| exercises | `/api/v1/exercises` | 运动库 |
| exercise_checkin | `/api/v1/exercise-checkin` | 运动打卡 |
| dashboard | `/api/v1/dashboard` | 仪表板数据 |
| chat | `/api/v1/chat` | AI 聊天 |
| ai | `/api/v1/ai` | AI 服务 |
| memory | `/api/v1/memory` | 记忆管理、语义搜索 |
| gamification | `/api/v1/gamification` | 游戏化统计 |
| rewards | `/api/v1/rewards` | 徽章、积分 |
| health_assessment | `/api/v1/health-assessment` | 健康评估 |
| health_score | `/api/v1/health-score` | 健康评分 |
| system_config | `/api/v1/admin` | 系统配置 |

### API 端点模式

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.xxx import XXXCreate, XXXResponse

router = APIRouter()

@router.post("/", response_model=XXXResponse, status_code=status.HTTP_201_CREATED)
async def create_xxx(
    xxx_data: XXXCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """端点描述（中文）"""
    # 实现
    return xxx
```

---

## 前端组件结构

### 页面路由

**文件位置**: `frontend/src/App.tsx`

| 路径 | 组件 | 功能 |
|------|------|------|
| `/login` | Auth | 登录/注册 |
| `/dashboard` | DashboardSimple | 仪表板 |
| `/habits` | Habits | 习惯列表 |
| `/habits-stats` | HabitStats | 习惯统计 |
| `/habits/:habitId/detail` | HabitDetail | 习惯详情 |
| `/habits/patterns` | BehaviorPatterns | 行为模式 |
| `/nutrition` | Nutrition | 营养概览 |
| `/diet-tracking` | DietTracking | 饮食追踪 |
| `/health` | HealthTracker | 健康追踪 |
| `/health/assessment` | HealthAssessment | 健康评估 |
| `/gamification` | Gamification | 游戏化 |
| `/chat` | Chat | AI 聊天 |
| `/profile` | Profile | 个人资料 |
| `/exercise-checkin` | ExerciseCheckIn | 运动打卡 |

### Profile 组件结构

**文件位置**: `frontend/src/pages/Profile.tsx`

```typescript
interface UserProfile {
  id?: number;
  email?: string;
  username?: string;
  full_name?: string;
  age?: number;
  gender?: string;
  height?: number;         // 厘米
  initial_weight?: number; // 千克 (前端) / 克 (后端) ⚠️
  target_weight?: number;  // 千克 (前端) / 克 (后端) ⚠️
  activity_level?: string;
  dietary_preferences?: string[];
}
```

**当前字段**: 10 个 (需要扩展到 17 个)

**转换逻辑**:
```typescript
// 前端 → 后端：KG → G
initial_weight: profile.initial_weight * 1000

// 后端 → 前端：G → KG
initial_weight: data.initial_weight / 1000
```

### Dashboard 组件结构

**文件位置**: `frontend/src/pages/DashboardSimple.tsx`

```typescript
interface DashboardData {
  greeting?: string;
  quick_stats?: {
    today_calories?: number;
    daily_step_count?: number;
    sleep_hours?: number;
    water_intake_ml?: number;
    intake_calories?: number;
    basal_metabolism?: number;
    exercise_calories_burned?: number;
  };
}
```

**子组件**:
- `Cards.tsx`: CalorieCard, StepCountCard, SleepCard, WaterIntakeCard
- `ActivitySection.tsx`: 活动部分
- `ExerciseSection.tsx`: 运动部分

### API 客户端

**文件位置**: `frontend/src/api/client.ts`

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
});

// 请求拦截器：添加认证头
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，跳转登录
    }
    return Promise.reject(error);
  }
);
```

### 类型定义

**文件位置**: `frontend/src/types/index.ts`

包含 20+ 接口定义：
- User, AuthState
- HealthRecord
- Habit, HabitCompletion
- NutritionRecommendation
- Gamification 相关 (UserPoints, Badge, Achievement, Challenge, etc.)
- HealthScore
- DashboardOverview

---

## 测试框架与覆盖率

### 后端测试

**配置文件**: `backend/pyproject.toml`, `backend/tests/conftest.py`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --strict-config"
asyncio_mode = "auto"
```

### 测试优先级标记

| 标记 | 说明 | 要求 |
|------|------|------|
| `p0` | 核心功能 | 必须通过 (注册、登录) |
| `p1` | 重要功能 | 高优先级 |
| `p2` | 一般功能、性能 | 中优先级 |
| `p3` | 边缘情况 | 低优先级 |

### 测试数据库配置

```python
# 使用独立 PostgreSQL 测试数据库
TEST_DATABASE_URL = "postgresql://weight_ai_test_user:weight_ai_test_password@127.0.0.1:5432/weight_ai_db_test"

# 测试会话自动清理
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    # TRUNCATE TABLE users RESTART IDENTITY CASCADE
```

### 测试数据工厂

```python
def create_test_user_data(overrides: dict = None) -> dict:
    """使用 UUID 确保并发测试不冲突"""
    unique_id = str(uuid.uuid4())[:8]
    base_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        # ...
    }
```

### 前端测试

**配置**: `frontend/package.json`, `frontend/playwright.config.ts`

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "e2e": "playwright test",
    "e2e:critical": "playwright test --grep @critical"
  }
}
```

### 测试覆盖现状

| 类型 | 覆盖率 | 目标 |
|------|--------|------|
| 后端单元测试 | ~75% | 80% |
| 后端 API 测试 | ~70% | 80% |
| 前端单元测试 | ~60% | 80% |
| E2E 测试 | ~40% | 60% |

---

## 代码规范与约定

### Python 后端

**格式化工具**: Black (88 字符行宽)

```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

**导入排序**: isort

```toml
[tool.isort]
profile = "black"
line_length = 88
```

**类型检查**: mypy (严格模式)

```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
no_implicit_optional = true
strict_equality = true
warn_return_any = true
```

### TypeScript 前端

**配置**: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `auth_service.py` |
| Python 类 | PascalCase | `class UserService` |
| Python 函数 | snake_case | `def get_user_by_email()` |
| Python 常量 | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| 数据库表 | 复数 snake_case | `users`, `health_records` |
| API 路由 | kebab-case | `/api/v1/user-profile` |
| TypeScript 组件 | PascalCase | `UserProfile.tsx` |
| TypeScript 工具 | camelCase | `utils.ts` |

### 日志规范

**后端**: 使用 structlog (禁止 print)

```python
import structlog
logger = structlog.get_logger()

logger.info("Creating user", email=user_data.get("email"))
logger.error("Operation failed", error=str(e), user_id=user_id)
```

### 错误处理

**API 错误响应**:

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"error": "validation_error", "message": "Email already registered"}
)
```

**前端错误处理**:

```typescript
try {
  await api.updateProfile(data);
  toast.success('更新成功');
} catch (err) {
  toast.error(err.response?.data?.message || '更新失败');
}
```

---

## 实现约束与注意事项

### ⚠️ CRITICAL: 重量单位约定

```
🚨 所有重量字段使用克 (grams)，不是千克！

数据库字段:
- users.initial_weight: grams
- users.target_weight: grams
- health_records.weight: grams

前端展示:
- 用户输入：公斤 (KG)
- API 传输：克 (G)
- 展示：公斤 (KG)

转换公式:
- 前端 → 后端：value * 1000
- 后端 → 前端：value / 1000
```

### ⚠️ 个人档案扩展约束

当前 User 模型只有 6 个档案字段，需要扩展到 17 个：

**现有字段**:
1. age
2. gender
3. height
4. initial_weight
5. target_weight
6. activity_level
7. dietary_preferences (JSON)

**需要新增字段** (示例):
1. current_weight (当前体重)
2. waist_circumference (腰围)
3. hip_circumference (臀围)
4. body_fat_percentage (体脂率)
5. muscle_mass (肌肉量)
6. bone_density (骨密度)
7. metabolism_rate (基础代谢率)
8. health_conditions (健康状况，JSON)
9. medications (用药情况，JSON)
10. allergies (过敏信息，JSON)

### ⚠️ 数据库迁移策略

```python
# 使用 Alembic 进行增量迁移
# 文件位置：backend/alembic/versions/

# 示例迁移步骤:
# 1. 创建迁移脚本
alembic revision -m "add_extended_profile_fields"

# 2. 编辑迁移脚本
# 3. 应用迁移
alembic upgrade head
```

### ⚠️ 向后兼容性

```
修改 User 模型时需注意:
1. 现有用户数据不能丢失
2. 新增字段需要设置 nullable=True 或 default 值
3. 前端需要逐步迁移，支持旧数据结构
4. API 响应需要版本控制或渐进式增强
```

### ⚠️ AI 记忆集成约束

```
记忆系统集成要点:
1. UnifiedMemory 使用 pgvector 进行语义搜索
2. 向量维度：768
3. 记忆类型预定义，不能随意扩展
4. 需要定期运行记忆索引任务
5. 嵌入模型：本地 bge-small-zh-v1.5
```

---

## 技术债务与风险点

### 🔴 高优先级技术债务

| ID | 问题 | 影响 | 建议 |
|----|------|------|------|
| TD-001 | 重量单位混用风险 | 数据不一致 | 统一转换为克，前端明确标注 |
| TD-002 | User 模型字段不足 | 无法支持新需求 | 执行数据库迁移扩展字段 |
| TD-003 | 测试覆盖率不足 | 回归风险 | 优先补充 p0/p1 测试 |
| TD-004 | 通知端点被注释 | 功能不可用 | 修复认证依赖后启用 |

### 🟡 中优先级技术债务

| ID | 问题 | 影响 | 建议 |
|----|------|------|------|
| TD-005 | 前后端单位转换逻辑分散 | 维护困难 | 集中到工具函数 |
| TD-006 | Profile 页面缺少验证 | 数据质量问题 | 添加表单验证 |
| TD-007 | 游戏化与核心业务耦合 | 扩展困难 | 解耦为独立模块 |
| TD-008 | 记忆系统有 legacy 字段 | 技术混乱 | 清理 embedding_legacy |

### ⚠️ 潜在风险点

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 数据库迁移失败导致数据丢失 | 低 | 高 | 备份 + 回滚脚本 |
| 前后端单位转换错误 | 中 | 高 | 添加单元测试 |
| AI 记忆语义搜索性能问题 | 中 | 中 | 添加索引 + 缓存 |
| 游戏化系统刷分漏洞 | 中 | 中 | 添加反作弊逻辑 |

---

## Epic/Story 拆解建议

### Epic 1: 个人档案扩展

**目标**: 将用户档案从 6 字段扩展到 17 字段

```
Epic: PA-001 个人档案扩展
├── Story: PA-001-01 数据库模型扩展
│   ├── Task: 添加新字段到 User 模型
│   ├── Task: 创建 Alembic 迁移脚本
│   └── Task: 添加字段验证逻辑
├── Story: PA-001-02 Schema 更新
│   ├── Task: 更新 UserBase schema
│   ├── Task: 更新 UserCreate schema
│   └── Task: 更新 UserUpdate schema
├── Story: PA-001-03 API 端点更新
│   ├── Task: 更新 GET /users/me 响应
│   ├── Task: 更新 PUT /users/me 请求处理
│   └── Task: 添加字段级权限控制
├── Story: PA-001-04 前端 Profile 页面
│   ├── Task: 添加新表单字段
│   ├── Task: 实现单位转换逻辑
│   └── Task: 添加表单验证
└── Story: PA-001-05 测试与文档
    ├── Task: 添加后端单元测试
    ├── Task: 添加前端组件测试
    └── Task: 更新 API 文档
```

### Epic 2: 目标系统新增

**目标**: 实现 4 维度目标追踪

```
Epic: GS-001 目标系统
├── Story: GS-001-01 数据模型设计
│   ├── Task: 设计 Goal 模型 (4 维度)
│   ├── Task: 设计 GoalProgress 模型
│   └── Task: 创建数据库迁移
├── Story: GS-001-02 后端服务实现
│   ├── Task: 实现 GoalService
│   ├── Task: 实现进度追踪逻辑
│   └── Task: 实现目标达成判定
├── Story: GS-001-03 API 端点
│   ├── Task: CRUD 端点
│   ├── Task: 进度更新端点
│   └── Task: 统计分析端点
├── Story: GS-001-04 前端目标管理
│   ├── Task: 目标创建页面
│   ├── Task: 目标进度仪表板
│   └── Task: 目标达成通知
└── Story: GS-001-05 与现有系统集成
    ├── Task: 与习惯系统关联
    ├── Task: 与健康评估关联
    └── Task: 与游戏化系统关联
```

### Epic 3: 饮食/运动成就系统

**目标**: 扩展游戏化成就系统

```
Epic: GA-001 成就系统扩展
├── Story: GA-001-01 成就定义
│   ├── Task: 设计饮食成就 (10+)
│   ├── Task: 设计运动成就 (10+)
│   └── Task: 创建成就配置表
├── Story: GA-001-02 成就追踪
│   ├── Task: 实现成就进度追踪
│   ├── Task: 实现自动达成检测
│   └── Task: 实现成就通知
├── Story: GA-001-03 前端展示
│   ├── Task: 成就页面
│   ├── Task: 成就获得动画
│   └── Task: 成就分享功能
└── Story: GA-001-04 数据分析
    ├── Task: 成就统计 API
    └── Task: 成就推荐算法
```

### Epic 4: AI 记忆集成

**目标**: 增强 AI 个性化推荐

```
Epic: AI-001 记忆集成
├── Story: AI-001-01 记忆提取
│   ├── Task: 饮食记忆提取
│   ├── Task: 运动记忆提取
│   └── Task: 习惯记忆提取
├── Story: AI-001-02 记忆检索
│   ├── Task: 语义搜索优化
│   ├── Task: 记忆关联分析
│   └── Task: 记忆重要性评分
├── Story: AI-001-03 AI 推荐增强
│   ├── Task: 基于记忆的个性化建议
│   ├── Task: 记忆驱动的对话上下文
│   └── Task: 记忆驱动的目标推荐
└── Story: AI-001-04 性能优化
    ├── Task: 嵌入缓存
    ├── Task: 向量索引优化
    └── Task: 异步记忆处理
```

### Epic 5: Onboarding 引导流程

**目标**: 5 步新手引导

```
Epic: OB-001 Onboarding
├── Story: OB-001-01 流程设计
│   ├── Task: 步骤 1: 基本信息
│   ├── Task: 步骤 2: 健康目标
│   ├── Task: 步骤 3: 生活习惯
│   ├── Task: 步骤 4: 饮食偏好
│   └── Task: 步骤 5: 运动习惯
├── Story: OB-001-02 前端实现
│   ├── Task: 引导组件
│   ├── Task: 进度保存
│   └── Task: 跳过/返回逻辑
├── Story: OB-001-03 后端支持
│   ├── Task: 引导状态存储
│   ├── Task: 引导数据分析
│   └── Task: 引导完成率统计
└── Story: OB-001-04 优化迭代
    ├── Task: A/B 测试框架
    └── Task: 转化漏斗分析
```

---

## 附录

### A. 数据库迁移历史

| 迁移 ID | 日期 | 说明 |
|---------|------|------|
| 001_initial_migration | - | 初始迁移 |
| 002_add_memory_tables | - | 添加记忆表 |
| 003_add_role_switching | - | AI 角色切换 |
| 004_add_habit_goals | - | 习惯目标 |
| 005_add_health_assessments | - | 健康评估 |
| 006_add_notification_system | - | 通知系统 |
| 007_add_system_config_management | - | 系统配置 |
| 008_add_ai_prompt_versioning | - | AI 提示版本 |
| 3c2a37ef51de_add_pgvector | - | pgvector 支持 |
| 521bbf2caeb5_sync_schemas | - | 同步表结构 |
| 2026_02_26_v2_0_remove_is_indexed | - | 移除索引列 |

### B. 关键服务列表

| 服务 | 文件 | 职责 |
|------|------|------|
| AuthService | `auth_service.py` | 认证、令牌 |
| UserService | `user_service.py` | 用户管理 |
| HabitService | `habit_service.py` | 习惯管理 |
| NutritionService | `nutrition_service.py` | 营养计算 |
| GamificationService | `gamification_service.py` | 游戏化 |
| MemoryService | `memory_*_service.py` | 记忆管理 |
| DashboardService | `dashboard_service.py` | 仪表板数据 |

### C. 环境变量配置

```bash
# 数据库
DATABASE_URL=postgresql://...
SQLITE_DATABASE_URL=sqlite:///./weight_management.db

# AI 服务
QWEN_API_KEY=xxx
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# Redis
REDIS_URL=redis://localhost:6379

# 应用配置
ENVIRONMENT=development
SECRET_KEY=xxx
```

---

**文档状态**: ✅ 完整  
**最后更新**: 2026-02-27  
**维护者**: BMAD Analyst Agent
