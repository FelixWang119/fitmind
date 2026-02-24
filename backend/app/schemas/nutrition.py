from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CalorieTargets(BaseModel):
    """卡路里目标"""

    maintenance: float = Field(..., description="维持体重的卡路里")
    target: float = Field(..., description="目标卡路里")
    weight_loss: float = Field(..., description="减重卡路里")
    weight_gain: float = Field(..., description="增重卡路里")
    weight_difference: float = Field(..., description="体重差异(克)")


class Macronutrients(BaseModel):
    """宏量营养素"""

    protein_g: float = Field(..., description="蛋白质(克)")
    fat_g: float = Field(..., description="脂肪(克)")
    carb_g: float = Field(..., description="碳水化合物(克)")
    protein_percentage: float = Field(..., description="蛋白质占比(%)")
    fat_percentage: float = Field(..., description="脂肪占比(%)")
    carb_percentage: float = Field(..., description="碳水化合物占比(%)")


class MealSuggestion(BaseModel):
    """餐食建议"""

    meal_type: str = Field(..., description="餐食类型: breakfast, lunch, dinner, snack")
    name: str = Field(..., description="餐食名称")
    description: str = Field(..., description="餐食描述")
    calories: float = Field(..., description="卡路里")
    protein_g: float = Field(..., description="蛋白质(克)")
    fat_g: float = Field(..., description="脂肪(克)")
    carb_g: float = Field(..., description="碳水化合物(克)")


class NutritionRecommendation(BaseModel):
    """营养建议"""

    calorie_targets: CalorieTargets = Field(..., description="卡路里目标")
    macronutrients: Macronutrients = Field(..., description="宏量营养素目标")
    meal_suggestions: List[MealSuggestion] = Field(..., description="餐食建议")
    hydration_goal: float = Field(..., description="饮水目标(毫升)")
    supplement_recommendations: List[str] = Field(..., description="补充剂建议")
    user_weight: Optional[float] = Field(None, description="用户体重(kg)")
    user_height: Optional[int] = Field(None, description="用户身高(cm)")
    user_age: Optional[int] = Field(None, description="用户年龄")
    user_gender: Optional[str] = Field(None, description="用户性别")
    user_activity_level: Optional[str] = Field(None, description="用户活动水平")
    user_current_weight: Optional[float] = Field(None, description="用户当前体重(kg)")
    user_target_weight: Optional[float] = Field(None, description="用户目标体重(kg)")


class FoodItem(BaseModel):
    """食物项目"""

    name: str = Field(..., description="食物名称")
    meal_type: str = Field(..., description="餐食类型: breakfast, lunch, dinner, snack")
    calories: float = Field(..., description="卡路里")
    protein_g: float = Field(..., description="蛋白质(克)")
    fat_g: float = Field(..., description="脂肪(克)")
    carb_g: float = Field(..., description="碳水化合物(克)")
    serving_size: Optional[str] = Field(None, description="份量")
    timestamp: Optional[datetime] = Field(None, description="记录时间")


class NutritionTotal(BaseModel):
    """营养总计"""

    calories: float = Field(..., description="总卡路里")
    protein_g: float = Field(..., description="总蛋白质(克)")
    fat_g: float = Field(..., description="总脂肪(克)")
    carb_g: float = Field(..., description="总碳水化合物(克)")


class MealDistribution(BaseModel):
    """餐食分布"""

    breakfast: float = Field(..., description="早餐占比(%)")
    lunch: float = Field(..., description="午餐占比(%)")
    dinner: float = Field(..., description="晚餐占比(%)")
    snack: float = Field(..., description="加餐占比(%)")


class TargetComparison(BaseModel):
    """目标比较"""

    calories: Dict[str, float] = Field(..., description="卡路里比较")
    protein: Dict[str, float] = Field(..., description="蛋白质比较")
    fat: Dict[str, float] = Field(..., description="脂肪比较")
    carb: Dict[str, float] = Field(..., description="碳水化合物比较")


class FoodLogAnalysis(BaseModel):
    """食物日志分析"""

    total: NutritionTotal = Field(..., description="营养总计")
    meal_distribution: MealDistribution = Field(..., description="餐食分布")
    nutrition_score: int = Field(..., description="营养评分(0-100)")
    target_comparison: TargetComparison = Field(..., description="目标比较")


class BMRCalculation(BaseModel):
    """基础代谢率计算"""

    bmr: float = Field(..., description="基础代谢率(卡路里)")
    tdee: float = Field(..., description="每日总能量消耗(卡路里)")
    activity_level: str = Field(..., description="活动水平")
    calculation_method: str = Field(default="Mifflin-St Jeor", description="计算方法")
