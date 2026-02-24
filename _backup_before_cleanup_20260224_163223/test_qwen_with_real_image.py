#!/usr/bin/env python3
"""
使用真实的测试图片测试千问图像识别API

使用项目中的测试图片目录：
- /Users/felix/bmad/backend/tests/mealimg/
- /Users/felix/bmad/lunch.jpg
"""

import base64
import requests
import json
import sys
from pathlib import Path

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_TOKEN_FILE = "/Users/felix/bmad/test_token.txt"

# 测试图片目录
TEST_IMAGE_DIRS = ["/Users/felix/bmad/backend/tests/mealimg/", "/Users/felix/bmad/"]


def read_token():
    """读取测试token"""
    if Path(TEST_TOKEN_FILE).exists():
        with open(TEST_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def find_test_images():
    """查找项目中的测试图片"""
    test_images = []

    for dir_path in TEST_IMAGE_DIRS:
        dir_path_obj = Path(dir_path)
        if dir_path_obj.exists():
            # 查找图片文件
            for ext in [".jpg", ".jpeg", ".png"]:
                for img_file in dir_path_obj.glob(f"*{ext}"):
                    test_images.append(str(img_file))

    # 去重并排序
    test_images = sorted(set(test_images))
    return test_images


def image_to_base64(image_path):
    """将图片转换为base64格式"""
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode("utf-8")
            return base64_string
    except Exception as e:
        print(f"   ❌ 读取图片失败: {e}")
        return None


def test_image_file(image_path, token):
    """测试单个图片文件"""
    print(f"\n测试图片: {image_path}")

    # 获取文件信息
    file_size = Path(image_path).stat().st_size
    print(f"   📁 文件大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")

    # 转换为base64
    base64_image = image_to_base64(image_path)
    if not base64_image:
        return False

    print(f"   🔤 Base64长度: {len(base64_image):,} 字符")

    # 准备API请求
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {"image": base64_image, "date": "2026-02-24"}

    # 调用API
    try:
        print(f"   📤 调用API: {BASE_URL}/nutrition/analyze-food-image")
        response = requests.post(
            f"{BASE_URL}/nutrition/analyze-food-image",
            headers=headers,
            json=payload,
            timeout=60,  # 图像分析可能需要更长时间
        )

        print(f"   📥 响应状态: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API调用成功!")

            # 分析返回结果
            if "notes" in result:
                notes = result.get("notes", "")
                if "模拟数据" in notes:
                    print(f"   ⚠️  返回模拟数据")
                    print(f"   ⚠️  原因: {notes}")

                    # 检查是否有错误信息
                    if "AI服务错误" in notes:
                        # 提取错误信息
                        error_start = notes.find("AI服务错误")
                        error_msg = notes[error_start : error_start + 200] + "..."
                        print(f"   🔍 错误详情: {error_msg}")
                else:
                    print(f"   ✅ 可能使用了真实的千问API")
                    print(f"   📊 分析结果:")
                    print(f"      - 餐型: {result.get('meal_type', '未知')}")
                    print(f"      - 总热量: {result.get('total_calories', 0)} 卡路里")
                    print(f"      - 食材数量: {len(result.get('items', []))}")

                    # 显示前3个食材
                    items = result.get("items", [])
                    for i, item in enumerate(items[:3]):
                        print(
                            f"      - 食材{i + 1}: {item.get('name', '未知')} ({item.get('grams', 0)}g)"
                        )

            return True
        else:
            print(f"   ❌ API调用失败: {response.status_code}")
            print(f"   ❌ 响应: {response.text[:300]}")
            return False

    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器")
        print("     运行: cd /Users/felix/bmad && ./restart_efficient.sh")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时（60秒）")
        return False
    except Exception as e:
        print(f"   ❌ API测试错误: {e}")
        return False


def check_qwen_config():
    """检查千问API配置"""
    print("\n检查千问API配置...")

    # 检查.env文件
    env_file = "/Users/felix/bmad/.env"
    if Path(env_file).exists():
        with open(env_file, "r") as f:
            env_content = f.read()

        if "QWEN_API_KEY" in env_content:
            print("   ✅ .env 文件中包含 QWEN_API_KEY")
            # 提取API Key（隐藏部分）
            lines = env_content.split("\n")
            for line in lines:
                if "QWEN_API_KEY" in line:
                    parts = line.split("=")
                    if len(parts) > 1:
                        key_value = parts[1].strip()
                        if key_value:
                            masked_key = (
                                key_value[:10] + "..." + key_value[-4:]
                                if len(key_value) > 14
                                else "***"
                            )
                            print(f"   🔑 API Key: {masked_key}")
        else:
            print("   ❌ .env 文件中没有 QWEN_API_KEY")
    else:
        print("   ❌ .env 文件不存在")

    # 检查qwen_config.py
    config_file = "/Users/felix/bmad/backend/app/core/qwen_config.py"
    if Path(config_file).exists():
        with open(config_file, "r") as f:
            config_content = f.read()

        if "QWEN_API_KEY" in config_content:
            print("   ✅ qwen_config.py 包含 QWEN_API_KEY 配置")
        else:
            print("   ❌ qwen_config.py 中没有 QWEN_API_KEY 配置")


def main():
    """主函数"""
    print("=" * 70)
    print("使用真实测试图片测试千问图像识别API")
    print("=" * 70)

    # 检查后端是否运行
    print("\n1. 检查后端状态...")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ 后端运行正常")
        else:
            print(f"   ❌ 后端健康检查失败: {health_response.status_code}")
            return
    except:
        print("   ❌ 无法连接到后端")
        print("     运行: cd /Users/felix/bmad && ./restart_efficient.sh")
        return

    # 读取token
    token = read_token()
    if not token:
        print("\n❌ 没有找到测试token")
        print("   运行: python test_direct_token.py")
        return

    print(f"\n✅ 使用token: {token[:20]}...")

    # 检查千问配置
    check_qwen_config()

    # 查找测试图片
    print("\n2. 查找测试图片...")
    test_images = find_test_images()

    if not test_images:
        print("   ❌ 没有找到测试图片")
        print(f"   检查目录: {TEST_IMAGE_DIRS}")
        return

    print(f"   ✅ 找到 {len(test_images)} 个测试图片:")
    for img in test_images:
        print(f"      - {img}")

    # 测试每个图片
    print("\n3. 测试图片分析...")
    success_count = 0

    for i, image_path in enumerate(test_images):
        print(f"\n[{i + 1}/{len(test_images)}] ", end="")
        if test_image_file(image_path, token):
            success_count += 1

    # 总结
    print("\n" + "=" * 70)
    print("测试完成总结")
    print("=" * 70)
    print(f"📊 测试图片总数: {len(test_images)}")
    print(f"✅ 成功调用: {success_count}")
    print(f"❌ 失败: {len(test_images) - success_count}")

    if success_count > 0:
        print("\n🎉 千问图像识别API测试成功!")
        print("   系统能够接受base64格式的图像并进行处理")
    else:
        print("\n⚠️  所有测试都失败了")
        print("   可能的原因:")
        print("   1. 千问API Key未正确配置")
        print("   2. 图像格式或尺寸不符合要求")
        print("   3. 网络连接问题")
        print("   4. API服务暂时不可用")

    print("\n🔧 下一步:")
    print("   1. 检查 .env 文件中的 QWEN_API_KEY")
    print("   2. 确保图片是有效的食物图像")
    print("   3. 检查网络连接和API服务状态")


if __name__ == "__main__":
    main()
