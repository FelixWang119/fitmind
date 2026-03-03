---
sprint: 5
story_id: SP-10.1
title: "报告数据服务 (Report Data Service)"
priority: P0
story_points: 8
status: ready-for-dev
created_date: "2026-03-02"
assignee: "Developer"
epic: 10
epic_title: "健康报告"
---

# Story SP-10.1: 报告数据服务 (Report Data Service)

## 📋 用户故事

**作为** 系统  
**我想要** 准备好报告需要的数据  
**以便** 为 AI 生成报告提供基础

---

## 🎯 验收标准

### 数据查询要求

- [ ] **复用健康评估的数据查询逻辑**
  - [ ] 参考 `backend/app/api/v1/endpoints/health_reports.py` 中的现有查询
  - [ ] 重构为可复用的服务层

- [ ] **支持日报数据（当天）**
  - [ ] 查询当天体重记录
  - [ ] 查询当天饮食记录 (Meal)
  - [ ] 查询当天运动记录 (HealthRecord)
  - [ ] 查询当天习惯打卡记录

- [ ] **支持周报数据（本周7天）**
  - [ ] 聚合7天内的体重变化
  - [ ] 聚合7天内的热量摄入/消耗
  - [ ] 聚合7天内的运动分钟数
  - [ ] 聚合7天内的习惯打卡完成率

- [ ] **支持月报数据（本月30天）**
  - [ ] 聚合30天内的体重趋势
  - [ ] 聚合30天内的热量平衡
  - [ ] 聚合30天内的运动频率
  - [ ] 聚合30天内的习惯打卡统计

- [ ] **返回标准化的数据结构**
  - [ ] 定义 `ReportData` Pydantic 模型
  - [ ] 统一返回格式包含: period, period_type, metrics, trends

---

## 📐 技术规格

### 文件位置

**新建文件:**
- `backend/app/services/report_data_service.py` - 报告数据服务

**复用文件:**
- `backend/app/api/v1/endpoints/health_reports.py` - 现有数据查询逻辑
- `backend/app/schemas/health_report.py` - 现有 Schema
- `backend/app/models/health_record.py` - HealthRecord 模型
- `backend/app/models/nutrition.py` - Meal 模型

### 数据模型

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, datetime
from enum import Enum


class ReportType(str, Enum):
    DAILY = "daily"      # 日报
    WEEKLY = "weekly"    # 周报
    MONTHLY = "monthly"  # 月报


class PeriodInfo(BaseModel):
    """时间段信息"""
    start_date: date
    end_date: date
    report_type: ReportType
    days_count: int


class WeightMetrics(BaseModel):
    """体重指标"""
    current_weight: Optional[float] = None
    weight_change: Optional[float] = None
    weight_change_rate: Optional[float] = None
    average_weight: Optional[float] = None
    records_count: int = 0


class NutritionMetrics(BaseModel):
    """营养指标"""
    total_calories: float = 0
    average_daily_calories: float = 0
    meals_count: int = 0
    meal_breakdown: Dict[str, int] = {}  # breakfast/lunch/dinner/snack


class ExerciseMetrics(BaseModel):
    """运动指标"""
    total_minutes: int = 0
    average_daily_minutes: float = 0
    total_steps: int = 0
    total_calories_burned: float = 0
    sessions_count: int = 0


class HabitMetrics(BaseModel):
    """习惯打卡指标"""
    total_checkins: int = 0
    checkin_rate: float = 0  # 0-100%
    habits_completed: List[str] = []
    habits_partial: List[str] = []
    habits_missed: List[str] = []


class ReportData(BaseModel):
    """报告数据"""
    period: PeriodInfo
    weight: WeightMetrics
    nutrition: NutritionMetrics
    exercise: ExerciseMetrics
    habits: HabitMetrics
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": {
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-01",
                    "report_type": "daily",
                    "days_count": 1
                },
                "weight": {
                    "current_weight": 70.5,
                    "weight_change": -0.3,
                    "weight_change_rate": -0.42,
                    "average_weight": 70.6,
                    "records_count": 1
                },
                "nutrition": {
                    "total_calories": 1800,
                    "average_daily_calories": 1800,
                    "meals_count": 3,
                    "meal_breakdown": {"breakfast": 500, "lunch": 700, "dinner": 600}
                },
                "exercise": {
                    "total_minutes": 45,
                    "average_daily_minutes": 45,
                    "total_steps": 6000,
                    "total_calories_burned": 300,
                    "sessions_count": 1
                },
                "habits": {
                    "total_checkins": 5,
                    "checkin_rate": 83.3,
                    "habits_completed": ["water", "weight"],
                    "habits_partial": [],
                    "habits_missed": ["meditation"]
                },
                "generated_at": "2026-03-02T10:00:00"
            }
        }
