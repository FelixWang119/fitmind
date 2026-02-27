import base64
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.models.nutrition import Meal, MealItem
from app.models.user import User as UserModel
from app.services.calorie_service import get_calorie_service
from app.services.image_service import get_image_service
from app.services.short_term_memory import get_short_term_memory_service
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============ Schemas ============


class FoodItemInput(BaseModel):
    """食材输入"""

    name: str = Field(..., description="食材名称")
    grams: float = Field(..., gt=0, description="克数")
    calories: float = Field(..., ge=0, description="热量 (kcal)")
    protein: float = Field(default=0, ge=0, description="蛋白质 (g)")
    carbs: float = Field(default=0, ge=0, description="碳水化合物 (g)")
    fat: float = Field(default=0, ge=0, description="脂肪 (g)")


class UploadResponse(BaseModel):
    """上传响应"""

    meal_type: str
    items: List[FoodItemInput]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    notes: str = ""  # AI 营养评价和建议


class ConfirmRequest(BaseModel):
    """确认打卡请求"""

    meal_type: str = Field(..., description="餐饮类型: breakfast/lunch/dinner/snack")
    items: List[FoodItemInput] = Field(..., description="食材列表")
    photo_path: Optional[str] = Field(None, description="照片路径")


class RecalculateRequest(BaseModel):
    """重新计算请求"""

    items: List[FoodItemInput] = Field(..., description="调整后的食材列表")


class RecalculateResponse(BaseModel):
    """重新计算响应"""

    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float


# ============ Endpoints ============


