from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RewardBase(BaseModel):
    """奖励商品基类"""

    name: str = Field(..., max_length=200, description="奖品名称")
    description: Optional[str] = Field(None, description="奖品描述")
    category: str = Field(
        ..., max_length=100, description="类别: digital, physical, subscription等"
    )
    image_url: Optional[str] = Field(None, description="图片链接")
    cost_points: int = Field(..., ge=0, description="兑换所需积分")
    inventory_quantity: Optional[int] = Field(
        None, ge=0, description="库存数量，None表示无限"
    )
    min_points_threshold: int = Field(0, ge=0, description="最低积分限制")
    is_available: bool = Field(True, description="是否可用")
    is_on_sale: bool = Field(False, description="是否促销")
    sale_discount: float = Field(1.0, ge=0.0, le=1.0, description="折扣 0.8 = 80%价格")
    max_redemptions: Optional[int] = Field(None, ge=0, description="最大兑换数")
    available_until: Optional[datetime] = Field(None, description="有效期截止")


class RewardCreate(RewardBase):
    """创建奖励商品"""

    pass


class RewardUpdate(BaseModel):
    """更新奖励商品"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None)
    cost_points: Optional[int] = Field(None, ge=0)
    inventory_quantity: Optional[int] = Field(None, ge=0)
    min_points_threshold: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = Field(None)
    is_on_sale: Optional[bool] = Field(None)
    sale_discount: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_redemptions: Optional[int] = Field(None, ge=0)
    available_until: Optional[datetime] = Field(None)


class RewardInDB(RewardBase):
    """数据库奖励商品"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RewardRedemptionBase(BaseModel):
    """奖励兑换基类"""

    reward_id: int = Field(..., description="奖励ID")
    redemption_point_cost: int = Field(..., ge=0, description="实际兑换点数")
    recipient_name: Optional[str] = Field(
        None, max_length=100, description="收货人姓名"
    )
    shipping_address: Optional[str] = Field(None, description="收货地址")
    phone_number: Optional[str] = Field(None, max_length=20, description="电话")
    tracking_number: Optional[str] = Field(None, max_length=100, description="物流单号")
    notes_internal: Optional[str] = Field(None, description="内部备注")


class RewardRedemptionCreate(RewardRedemptionBase):
    """创建奖励兑换记录"""

    reward_id: int
    shipping_address: Optional[str] = Field(None, description="收货地址(物理奖品需要)")
    recipient_name: Optional[str] = Field(
        None, max_length=100, description="收货人姓名(物理奖品需要)"
    )
    phone_number: Optional[str] = Field(
        None, max_length=20, description="联系电话(物理奖品需要)"
    )


class RewardRedemptionUpdate(BaseModel):
    """更新奖励兑换状态"""

    status: Optional[str] = Field(
        None, description="状态: pending, completed, shipped, cancelled"
    )
    tracking_number: Optional[str] = Field(None, max_length=100, description="物流单号")
    notes_internal: Optional[str] = Field(None, description="内部备注")


class RewardRedemptionInDB(RewardRedemptionBase):
    """数据库奖励兑换记录"""

    id: int
    user_id: int
    status: str  # pending, completed, shipped, cancelled
    redemption_datetime: datetime
    completed_datetime: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RewardShopItem(BaseModel):
    """奖励商城商品"""

    reward: RewardInDB = Field(..., description="奖励商品信息")
    availability_info: dict = Field(..., description="可用性信息")


class RedemptionRequest(BaseModel):
    """兑换请求"""

    reward_id: int = Field(..., description="要兑换的商品ID")
    recipient_name: Optional[str] = Field(None, description="收货人姓名(物理商品必需)")
    shipping_address: Optional[str] = Field(
        None, description="shipping addresses(物理商品必需)"
    )
    phone_number: Optional[str] = Field(None, description="联系电话(物理商品必需)")


class RedemptionResponse(BaseModel):
    """兑换响应"""

    success: bool = Field(..., description="是否成功")
    redemption_record: Optional[RewardRedemptionInDB] = Field(
        None, description="兑换记录"
    )
    message: str = Field(..., description="响应消息")
    remaining_points: Optional[int] = Field(None, description="剩余积分")


class RewardCatalog(BaseModel):
    """奖励目录"""

    items: List[RewardInDB] = Field(..., description="奖品列表")
    filtered_count: int = Field(..., description="筛选后数量")
    total_count: int = Field(..., description="总数量")
