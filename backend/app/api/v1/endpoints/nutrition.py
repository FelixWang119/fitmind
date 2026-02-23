from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.nutrition import (
    FoodItem,
    FoodLogAnalysis,
    MealSuggestion,
    NutritionRecommendation,
)
from app.services.nutrition_service import get_nutrition_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/recommendations", response_model=NutritionRecommendation)
async def get_nutrition_recommendations(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取营养建议"""
    logger.info("Getting nutrition recommendations", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        recommendations = nutrition_service.get_dietary_recommendations(current_user)

        # 转换餐食建议格式
        meal_suggestions = []
        for meal_type, options in recommendations["meal_suggestions"].items():
            for option in options:
                meal_suggestions.append(
                    MealSuggestion(
                        meal_type=meal_type,
                        name=option["name"],
                        description=option["description"],
                        calories=option["calories"],
                        protein_g=option["protein"],
                        fat_g=option["fat"],
                        carb_g=option["carb"],
                    )
                )

        return NutritionRecommendation(
            calorie_targets=recommendations["calorie_targets"],
            macronutrients=recommendations["macronutrients"],
            meal_suggestions=meal_suggestions,
            hydration_goal=recommendations["hydration_goal"],
            supplement_recommendations=recommendations["supplement_recommendations"],
        )

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
async def get_calorie_target(
    current_user: UserModel = Depends(get_current_active_user),
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


@router.get("/macronutrients")
async def get_macronutrients(
    current_user: UserModel = Depends(get_current_active_user),
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
            "target_calories": target_calories,
            **macros,
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
async def analyze_food_log(
    food_items: List[FoodItem],
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """分析食物日志"""
    logger.info(
        "Analyzing food log", user_id=current_user.id, item_count=len(food_items)
    )

    nutrition_service = get_nutrition_service(db)

    try:
        analysis = nutrition_service.analyze_food_log(food_items)

        # 获取用户目标进行比较
        calorie_targets = nutrition_service.calculate_calorie_target(current_user)
        target_calories = calorie_targets.get("target", calorie_targets["maintenance"])
        target_macros = nutrition_service.calculate_macronutrients(
            current_user, target_calories
        )

        # 计算目标达成度
        total = analysis["total"]
        calorie_percentage = (
            (total["calories"] / target_calories * 100) if target_calories > 0 else 0
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

        return FoodLogAnalysis(
            total=total,
            meal_distribution=analysis["meal_distribution"],
            nutrition_score=analysis["nutrition_score"],
            target_comparison={
                "calories": {
                    "actual": total["calories"],
                    "target": target_calories,
                    "percentage": round(calorie_percentage, 1),
                },
                "protein": {
                    "actual": total["protein_g"],
                    "target": target_macros["protein_g"],
                    "percentage": round(protein_percentage, 1),
                },
                "fat": {
                    "actual": total["fat_g"],
                    "target": target_macros["fat_g"],
                    "percentage": round(fat_percentage, 1),
                },
                "carb": {
                    "actual": total["carb_g"],
                    "target": target_macros["carb_g"],
                    "percentage": round(carb_percentage, 1),
                },
            },
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
async def get_meal_suggestions(
    meal_type: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
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
async def get_hydration_goal(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取饮水目标"""
    logger.info("Getting hydration goal", user_id=current_user.id)

    nutrition_service = get_nutrition_service(db)

    try:
        hydration_goal = nutrition_service._calculate_hydration_goal(current_user)

        return {
            "hydration_goal_ml": hydration_goal,
            "hydration_goal_cups": round(hydration_goal / 240, 1),  # 1杯 ≈ 240ml
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
async def get_supplement_recommendations(
    current_user: UserModel = Depends(get_current_active_user),
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
