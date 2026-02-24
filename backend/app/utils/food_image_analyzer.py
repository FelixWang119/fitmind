import os
import json
from typing import Dict, Any, List
from PIL import Image
import base64
from io import BytesIO
import structlog
import httpx
from fastapi import HTTPException, status
import asyncio

from app.core.config import settings
from app.core.qwen_config import qwen_config

logger = structlog.get_logger(__name__)


def get_fallback_data(reason: str = "开发模式") -> Dict[str, Any]:
    """获取后备数据（当AI分析失败时使用）"""
    return {
        "meal_type": "lunch",
        "items": [
            {
                "name": "米饭",
                "grams": 150,
                "calories": 174,
                "protein": 3,
                "carbs": 38,
                "fat": 0.5,
            },
            {
                "name": "红烧肉",
                "grams": 100,
                "calories": 350,
                "protein": 12,
                "carbs": 8,
                "fat": 30,
            },
        ],
        "total_calories": 524,
        "total_protein": 15,
        "total_carbs": 46,
        "total_fat": 30.5,
        "notes": f"模拟数据（{reason}）",
    }


class FoodItemAnalysis:
    """单个食材分析结果"""

    def __init__(
        self,
        name: str,
        grams: float,
        calories: float,
        protein: float,
        carbs: float,
        fat: float,
    ):
        self.name = name
        self.grams = grams
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat


class MealAnalysisResult:
    """餐饮分析结果（包含多个食材）"""

    def __init__(self, meal_type: str, items: List[FoodItemAnalysis]):
        self.meal_type = meal_type
        self.items = items
        self.total_calories = sum(item.calories for item in items)
        self.total_protein = sum(item.protein for item in items)
        self.total_carbs = sum(item.carbs for item in items)
        self.total_fat = sum(item.fat for item in items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meal_type": self.meal_type,
            "items": [
                {
                    "name": item.name,
                    "grams": item.grams,
                    "calories": item.calories,
                    "protein": item.protein,
                    "carbs": item.carbs,
                    "fat": item.fat,
                }
                for item in self.items
            ],
            "total_calories": self.total_calories,
            "total_protein": self.total_protein,
            "total_carbs": self.total_carbs,
            "total_fat": self.total_fat,
        }


