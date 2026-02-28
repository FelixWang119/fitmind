"""
目标相关 Pydantic Schemas
Story 2.1 & 2.2: 目标数据模型与创建追踪
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator


# ==================== 目标推荐相关 Schema ====================


class UserProfileInput(BaseModel):
    """用户资料输入 (用于目标推荐)"""

    height: Optional[int] = Field(None, ge=50, le=250, description="身高 (厘米)")
    current_weight: Optional[int] = Field(
        None, ge=10000, le=300000, description="当前体重 (克)"
    )
    age: Optional[int] = Field(None, ge=0, le=120, description="年龄")
    gender: Optional[str] = Field(None, description="性别: male/female")
    activity_level: Optional[str] = Field(
        None, description="活动水平: sedentary/light/moderate/active"
    )
    current_steps: Optional[int] = Field(None, ge=0, description="当前步数")
    current_water_ml: Optional[int] = Field(None, ge=0, description="当前饮水量 (毫升)")
    current_sleep_hours: Optional[float] = Field(
        None, ge=0, le=24, description="当前睡眠时长 (小时)"
    )
    diet_goal: Optional[str] = Field(None, description="饮食目标: lose/maintain/gain")


class GoalRecommendationRequest(BaseModel):
    """目标推荐请求"""

    goal_type: str = Field(..., description="目标类型: weight/exercise/diet/habit")
    user_profile: Optional[UserProfileInput] = None


class WeightRecommendationResponse(BaseModel):
    """体重目标推荐响应"""

    recommended_range: Dict[str, Any] = Field(..., description="推荐范围")
    recommended_target_g: Optional[float] = Field(None, description="推荐目标 (克)")
    ideal_g: float = Field(..., description="理想体重 (克)")
    ideal_kg: float = Field(..., description="理想体重 (千克)")
    current_bmi: float = Field(..., description="当前 BMI")
    bmi_category: str = Field(..., description="BMI 分类")
    weekly_safe_loss_g: Dict[str, int] = Field(..., description="每周安全减重范围 (克)")
    estimated_days_to_goal: Optional[int] = Field(None, description="预计达成天数")
    reasoning: str = Field(..., description="推荐理由")


class ExerciseRecommendationResponse(BaseModel):
    """运动目标推荐响应"""

    daily_steps: int = Field(..., description="每日步数目标")
    weekly_steps: int = Field(..., description="每周步数目标")
    daily_exercise_minutes: float = Field(..., description="每日运动分钟数")
    weekly_exercise_minutes: int = Field(..., description="每周运动分钟数")
    activity_level: str = Field(..., description="活动水平")
    reasoning: str = Field(..., description="推荐理由")
    # 可选字段
    current_steps: Optional[int] = Field(None, description="当前步数")
    progress_percentage: Optional[float] = Field(None, description="进度百分比")
    steps_remaining: Optional[int] = Field(None, description="剩余步数")
    encouragement: Optional[str] = Field(None, description="鼓励消息")


class MacroNutrients(BaseModel):
    """宏量营养素"""

    protein_g: float = Field(..., description="蛋白质 (克)")
    carbs_g: float = Field(..., description="碳水 (克)")
    fat_g: float = Field(..., description="脂肪 (克)")


class MealBreakdown(BaseModel):
    """餐次热量分配"""

    breakfast: float = Field(..., description="早餐热量")
    lunch: float = Field(..., description="午餐热量")
    dinner: float = Field(..., description="晚餐热量")
    snacks: float = Field(..., description="零食热量")


class DietRecommendationResponse(BaseModel):
    """饮食目标推荐响应"""

    bmr: float = Field(..., description="基础代谢率 (kcal)")
    tdee: float = Field(..., description="总日常能量消耗 (kcal)")
    target_calories: float = Field(..., description="目标热量 (kcal)")
    calorie_adjustment: int = Field(..., description="热量调整")
    diet_goal_type: str = Field(..., description="饮食目标类型")
    activity_level: str = Field(..., description="活动水平")
    macros: MacroNutrients = Field(..., description="宏量营养素推荐")
    meal_breakdown: MealBreakdown = Field(..., description="餐次热量分配")
    reasoning: str = Field(..., description="推荐理由")


class HabitRecommendationResponse(BaseModel):
    """习惯目标推荐响应"""

    water_ml: int = Field(..., description="每日饮水量 (毫升)")
    water_glasses: float = Field(..., description="每日饮水杯数 (每杯约250ml)")
    sleep_hours: float = Field(..., description="每日睡眠时长 (小时)")
    defecation_per_day: int = Field(..., description="每日如厕次数")
    reasoning: str = Field(..., description="推荐理由")
    # 可选字段
    current_water_ml: Optional[int] = Field(None, description="当前饮水量")
    water_progress_percentage: Optional[float] = Field(
        None, description="饮水进度百分比"
    )
    current_sleep_hours: Optional[float] = Field(None, description="当前睡眠时长")
    sleep_progress_percentage: Optional[float] = Field(
        None, description="睡眠进度百分比"
    )


class PredictionResponse(BaseModel):
    """预测响应"""

    predicted_date: str = Field(..., description="预测完成日期 (ISO格式)")
    days_remaining: int = Field(..., description="剩余天数")
    is_achieved: bool = Field(..., description="是否已达成")
    reasoning: str = Field(..., description="预测理由")
    avg_daily_progress: Optional[float] = Field(None, description="每日平均进步量")


class GoalRecommendationResponse(BaseModel):
    """目标推荐响应 (单一类型)"""

    goal_type: str = Field(..., description="目标类型")
    recommendation: Dict[str, Any] = Field(..., description="推荐详情")
    prediction: Optional[PredictionResponse] = Field(None, description="完成预测")


class AllRecommendationsResponse(BaseModel):
    """所有目标推荐响应"""

    weight: Optional[WeightRecommendationResponse] = None
    exercise: Optional[ExerciseRecommendationResponse] = None
    diet: Optional[DietRecommendationResponse] = None
    habit: Optional[HabitRecommendationResponse] = None


# ==================== 目标创建/更新相关 Schema ====================


class GoalCreate(BaseModel):
    """创建目标请求"""

    goal_type: str = Field(..., description="目标类型: weight/exercise/diet/habit")
    current_value: Optional[float] = Field(None, description="当前值")
    target_value: float = Field(..., gt=0, description="目标值")
    unit: str = Field(..., description="单位: kg/步/kcal/ml/小时")
    target_date: Optional[datetime] = Field(None, description="目标日期")

    @field_validator("goal_type")
    @classmethod
    def validate_goal_type(cls, v):
        """验证目标类型"""
        valid_types = ["weight", "exercise", "diet", "habit"]
        if v not in valid_types:
            raise ValueError(f"目标类型必须是: {', '.join(valid_types)}")
        return v

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v):
        """验证单位"""
        valid_units = ["kg", "g", "步", "kcal", "ml", "小时", "次"]
        if v not in valid_units:
            raise ValueError(f"单位必须是: {', '.join(valid_units)}")
        return v


class GoalUpdate(BaseModel):
    """更新目标请求"""

    target_value: Optional[float] = Field(None, gt=0, description="目标值")
    target_date: Optional[datetime] = Field(None, description="目标日期")
    current_value: Optional[float] = Field(None, description="当前值")
    status: Optional[str] = Field(
        None, description="状态: active/paused/cancelled/completed"
    )


class GoalProgressCreate(BaseModel):
    """记录进度请求"""

    value: float = Field(..., description="进度值")
    daily_target_met: bool = Field(False, description="是否达成每日目标")
    recorded_date: Optional[datetime] = Field(None, description="记录日期")


# ==================== 响应 Schema ====================


class GoalProgressResponse(BaseModel):
    """进度响应"""

    progress_id: int = Field(..., description="进度ID")
    goal_id: int = Field(..., description="目标ID")
    recorded_date: datetime = Field(..., description="记录日期")
    value: float = Field(..., description="值")
    daily_target_met: bool = Field(..., description="是否达成每日目标")
    streak_count: int = Field(..., description="连续达成天数")

    class Config:
        from_attributes = True


class GoalResponse(BaseModel):
    """目标响应"""

    goal_id: int = Field(..., description="目标ID")
    user_id: int = Field(..., description="用户ID")
    goal_type: str = Field(..., description="目标类型")
    current_value: Optional[float] = Field(None, description="当前值")
    target_value: float = Field(..., description="目标值")
    unit: str = Field(..., description="单位")
    start_date: datetime = Field(..., description="开始日期")
    target_date: Optional[datetime] = Field(None, description="目标日期")
    predicted_date: Optional[datetime] = Field(None, description="预测完成日期")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 计算属性
    progress_percentage: Optional[float] = Field(None, description="完成百分比")

    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """目标列表响应 (简化版)"""

    goal_id: int = Field(..., description="目标ID")
    goal_type: str = Field(..., description="目标类型")
    current_value: Optional[float] = Field(None, description="当前值")
    target_value: float = Field(..., description="目标值")
    unit: str = Field(..., description="单位")
    status: str = Field(..., description="状态")
    predicted_date: Optional[datetime] = Field(None, description="预测完成日期")
    progress_percentage: float = Field(..., description="完成百分比")

    class Config:
        from_attributes = True


class GoalHistoryResponse(BaseModel):
    """目标历史响应"""

    history_id: int = Field(..., description="历史ID")
    goal_id: int = Field(..., description="目标ID")
    change_type: str = Field(..., description="变更类型")
    previous_state: Optional[Dict[str, Any]] = Field(None, description="变更前状态")
    new_state: Dict[str, Any] = Field(..., description="变更后状态")
    reason: Optional[str] = Field(None, description="变更原因")
    ai_suggested: bool = Field(..., description="是否AI建议")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
