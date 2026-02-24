#!/usr/bin/env python3
"""
测试餐食记录中的食材详情问题

问题：保存后，今日餐食记录里没有"食材详情"
可能原因：
1. 后端没有正确保存items
2. 后端API返回的数据格式不对
3. 前端显示逻辑有问题
"""

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


def test_create_meal_with_items(token):
    """测试创建包含食材的餐食记录"""
    print("测试创建包含食材的餐食记录...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 模拟前端发送的数据格式
    meal_data = {
        "name": "测试午餐",
        "meal_type": "lunch",
        "calories": 715,
        "protein": 35,
        "carbs": 80,
        "fat": 25,
        "notes": "测试餐食",
        "meal_datetime": "2026-02-24T12:00:00+08:00",
        "items": [
            {
                "name": "面条",
                "serving_size": 150,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 174,
                "protein_per_serving": 3,
                "carbs_per_serving": 38,
                "fat_per_serving": 0.5,
            },
            {
                "name": "牛肉片",
                "serving_size": 80,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 200,
                "protein_per_serving": 20,
                "carbs_per_serving": 0,
                "fat_per_serving": 12,
            },
            {
                "name": "肉丸",
                "serving_size": 60,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 150,
                "protein_per_serving": 12,
                "carbs_per_serving": 5,
                "fat_per_serving": 10,
            },
        ],
    }

    try:
        # 创建餐食
        print("创建餐食记录...")
        response = requests.post(
            f"{BASE_URL}/meals", headers=headers, json=meal_data, timeout=30
        )

        print(f"创建响应状态: {response.status_code}")

        if response.status_code in [200, 201]:
            created_meal = response.json()
            print(f"✅ 餐食创建成功!")
            print(f"   餐食ID: {created_meal.get('id')}")
            print(f"   名称: {created_meal.get('name')}")
            print(f"   餐型: {created_meal.get('meal_type')}")

            # 检查返回的items
            items = created_meal.get("items", [])
            print(f"   返回的items数量: {len(items)}")

            if items:
                print("   ✅ 餐食包含食材详情:")
                for i, item in enumerate(items[:3]):  # 只显示前3个
                    print(
                        f"     食材{i + 1}: {item.get('name')} ({item.get('serving_size')}{item.get('serving_unit')})"
                    )
            else:
                print("   ❌ 餐食没有返回食材详情")

            return created_meal.get("id")
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"❌ 创建餐食异常: {e}")
        return None


def test_get_daily_meals(token, date):
    """测试获取每日餐食"""
    print(f"\n获取 {date} 的餐食记录...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.get(
            f"{BASE_URL}/meals/daily-nutrition-summary",
            headers=headers,
            params={"target_date": date},
            timeout=30,
        )

        print(f"获取响应状态: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            meals = data.get("meals", [])
            print(f"✅ 获取到 {len(meals)} 条餐食记录")

            for i, meal in enumerate(meals):
                print(f"\n  餐食{i + 1}:")
                print(f"    ID: {meal.get('id')}")
                print(f"    名称: {meal.get('name')}")
                print(f"    餐型: {meal.get('meal_type')}")
                print(f"    热量: {meal.get('calories')} 卡路里")

                # 检查items
                items = meal.get("items", [])
                print(f"    食材数量: {len(items)}")

                if items:
                    print("    ✅ 包含食材详情:")
                    for j, item in enumerate(items[:3]):  # 只显示前3个
                        print(
                            f"       食材{j + 1}: {item.get('name')} ({item.get('serving_size')}{item.get('serving_unit')})"
                        )
                else:
                    print("    ❌ 没有食材详情")

                    # 检查是否有其他字段包含食材信息
                    print(f"    所有字段: {list(meal.keys())}")

            return meals
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return []

    except Exception as e:
        print(f"❌ 获取餐食异常: {e}")
        return []


def test_meal_api_structure(token):
    """测试餐食API的数据结构"""
    print("\n测试餐食API数据结构...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 先获取今天的餐食
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        response = requests.get(
            f"{BASE_URL}/meals/daily-nutrition-summary",
            headers=headers,
            params={"target_date": today},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"API返回数据结构:")
            print(f"  根字段: {list(data.keys())}")

            if "meals" in data:
                meals = data["meals"]
                if meals:
                    meal = meals[0]
                    print(f"\n  第一条餐食的字段:")
                    print(f"    字段列表: {list(meal.keys())}")

                    # 特别检查items字段
                    if "items" in meal:
                        items = meal["items"]
                        print(f"    items类型: {type(items)}")
                        print(f"    items长度: {len(items)}")

                        if items:
                            item = items[0]
                            print(f"\n    第一条食材的字段:")
                            print(f"      字段列表: {list(item.keys())}")
                            print(f"      示例数据: {item}")
                    else:
                        print(f"    ❌ meal对象没有items字段")
            else:
                print(f"  ❌ 返回数据没有meals字段")

    except Exception as e:
        print(f"❌ 测试API结构异常: {e}")


def test_backend_meal_model():
    """检查后端餐食模型"""
    print("\n检查后端餐食模型...")

    # 查看后端模型定义
    model_file = "/Users/felix/bmad/backend/app/models/meal.py"
    if Path(model_file).exists():
        with open(model_file, "r") as f:
            content = f.read()

        # 查找items关系定义
        if "items = relationship" in content:
            print("  ✅ 后端模型定义了items关系")

            # 提取相关代码
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "items = relationship" in line:
                    print(f"    行 {i + 1}: {line.strip()}")
                    # 显示上下文
                    for j in range(max(0, i - 2), min(len(lines), i + 3)):
                        print(f"      {lines[j].strip()}")
        else:
            print("  ❌ 后端模型没有定义items关系")
    else:
        print(f"  ❌ 模型文件不存在: {model_file}")


def main():
    """主函数"""
    print("=" * 70)
    print("测试餐食记录中的食材详情问题")
    print("=" * 70)

    # 读取token
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        print("   运行: python test_direct_token.py")
        return

    print(f"✅ 使用token: {token[:20]}...")

    # 1. 测试API数据结构
    test_meal_api_structure(token)

    # 2. 检查后端模型
    test_backend_meal_model()

    # 3. 测试创建包含食材的餐食
    meal_id = test_create_meal_with_items(token)

    # 4. 测试获取餐食
    if meal_id:
        print(f"\n✅ 创建了测试餐食，ID: {meal_id}")

    # 获取今天的餐食
    today = datetime.now().strftime("%Y-%m-%d")
    meals = test_get_daily_meals(token, today)

    # 分析问题
    print("\n" + "=" * 70)
    print("问题分析")
    print("=" * 70)

    if meals:
        for meal in meals:
            items = meal.get("items", [])
            if not items:
                print(f"❌ 餐食ID {meal.get('id')} 没有食材详情")
                print(f"   可能的原因:")
                print(f"   1. 后端没有保存items")
                print(f"   2. 后端API没有返回items")
                print(f"   3. items字段名为其他名称")
                print(f"   4. 数据库关系配置有问题")
            else:
                print(f"✅ 餐食ID {meal.get('id')} 有 {len(items)} 个食材")
    else:
        print("❌ 没有找到餐食记录")

    print("\n🔧 建议的调试步骤:")
    print("   1. 检查后端餐食模型的items关系定义")
    print("   2. 检查后端API端点是否包含items数据")
    print("   3. 检查数据库查询是否包含关联的items")
    print("   4. 在前端添加调试日志，查看API返回的完整数据")


if __name__ == "__main__":
    main()
