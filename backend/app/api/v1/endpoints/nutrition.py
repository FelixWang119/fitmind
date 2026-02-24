from typing import Dict, List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
from datetime import datetime

from app.api.v1.endpoints.auth import (
    get_current_active_user,
    get_current_active_user as get_current_user_alias,
)
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.nutrition import (
    FoodItem,
    FoodLogAnalysis,  # 这個導入確保了目標比較結構
    MealSuggestion,
    NutritionRecommendation,
    CalorieTargets,
    Macronutrients,
    TargetComparison,
)
from app.services.nutrition_service import get_nutrition_service

try:
    from app.utils.food_image_analyzer import analyze_food_with_qwen_vision
except ImportError:
    # 如果 AI 分析文件不存在，创建一个模拟实现
    async def analyze_food_with_qwen_vision(image_data) -> Dict[str, any]:
        """模拟食物分析实现"""
        return {
            "meal_name": "模拟餐食",
            "meal_type": "lunch",
            "total_calories": 350,
            "protein_g": 20,
            "carbs_g": 40,
            "fat_g": 10,
            "notes": "这是一条模拟的食物分析结果",
            "suggestions": ["增加蛋白质摄入", "注意碳水化合物搭配"],
        }


logger = structlog.get_logger()

router = APIRouter()


def current_date_str_unique():
    return datetime.now().strftime("%Y-%m-%d")


