# Story 2.2: 目标创建与追踪

**Epic**: 2 - 目标系统实现  
**Story ID**: 2.2  
**Story Key**: `2-2-goal-creation-tracking`  
**优先级**: P0 (MVP 核心)  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 设置和追踪我的健康目标  
**以便** 我能可视化我的进度并保持动力  

---

## ✅ 验收标准 (BDD 格式)

### AC 2.2.1: 目标创建 UI

**Given** 用户进入目标设置页面  
**When** 选择目标维度 (体重/运动/饮食/习惯)  
**Then** 显示:
- AI 推荐的范围值
- 当前值输入框
- 目标值输入框
- 目标日期选择器

### AC 2.2.2: 目标创建 API

**Given** 用户提交目标表单  
**When** POST /api/v1/goals 被调用  
**Then** 创建 UserGoal 记录:
- 返回 201 Created
- 包含 goal_id 和推荐进度
- 自动生成首次预测日期

### AC 2.2.3: 进度记录 API

**Given** 用户记录每日进度  
**When** POST /api/v1/goals/{goal_id}/progress 被调用  
**Then**:
- 创建 GoalProgress 记录
- 更新 UserGoal.current_value
- 计算连续达成天数 (streak)
- 返回更新后的进度

### AC 2.2.4: 目标列表 API

**Given** 用户查看目标  
**When** GET /api/v1/goals 被调用  
**Then** 返回:
- 所有活跃目标
- 每个目标的进度百分比
- 预测完成日期
- 今日完成状态

### AC 2.2.5: 目标详情 API

**Given** 用户查看单个目标  
**When** GET /api/v1/goals/{goal_id} 被调用  
**Then** 返回:
- 目标完整信息
- 最近 30 天进度历史
- 趋势图表数据
- 与预测对比

### AC 2.2.6: 目标更新 API

**Given** 用户调整目标  
**When** PATCH /api/v1/goals/{goal_id} 被调用  
**Then**:
- 更新目标值
- 创建 GoalHistory 记录
- 重新计算预测日期
- 返回更新后的目标

### AC 2.2.7: 目标取消/暂停 API

**Given** 用户想暂停或取消目标  
**When** PATCH /api/v1/goals/{goal_id}/status 被调用  
**Then**:
- 更新目标状态 (paused/cancelled)
- 记录到 GoalHistory
- 返回确认消息

### AC 2.2.8: 前端进度展示

**Given** 用户查看目标页面  
**When** 页面加载  
**Then** 显示:
- 进度条 (实时百分比)
- 趋势图 (最近 30 天)
- 预测达成日期
- 完成/未完成徽章

---

## 🏗️ 技术需求

### API Endpoints

**文件位置**: `backend/app/api/v1/endpoints/goals.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.goal import UserGoal, GoalProgress, GoalStatus
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalProgressCreate,
    GoalProgressResponse,
    GoalListResponse,
)

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新目标"""
    goal = UserGoal(
        user_id=current_user.id,
        goal_type=goal_data.goal_type,
        current_value=goal_data.current_value,
        target_value=goal_data.target_value,
        unit=goal_data.unit,
        target_date=goal_data.target_date,
        status=GoalStatus.ACTIVE.value
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=List[GoalListResponse])
def list_goals(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标列表"""
    query = db.query(UserGoal).filter(UserGoal.user_id == current_user.id)
    
    if status:
        query = query.filter(UserGoal.status == status)
    
    goals = query.order_by(UserGoal.created_at.desc()).all()
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标详情"""
    goal = db.query(UserGoal).filter(
        UserGoal.goal_id == goal_id,
        UserGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新目标"""
    goal = db.query(UserGoal).filter(
        UserGoal.goal_id == goal_id,
        UserGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    # 记录历史
    # ... (创建 GoalHistory)
    
    # 更新字段
    for key, value in goal_data.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/progress", response_model=GoalProgressResponse)
def record_progress(
    goal_id: int,
    progress_data: GoalProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录进度"""
    goal = db.query(UserGoal).filter(
        UserGoal.goal_id == goal_id,
        UserGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    # 计算连续达成
    last_progress = db.query(GoalProgress).filter(
        GoalProgress.goal_id == goal_id
    ).order_by(GoalProgress.recorded_date.desc()).first()
    
    streak = 1
    if last_progress and last_progress.daily_target_met:
        streak = last_progress.streak_count + 1
    
    # 创建进度记录
    progress = GoalProgress(
        goal_id=goal_id,
        recorded_date=progress_data.recorded_date or datetime.now(),
        value=progress_data.value,
        daily_target_met=progress_data.daily_target_met,
        streak_count=streak
    )
    
    # 更新目标当前值
    goal.current_value = progress_data.value
    
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/{goal_id}/progress", response_model=List[GoalProgressResponse])
def get_goal_progress(
    goal_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标进度历史"""
    from datetime import timedelta
    
    goal = db.query(UserGoal).filter(
        UserGoal.goal_id == goal_id,
        UserGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    progress_list = db.query(GoalProgress).filter(
        GoalProgress.goal_id == goal_id,
        GoalProgress.recorded_date >= datetime.now() - timedelta(days=days)
    ).order_by(GoalProgress.recorded_date.asc()).all()
    
    return progress_list


@router.patch("/{goal_id}/status", response_model=GoalResponse)
def update_goal_status(
    goal_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新目标状态 (暂停/取消/恢复)"""
    goal = db.query(UserGoal).filter(
        UserGoal.goal_id == goal_id,
        UserGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    if status not in ["active", "paused", "cancelled", "completed"]:
        raise HTTPException(status_code=400, detail="无效状态")
    
    goal.status = status
    db.commit()
    db.refresh(goal)
    return goal
```

