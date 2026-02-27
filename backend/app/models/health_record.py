from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HealthRecord(Base):
    """健康记录模型"""

    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 体重相关
    weight = Column(Integer)  # 克
    height = Column(Integer)  # 厘米
    body_fat_percentage = Column(Float)  # 体脂百分比
    muscle_mass = Column(Integer)  # 肌肉量（克）

    # 血糖相关
    blood_sugar = Column(Float)  # 血糖值（mmol/L）
    blood_sugar_type = Column(String(20))  # fasting, postprandial, random

    # 血压相关
    systolic_pressure = Column(Integer)  # 收缩压
    diastolic_pressure = Column(Integer)  # 舒张压

    # 其他指标
    heart_rate = Column(Integer)  # 心率
    sleep_hours = Column(Float)  # 睡眠时长
    stress_level = Column(Integer)  # 压力等级 1-10
    energy_level = Column(Integer)  # 能量等级 1-10

    # 饮食记录
    calories_intake = Column(Integer)  # 卡路里摄入
    protein_intake = Column(Integer)  # 蛋白质摄入（克）
    carbs_intake = Column(Integer)  # 碳水化合物摄入（克）
    fat_intake = Column(Integer)  # 脂肪摄入（克）

    # 运动记录
    exercise_minutes = Column(Integer)  # 运动分钟数
    exercise_type = Column(String(100))  # 运动类型
    steps_count = Column(Integer)  # 步数

    # 备注
    notes = Column(Text)

    # 记录时间
    record_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="health_records")

    def __repr__(self):
        return f"<HealthRecord(id={self.id}, user_id={self.user_id}, date={self.record_date})>"