@router.get("/recommendations", response_model=NutritionRecommendation)
async def get_nutrition_recommendations_main(
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取营养建议"""
    logger.info("Getting nutrition recommendations", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        recommendations = nutrition_service.get_dietary_recommendations(current_user)

        # 转换餐食建议格式
        meal_suggestions = []
        try:
            suggestion_map = recommendations["meal_suggestions"]
            if isinstance(suggestion_map, dict):
                for meal_type, options in suggestion_map.items():
                    if options is None:
                        continue  # 安全跳过None值
                    for option in options:
                        if option:
                            meal_suggestions.append(
                                MealSuggestion(
                                    meal_type=meal_type,
                                    name=option.get("name", ""),
                                    description=option.get("description", ""),
                                    calories=option.get("calories", 0),
                                    protein_g=option.get("protein", 0),
                                    fat_g=option.get("fat", 0),
                                    carb_g=option.get("carb", 0),
                                )
                            )
        except KeyError:
            meal_suggestions = []

        # 确保 calorie_targets 是有效的字典
        calorie_targets = recommendations.get("calorie_targets", {})

        # 确保 macronutrients 是有效的字典
        macronutrients = recommendations.get("macronutrients", {})

        # 创建 NutritionRecommendation 对象时提供安全的默认值
        nutrition_recommendation = NutritionRecommendation(
            user_weight=getattr(current_user, "initial_weight", 70000) / 1000
            if getattr(current_user, "initial_weight", 70000)
            else 70.0,
            user_height=getattr(current_user, "height", 170)
            if getattr(current_user, "height", 170)
            else 170,
            user_age=getattr(current_user, "age", 30)
            if getattr(current_user, "age", 30)
            else 30,
            user_gender=getattr(current_user, "gender", "male")
            if getattr(current_user, "gender", "male")
            else "male",
            user_activity_level=getattr(current_user, "activity_level", "moderate")
            if getattr(current_user, "activity_level", "moderate")
            else "moderate",
            user_current_weight=getattr(current_user, "initial_weight", 70000) / 1000
            if getattr(current_user, "initial_weight", 70000)
            else 70.0,
            user_target_weight=getattr(current_user, "target_weight", 65000) / 1000
            if getattr(current_user, "target_weight", 65000)
            else 65.0,
            calorie_targets=CalorieTargets(
                maintenance=calorie_targets.get("maintenance", 2000.0),
                target=calorie_targets.get("target", 2000.0),
                weight_loss=calorie_targets.get("weight_loss", 1700.0),
                weight_gain=calorie_targets.get("weight_gain", 2300.0),
                weight_difference=calorie_targets.get("weight_difference_kg", 0.0),
            ),
            macronutrients=Macronutrients(
                protein_g=macronutrients.get("protein_g", 150.0),
                fat_g=macronutrients.get("fat_g", 65.0),
                carb_g=macronutrients.get("carb_g", 200.0),
                protein_percentage=macronutrients.get("protein_percentage", 30.0),
                fat_percentage=macronutrients.get("fat_percentage", 25.0),
                carb_percentage=macronutrients.get("carb_percentage", 45.0),
            ),
            meal_suggestions=meal_suggestions,
            hydration_goal=recommendations.get("hydration_goal", 2450.0),
            supplement_recommendations=recommendations.get(
                "supplement_recommendations", ["维生素D"]
            ),
        )

        return nutrition_recommendation

    except Exception as e:
        logger.error(
            "Failed to get nutrition recommendations",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate nutrition recommendations",
        )


@router.get("/calorie-target")
async def get_calorie_target_main(
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取卡路里目标"""
    logger.info("Getting calorie target", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        calorie_targets = nutrition_service.calculate_calorie_target(current_user)

        # 计算基础代谢率和TDEE
        bmr = nutrition_service.calculate_bmr(current_user)
        tdee = nutrition_service.calculate_tdee(current_user)

        return {
            "bmr": bmr,
            "tdee": tdee,
            "current_weight_kg": (
                getattr(current_user, "initial_weight", 70000) / 1000.0
            )
            if getattr(current_user, "initial_weight", 70000)
            else 70.0,
            "target_weight_kg": (getattr(current_user, "target_weight", 65000) / 1000.0)
            if getattr(current_user, "target_weight", 65000)
            else 65.0,
            **calorie_targets,
        }

    except Exception as e:
        logger.error(
            "Failed to calculate calorie target", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate calorie target",
        )


@router.post("/analyze-food-image")
async def analyze_food_image_endpoint_unique(
    image_data: dict,
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """分析食物图像 - 获取POST数据"""
    logger.info("Analyzing food from image", user_id=current_user.id)

    try:
        image_base64 = image_data.get("image")
        requested_date = image_data.get("date", current_date_str_unique())

        if not image_base64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required"
            )

        # 使用Qwen AI进行图像分析
        analysis_result = await analyze_food_with_qwen_vision(image_base64)
        return analysis_result

    except HTTPException:
        # 如果是前端抛出的HTTP异常
        raise
    except Exception as e:
        logger.error(
            "Failed to analyze food image", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze food image",
        )


@router.get("/macronutrients")
async def get_macronutrients_main(
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取宏量营养素目标"""
    logger.info("Getting macronutrients", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        calorie_targets = nutrition_service.calculate_calorie_target(current_user)
        target_calories = calorie_targets.get("target", calorie_targets["maintenance"])

        macros = nutrition_service.calculate_macronutrients(
            current_user, target_calories
        )

        return {
            "target_calories": float(target_calories),
            "protein_g": float(macros["protein_g"]),
            "fat_g": float(macros["fat_g"]),
            "carb_g": float(macros["carb_g"]),
            "protein_percentage": float(macros["protein_percentage"]),
            "fat_percentage": float(macros["fat_percentage"]),
            "carb_percentage": float(macros["carb_percentage"]),
        }

    except Exception as e:
        logger.error(
            "Failed to calculate macronutrients", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate macronutrients",
        )


@router.post("/analyze-food-log", response_model=FoodLogAnalysis)
async def analyze_food_log_main(
    food_items: List[FoodItem],
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """分析食物日志"""
    logger.info(
        "Analyzing food log", user_id=current_user.id, item_count=len(food_items)
    )

    nutrition_service = get_nutrition_service(db)

    try:
        # 将 FoodItem 列表轉換為字典列表
        food_items_dict = [item.dict() for item in food_items]
        analysis = nutrition_service.analyze_food_log(food_items_dict)

        # 获取用户目标进行比较
        calorie_targets = nutrition_service.calculate_calorie_target(current_user)
        target_calories = calorie_targets.get("target", calorie_targets["maintenance"])
        target_macros = nutrition_service.calculate_macronutrients(
            current_user, target_calories
        )

        # 计算目標達成度
        total = analysis["total"]
        try:
            calorie_percentage = (
                (total["calories"] / target_calories * 100)
                if target_calories > 0
                else 0
            )
            protein_percentage = (
                (total["protein_g"] / target_macros["protein_g"] * 100)
                if target_macros["protein_g"] > 0
                else 0
            )
            fat_percentage = (
                (total["fat_g"] / target_macros["fat_g"] * 100)
                if target_macros["fat_g"] > 0
                else 0
            )
            carb_percentage = (
                (total["carb_g"] / target_macros["carb_g"] * 100)
                if target_macros["carb_g"] > 0
                else 0
            )
        except (TypeError, ValueError, ZeroDivisionError):
            calorie_percentage = 0
            protein_percentage = 0
            fat_percentage = 0
            carb_percentage = 0

        # 创建目标比较对象
        target_comparison_obj = TargetComparison(
            calories={
                "actual": float(total["calories"]),
                "target": float(target_calories),
                "percentage": round(calorie_percentage, 1),
            },
            protein={
                "actual": float(total["protein_g"]),
                "target": float(target_macros["protein_g"]),
                "percentage": round(protein_percentage, 1),
            },
            fat={
                "actual": float(total["fat_g"]),
                "target": float(target_macros["fat_g"]),
                "percentage": round(fat_percentage, 1),
            },
            carb={
                "actual": float(total["carb_g"]),
                "target": float(target_macros["carb_g"]),
                "percentage": round(carb_percentage, 1),
            },
        )

        return FoodLogAnalysis(
            total=total,
            meal_distribution=analysis["meal_distribution"],
            nutrition_score=analysis["nutrition_score"],
            target_comparison=target_comparison_obj,
        )

    except Exception as e:
        logger.error(
            "Failed to analyze food log", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze food log",
        )


@router.get("/meal-suggestions")
async def get_meal_suggestions_main(
    meal_type: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取餐食建议"""
    logger.info(
        "Getting meal suggestions", user_id=current_user.id, meal_type=meal_type
    )

    nutrition_service = get_nutrition_service(db)

    try:
        recommendations = nutrition_service.get_dietary_recommendations(current_user)
        meal_suggestions = recommendations["meal_suggestions"]

        if meal_type and meal_type in meal_suggestions:
            # 返回特定餐食类型的建议
            return {
                "meal_type": meal_type,
                "suggestions": meal_suggestions[meal_type],
            }
        else:
            # 返回所有餐食建议
            return meal_suggestions

    except Exception as e:
        logger.error(
            "Failed to get meal suggestions", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate meal suggestions",
        )


@router.get("/hydration-goal")
async def get_hydration_goal_main(
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取饮水目标"""
    logger.info("Getting hydration goal", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        hydration_goal = nutrition_service._calculate_hydration_goal(current_user)

        return {
            "hydration_goal_ml": float(hydration_goal),
            "hydration_goal_cups": float(round(hydration_goal / 240, 1)),  # 1杯 ≈ 240ml
            "recommendation": f"每天至少饮用 {hydration_goal}ml ({round(hydration_goal / 240, 1)}杯) 水",
        }

    except Exception as e:
        logger.error(
            "Failed to calculate hydration goal", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate hydration goal",
        )


@router.get("/supplement-recommendations")
async def get_supplement_recommendations_main(
    current_user: UserModel = Depends(get_current_user_alias),
    db: Session = Depends(get_db),
):
    """获取补充剂建议"""
    logger.info("Getting supplement recommendations", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        recommendations = nutrition_service._get_supplement_recommendations(
            current_user
        )

        return {
            "recommendations": recommendations,
            "note": "请咨询医生或营养师后服用补充剂",
        }

    except Exception as e:
        logger.error(
            "Failed to get supplement recommendations",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate supplement recommendations",
        )
