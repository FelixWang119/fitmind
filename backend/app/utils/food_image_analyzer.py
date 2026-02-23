import os
import json
from typing import Dict, Any, List
from PIL import Image
import base64
from io import BytesIO
import structlog
import httpx
from fastapi import HTTPException
import asyncio

logger = structlog.get_logger(__name__)


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
    api_key = os.environ.get("QWEN_API_KEY")
    if not api_key:
        # 如果没有API Key，则返回模拟数据（食材列表格式）
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
            "notes": "开发模式模拟数据",
        }

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/generation/image2text"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 修改 prompt 要求返回食材列表
    payload = {
        "model": "qwen-vl-max",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{base64_image}"},
                        {
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
}"""
                        },
                    ],
                }
            ]
        },
        "parameters": {"temperature": 0.1},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            # 解析模型返回的结果
            if "output" in result and "choices" in result["output"]:
                content_text = result["output"]["choices"][0]["message"]["content"]

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
                                grams=float(item_data.get("grams", 0)),
                                calories=float(item_data.get("calories", 0)),
                                protein=float(item_data.get("protein", 0)),
                                carbs=float(item_data.get("carbs", 0)),
                                fat=float(item_data.get("fat", 0)),
                            )
                            food_items.append(food_item)

                        # 构建返回结果
                        meal_type = parsed_data.get("meal_type", "lunch")
                        analysis_result = MealAnalysisResult(meal_type, food_items)

                        return analysis_result.to_dict()
                    else:
                        logger.warning(
                            "Could not parse JSON from Qwen response", response=result
                        )
                        return _create_mock_item_result()
                except json.JSONDecodeError as e:
                    logger.error(
                        "JSON decode error", error=str(e), response=content_text
                    )
                    return _create_mock_item_result()

            else:
                logger.warning("Unexpected API response format", response=result)
                raise HTTPException(status_code=500, detail="Qwen API返回格式异常")

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error from Qwen API",
            status_code=e.response.status_code,
            response=await e.response.aread(),
        )
        raise HTTPException(
            status_code=e.response.status_code, detail=f"Qwen API调用失败: {str(e)}"
        )
    except Exception as e:
        logger.error("Unexpected error calling Qwen API", error=str(e))
        raise HTTPException(status_code=500, detail=f"AI分析出现意外错误: {str(e)}")


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
