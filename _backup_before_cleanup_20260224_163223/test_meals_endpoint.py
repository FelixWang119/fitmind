#!/usr/bin/env python3
"""测试meals端点是否工作"""

import requests
import json

# 获取token
with open("/Users/felix/bmad/test_token.txt", "r") as f:
    token = f.read().strip()

print(f"Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 测试1: 获取所有meals
print("\n1. 测试获取所有meals...")
try:
    response = requests.get(
        "http://localhost:8000/api/v1/meals", headers=headers, timeout=10
    )
    print(f"   状态: {response.status_code}")
    if response.status_code == 200:
        meals = response.json()
        print(f"   ✅ 成功获取 {len(meals)} 个meal")
        if meals:
            print(f"   第一个meal: {meals[0].get('name')}")
            print(f"   是否有items字段: {'items' in meals[0]}")
            if "items" in meals[0]:
                print(f"   items数量: {len(meals[0]['items'])}")
    else:
        print(f"   ❌ 失败: {response.text}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试2: 创建meal
print("\n2. 测试创建meal...")
from datetime import datetime, timezone

meal_data = {
    "meal_type": "dinner",
    "name": "测试晚餐",
    "meal_datetime": datetime.now(timezone.utc).isoformat(),
    "notes": "API测试",
    "items": [
        {
            "name": "测试食物",
            "serving_size": 100,
            "serving_unit": "g",
            "quantity": 1,
            "calories_per_serving": 200,
        }
    ],
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/meals",
        json=meal_data,
        headers=headers,
        timeout=10,
    )
    print(f"   状态: {response.status_code}")
    if response.status_code == 201:
        meal = response.json()
        print(f"   ✅ 成功创建meal ID: {meal.get('id')}")
        print(f"   响应字段: {list(meal.keys())}")

        if "items" in meal:
            print(f"   ✅ meal包含items字段，数量: {len(meal['items'])}")
        elif "meal_items" in meal:
            print(f"   ⚠️ meal包含meal_items字段 (不是items)")
        else:
            print(f"   ❌ meal没有items字段")
            print(f"   完整响应: {json.dumps(meal, indent=2, ensure_ascii=False)}")

        # 测试获取刚创建的meal
        meal_id = meal.get("id")
        print(f"\n3. 测试获取刚创建的meal (ID: {meal_id})...")
        response = requests.get(
            f"http://localhost:8000/api/v1/meals/{meal_id}", headers=headers, timeout=10
        )
        print(f"   状态: {response.status_code}")
        if response.status_code == 200:
            retrieved_meal = response.json()
            print(f"   ✅ 成功获取meal")
            if "items" in retrieved_meal:
                print(
                    f"   ✅ 获取的meal包含items字段，数量: {len(retrieved_meal['items'])}"
                )
            else:
                print(f"   ❌ 获取的meal没有items字段")
    else:
        print(f"   ❌ 创建失败: {response.text}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 50)
print("测试完成")
