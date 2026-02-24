#!/usr/bin/env python3
"""
测试settings配置加载
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings

print("测试settings配置加载...")
print("=" * 60)

print(f"1. 当前工作目录: {os.getcwd()}")
print(f"2. .env文件路径: {os.path.join(os.getcwd(), 'backend/.env')}")
print(f"3. .env文件存在: {os.path.exists(os.path.join(os.getcwd(), 'backend/.env'))}")

print(f"\n4. Settings配置:")
print(f"   QWEN_API_KEY: {settings.QWEN_API_KEY}")
print(f"   QWEN_API_URL: {settings.QWEN_API_URL}")
print(f"   QWEN_MODEL: {settings.QWEN_MODEL}")
print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")

# 检查是否是模拟密钥
if settings.QWEN_API_KEY and settings.QWEN_API_KEY.startswith("mock_key_"):
    print(f"\n⚠️ 警告: 使用的是模拟API密钥!")
    print(f"   实际密钥: {settings.QWEN_API_KEY[:20]}...")
elif settings.QWEN_API_KEY:
    print(f"\n✅ API密钥格式正确: {settings.QWEN_API_KEY[:10]}...")
else:
    print(f"\n❌ 错误: QWEN_API_KEY未设置!")

# 检查环境变量
print(f"\n5. 环境变量检查:")
print(f"   os.environ.get('QWEN_API_KEY'): {os.environ.get('QWEN_API_KEY', '未设置')}")
print(f"   os.environ.get('ENVIRONMENT'): {os.environ.get('ENVIRONMENT', '未设置')}")
