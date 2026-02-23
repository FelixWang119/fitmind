from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.gamification import UserPoints, PointsTransaction
from app.models.rewards import (
    Reward as RewardModel,
    RewardRedemption as RewardRedemptionModel,
)
from app.schemas.reward import (
    RewardCreate,
    RewardInDB,
    RewardUpdate,
    RewardRedemptionCreate,
    RewardRedemptionInDB,
    RewardRedemptionUpdate,
    RewardShopItem,
    RedemptionRequest,
    RedemptionResponse,
    RewardCatalog,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/rewards", response_model=List[RewardInDB])
async def get_rewards(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = Query(None, description="商品类别过滤"),
    is_available: Optional[bool] = Query(None, description="是否可用过滤"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励商品列表"""
    query = db.query(RewardModel).filter(
        RewardModel.is_available == True
    )  # Only available rewards

    # Apply filters
    if category:
        query = query.filter(RewardModel.category == category)
    if is_available is not None:
        query = query.filter(RewardModel.is_available == is_available)

    # Handle pagination
    rewards = query.offset(skip).limit(limit).all()

    logger.info(
        "Fetched rewards",
        user_id=current_user.id,
        count=len(rewards),
        category=category,
    )

    return rewards


@router.get("/rewards/catalog", response_model=RewardCatalog)
async def get_reward_catalog(
    category: Optional[str] = Query(None, description="商品类别过滤"),
    is_on_sale: Optional[bool] = Query(None, description="是否仅显示促销商品"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励商城目录带可用性信息"""
    query = db.query(RewardModel)

    # Apply filters
    if category:
        query = query.filter(RewardModel.category == category)

    if is_on_sale is not None:
        query = query.filter(RewardModel.is_on_sale == is_on_sale)

    # Exclude unavailable items with no inventory
    query = query.filter(
        (RewardModel.is_available == True)
        & (
            (RewardModel.inventory_quantity == None)
            | (RewardModel.inventory_quantity > 0)
        )
    )

    all_rewards = query.all()
    total_count = len(all_rewards)

    catalog_items = []
    available_count = 0

    for reward in all_rewards:
        availability_info = {
            "is_available": reward.is_available,
            "is_out_of_stock": reward.inventory_quantity is not None
            and reward.inventory_quantity <= 0,
            "current_inventory": reward.inventory_quantity,
            "max_redemptions_left": reward.max_redemptions,
            "discounted_price": reward.discounted_cost
            if reward.is_on_sale
            else reward.cost_points,
        }

        catalog_items.append({"reward": reward, "availability_info": availability_info})

    return {
        "items": catalog_items,
        "filtered_count": len(catalog_items),
        "total_count": total_count,
    }


@router.post("/rewards", response_model=RewardInDB)
async def create_reward(
    reward_create: RewardCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建奖励商品（需要管理权限）"""
    # 检查管理权限 (简化为检查普通用户，可在生产环境中增强)
    if (
        current_user.id != 1 and not current_user.is_superuser
    ):  # Only super admin can create rewards
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create rewards",
        )

    reward = RewardModel(
        name=reward_create.name,
        description=reward_create.description,
        category=reward_create.category,
        image_url=reward_create.image_url,
        cost_points=reward_create.cost_points,
        inventory_quantity=reward_create.inventory_quantity,
        min_points_threshold=reward_create.min_points_threshold,
        is_available=reward_create.is_available,
        is_on_sale=reward_create.is_on_sale,
        sale_discount=reward_create.sale_discount,
        max_redemptions=reward_create.max_redemptions,
        available_until=reward_create.available_until,
    )

    db.add(reward)
    db.commit()
    db.refresh(reward)

    logger.info("Reward created", user_id=current_user.id, reward_id=reward.id)

    return reward


@router.put("/rewards/{reward_id}", response_model=RewardInDB)
async def update_reward(
    reward_id: int,
    reward_update: RewardUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新奖励商品信息（需要管理权限）"""
    # Check admin permissions
    if current_user.id != 1 and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update rewards",
        )

    reward = db.query(RewardModel).filter(RewardModel.id == reward_id).first()

    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found"
        )

    # Update fields
    update_data = reward_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(reward, field, value)

    db.commit()
    db.refresh(reward)

    logger.info("Reward updated", user_id=current_user.id, reward_id=reward_id)

    return reward


@router.get("/rewards/{reward_id}", response_model=RewardInDB)
async def get_reward(
    reward_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取奖励商品详情"""
    reward = (
        db.query(RewardModel)
        .filter(RewardModel.id == reward_id, RewardModel.is_available == True)
        .first()
    )

    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found or no longer available",
        )

    logger.info("Reward retrieved", user_id=current_user.id, reward_id=reward_id)

    return reward


@router.get("/rewards/{reward_id}/availability", response_model=dict)
async def check_availability(
    reward_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """检查奖励商品可用性"""
    reward = db.query(RewardModel).filter(RewardModel.id == reward_id).first()

    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found"
        )

    # Get user's points to check if sufficient
    user_points_record = (
        db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
    )

    has_enough_points = (
        user_points_record and user_points_record.current_points >= reward.cost_points
    )

    availability_info = {
        "is_available": reward.is_available,
        "has_enough_points": has_enough_points,
        "cost_points": reward.discounted_cost
        if reward.is_on_sale
        else reward.cost_points,
        "inventory_count": reward.inventory_quantity,
        "is_out_of_stock": reward.inventory_quantity is not None
        and reward.inventory_quantity <= 0,
        "can_user_purchase": (
            reward.is_available
            and (reward.inventory_quantity is None or reward.inventory_quantity > 0)
            and has_enough_points
        ),
        "user_current_points": user_points_record.current_points
        if user_points_record
        else 0,
    }

    logger.info(
        "Availability checked",
        user_id=current_user.id,
        reward_id=reward_id,
        available=availability_info["can_user_purchase"],
    )

    return availability_info


@router.post("/rewards/{reward_id}/redeem", response_model=RedemptionResponse)
async def redeem_reward(
    reward_id: int,
    redemption_request: RedemptionRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """兑换奖励"""
    # 找到奖励项目
    reward = (
        db.query(RewardModel)
        .filter(RewardModel.id == reward_id, RewardModel.is_available == True)
        .first()
    )

    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found"
        )

    # Check stock and thresholds
    if reward.inventory_quantity is not None and reward.inventory_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Reward is out of stock"
        )

    # Get user points
    user_points_record = (
        db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
    )

    if not user_points_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User points record not found",
        )

    # Check if user has sufficient points
    cost = reward.discounted_cost if reward.is_on_sale else reward.cost_points
    if user_points_record.current_points < cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient points. Cost: {cost}, Available: {user_points_record.current_points}",
        )

    # Check if reward has exceeded max redemptions
    if reward.max_redemptions is not None:
        redemption_count = (
            db.query(RewardRedemptionModel)
            .filter(RewardRedemptionModel.reward_id == reward_id)
            .count()
        )

        if redemption_count >= reward.max_redemptions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This reward has reached maximum redemption limit",
            )

    # Perform the redemption
    try:
        # Start transaction
        db.begin_nested()

        # Create redemption record
        redemption = RewardRedemptionModel(
            user_id=current_user.id,
            reward_id=reward_id,
            redemption_point_cost=cost,
            redemption_datetime=datetime.utcnow(),
            status="pending",  # Initial status, will be updated based on reward type
            recipient_name=redemption_request.recipient_name,
            shipping_address=redemption_request.shipping_address,
            phone_number=redemption_request.phone_number,
        )

        db.add(redemption)

        # Deduct points
        user_points_record.current_points -= cost
        user_points_record.total_points -= cost

        # Record transaction
        transaction = PointsTransaction(
            user_id=current_user.id,
            points_amount=-cost,  # Negative for deduction
            transaction_type="reward_redemption",
            description=f"Redeemed '{reward.name}' reward",
            reference_id=redemption.id,
            reference_type="RewardRedemption",
        )
        db.add(transaction)

        # Update inventory if applicable
        if reward.inventory_quantity is not None:
            reward.inventory_quantity -= 1

        # For digital rewards, update status immediately
        if reward.category == "digital":
            redemption.status = "completed"
            redemption.completed_datetime = datetime.utcnow()

        db.commit()

        logger.info(
            "Reward redeemed successfully",
            user_id=current_user.id,
            reward_id=reward_id,
            redemption_id=redemption.id,
        )

        # Get updated user points
        updated_points_record = (
            db.query(UserPoints).filter(UserPoints.user_id == current_user.id).first()
        )

        return RedemptionResponse(
            success=True,
            redemption_record=redemption,
            message=f"成功兑换'{reward.name}'! 已扣除{cost}积分。",
            remaining_points=updated_points_record.current_points
            if updated_points_record
            else 0,
        )

    except Exception as e:
        db.rollback()
        logger.error(
            "Reward redemption failed",
            user_id=current_user.id,
            reward_id=reward_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reward redemption failed, please try again",
        )


@router.get("/rewards/redemptions", response_model=List[RewardRedemptionInDB])
async def get_user_redemptions(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = Query(
        None, description="状态过滤: pending, completed, shipped, cancelled"
    ),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户的兑换记录"""
    query = db.query(RewardRedemptionModel).filter(
        RewardRedemptionModel.user_id == current_user.id
    )

    if status_filter:
        query = query.filter(RewardRedemptionModel.status == status_filter)

    redemptions = (
        query.order_by(RewardRedemptionModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info(
        "User redemptions fetched",
        user_id=current_user.id,
        count=len(redemptions),
        status_filter=status_filter,
    )

    return redemptions


@router.put("/rewards/redemptions/{redemption_id}", response_model=RewardRedemptionInDB)
async def update_redemption_status(
    redemption_id: int,
    status_update: RewardRedemptionUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新兑换状态（如发货、完成等）"""
    # Check admin permissions
    if current_user.id != 1 and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    redemption = (
        db.query(RewardRedemptionModel)
        .filter(RewardRedemptionModel.id == redemption_id)
        .first()
    )

    if not redemption:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Redemption record not found"
        )

    # Update allowed fields
    if status_update.status is not None:
        redemption.status = status_update.status
    if status_update.tracking_number is not None:
        redemption.tracking_number = status_update.tracking_number
    if status_update.notes_internal is not None:
        redemption.notes_internal = status_update.notes_internal

    if redemption.status == "completed" and redemption.completed_datetime is None:
        redemption.completed_datetime = datetime.utcnow()

    db.commit()
    db.refresh(redemption)

    logger.info(
        "Redemption status updated",
        user_id=current_user.id,
        redemption_id=redemption_id,
        new_status=status_update.status,
    )

    return redemption
