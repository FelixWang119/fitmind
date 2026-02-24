#!/usr/bin/env python3
"""
简单测试前端修复
"""

import base64
import requests
import json
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


def main():
    """主函数"""
    print("测试前端修复")
    print("=" * 60)

    # 读取token
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        return

    print(f"✅ 使用token: {token[:20]}...")

    # 使用测试图片
    test_image = "/Users/felix/bmad/backend/tests/mealimg/lunch.jpg"
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return

    # 读取图片
    with open(test_image, "rb") as f:
        image_data = f.read()

    # 转换为base64
    base64_string = base64.b64encode(image_data).decode("utf-8")

    # 创建data URL（前端修复前的错误格式）
    data_url = f"data:image/jpeg;base64,{base64_string}"

    # 纯base64（前端修复后的正确格式）
    pure_base64 = base64_string

    print(f"\n📊 测试数据:")
    print(f"  图片大小: {len(image_data):,} 字节")
    print(f"  Base64长度: {len(base64_string):,} 字符")
    print(f"  Data URL长度: {len(data_url):,} 字符")

    # 测试函数
    def test_format(name, image_data):
        print(f"\n🔍 测试: {name}")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {"image": image_data, "date": "2026-02-24"}

        try:
            response = requests.post(
                f"{BASE_URL}/nutrition/analyze-food-image",
                headers=headers,
                json=payload,
                timeout=30,
            )

            print(f"  状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                notes = result.get("notes", "")

                if "模拟数据" in notes:
                    print(f"  ❌ 返回模拟数据")
                    print(f"  原因: {notes[:100]}...")

                    # 检查是否是红烧肉和米饭
                    items = result.get("items", [])
                    item_names = [item.get("name", "") for item in items]
                    if "红烧肉" in item_names and "米饭" in item_names:
                        print(f"  🔍 找到红烧肉和米饭！")
                        return False
                    else:
                        return False
                else:
                    print(f"  ✅ 真实千问分析")
                    print(f"  餐型: {result.get('meal_type')}")
                    print(f"  食材数: {len(result.get('items', []))}")
                    print(f"  总热量: {result.get('total_calories')} 卡路里")
                    return True
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return False

    # 测试1: 前端修复前（错误格式）
    print("\n" + "=" * 60)
    print("测试1: 前端修复前（发送完整data URL）")
    print("=" * 60)
    result1 = test_format("发送完整data URL", data_url)

    # 测试2: 前端修复后（正确格式）
    print("\n" + "=" * 60)
    print("测试2: 前端修复后（发送纯base64）")
    print("=" * 60)
    result2 = test_format("发送纯base64", pure_base64)

    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)

    if result1 == False and result2 == True:
        print("✅ 测试通过！")
        print("  前端修复前: ❌ 返回模拟数据（红烧肉和米饭）")
        print("  前端修复后: ✅ 返回真实千问分析")
        print("\n🎯 问题已确认并修复:")
        print("  1. 前端使用 readAsDataURL() 返回完整data URL")
        print("  2. 后端期望纯base64字符串")
        print("  3. 修复: 从data URL中提取纯base64部分")
    else:
        print("❌ 测试失败")
        print("  需要进一步调试")


if __name__ == "__main__":
    main()
