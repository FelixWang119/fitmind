#!/usr/bin/env python3
"""
测试真实的照片识别功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import asyncio
import base64
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision
from app.core.config import settings


async def test_real_photo_analysis():
    """测试真实的照片分析功能"""

    print("测试真实的照片分析功能...")
    print("=" * 60)

    # 检查API密钥
    print(f"1. 检查QWEN_API_KEY: {'已设置' if settings.QWEN_API_KEY else '未设置'}")
    if settings.QWEN_API_KEY:
        print(f"   API密钥: {settings.QWEN_API_KEY[:10]}...")
        if settings.QWEN_API_KEY.startswith("mock_key_"):
            print("   ⚠️ 警告: 使用的是模拟API密钥!")
            return
    else:
        print("   ❌ 错误: QWEN_API_KEY未设置!")
        return

    # 创建一个更真实的测试图像（一个小尺寸的简单图像）
    # 使用一个简单的base64编码的1x1红色像素JPEG
    # 这是一个有效的JPEG图像base64编码
    test_base64_image = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="

    print(f"\n2. 测试图像信息:")
    print(f"   Base64长度: {len(test_base64_image)}")
    print(f"   解码后长度: {len(base64.b64decode(test_base64_image))} bytes")

    print(f"\n3. 调用analyze_food_with_qwen_vision...")
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

            # 检查错误详情
            if "400" in notes:
                print(f"   ❌ API返回400错误: 请求格式可能有问题")
            elif "401" in notes:
                print(f"   ❌ API返回401错误: API密钥无效")
            elif "网络错误" in notes:
                print(f"   ❌ 网络错误: 可能无法连接到API服务")
        else:
            print(f"\n   ✅ 成功调用AI分析!")

    except Exception as e:
        print(f"   调用失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_real_photo_analysis())
