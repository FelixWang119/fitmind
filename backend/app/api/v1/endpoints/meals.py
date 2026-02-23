from datetime import datetime, date, timedelta
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.nutrition import Meal, MealItem, FoodItem
from app.models.user import User as UserModel
from app.schemas.meal_models import (
    Meal as MealSchema,
    MealCreate,
    MealUpdate,
    MealItem as MealItemSchema,
    MealItemCreate,
    MealItemUpdate,
    FoodItem as FoodItemSchema,
    FoodItemCreate,
    FoodItemUpdate,
    DailyNutritionSummary,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/meals", response_model=List[MealSchema])
async def get_meals(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户的餐食记录列表"""
    query = db.query(Meal).filter(Meal.user_id == current_user.id)

    # 日期过滤
    if start_date:
        query = query.filter(Meal.meal_datetime >= start_date)
    if end_date:
        query = query.filter(Meal.meal_datetime <= end_date)

    # 获取记录
    meals = query.order_by(Meal.meal_datetime.desc()).offset(skip).limit(limit).all()

    return meals


@router.get("/meals/{meal_id}", response_model=MealSchema)
async def get_meal(
    meal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定的餐食记录"""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    return meal


@router.post("/meals", response_model=MealSchema, status_code=status.HTTP_201_CREATED)
async def create_meal(
    meal_data: MealCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建餐食记录"""
    # 计算总营养值
    total_calories = 0
    total_proteins = 0
    total_carbs = 0
    total_fat = 0

    for item in meal_data.items:
        if item.calories_per_serving:
            if item.quantity:
                total_calories += item.calories_per_serving * item.quantity
            else:
                total_calories += item.calories_per_serving
        if item.protein_per_serving:
            if item.quantity:
                total_proteins += item.protein_per_serving * item.quantity
            else:
                total_proteins += item.protein_per_serving
        if item.carbs_per_serving:
            if item.quantity:
                total_carbs += item.carbs_per_serving * item.quantity
            else:
                total_carbs += item.carbs_per_serving
        if item.fat_per_serving:
            if item.quantity:
                total_fat += item.fat_per_serving * item.quantity
            else:
                total_fat += item.fat_per_serving

    meal = Meal(
        user_id=current_user.id,
        meal_type=meal_data.meal_type,
        name=meal_data.name,
        meal_datetime=meal_data.meal_datetime,
        notes=meal_data.notes,
        calories=total_calories,
        protein=total_proteins,
        carbs=total_carbs,
        fat=total_fat,
    )

    db.add(meal)
    db.commit()
    db.refresh(meal)

    # 如果提供餐品项目，一并创建
    if meal_data.items:
        for item_data in meal_data.items:
            meal_item = MealItem(
                meal_id=meal.id,
                name=item_data.name,
                serving_size=item_data.serving_size,
                serving_unit=item_data.serving_unit,
                quantity=item_data.quantity,
                notes=item_data.notes,
                calories_per_serving=item_data.calories_per_serving,
                protein_per_serving=item_data.protein_per_serving,
                carbs_per_serving=item_data.carbs_per_serving,
                fat_per_serving=item_data.fat_per_serving,
            )
            db.add(meal_item)

    db.commit()
    db.refresh(meal)

    logger.info("Meal created", meal_id=meal.id, user_id=current_user.id)

    return meal


@router.put("/meals/{meal_id}", response_model=MealSchema)
async def update_meal(
    meal_id: int,
    meal_update: MealUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新餐食记录"""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    # 更新字段
    update_data = meal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)

    db.commit()
    db.refresh(meal)

    logger.info("Meal updated", meal_id=meal.id, user_id=current_user.id)

    return meal


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(
    meal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除餐食记录"""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    # 删除相关的餐品项目
    for item in meal.meal_items:
        db.delete(item)

    db.delete(meal)
    db.commit()

    logger.info("Meal deleted", meal_id=meal_id, user_id=current_user.id)


@router.get("/meals/{meal_id}/items", response_model=List[MealItemSchema])
async def get_meal_items(
    meal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定餐食的餐品项目"""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    return meal.meal_items


@router.post(
    "/meals/{meal_id}/items",
    response_model=MealItemSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_meal_item(
    meal_id: int,
    item_data: MealItemCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """向餐食添加餐品项目"""
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    # 创建餐品项目
    meal_item = MealItem(
        meal_id=meal.id,
        food_item_id=item_data.food_item_id,
        name=item_data.name,
        serving_size=item_data.serving_size,
        serving_unit=item_data.serving_unit,
        quantity=item_data.quantity,
        notes=item_data.notes,
        calories_per_serving=item_data.calories_per_serving,
        protein_per_serving=item_data.protein_per_serving,
        carbs_per_serving=item_data.carbs_per_serving,
        fat_per_serving=item_data.fat_per_serving,
    )

    db.add(meal_item)
    db.commit()
    db.refresh(meal_item)

    logger.info(
        "MealItem added", item_id=meal_item.id, meal_id=meal_id, user_id=current_user.id
    )

    return meal_item


@router.get("/food-items", response_model=List[FoodItemSchema])
async def get_food_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_custom: Optional[bool] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取食物库中的食物"""
    query = db.query(FoodItem)

    # 筛选条件
    if category:
        query = query.filter(FoodItem.category == category)
    if is_custom is not None:
        query = query.filter(FoodItem.is_custom == is_custom)

    food_items = query.offset(skip).limit(limit).all()

    return food_items


@router.post(
    "/food-items", response_model=FoodItemSchema, status_code=status.HTTP_201_CREATED
)
async def create_food_item(
    food_data: FoodItemCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建食物（用户自定义食物）"""
    # 检查食物是否已存在
    existing_food = (
        db.query(FoodItem)
        .filter(FoodItem.name == food_data.name, FoodItem.is_custom == True)
        .first()
    )
    if existing_food:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Food item with this name already exists",
        )

    food_item = FoodItem(
        **food_data.model_dump(),
        created_by_user_id=current_user.id,
        is_custom=True,  # 用户添加的食物总是自定义的
    )

    db.add(food_item)
    db.commit()
    db.refresh(food_item)

    logger.info(
        "Custom food item created", food_item_id=food_item.id, user_id=current_user.id
    )

    return food_item


@router.get("/daily-nutrition-summary", response_model=DailyNutritionSummary)
async def get_daily_nutrition_summary(
    target_date: date = Query(default=None, description="目标日期"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日营养摘要"""
    if not target_date:
        target_date = datetime.today().date()

    start_date = datetime.combine(target_date, datetime.min.time())
    end_date = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    # 获取用户当日的餐食记录
    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.meal_datetime >= start_date,
            Meal.meal_datetime < end_date,
        )
        .all()
    )

    # 计算总营养值
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    meal_count = 0

    for meal in meals:
        meal_count += 1
        if meal.calories:
            total_calories += meal.calories
        if meal.protein:
            total_protein += meal.protein
        if meal.carbs:
            total_carbs += meal.carbs
        if meal.fat:
            total_fat += meal.fat

    # 构造返回数据
    summary = DailyNutritionSummary(
        date=target_date.isoformat(),
        total_calories=int(total_calories),
        total_protein=int(total_protein),
        total_carbs=int(total_carbs),
        total_fat=int(total_fat),
        meal_count=meal_count,
        meals=meals,
    )

    logger.info("Daily summary retrieved", user_id=current_user.id, date=target_date)

    return summary
