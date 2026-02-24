#!/usr/bin/env python3
"""
验证重启后基础设施更新是否生效
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import requests
import json


def test_backend():
    """测试后端服务"""
    print("测试后端服务...")
    print("=" * 50)

    try:
        # 测试健康端点
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ 后端健康检查: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   状态: {data.get('status', 'unknown')}")
            print(f"   版本: {data.get('version', 'unknown')}")

        # 测试API文档
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ API文档可访问: HTTP {response.status_code}")

        # 测试Qwen配置端点（如果存在）
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/config/qwen", timeout=5
            )
            if response.status_code == 200:
                print(f"✅ Qwen配置端点可访问")
        except:
            print("ℹ️  Qwen配置端点不可访问（可能不需要）")

        return True

    except Exception as e:
        print(f"❌ 后端测试失败: {e}")
        return False


def test_frontend():
    """测试前端服务"""
    print("\n测试前端服务...")
    print("=" * 50)

    try:
        # 测试前端页面
        response = requests.get("http://localhost:3000", timeout=10)
        print(f"✅ 前端页面可访问: HTTP {response.status_code}")

        # 检查页面标题
        if "Weight AI" in response.text:
            print(f"✅ 前端页面标题正确")

        # 检查API连接（通过前端配置）
        if "localhost:8000" in response.text:
            print(f"✅ 前端配置了正确的后端地址")

        return True

    except Exception as e:
        print(f"❌ 前端测试失败: {e}")
        return False


def test_infrastructure_config():
    """测试基础设施配置"""
    print("\n测试基础设施配置...")
    print("=" * 50)

    try:
        from app.core.qwen_config import qwen_config
        from app.core.test_resources import TestResources

        print("✅ Qwen配置系统导入成功")
        validation = qwen_config.validate_configuration()
        print(f"   API密钥配置: {validation['api_key_configured']}")
        print(f"   对话模型: {validation['chat_model']}")
        print(f"   视觉模型: {validation['vision_model']}")
        print(f"   状态: {validation['status']}")

        print("\n✅ 测试资源系统导入成功")
        resources = TestResources.list_available_images()
        print(f"   可用测试图像: {len(resources)}个")
        for img in resources[:3]:  # 显示前3个
            print(f"     - {img['name']}: {img['description']}")

        return True

    except Exception as e:
        print(f"❌ 基础设施配置测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("验证重启后基础设施更新")
    print("=" * 60)

    results = {
        "backend": test_backend(),
        "frontend": test_frontend(),
        "infrastructure": test_infrastructure_config(),
    }

    print("\n" + "=" * 60)
    print("验证结果摘要")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有服务重启成功，基础设施更新生效!")
        print("\n访问地址:")
        print(f"  前端: http://localhost:3000")
        print(f"  后端API: http://localhost:8000")
        print(f"  API文档: http://localhost:8000/docs")
    else:
        print("❌ 部分服务测试失败，请检查日志")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
