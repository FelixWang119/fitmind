#!/usr/bin/env python3
"""
测试照片识别功能是否调用AI
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import asyncio
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision
from app.core.config import settings


async def test_photo_analysis():
    """测试照片分析功能"""

    print("测试照片分析功能...")
    print("=" * 60)

    # 检查API密钥
    print(f"1. 检查QWEN_API_KEY: {'已设置' if settings.QWEN_API_KEY else '未设置'}")
    if settings.QWEN_API_KEY:
        print(f"   API密钥前几位: {settings.QWEN_API_KEY[:10]}...")
    else:
        print("   ⚠️ 警告: QWEN_API_KEY未设置，将使用模拟数据")

    # 创建一个模拟的base64图像数据（只是一个测试字符串）
    test_base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # 1x1像素的透明PNG

    print(f"\n2. 调用analyze_food_with_qwen_vision...")
    try:
        result = await analyze_food_with_qwen_vision(test_base64_image)

        print(f"   调用成功!")
        print(f"   返回结果类型: {type(result)}")
        print(f"   是否有'items'字段: {'items' in result}")
        print(f"   items数量: {len(result.get('items', []))}")
        print(f"   餐次类型: {result.get('meal_type', 'N/A')}")
        print(f"   总热量: {result.get('total_calories', 'N/A')}")
        print(f"   备注: {result.get('notes', 'N/A')}")

        # 检查是否是模拟数据
        notes = result.get("notes", "")
        if "模拟" in notes or "未设置API Key" in notes or "AI服务暂时不可用" in notes:
            print(f"\n   ⚠️ 注意: 返回的是模拟数据!")
            print(f"   原因: {notes}")
        else:
            print(f"\n   ✅ 成功调用AI分析!")

    except Exception as e:
        print(f"   调用失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_photo_analysis())
