from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class CalorieGoalBase(BaseModel):
    """热量目标基础 Schema"""

    goal_date: date = Field(..., description="目标日期")
    target_calories: int = Field(default=2000, ge=0, description="目标热量 (kcal)")
    target_protein: Optional[int] = Field(
        default=50, ge=0, description="蛋白质目标 (g)"
    )
    target_carbs: Optional[int] = Field(
        default=250, ge=0, description="碳水化合物目标 (g)"
    )
    target_fat: Optional[int] = Field(default=65, ge=0, description="脂肪目标 (g)")
    is_auto_calculated: bool = Field(default=True, description="是否自动计算")


class CalorieGoalCreate(CalorieGoalBase):
    """创建热量目标 Schema"""

    pass


class CalorieGoalUpdate(BaseModel):
    """更新热量目标 Schema"""

    target_calories: Optional[int] = Field(None, ge=0)
    target_protein: Optional[int] = Field(None, ge=0)
    target_carbs: Optional[int] = Field(None, ge=0)
    target_fat: Optional[int] = Field(None, ge=0)
    is_auto_calculated: Optional[bool] = None


class CalorieGoalResponse(CalorieGoalBase):
    """热量目标响应 Schema"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
