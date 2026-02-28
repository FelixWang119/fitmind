from datetime import datetime, date, timedelta, timezone
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

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


@router.get("", response_model=List[MealSchema])
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

    # 获取记录（包含餐品项目）
    meals = (
        query.options(joinedload(Meal.meal_items))
        .order_by(Meal.meal_datetime.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return meals


@router.get("/daily-nutrition-summary", response_model=DailyNutritionSummary)
async def get_daily_nutrition_summary(
    target_date: date = Query(default=None, description="目标日期"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日营养摘要"""
    if not target_date:
        target_date = datetime.today().date()

    # 使用时区无关的日期范围查询
    # 将 date 转换为当天的开始和结束时间（本地时间）
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(
        target_date + timedelta(days=1), datetime.min.time()
    )

    # 获取用户当日的餐食记录（包含食材详情）
    # 使用 date() 函数提取日期部分进行比较，避免时区问题
    from sqlalchemy import func

    meals = (
        db.query(Meal)
        .options(joinedload(Meal.meal_items))
        .filter(
            Meal.user_id == current_user.id,
            func.date(Meal.meal_datetime) == target_date,
        )
        .order_by(Meal.meal_datetime.asc())  # 按时间排序
        .all()
    )

    # 安全地获取营养值的辅助函数
    def safe_get_nutrition_value(value):
        """安全地获取营养值，处理None和SQLAlchemy Column对象"""
        if value is None:
            return 0.0

        # 如果是SQLAlchemy Column对象，尝试获取其值
        try:
            # 检查是否是SQLAlchemy Column对象
            if hasattr(value, "__class__") and "Column" in str(value.__class__):
                # 对于Column对象，我们无法直接获取值，返回0
                return 0.0

            # 尝试转换为浮点数
            return float(value)
        except (TypeError, ValueError, AttributeError):
            # 如果转换失败，返回0
            return 0.0

    # 计算总营养值 - 使用更安全的方式处理可能为None或Column对象的值
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    meal_count = 0
    meal_schemas = []

    for meal in meals:
        meal_count += 1
        # 转换 SQLAlchemy 模型为 Pydantic 模型
        meal_schema = MealSchema.model_validate(meal)
        meal_schemas.append(meal_schema)

        # 累加营养值
        total_calories += safe_get_nutrition_value(meal.calories)
        total_protein += safe_get_nutrition_value(meal.protein)
        total_carbs += safe_get_nutrition_value(meal.carbs)
        total_fat += safe_get_nutrition_value(meal.fat)

    # 构造返回数据 - 已经是浮点数，直接使用
    total_calories_float = total_calories
    total_protein_float = total_protein
    total_carbs_float = total_carbs
    total_fat_float = total_fat

    summary = DailyNutritionSummary(
        date=target_date.isoformat(),
        total_calories=total_calories_float,
        total_protein=total_protein_float,
        total_carbs=total_carbs_float,
        total_fat=total_fat_float,
        meal_count=meal_count,
        meals=meal_schemas,
    )

    logger.info("Daily summary retrieved", user_id=current_user.id, date=target_date)

    # Debug: log what we're returning
    logger.debug(
        "Summary structure",
        has_meals=hasattr(summary, "meals"),
        meals_count=len(summary.meals) if hasattr(summary, "meals") else 0,
    )
    if hasattr(summary, "meals") and summary.meals:
        first_meal = summary.meals[0]
        logger.debug(
            "First meal structure",
            has_items=hasattr(first_meal, "items"),
            items_count=len(first_meal.items) if hasattr(first_meal, "items") else 0,
        )
        # Convert to dict to see field names
        meal_dict = first_meal.model_dump()
        logger.debug("First meal dict keys", keys=str(list(meal_dict.keys())))

    return summary


@router.get("/{meal_id}", response_model=MealSchema)
async def get_meal(
    meal_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定的餐食记录"""
    meal = (
        db.query(Meal)
        .options(joinedload(Meal.meal_items))
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal record not found"
        )

    return meal


@router.post("", response_model=MealSchema, status_code=status.HTTP_201_CREATED)
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
        calories=int(total_calories) if total_calories else 0,
        protein=int(total_proteins) if total_proteins else 0,
        carbs=int(total_carbs) if total_carbs else 0,
        fat=int(total_fat) if total_fat else 0,
    )

    db.add(meal)
    db.flush()  # 获取meal.id但不提交事务

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

    # 重新查询meal以加载meal_items关系
    # 使用joinedload确保关系被加载
    meal_with_items = (
        db.query(Meal)
        .options(joinedload(Meal.meal_items))
        .filter(Meal.id == meal.id)
        .first()
    )

    logger.info("Meal created", meal_id=meal.id, user_id=current_user.id)

    # 添加到短期记忆队列
    try:
        from app.services.short_term_memory import get_short_term_memory_service

        meal_type_map = {
            "breakfast": "早餐",
            "lunch": "午餐",
            "dinner": "晚餐",
            "snack": "加餐",
        }
        meal_type_cn = meal_type_map.get(meal.meal_type, meal.meal_type)

        # 构建食材内容描述
        if meal_with_items.meal_items:
            items_text = ", ".join(
                [
                    f"{item.name} {int(item.serving_size)}{item.serving_unit}"
                    for item in meal_with_items.meal_items[:5]
                ]
            )
            if len(meal_with_items.meal_items) > 5:
                items_text += f" 等{len(meal_with_items.meal_items)}种食材"
            content = f"记录了{meal_type_cn}（{meal.name}）：{items_text}，总热量{meal.calories or 0}千卡"
        else:
            content = (
                f"记录了{meal_type_cn}（{meal.name}），摄入热量{meal.calories or 0}千卡"
            )

        # 添加到短期记忆队列（溢出索引由队列内部自动处理）
        # 注意：需要将 Decimal 转换为 float 以支持 JSON 序列化
        get_short_term_memory_service().add_memory(
            user_id=int(current_user.id),
            event_type="meal",
            event_source=meal.meal_type,
            content=content,
            metrics={
                "calories": float(meal.calories) if meal.calories else 0.0,
                "protein": float(meal.protein) if meal.protein else 0.0,
                "carbs": float(meal.carbs) if meal.carbs else 0.0,
                "fat": float(meal.fat) if meal.fat else 0.0,
            },
            context={"meal_type": meal.meal_type},
            source_table="meals",
            source_id=meal.id,
        )

        logger.info(f"餐食已添加到短期记忆队列：{meal.id}")
    except Exception as e:
        logger.error(f"添加餐食到短期记忆失败：{e}")

    # ===== Story 4.1: 更新营养成就 =====
    try:
        from app.services.gamification_service import get_gamification_service

        gamification_service = get_gamification_service(db)

        # 更新饮食连续成就
        gamification_service.check_and_update_nutrition_streak(
            current_user, has_meal_today=True
        )

        # 更新尝试新食物成就 (如果有新食材)
        if meal_with_items and meal_with_items.meal_items:
            # 这里可以添加检测新食物的逻辑
            # 简化处理：每次记录都增加进度
            gamification_service.update_nutrition_achievement(
                current_user,
                "variety_explorer_10",
                increment=len(meal_with_items.meal_items),
            )

        logger.info("Nutrition achievements updated", user_id=current_user.id)
    except Exception as e:
        logger.error(f"更新营养成就失败：{e}")
        # 不阻塞餐食创建流程

    return meal_with_items


@router.put("/{meal_id}", response_model=MealSchema)
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

    # 分离 items 和其他字段
    items_data = update_data.pop("items", None)

    # 更新基本字段
    for field, value in update_data.items():
        setattr(meal, field, value)

    # 处理 items 的更新
    if items_data is not None:
        # 删除现有的 meal_items
        for existing_item in meal.meal_items:
            db.delete(existing_item)
        db.flush()

        # 创建新的 meal_items
        if items_data:
            for item_data in items_data:
                meal_item = MealItem(
                    meal_id=meal.id,
                    name=item_data.get("name", "未知食材"),
                    serving_size=item_data.get("serving_size")
                    or item_data.get("grams"),
                    serving_unit=item_data.get("serving_unit", "g"),
                    quantity=item_data.get("quantity", 1),
                    notes=item_data.get("notes"),
                    calories_per_serving=item_data.get("calories_per_serving")
                    or item_data.get("calories", 0),
                    protein_per_serving=item_data.get("protein_per_serving")
                    or item_data.get("protein", 0),
                    carbs_per_serving=item_data.get("carbs_per_serving")
                    or item_data.get("carbs", 0),
                    fat_per_serving=item_data.get("fat_per_serving")
                    or item_data.get("fat", 0),
                )
                db.add(meal_item)

    db.commit()
    db.refresh(meal)

    # 重新加载 meal_items
    db.refresh(meal, attribute_names=["meal_items"])

    logger.info("Meal updated", meal_id=meal.id, user_id=current_user.id)

    # ========== 添加到短期记忆队列（更新也写入） ==========
    try:
        from app.services.short_term_memory import get_short_term_memory_service

        meal_type_map = {
            "breakfast": "早餐",
            "lunch": "午餐",
            "dinner": "晚餐",
            "snack": "加餐",
        }
        meal_type_cn = meal_type_map.get(meal.meal_type, meal.meal_type)

        # 构建食材内容描述
        if meal.meal_items:
            items_text = ", ".join(
                [
                    f"{item.name} {int(item.serving_size)}{item.serving_unit}"
                    for item in meal.meal_items[:5]
                ]
            )
            if len(meal.meal_items) > 5:
                items_text += f" 等{len(meal.meal_items)}种食材"
            content = f"更新了{meal_type_cn}（{meal.name}）：{items_text}，总热量{meal.calories or 0}千卡"
        else:
            content = (
                f"更新了{meal_type_cn}（{meal.name}），摄入热量{meal.calories or 0}千卡"
            )

        get_short_term_memory_service().add_memory(
            user_id=int(current_user.id),
            event_type="meal",
            event_source=meal.meal_type,
            content=content,
            metrics={
                "calories": float(meal.calories) if meal.calories else 0.0,
                "protein": float(meal.protein) if meal.protein else 0.0,
                "carbs": float(meal.carbs) if meal.carbs else 0.0,
                "fat": float(meal.fat) if meal.fat else 0.0,
            },
            context={"meal_type": meal.meal_type, "updated": True},
            source_table="meals",
            source_id=meal.id,
        )

        logger.info(f"餐食更新已添加到短期记忆队列：{meal.id}")
    except Exception as e:
        logger.error(f"添加餐食更新到短期记忆失败：{e}")
    # ====================================================

    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/{meal_id}/items", response_model=List[MealItemSchema])
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
    "/{meal_id}/items",
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
        food_item_id=None,  # food_item_id is optional
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
