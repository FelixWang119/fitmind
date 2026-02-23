from datetime import date
from sqlalchemy import Column, DateTime, Date, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CalorieGoal(Base):
    """每日热量目标模型"""

    __tablename__ = "calorie_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 日期
    goal_date = Column(Date, nullable=False, index=True)

    # 目标营养素（单位：克/g 或 千卡/kcal）
    target_calories = Column(Integer, nullable=False, default=2000)  # 目标热量
    target_protein = Column(Integer, default=50)  # 蛋白质(g)
    target_carbs = Column(Integer, default=250)  # 碳水化合物(g)
    target_fat = Column(Integer, default=65)  # 脂肪(g)

    # 是否自动计算
    is_auto_calculated = Column(Boolean, default=True)

    # 创建/更新时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="calorie_goals")

    # 复合唯一索引：同一用户同一天只有一个目标
    __table_args__ = ({"sqlite_autoincrement": True},)

    def __repr__(self):
        return f"<CalorieGoal(id={self.id}, user_id={self.user_id}, date={self.goal_date}, calories={self.target_calories})>"
