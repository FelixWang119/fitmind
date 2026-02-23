from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MealItemBase(BaseModel):
    name: str = Field(..., description="食物名称")
    serving_size: Optional[float] = Field(None, description="份量大小")
    serving_unit: Optional[str] = Field(None, description="份量单位")
    quantity: Optional[float] = Field(None, description="数量")
    notes: Optional[str] = Field(None, description="备注")
    calories_per_serving: Optional[float] = Field(None, description="每份热量")
    protein_per_serving: Optional[float] = Field(None, description="每份蛋白质(g)")
    carbs_per_serving: Optional[float] = Field(None, description="每份碳水化合物(g)")
    fat_per_serving: Optional[float] = Field(None, description="每份脂肪(g)")


class MealItemCreate(MealItemBase):
    """创建餐品项"""

    pass


class MealItemUpdate(BaseModel):
    """更新餐品项"""

    name: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    quantity: Optional[float] = None
    notes: Optional[str] = None
    calories_per_serving: Optional[float] = None
    protein_per_serving: Optional[int] = None
    carbs_per_serving: Optional[int] = None
    fat_per_serving: Optional[int] = None


class MealItem(MealItemBase):
    """餐品项目"""

    id: int
    meal_id: int
    food_item_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MealBase(BaseModel):
    meal_type: str = Field(..., description="餐饮类型: breakfast, lunch, dinner, snack")
    name: str = Field(..., max_length=200, description="餐饮名称")
    notes: Optional[str] = Field(None, description="备注")
    meal_datetime: datetime = Field(..., description="餐饮时间")


class MealCreate(MealBase):
    """创建餐饮"""

    items: List[MealItemCreate] = Field([], description="包含的餐品项列表")


class MealUpdate(BaseModel):
    """更新餐饮"""

    meal_type: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    meal_datetime: Optional[datetime] = None
    notes: Optional[str] = None


class Meal(MealBase):
    """餐饮"""

    id: int
    user_id: int
    calories: Optional[int] = Field(None, description="总热量")
    protein: Optional[int] = Field(None, description="总蛋白质(g)")
    carbs: Optional[int] = Field(None, description="总碳水化合物(g)")
    fat: Optional[int] = Field(None, description="总脂肪(g)")
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[MealItem] = []

    class Config:
        from_attributes = True


class FoodItemBase(BaseModel):
    name: str = Field(..., max_length=200, description="食物名称")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    serving_size: float = Field(..., gt=0, description="标准份量")
    serving_unit: str = Field(..., max_length=50, description="份量单位")
    calories_per_serving: float = Field(..., ge=0, description="每份热量")
    protein_per_serving: Optional[int] = Field(None, ge=0, description="每份蛋白质(g)")
    carbs_per_serving: Optional[int] = Field(
        None, ge=0, description="每份碳水化合物(g)"
    )
    fat_per_serving: Optional[int] = Field(None, ge=0, description="每份脂肪(g)")
    fiber_per_serving: Optional[int] = Field(None, ge=0, description="每份纤维(g)")
    sugar_per_serving: Optional[int] = Field(None, ge=0, description="每份糖(g)")
    sodium_per_serving: Optional[int] = Field(None, ge=0, description="每份钠(mg)")
    description: Optional[str] = Field(None, description="描述信息")
    tags: Optional[str] = Field(None, description="标签")  # JSON format


class FoodItemCreate(FoodItemBase):
    """创建食物项"""

    pass


class FoodItemUpdate(BaseModel):
    """更新食物项"""

    name: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    brand: Optional[str] = Field(None)
    serving_size: Optional[float] = Field(None)
    serving_unit: Optional[str] = Field(None)
    calories_per_serving: Optional[float] = Field(None)
    protein_per_serving: Optional[int] = Field(None)
    carbs_per_serving: Optional[int] = Field(None)
    fat_per_serving: Optional[int] = Field(None)
    fiber_per_serving: Optional[int] = Field(None)
    sugar_per_serving: Optional[int] = Field(None)
    sodium_per_serving: Optional[int] = Field(None)
    description: Optional[str] = Field(None)
    tags: Optional[str] = Field(None)


class FoodItem(FoodItemBase):
    """食物项"""

    id: int
    is_custom: bool = Field(False, description="是否自定义食物")
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = Field(None, description="创建用户ID")

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    """日常营养摘要"""

    date: str
    total_calories: int
    total_protein: int
    total_carbs: int
    total_fat: int
    meal_count: int
    meals: List[Meal]


class AIRequest(BaseModel):
    """AI请求"""

    message: str = Field(..., description="用户消息")
    conversation_id: Optional[int] = Field(None, description="对话ID")
    context: Optional[dict] = Field(None, description="上下文信息")


class AIResponse(BaseModel):
    """AI响应"""

    response: str = Field(..., description="AI回复内容")
    model: str = Field("qwen", description="AI模型名称")
    conversation_id: int = Field(..., description="对话ID")
    conversation_title: Optional[str] = Field(None, description="对话标题")