### Schemas

**文件位置**: `backend/app/schemas/goal.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class GoalCreate(BaseModel):
    """创建目标请求"""
    goal_type: str = Field(..., description="目标类型: weight/exercise/diet/habit")
    current_value: Optional[float] = None
    target_value: float = Field(..., gt=0)
    unit: str = Field(..., description="单位: kg/步/kcal/小时")
    target_date: Optional[datetime] = None


class GoalUpdate(BaseModel):
    """更新目标请求"""
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None
    current_value: Optional[float] = None


class GoalProgressCreate(BaseModel):
    """记录进度请求"""
    value: float
    daily_target_met: bool = False
    recorded_date: Optional[datetime] = None


class GoalProgressResponse(BaseModel):
    """进度响应"""
    progress_id: int
    goal_id: int
    recorded_date: datetime
    value: float
    daily_target_met: bool
    streak_count: int

    class Config:
        from_attributes = True


class GoalResponse(BaseModel):
    """目标响应"""
    goal_id: int
    user_id: int
    goal_type: str
    current_value: Optional[float]
    target_value: float
    unit: str
    start_date: datetime
    target_date: Optional[datetime]
    predicted_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

    # 计算属性
    progress_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """目标列表响应 (简化版)"""
    goal_id: int
    goal_type: str
    current_value: Optional[float]
    target_value: float
    unit: str
    status: str
    predicted_date: Optional[datetime]
    progress_percentage: float
    
    class Config:
        from_attributes = True
```

### 前端组件

**文件位置**: `frontend/src/pages/Goals.tsx`

```typescript
// 目标列表页面
// - 显示所有活跃/已完成目标
// - 进度条 + 预测日期
// - 创建新目标按钮
// - 目标卡片点击跳转详情
```

**文件位置**: `frontend/src/components/Goals/GoalCard.tsx`

```typescript
// 目标卡片组件
// - 显示进度条 (ProgressBar)
// - 显示目标类型图标
// - 显示完成百分比
// - 显示预测日期
```

**文件位置**: `frontend/src/components/Goals/GoalCreateModal.tsx`

```typescript
// 创建目标弹窗
// - 目标类型选择 (Tabs)
// - AI 推荐范围展示
// - 目标值输入
// - 目标日期选择
// - 提交按钮
```

---

## 🔄 依赖关系

- **前置**: 
  - Story 1.6 (目标数据模型) - 已完成 ✅
  - Story 2.1 (AI 推荐逻辑) - 本 Epic 内
- **后续**: Story 2.3 (AI 反馈策略)

---

## 🧪 测试用例

1. `test_create_goal_success` - 创建目标成功
2. `test_create_goal_validation` - 目标值验证
3. `test_record_progress_streak` - 连续达成计算
4. `test_list_goals_filter` - 目标列表筛选
5. `test_update_goal_creates_history` - 更新创建历史记录
6. `test_pause_goal_status` - 暂停目标
7. `test_progress_chart_data` - 进度图表数据格式