```

### 服务接口

```python
class ReportDataService:
    """报告数据服务"""
    
    async def get_daily_report_data(
        self, 
        user_id: int, 
        target_date: date,
        db: Session
    ) -> ReportData:
        """获取日报数据"""
        pass
    
    async def get_weekly_report_data(
        self, 
        user_id: int, 
        week_start: date,
        db: Session
    ) -> ReportData:
        """获取周报数据"""
        pass
    
    async def get_monthly_report_data(
        self, 
        user_id: int, 
        month_start: date,
        db: Session
    ) -> ReportData:
        """获取月报数据"""
        pass
    
    async def get_report_data(
        self,
        user_id: int,
        report_type: ReportType,
        target_date: date,
        db: Session
    ) -> ReportData:
        """统一入口：根据报告类型获取数据"""
        pass
```

### 依赖关系

```
Story 10.1 (报告数据服务)
    │
    ├── 复用: health_reports.py 数据查询
    ├── 复用: HealthRecord 模型
    ├── 依赖: Meal 模型 (已有)
    └── 产出: ReportData Service
              │
              └──▶ Story 10.2 (AI 报告生成)
```

---

## ✅ 验收测试

### 单元测试

```python
# tests/test_report_data_service.py

import pytest
from datetime import date
from app.services.report_data_service import ReportDataService, ReportType


class TestReportDataService:
    """报告数据服务测试"""
    
    @pytest.mark.asyncio
    async def test_get_daily_report_data(self, db_session, test_user):
        """测试日报数据查询"""
        # Arrange
        service = ReportDataService()
        
        # Act
        result = await service.get_daily_report_data(
            user_id=test_user.id,
            target_date=date(2026, 3, 2),
            db=db_session
        )
        
        # Assert
        assert result.period.report_type == ReportType.DAILY
        assert result.period.days_count == 1
        assert result.weight is not None
        assert result.nutrition is not None
        assert result.exercise is not None
    
    @pytest.mark.asyncio
    async def test_get_weekly_report_data(self, db_session, test_user):
        """测试周报数据聚合"""
        # Arrange
        service = ReportDataService()
        
        # Act
        result = await service.get_weekly_report_data(
            user_id=test_user.id,
            week_start=date(2026, 2, 24),
            db=db_session
        )
        
        # Assert
        assert result.period.report_type == ReportType.WEEKLY
        assert result.period.days_count == 7
    
    @pytest.mark.asyncio
    async def test_get_monthly_report_data(self, db_session, test_user):
        """测试月报数据聚合"""
        # Arrange
        service = ReportDataService()
        
        # Act
        result = await service.get_monthly_report_data(
            user_id=test_user.id,
            month_start=date(2026, 3, 1),
            db=db_session
        )
        
        # Assert
        assert result.period.report_type == ReportType.MONTHLY
        assert result.period.days_count >= 28
```

### 边界情况测试

- [ ] 无数据时返回默认值
- [ ] 部分数据缺失时正常处理
- [ ] 跨月份数据聚合正确
- [ ] 体重变化计算正确（含正负）
- [ ] 热量平衡正负判断正确

---

## 🔗 相关文档

- **Epic 需求**: `_bmad_out/planning-artifacts/epic-10-health-report.md`
- **现有实现**: `backend/app/api/v1/endpoints/health_reports.py`
- **数据模型**: `backend/app/schemas/health_report.py`
- **项目规范**: `_bmad_out/project-context.md`

---

## 📝 开发注意事项

1. **复用优先**: 现有 `health_reports.py` 有完整的数据查询逻辑，重构为服务层而非重新实现
2. **时间处理**: 使用 `date` 而非 `datetime`，确保日期边界正确
3. **空值处理**: 使用 `Optional` 和默认值，避免 None 导致前端报错
4. **性能考虑**: 
   - 考虑添加缓存（复用 Redis）
   - 大数据量时使用分页或流式处理
5. **一致性**: 与现有 API 响应格式保持一致