@router.post("/upload", response_model=UploadResponse)
async def upload_meal_photo(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    上传食物照片，返回识别结果（食材列表）
    """
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的图片格式，仅支持 jpg, png, webp",
        )

    # 读取文件内容
    content = await file.read()

    # 验证文件大小
    if len(content) > settings.IMAGE_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制 (最大 10MB)",
        )

    # 转换为 base64
    base64_image = base64.b64encode(content).decode("utf-8")

    try:
        # 调用 AI 识别
        result = await analyze_food_with_qwen_vision(base64_image)

        # 转换为响应格式
        items = [
            FoodItemInput(
                name=item.get("name", "未知食材"),
                grams=item.get("grams", 100),
                calories=item.get("calories", 0),
                protein=item.get("protein", 0),
                carbs=item.get("carbs", 0),
                fat=item.get("fat", 0),
            )
            for item in result.get("items", [])
        ]

        logger.info(
            "Meal photo analyzed",
            user_id=current_user.id,
            items_count=len(items),
        )

        return UploadResponse(
            meal_type=result.get("meal_type", "lunch"),
            items=items,
            total_calories=result.get("total_calories", 0),
            total_protein=result.get("total_protein", 0),
            total_carbs=result.get("total_carbs", 0),
            total_fat=result.get("total_fat", 0),
        )

    except Exception as e:
        logger.error("Food analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="识别服务暂时不可用，请稍后重试",
        )


@router.post("/recalculate", response_model=RecalculateResponse)
def recalculate_nutrition(
    request: RecalculateRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    用户调整食材数量后重新计算热量
    """
    calorie_service = get_calorie_service(db)

    items_dict = [item.model_dump() for item in request.items]
    result = calorie_service.recalculate_from_items(items_dict)

    logger.info(
        "Nutrition recalculated",
        user_id=current_user.id,
        items_count=len(request.items),
    )

    # 转换字段名以匹配 RecalculateResponse
    return RecalculateResponse(
        total_calories=result["calories"],
        total_protein=result["protein"],
        total_carbs=result["carbs"],
        total_fat=result["fat"],
    )


@router.post("/confirm")
def confirm_meal_checkin(
    request: ConfirmRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    用户确认后创建打卡记录
    """
    calorie_service = get_calorie_service(db)
    image_service = get_image_service()

    # 计算总营养
    items_dict = [item.model_dump() for item in request.items]
    nutrition = calorie_service.recalculate_from_items(items_dict)

    # 保存照片（如果提供）
    photo_url = None
    if request.photo_path:
        photo_url = image_service.get_image_url(request.photo_path)

    # 创建 Meal 记录
    meal = Meal(
        user_id=current_user.id,
        meal_type=request.meal_type,
        name=f"{request.meal_type.capitalize()} 打卡",
        meal_datetime=datetime.now(),
        calories=int(nutrition["calories"]),
        protein=int(nutrition["protein"]),
        carbs=int(nutrition["carbs"]),
        fat=int(nutrition["fat"]),
        photo_url=photo_url,
    )

    db.add(meal)
    db.flush()

    # 创建 MealItem 记录
    for item in request.items:
        meal_item = MealItem(
            meal_id=meal.id,
            name=item.name,
            serving_size=item.grams,
            serving_unit="g",
            quantity=1,
            calories_per_serving=item.calories,
            protein_per_serving=int(item.protein),
            carbs_per_serving=int(item.carbs),
            fat_per_serving=int(item.fat),
        )
        db.add(meal_item)

    db.commit()
    db.refresh(meal)

    logger.info(
        "Meal checkin confirmed",
        user_id=current_user.id,
        meal_id=meal.id,
        calories=nutrition["calories"],
    )

    # ========== 添加到短期记忆队列 ==========
    try:
        meal_type_map = {
            "breakfast": "早餐",
            "lunch": "午餐",
            "dinner": "晚餐",
            "snack": "加餐",
        }
        meal_type_cn = meal_type_map.get(request.meal_type, request.meal_type)

        # 构建食物内容描述
        items_text = ", ".join(
            [f"{item.name} {int(item.grams)}g" for item in request.items[:5]]
        )
        if len(request.items) > 5:
            items_text += f" 等{len(request.items)}种食材"

        content = f"记录了{meal_type_cn}（{meal.name}）：{items_text}，总热量{int(nutrition['calories'])}千卡"

        get_short_term_memory_service().add_memory(
            user_id=int(current_user.id),
            event_type="meal",
            event_source=request.meal_type,
            content=content,
            metrics={
                "calories": float(nutrition["calories"]),
                "protein": float(nutrition["protein"]),
                "carbs": float(nutrition["carbs"]),
                "fat": float(nutrition["fat"]),
            },
            context={
                "meal_type": request.meal_type,
                "items_count": len(request.items),
            },
            source_table="meals",
            source_id=meal.id,
        )

        logger.info(f"餐食打卡已添加到短期记忆队列：{meal.id}")
    except Exception as e:
        logger.error(f"添加餐食打卡到短期记忆失败：{e}")
    # ====================================

    return {
        "message": "打卡成功",
        "meal_id": meal.id,
        "nutrition": nutrition,
    }


# ============ 热量目标 API ============

from datetime import date as date_type

from app.schemas.calorie_goal import (
    CalorieGoalCreate,
    CalorieGoalResponse,
    CalorieGoalUpdate,
)
from app.models.calorie_goal import CalorieGoal


@router.get("/calorie-goal", response_model=Dict)
def get_calorie_goal(
    target_date: Optional[date_type] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取热量目标"""
    calorie_service = get_calorie_service(db)
    return calorie_service.get_calorie_goal(current_user.id, target_date)


@router.post("/calorie-goal", response_model=CalorieGoalResponse)
def set_calorie_goal(
    goal_data: CalorieGoalCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """设置热量目标"""
    calorie_service = get_calorie_service(db)
    goal = calorie_service.set_calorie_goal(
        current_user.id,
        goal_data.model_dump(),
        goal_data.goal_date,
    )
    return goal


@router.get("/daily-balance", response_model=Dict)
def get_daily_balance(
    target_date: Optional[date_type] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当日热量余额"""
    calorie_service = get_calorie_service(db)
    return calorie_service.calculate_daily_balance(current_user.id, target_date)
