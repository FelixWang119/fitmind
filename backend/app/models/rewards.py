from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Reward(Base):
    """奖励商品模型"""

    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)

    # 商品基本信息
    name = Column(String(200), nullable=False, index=True)  # 奖品名称
    description = Column(Text)  # 奖品描述
    category = Column(
        String(100), nullable=False
    )  # 类别: digital, physical, subscription等
    image_url = Column(String(500))  # 图片链接

    # 价格和库存
    cost_points = Column(Integer, nullable=False)  # 兑换所需积分
    inventory_quantity = Column(Integer)  # 库存数量，None表示无限
    min_points_threshold = Column(Integer, default=0)  # 最低积分限制

    # 条件和限制
    is_available = Column(Boolean, default=True)  # 是否可用
    is_on_sale = Column(Boolean, default=False)  # 是否促销
    sale_discount = Column(Float, default=1.0)  # 折扣 0.8 = 80%价格
    max_redemptions = Column(Integer)  # 最大兑换数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    available_until = Column(DateTime(timezone=True))  # 有效期截止

    # 关系
    # reward_redemptions = relationship("RewardRedemption", back_populates="reward")

    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', points={self.cost_points})>"

    @property
    def discounted_cost(self) -> int:
        """返回折扣后的成本"""
        if self.is_on_sale:
            return int(self.cost_points * self.sale_discount)
        return self.cost_points

    @property
    def is_out_of_stock(self) -> bool:
        """判断是否缺货"""
        return self.inventory_quantity is not None and self.inventory_quantity <= 0


class RewardRedemption(Base):
    """奖励兑换记录模型"""

    __tablename__ = "reward_redemptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reward_id = Column(
        Integer, ForeignKey("rewards.id", ondelete="CASCADE"), nullable=False
    )

    # 兑换信息
    redemption_point_cost = Column(Integer, nullable=False)  # 实际兑换点数
    status = Column(
        String(20), default="pending"
    )  # pending, completed, shipped, cancelled

    # 收货人信息及发货状态
    recipient_name = Column(String(100))  # 收货人姓名
    shipping_address = Column(Text)  # 收货地址
    phone_number = Column(String(20))  # 电话
    tracking_number = Column(String(100))  # 物流单号

    # 处理日志
    notes_internal = Column(Text)  # 内部备注

    # 时间戳
    redemption_datetime = Column(DateTime(timezone=True), nullable=False)
    completed_datetime = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="reward_redemptions")
    reward = relationship(
        "Reward"
    )  # Not adding reverse relation to avoid circular import

    def __repr__(self):
        return f"<RewardRedemption(id={self.id}, user_id={self.user_id}, reward_id={self.reward_id})>"
