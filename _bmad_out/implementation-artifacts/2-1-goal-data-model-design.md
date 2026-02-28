# Story 2.1: 目标数据模型设计

**Epic**: 2 - 目标系统实现  
**Story ID**: 2.1  
**Story Key**: `2-1-goal-data-model-design`  
**优先级**: P0 (MVP 核心)  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 开发者  
**我想要** 实现 AI 驱动的目标推荐逻辑  
**以便** 用户能获得科学合理的个性化目标建议  

---

## ✅ 验收标准 (BDD 格式)

### AC 2.1.1: 4 维度目标类型支持

**Given** 需要支持多维度目标  
**When** 系统处理目标类型  
**Then** 支持以下类型:
- `weight` (体重目标)
- `exercise` (运动目标)
- `diet` (饮食目标)
- `habit` (习惯目标)

### AC 2.1.2: 体重目标 AI 推荐

**Given** 用户设置体重目标  
**When** AI 计算推荐范围  
**Then** 基于健康 BMI (18.5-24) 计算:
- 推荐目标体重 = 身高(m)² × 22 (中间值)
- 允许范围: 身高(m)² × 18.5 ~ 身高(m)² × 24
- 每周安全减重: 0.5-1kg

### AC 2.1.3: 运动目标 AI 推荐

**Given** 用户设置运动目标  
**When** AI 计算推荐值  
**Then** 基于活动水平推荐:
- 久坐: 3000-5000 步/天
- 轻度活动: 5000-7000 步/天
- 中度活动: 7000-10000 步/天
- 每周运动: 150-300 分钟中等强度

### AC 2.1.4: 饮食目标 AI 推荐

**Given** 用户设置饮食目标  
**When** AI 计算推荐值  
**Then** 基于 BMR + 活动量 - 热量缺口:
- BMR = 体重(kg) × 10 + 身高(cm) × 6.25 - 年龄 × 5 + 5 (男性)
- BMR = 体重(kg) × 10 + 身高(cm) × 6.25 - 年龄 × 5 - 161 (女性)
- 活动系数: 1.2/1.375/1.55/1.725
- 热量缺口: 300-500 kcal/天 (减重)

### AC 2.1.5: 习惯目标 AI 推荐

**Given** 用户设置习惯目标  
**When** AI 计算推荐值  
**Then** 基于体重计算:
- 饮水: 体重(kg) × 30-35 ml/天
- 睡眠: 7-8 小时/天
- 如厕: 1-2 次/天

### AC 2.1.6: 预测达成日期计算

**Given** 用户设置目标  
**When** 计算预测日期  
**Then** 基于:
- 当前值与目标值的差值
- 用户历史数据趋势
- 每日平均进步量
- 考虑平台期调整

---

## 🏗️ 技术需求

### 核心模块

**文件位置**: `backend/app/services/goal_recommendation.py`

```python
from typing import Optional
from datetime import datetime, timedelta

class GoalRecommendationService:
    """AI 驱动的目标推荐服务"""
    
    def calculate_weight_goal(
        self,
        height_cm: float,
        current_weight_g: float,
        target_weight_g: Optional[float] = None
    ) -> dict:
        """计算体重目标"""
        # BMI = weight(kg) / height(m)²
        height_m = height_cm / 100
        bmi = (current_weight_g / 1000) / (height_m ** 2)
        
        min_weight = 18.5 * height_m ** 2 * 1000  # 克
        max_weight = 24 * height_m ** 2 * 1000
        ideal_weight = 22 * height_m ** 2 * 1000
        
        return {
            "recommended_range": {"min": min_weight, "max": max_weight},
            "ideal": ideal_weight,
            "current_bmi": bmi,
            "weekly_safe_loss_g": 500000,  # 500g/周
        }
    
    def calculate_exercise_goal(
        self,
        activity_level: str,  # sedentary/light/moderate/active
        current_steps: Optional[int] = None
    ) -> dict:
        """计算运动目标"""
        step_targets = {
            "sedentary": 5000,
            "light": 7000,
            "moderate": 10000,
            "active": 12000
        }
        
        weekly_minutes = {
            "sedentary": 90,
            "light": 150,
            "moderate": 225,
            "active": 300
        }
        
        return {
            "daily_steps": step_targets.get(activity_level, 7000),
            "weekly_exercise_minutes": weekly_minutes.get(activity_level, 150),
        }
    
    def calculate_diet_goal(
        self,
        weight_g: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str,
        goal_type: str = "lose"  # lose/maintain/gain
    ) -> dict:
        """计算饮食目标"""
        # BMR 计算
        if gender == "male":
            bmr = (weight_g / 1000) * 10 + height_cm * 6.25 - age * 5 + 5
        else:
            bmr = (weight_g / 1000) * 10 + height_cm * 6.25 - age * 5 - 161
        
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)
        
        # 热量调整
        calorie_adjustments = {
            "lose": -400,
            "maintain": 0,
            "gain": 300
        }
        
        target_calories = tdee + calorie_adjustments.get(goal_type, 0)
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_calories,
            "macros": {
                "protein_g": (target_calories * 0.3) / 4,
                "carbs_g": (target_calories * 0.4) / 4,
                "fat_g": (target_calories * 0.3) / 9
            }
        }
    
    def calculate_habit_goals(self, weight_g: float) -> dict:
        """计算习惯目标"""
        weight_kg = weight_g / 1000
        
        return {
            "water_ml": int(weight_kg * 33),  # ml/天
            "sleep_hours": 7.5,
            "defecation_per_day": 1
        }
    
    def predict_completion_date(
        self,
        current_value: float,
        target_value: float,
        daily_progress: float,
        goal_type: str
    ) -> Optional[datetime]:
        """预测目标完成日期"""
        if daily_progress == 0:
            return None
        
        if goal_type in ["weight", "diet"]:
            # 减重/减脂目标: current > target
            remaining = current_value - target_value
        else:
            # 增肌/运动目标: current < target
            remaining = target_value - current_value
        
        days_needed = remaining / abs(daily_progress)
        
        # 考虑平台期 (每 2 周休息 1 天)
        platform_buffer = days_needed / 14
        
        return datetime.now() + timedelta(days=int(days_needed + platform_buffer))
```

### Schema 扩展

**文件位置**: `backend/app/schemas/goal.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class GoalRecommendationRequest(BaseModel):
    """目标推荐请求"""
    goal_type: str = Field(..., description="目标类型: weight/exercise/diet/habit")
    current_value: Optional[float] = None
    user_profile: Optional[dict] = None  # 身高、体重、年龄等

class GoalRecommendationResponse(BaseModel):
    """目标推荐响应"""
    recommended_value: float
    recommended_range: dict
    reasoning: str
    predicted_completion_date: Optional[datetime] = None
```

---

## 🔄 依赖关系

- **前置**: Story 1.6 (目标数据模型) - 已完成 ✅
- **后续**: Story 2.2 (目标创建与追踪)

---

## 🧪 测试用例

1. `test_weight_goal_bmi_calculation` - BMI 计算正确性
2. `test_exercise_goal_activity_levels` - 不同活动水平推荐
3. `test_diet_goal_bmr_calculation` - BMR 计算 (男/女)
4. `test_habit_goals_water_calculation` - 饮水目标计算
5. `test_prediction_date_platform_adjustment` - 平台期调整