async def analyze_food_with_qwen_vision(base64_image: str) -> Dict[str, Any]:
    """
    使用Qwen视觉模型分析食物图片
    """
    # 使用集中式配置
    api_key = qwen_config.QWEN_API_KEY
    if not api_key:
        # 如果没有API Key，则返回模拟数据（食材列表格式）
        logger.warning("QWEN_API_KEY not set, returning mock data")
        return get_fallback_data("未设置API Key")

    # 使用集中式配置的URL和模型
    url = qwen_config.QWEN_API_URL
    headers = qwen_config.get_headers()

    # 使用视觉模型
    model_to_try = qwen_config.QWEN_VISION_MODEL

    payload = {
        "model": model_to_try,  # 使用视觉语言模型
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": """请分析这张食物图片，识别出所有食材及其估计克数，并计算营养成分。请按照以下JSON格式返回分析结果：
{
    "meal_type": "breakfast/lunch/dinner/snack",
    "items": [
        {
            "name": "食材名称",
            "grams": 估计的克数,
            "calories": 热量(kcal),
            "protein": 蛋白质(g),
            "carbs": 碳水化合物(g),
            "fat": 脂肪(g)
        }
    ],
    "notes": "营养评价和建议"
}

请只返回JSON格式，不要有其他文本。""",
                    },
                ],
            }
        ],
        "temperature": qwen_config.get_temperature_for_model(model_to_try),
    }

    try:
        logger.info(f"Calling Qwen vision API with model: {model_to_try}")
        timeout = qwen_config.get_timeout_for_model(model_to_try)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            # 解析模型返回的结果 - 兼容模式格式
            if "choices" in result:
                content_text = result["choices"][0]["message"]["content"]

                # 尝试從返回文本解析JSON
                try:
                    # 查找JSON部分
                    start_brace = content_text.find("{")
                    end_brace = content_text.rfind("}")

                    if start_brace != -1 and end_brace != -1:
                        json_str = content_text[start_brace : end_brace + 1]
                        parsed_data = json.loads(json_str)

                        # 解析食材列表
                        items_data = parsed_data.get("items", [])
                        food_items = []
                        for item_data in items_data:
                            food_item = FoodItemAnalysis(
                                name=item_data.get("name", "未知食材"),
                                grams=item_data.get("grams", 0),
                                calories=item_data.get("calories", 0),
                                protein=item_data.get("protein", 0),
                                carbs=item_data.get("carbs", 0),
                                fat=item_data.get("fat", 0),
                            )
                            food_items.append(food_item)

                        meal_analysis = MealAnalysisResult(
                            meal_type=parsed_data.get("meal_type", "lunch"),
                            items=food_items,
                        )

                        result_dict = meal_analysis.to_dict()
                        result_dict["notes"] = parsed_data.get("notes", "AI分析完成")

                        logger.info(
                            "Food image analysis successful",
                            items_count=len(food_items),
                            total_calories=result_dict["total_calories"],
                        )

                        return result_dict
                    else:
                        logger.warning(
                            "No JSON found in response, using fallback",
                            response=content_text[:200],
                        )
                        # 返回模拟数据作为后备
                        return get_fallback_data("AI响应格式错误")

                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse JSON from response, using fallback",
                        error=str(e),
                        text=content_text[:200],
                    )
                    # 返回模拟数据作为后备
                    return get_fallback_data("AI响应解析失败")

            else:
                logger.error(
                    "Unexpected response format, using fallback",
                    response=str(result)[:200],
                )
                # 返回模拟数据作为后备
                return get_fallback_data("AI响应格式异常")

    except httpx.HTTPError as e:
        # Handle HTTP errors from the API
        error_msg = str(e)

        # 尝试获取响应体以获取更多错误信息
        try:
            if hasattr(e, "response") and e.response:
                error_detail = e.response.text[:500]
                logger.error(
                    "HTTP error from Qwen API, using fallback",
                    status_code=e.response.status_code,
                    error_detail=error_detail,
                )
                return get_fallback_data(
                    f"AI服务错误 {e.response.status_code}: {error_detail[:100]}"
                )
        except:
            pass

        logger.error(
            "HTTP error from Qwen API, using fallback",
            response=error_msg[:200],
        )
        # 返回模拟数据作为后备
        return get_fallback_data(f"AI服务暂时不可用: {error_msg[:100]}")
    except Exception as e:
        logger.error(
            "Unexpected error in food image analysis, using fallback", error=str(e)
        )
        # 返回模拟数据作为后备
        return get_fallback_data(f"分析过程出错: {str(e)[:50]}")


def _create_mock_item_result() -> Dict[str, Any]:
    """创建模拟的食材列表结果（用于开发/测试）"""
    return {
        "meal_type": "lunch",
        "items": [
            {
                "name": "米饭",
                "grams": 150,
                "calories": 174,
                "protein": 3,
                "carbs": 38,
                "fat": 0.5,
            },
            {
                "name": "红烧肉",
                "grams": 100,
                "calories": 350,
                "protein": 12,
                "carbs": 8,
                "fat": 30,
            },
        ],
        "total_calories": 524,
        "total_protein": 15,
        "total_carbs": 46,
        "total_fat": 30.5,
    }


# 保留向后兼容的旧接口
async def analyze_food_legacy(base64_image: str) -> Dict[str, Any]:
    """旧版接口，返回总热量（保留用于兼容）"""
    result = await analyze_food_with_qwen_vision(base64_image)
    return {
        "meal_name": "待识别食品",
        "meal_type": result.get("meal_type", "lunch"),
        "total_calories": result.get("total_calories", 0),
        "protein_g": result.get("total_protein", 0),
        "carbs_g": result.get("total_carbs", 0),
        "fat_g": result.get("total_fat", 0),
    }
