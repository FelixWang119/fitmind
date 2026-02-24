#!/usr/bin/env python3
"""
测试配置修复是否生效
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings

print("测试配置修复...")
print("=" * 60)

print(f"1. 文本模型配置:")
print(f"   QWEN_TEXT_MODEL: {settings.QWEN_TEXT_MODEL}")
print(f"   预期: qwen-turbo")

print(f"\n2. 视觉模型配置:")
print(f"   QWEN_VISION_MODEL: {settings.QWEN_VISION_MODEL}")
print(f"   预期: qwen-vl-max")

print(f"\n3. API密钥:")
print(f"   QWEN_API_KEY: {settings.QWEN_API_KEY[:10]}...")

print(f"\n4. 检查food_image_analyzer导入:")
try:
    from app.utils.food_image_analyzer import analyze_food_with_qwen_vision

    print("   ✅ 导入成功")

    # 检查函数是否使用正确的模型
    import inspect

    source = inspect.getsource(analyze_food_with_qwen_vision)
    if "settings.QWEN_VISION_MODEL" in source:
        print("   ✅ 使用配置的视觉模型")
    else:
        print("   ❌ 未使用配置的视觉模型")

except ImportError as e:
    print(f"   ❌ 导入失败: {e}")

print(f"\n5. 验证.env文件:")
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
        if "QWEN_TEXT_MODEL" in content and "QWEN_VISION_MODEL" in content:
            print("   ✅ .env文件包含分离的模型配置")
        else:
            print("   ❌ .env文件缺少分离的模型配置")
else:
    print("   ❌ .env文件不存在")
