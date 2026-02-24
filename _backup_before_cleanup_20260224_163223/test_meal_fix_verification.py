#!/usr/bin/env python3
"""测试修复后的餐食API"""

import requests
import json
from pathlib import Path
from datetime import datetime

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_TOKEN_FILE = "/Users/felix/bmad/test_token.txt"


def read_token():
    """读取测试token"""
    if Path(TEST_TOKEN_FILE).exists():
        with open(TEST_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def test_meal_with_items():
    """测试包含食材的餐食"""
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 创建测试餐食
    meal_data = {
        "name": "修复测试午餐",
        "meal_type": "lunch",
        "calories": 715,
        "protein": 35,
        "carbs": 80,
        "fat": 25,
        "notes": "修复测试",
        "meal_datetime": "2026-02-24T12:00:00+08:00",
        "items": [
            {
                "name": "测试面条",
                "serving_size": 150,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 174,
                "protein_per_serving": 3,
                "carbs_per_serving": 38,
                "fat_per_serving": 0.5,
            }
        ],
    }

    print("创建测试餐食...")
    response = requests.post(
        f"{BASE_URL}/meals", headers=headers, json=meal_data, timeout=30
    )

    print(f"创建响应: {response.status_code}")

    if response.status_code in [200, 201]:
        meal = response.json()
        print(f"✅ 餐食创建成功，ID: {meal.get('id')}")

        # 检查返回的items
        items = meal.get("items", [])
        print(f"返回的items数量: {len(items)}")

        if items:
            print("✅ 餐食包含食材详情!")
            for item in items:
                print(f"  食材: {item.get('name')}")
        else:
            print("❌ 餐食没有食材详情")

        # 获取今日餐食
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n获取 {today} 的餐食记录...")

        response = requests.get(
            f"{BASE_URL}/meals/daily-nutrition-summary",
            headers=headers,
            params={"target_date": today},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            meals = data.get("meals", [])
            print(f"获取到 {len(meals)} 条餐食记录")

            for meal in meals:
                items = meal.get("items", [])
                print(f"餐食ID {meal.get('id')} 有 {len(items)} 个食材")

                if items:
                    print("✅ 前端应该能显示食材详情了!")
                    print("  食材列表:")
                    for item in items:
                        print(
                            f"    - {item.get('name')} ({item.get('serving_size')}{item.get('serving_unit')})"
                        )
                else:
                    print("❌ 仍然没有食材详情")
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(f"响应: {response.text[:500]}")


if __name__ == "__main__":
    test_meal_with_items()
