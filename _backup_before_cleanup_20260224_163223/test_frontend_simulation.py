#!/usr/bin/env python3
"""
模拟前端集成测试，找出为什么返回模拟数据（红烧肉和米饭）

前端可能的问题：
1. 图像格式不正确
2. base64编码有问题
3. 请求格式不对
4. 触发了fallback机制
"""

import base64
import requests
import json
import sys
from pathlib import Path

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_TOKEN_FILE = "/Users/felix/bmad/test_token.txt"


def read_token():
    """读取测试token"""
    if Path(TEST_TOKEN_FILE).exists():
        with open(TEST_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def test_different_formats(image_path, token):
    """测试不同的请求格式，找出前端的问题"""
    print(f"\n测试图片: {image_path}")

    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()

    # 不同的base64编码方式
    base64_standard = base64.b64encode(image_data).decode("utf-8")

    # 前端可能使用的格式
    test_cases = [
        {
            "name": "标准格式（我们测试成功的）",
            "payload": {"image": base64_standard, "date": "2026-02-24"},
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        },
        {
            "name": "前端可能格式1 - 缺少date字段",
            "payload": {"image": base64_standard},
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        },
        {
            "name": "前端可能格式2 - 错误的Content-Type",
            "payload": {"image": base64_standard, "date": "2026-02-24"},
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "multipart/form-data",
            },
        },
        {
            "name": "前端可能格式3 - 使用FormData格式",
            "data": {"image": base64_standard, "date": "2026-02-24"},
            "headers": {"Authorization": f"Bearer {token}"},
        },
        {
            "name": "前端可能格式4 - 包含data:image前缀",
            "payload": {
                "image": f"data:image/jpeg;base64,{base64_standard}",
                "date": "2026-02-24",
            },
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        },
        {
            "name": "前端可能格式5 - 图像数据损坏（截断）",
            "payload": {
                "image": base64_standard[:1000],
                "date": "2026-02-24",
            },  # 截断的base64
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        },
        {
            "name": "前端可能格式6 - 空图像",
            "payload": {"image": "", "date": "2026-02-24"},
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n  [{i + 1}] {test_case['name']}")

        try:
            if "payload" in test_case:
                response = requests.post(
                    f"{BASE_URL}/nutrition/analyze-food-image",
                    json=test_case["payload"],
                    headers=test_case["headers"],
                    timeout=30,
                )
            elif "data" in test_case:
                response = requests.post(
                    f"{BASE_URL}/nutrition/analyze-food-image",
                    data=test_case["data"],
                    headers=test_case["headers"],
                    timeout=30,
                )

            print(f"    状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                notes = result.get("notes", "")

                if "模拟数据" in notes:
                    print(f"    ❌ 返回模拟数据")
                    print(f"    原因: {notes[:100]}...")

                    # 检查是否是红烧肉和米饭
                    items = result.get("items", [])
                    item_names = [item.get("name", "") for item in items]
                    if "红烧肉" in item_names and "米饭" in item_names:
                        print(f"    🔍 找到红烧肉和米饭！这就是前端的问题！")
                        results.append(
                            {
                                "test": test_case["name"],
                                "result": "模拟数据（红烧肉和米饭）",
                                "notes": notes,
                            }
                        )
                    else:
                        print(f"    ⚠️  模拟数据，但不是红烧肉和米饭")
                        results.append(
                            {
                                "test": test_case["name"],
                                "result": "模拟数据（其他）",
                                "notes": notes,
                            }
                        )
                else:
                    print(f"    ✅ 真实千问分析")
                    print(
                        f"    餐型: {result.get('meal_type')}, 食材数: {len(result.get('items', []))}"
                    )
                    results.append(
                        {
                            "test": test_case["name"],
                            "result": "真实分析",
                            "meal_type": result.get("meal_type"),
                            "item_count": len(result.get("items", [])),
                        }
                    )
            else:
                print(f"    ❌ 请求失败: {response.status_code}")
                print(f"    响应: {response.text[:200]}")
                results.append(
                    {
                        "test": test_case["name"],
                        "result": f"失败 {response.status_code}",
                        "error": response.text[:200],
                    }
                )

        except Exception as e:
            print(f"    ❌ 异常: {e}")
            results.append(
                {"test": test_case["name"], "result": f"异常: {str(e)[:100]}"}
            )

    return results


def check_fallback_mechanism():
    """检查fallback机制"""
    print("\n检查fallback机制...")

    # 查看food_image_analyzer.py中的fallback数据
    analyzer_file = "/Users/felix/bmad/backend/app/utils/food_image_analyzer.py"
    with open(analyzer_file, "r") as f:
        content = f.read()

    # 查找get_fallback_data函数
    if "def get_fallback_data" in content:
        start = content.find("def get_fallback_data")
        end = content.find("def ", start + 1)
        fallback_section = content[start:end]

        print("  ✅ 找到get_fallback_data函数")

        # 检查是否包含红烧肉和米饭
        if "红烧肉" in fallback_section and "米饭" in fallback_section:
            print("  🔍 fallback数据包含红烧肉和米饭！")

            # 提取fallback数据
            lines = fallback_section.split("\n")
            for i, line in enumerate(lines):
                if "红烧肉" in line or "米饭" in line:
                    print(f"    行 {i + 1}: {line.strip()}")
        else:
            print("  ⚠️  fallback数据不包含红烧肉和米饭")
    else:
        print("  ❌ 没有找到get_fallback_data函数")


def check_api_endpoint_logic():
    """检查API端点逻辑"""
    print("\n检查API端点逻辑...")

    endpoint_file = "/Users/felix/bmad/backend/app/api/v1/endpoints/nutrition.py"
    with open(endpoint_file, "r") as f:
        content = f.read()

    # 查找analyze_food_image_endpoint_unique函数
    if "def analyze_food_image_endpoint_unique" in content:
        start = content.find("def analyze_food_image_endpoint_unique")
        end = content.find("def ", start + 1)
        endpoint_section = content[start:end]

        print("  ✅ 找到analyze_food_image_endpoint_unique函数")

        # 检查异常处理
        lines = endpoint_section.split("\n")
        for i, line in enumerate(lines):
            if "except Exception" in line or "except HTTPException" in line:
                print(f"    行 {i + 1}: {line.strip()}")
                # 查看接下来的几行
                for j in range(i + 1, min(i + 5, len(lines))):
                    print(f"        {lines[j].strip()}")

    # 检查是否有模拟实现
    if (
        "def analyze_food_with_qwen_vision(image_data)" in content
        and "模拟食物分析实现" in content
    ):
        print("  ⚠️  找到模拟实现（当导入失败时使用）")


def check_frontend_code():
    """检查前端代码如何调用API"""
    print("\n检查前端代码...")

    # 查找前端调用analyze-food-image的代码
    frontend_dir = "/Users/felix/bmad/frontend"

    # 使用简单的grep（在实际环境中应该用更复杂的方法）
    import subprocess

    try:
        result = subprocess.run(
            ["grep", "-r", "analyze-food-image", frontend_dir],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print("  ✅ 找到前端调用analyze-food-image的代码:")
            lines = result.stdout.split("\n")[:10]  # 只显示前10行
            for line in lines:
                if line:
                    print(f"    {line}")
        else:
            print("  ⚠️  没有找到analyze-food-image的调用")

    except:
        print("  ⚠️  无法搜索前端代码")


def main():
    """主函数"""
    print("=" * 70)
    print("分析前端集成测试返回模拟数据（红烧肉和米饭）的问题")
    print("=" * 70)

    # 读取token
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        print("   运行: python test_direct_token.py")
        return

    print(f"✅ 使用token: {token[:20]}...")

    # 使用一个测试图片
    test_image = "/Users/felix/bmad/backend/tests/mealimg/lunch.jpg"
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return

    # 1. 检查fallback机制
    check_fallback_mechanism()

    # 2. 检查API端点逻辑
    check_api_endpoint_logic()

    # 3. 检查前端代码
    check_frontend_code()

    # 4. 测试不同的格式
    print("\n" + "=" * 70)
    print("测试不同的请求格式...")
    print("=" * 70)

    results = test_different_formats(test_image, token)

    # 总结
    print("\n" + "=" * 70)
    print("问题分析总结")
    print("=" * 70)

    print("\n可能的原因:")

    # 分析结果
    sim_count = sum(1 for r in results if "模拟数据" in str(r.get("result", "")))
    real_count = sum(1 for r in results if "真实分析" in str(r.get("result", "")))

    print(f"  模拟数据次数: {sim_count}")
    print(f"  真实分析次数: {real_count}")

    # 找出哪些测试返回了模拟数据
    sim_tests = [r for r in results if "模拟数据" in str(r.get("result", ""))]

    if sim_tests:
        print("\n🔍 以下测试返回了模拟数据:")
        for test in sim_tests:
            print(f"  - {test['test']}")
            print(f"    结果: {test['result']}")
            if "notes" in test:
                print(f"    备注: {test['notes'][:100]}...")

    # 推测前端的问题
    print("\n🤔 推测前端可能的问题:")
    print("  1. 图像数据格式不正确（可能包含data:image前缀或不包含）")
    print("  2. 图像数据损坏或截断")
    print("  3. 请求格式错误（Content-Type、JSON格式等）")
    print("  4. 触发了fallback机制（API Key问题、网络问题等）")

    print("\n🔧 建议的解决方案:")
    print("  1. 检查前端如何编码和发送图像数据")
    print("  2. 在前端添加调试日志，记录发送的数据")
    print("  3. 比较前端发送的数据和我们测试成功的数据")
    print("  4. 确保前端使用正确的Content-Type: application/json")
    print("  5. 确保图像数据是纯base64，没有data:image前缀")


if __name__ == "__main__":
    main()
