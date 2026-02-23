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


class Meal(Base):
    """餐饮记录模型"""

    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 餐饮基本信息
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    name = Column(String(200), nullable=False)  # 餐名，如"早餐"、"午餐"等
    notes = Column(Text)  # 餐饮备注
    photo_url = Column(String(500), nullable=True)  # 照片URL

    # 营养信息
    calories = Column(Integer)  # 总卡路里
    protein = Column(Integer)  # 蛋白质(g)
    carbs = Column(Integer)  # 碳水化合物(g)
    fat = Column(Integer)  # 脂肪(g)
    fiber = Column(Integer)  # 纤维(g)
    sugar = Column(Integer)  # 糖(g)
    sodium = Column(Integer)  # 钠(mg)

    # 时间信息
    meal_datetime = Column(DateTime(timezone=True), nullable=False)  # 用餐时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="meals")
    meal_items = relationship(
        "MealItem", back_populates="meal", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Meal(id={self.id}, user_id={self.user_id}, type={self.meal_type}, datetime={self.meal_datetime})>"


class MealItem(Base):
    """餐品项目模型"""

    __tablename__ = "meal_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(
        Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    food_item_id = Column(Integer, ForeignKey("food_items.id"))  # 外键可能是食物库

    # 食物信息
    name = Column(String(200), nullable=False)  # 食物名称
    serving_size = Column(Float)  # 份量
    serving_unit = Column(String(50))  # 份量单位（g, ml, cup等）
    quantity = Column(Float)  # 数量
    notes = Column(Text)  # 特殊说明

    # 营养成分（每份）
    calories_per_serving = Column(Float)  # 每份卡路里
    protein_per_serving = Column(Integer)  # 每份蛋白质(g)
    carbs_per_serving = Column(Integer)  # 每份碳水化合物(g)
    fat_per_serving = Column(Integer)  # 每份脂肪(g)

    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    meal = relationship("Meal", back_populates="meal_items")
    food_item = relationship("FoodItem", back_populates="meal_items")

    def __repr__(self):
        return f"<MealItem(id={self.id}, meal_id={self.meal_id}, name={self.name})>"


class FoodItem(Base):
    """食物项目模型（预设食物库）"""

    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    name = Column(String(200), nullable=False, unique=True)  # 食物名称
    category = Column(String(100))  # 分类（如：蔬菜、肉类、乳制品等）
    brand = Column(String(100))  # 品牌
    is_custom = Column(Boolean, default=False)  # 是否为用户自定义食物

    # 营养成分（每份）
    serving_size = Column(Float, nullable=False)  # 标准份量
    serving_unit = Column(String(50), nullable=False)  # 份量单位
    calories_per_serving = Column(Float, nullable=False)  # 每份卡路里
    protein_per_serving = Column(Integer)  # 每份蛋白质(g)
    carbs_per_serving = Column(Integer)  # 每份碳水化合物(g)
    fat_per_serving = Column(Integer)  # 每份脂肪(g)
    fiber_per_serving = Column(Integer)  # 每份纤维(g)
    sugar_per_serving = Column(Integer)  # 每份糖(g)
    sodium_per_serving = Column(Integer)  # 每份钠(mg)

    # 描述
    description = Column(Text)

    # 营养密度（每100g的营养成分）
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)

    # 标签
    tags = Column(Text)  # JSON格式：如健康标签、适用人群等

    # 创建/更新时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))  # 如果是用户提交的食物

    # 关系
    meal_items = relationship("MealItem", back_populates="food_item")
    creator = relationship("User")

    def __repr__(self):
        return f"<FoodItem(id={self.id}, name={self.name}, is_custom={self.is_custom})>"


class WaterIntake(Base):
    """饮水记录模型"""

    __tablename__ = "water_intakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 饮水量
    amount_ml = Column(Integer, nullable=False)  # 毫升数

    # 时间信息
    intake_datetime = Column(DateTime(timezone=True), nullable=False)  # 饮水时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="water_intakes")

    def __repr__(self):
        return f"<WaterIntake(id={self.id}, user_id={self.user_id}, amount={self.amount_ml}ml)>"
