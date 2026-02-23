from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class HealthRecordBase(BaseModel):
    """健康记录基础模式"""

    # 体重相关
    weight: Optional[int] = Field(None, ge=20000, le=300000, description="体重（克）")
    body_fat_percentage: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="体脂百分比"
    )
    muscle_mass: Optional[int] = Field(None, ge=0, description="肌肉量（克）")

    # 血糖相关
    blood_sugar: Optional[float] = Field(
        None, ge=0.0, le=50.0, description="血糖值（mmol/L）"
    )
    blood_sugar_type: Optional[str] = Field(
        None, description="血糖类型：fasting, postprandial, random"
    )

    # 血压相关
    systolic_pressure: Optional[int] = Field(None, ge=50, le=300, description="收缩压")
    diastolic_pressure: Optional[int] = Field(None, ge=30, le=200, description="舒张压")

    # 其他指标
    heart_rate: Optional[int] = Field(None, ge=30, le=250, description="心率")
    sleep_hours: Optional[float] = Field(None, ge=0.0, le=24.0, description="睡眠时长")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="压力等级 1-10")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="能量等级 1-10")

    # 饮食记录
    calories_intake: Optional[int] = Field(None, ge=0, description="卡路里摄入")
    protein_intake: Optional[int] = Field(None, ge=0, description="蛋白质摄入（克）")
    carbs_intake: Optional[int] = Field(None, ge=0, description="碳水化合物摄入（克）")
    fat_intake: Optional[int] = Field(None, ge=0, description="脂肪摄入（克）")

    # 运动记录
    exercise_minutes: Optional[int] = Field(None, ge=0, description="运动分钟数")
    exercise_type: Optional[str] = Field(None, description="运动类型")
    steps_count: Optional[int] = Field(None, ge=0, description="步数")

    # 备注
    notes: Optional[str] = None

    # 记录时间
    record_date: datetime

    @validator("blood_sugar_type")
    def validate_blood_sugar_type(cls, v):
        if v and v not in ["fasting", "postprandial", "random"]:
            raise ValueError(
                "blood_sugar_type must be one of: fasting, postprandial, random"
            )
        return v


class HealthRecordCreate(HealthRecordBase):
    """创建健康记录"""

    pass


class HealthRecordUpdate(BaseModel):
    """更新健康记录"""

    weight: Optional[int] = Field(None, ge=20000, le=300000)
    body_fat_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    muscle_mass: Optional[int] = Field(None, ge=0)
    blood_sugar: Optional[float] = Field(None, ge=0.0, le=50.0)
    blood_sugar_type: Optional[str] = None
    systolic_pressure: Optional[int] = Field(None, ge=50, le=300)
    diastolic_pressure: Optional[int] = Field(None, ge=30, le=200)
    heart_rate: Optional[int] = Field(None, ge=30, le=250)
    sleep_hours: Optional[float] = Field(None, ge=0.0, le=24.0)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    calories_intake: Optional[int] = Field(None, ge=0)
    protein_intake: Optional[int] = Field(None, ge=0)
    carbs_intake: Optional[int] = Field(None, ge=0)
    fat_intake: Optional[int] = Field(None, ge=0)
    exercise_minutes: Optional[int] = Field(None, ge=0)
    exercise_type: Optional[str] = None
    steps_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class HealthRecord(HealthRecordBase):
    """健康记录响应"""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HealthRecordList(BaseModel):
    """健康记录列表"""

    records: List[HealthRecord]
    total: int
    skip: int
    limit: int


class HealthSummary(BaseModel):
    """健康数据摘要"""

    total_records: int
    date_range: dict
    averages: dict
    trends: dict


class DailyGoal(BaseModel):
    """每日目标"""

    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None
    exercise_minutes: Optional[int] = None
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    water_intake: Optional[float] = None  # 升
