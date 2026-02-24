#!/usr/bin/env python3
"""测试AI分析功能"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision
import asyncio


async def test_ai_analysis():
    print("测试AI分析功能")
    print("=" * 50)

    # 检查API Key
    print(f"QWEN_API_KEY 是否设置: {bool(settings.QWEN_API_KEY)}")
    if settings.QWEN_API_KEY:
        print(f"API Key 长度: {len(settings.QWEN_API_KEY)}")
        print(f"API Key 前10位: {settings.QWEN_API_KEY[:10]}...")
    else:
        print("警告: QWEN_API_KEY 未设置!")

    # 测试分析函数（使用模拟的base64图像数据）
    print("\n测试 analyze_food_with_qwen_vision 函数...")

    # 创建一个模拟的base64图像数据（实际上是一个很小的无效图像）
    mock_base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    try:
        result = await analyze_food_with_qwen_vision(mock_base64_image)
        print(f"分析结果类型: {type(result)}")
        print(f"是否包含 items: {'items' in result}")

        if "items" in result:
            print(f"食材数量: {len(result['items'])}")
            for i, item in enumerate(result["items"], 1):
                print(f"  食材{i}: {item.get('name')} - {item.get('grams')}g")

        print(f"总热量: {result.get('total_calories')} kcal")
        print(f"备注: {result.get('notes')}")

        # 检查是否是模拟数据
        if "模拟数据" in str(result.get("notes", "")):
            print("\n⚠️  注意: 返回的是模拟数据，可能因为:")
            print("  1. QWEN_API_KEY 未正确设置")
            print("  2. API Key 无效")
            print("  3. 网络连接问题")
        else:
            print("\n✅ AI分析功能正常!")

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ai_analysis())
