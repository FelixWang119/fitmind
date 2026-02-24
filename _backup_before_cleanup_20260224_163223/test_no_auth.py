#!/usr/bin/env python3
"""测试无认证的端点"""

import requests

print("测试无认证的端点...")

# 测试1: health端点（不需要认证）
print("\n1. 测试health端点...")
try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.text[:100]}...")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试2: meals端点（需要认证，应该返回401）
print("\n2. 测试meals端点（无认证）...")
try:
    response = requests.get("http://localhost:8000/api/v1/meals", timeout=5)
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.text[:100]}...")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试3: 使用错误的token
print("\n3. 测试meals端点（错误token）...")
try:
    headers = {"Authorization": "Bearer wrong_token"}
    response = requests.get(
        "http://localhost:8000/api/v1/meals", headers=headers, timeout=5
    )
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.text[:100]}...")
except Exception as e:
    print(f"   ❌ 错误: {e}")
