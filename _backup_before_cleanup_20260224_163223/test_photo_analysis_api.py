#!/usr/bin/env python3
"""
测试照片分析API是否调用AI
"""

import sys
import os
import requests
import json
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def get_test_image_base64():
    """获取测试图像的base64编码"""
    from app.core.test_resources import TestResources

    try:
        return TestResources.encode_image_to_base64("lunch")
    except Exception as e:
        print(f"❌ 无法获取测试图像: {e}")
        # 返回一个简单的测试base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def test_photo_analysis_direct():
    """直接测试照片分析功能"""
    print("直接测试照片分析功能...")
    print("=" * 60)

    try:
        from app.utils.food_image_analyzer import analyze_food_with_qwen_vision
        from app.core.qwen_config import qwen_config

        print(f"1. Qwen配置状态:")
        validation = qwen_config.validate_configuration()
        print(f"   API密钥配置: {validation['api_key_configured']}")
        print(f"   视觉模型: {validation['vision_model']}")
        print(f"   状态: {validation['status']}")

        if not validation["api_key_configured"]:
            print("   ⚠️ 警告: QWEN_API_KEY未设置，将使用模拟数据")

        # 获取测试图像
        test_base64 = get_test_image_base64()
        print(f"\n2. 测试图像信息:")
        print(f"   Base64长度: {len(test_base64)}")

        print(f"\n3. 调用analyze_food_with_qwen_vision...")
        import asyncio

        result = asyncio.run(analyze_food_with_qwen_vision(test_base64))

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
            return False
        else:
            print(f"\n   ✅ 成功调用AI分析!")
            return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_photo_analysis_api():
    """测试照片分析API端点"""
    print("\n测试照片分析API端点...")
    print("=" * 60)

    # 获取测试图像
    test_base64 = get_test_image_base64()

    # 构建请求
    url = "http://localhost:8000/api/v1/nutrition/analyze-food-image"
    headers = {"Content-Type": "application/json"}

    # 由于需要认证，我们先尝试直接调用
    print("⚠️  API需要认证，跳过直接API测试")
    print("   使用直接函数调用测试...")

    return True


def main():
    """主测试函数"""
    print("测试照片分析功能是否调用AI")
    print("=" * 60)

    # 测试直接功能
    direct_result = test_photo_analysis_direct()

    # 测试API端点
    api_result = test_photo_analysis_api()

    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    if direct_result:
        print("✅ 照片分析功能正常工作")
        print("\n如果前端仍然返回模拟数据，可能是以下原因:")
        print("1. 前端没有正确发送base64图像数据")
        print("2. 前端发送的数据格式不正确")
        print("3. API认证问题")
        print("\n建议检查:")
        print("1. 前端开发者工具网络请求")
        print("2. 后端日志输出")
        print("3. QWEN_API_KEY是否已设置")
    else:
        print("❌ 照片分析功能有问题")
        print("\n可能的原因:")
        print("1. QWEN_API_KEY未设置")
        print("2. 网络连接问题")
        print("3. Qwen API服务不可用")
        print("\n解决方案:")
        print("1. 检查.env文件中的QWEN_API_KEY")
        print("2. 运行: python validate_infrastructure.py")
        print("3. 检查网络连接")

    return 0 if direct_result else 1


if __name__ == "__main__":
    sys.exit(main())
