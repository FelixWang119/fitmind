#!/usr/bin/env python3
"""
简单高效测试工具 - 直接使用固定测试用户和手动获取令牌
避免所有重复注册和无效流程
"""

import sys
import os
import requests
import json
from typing import Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


class SimpleEfficientTester:
    """简单高效测试器 - 最直接的方式"""

    def __init__(self):
        self.base_url = "http://localhost:8000"

        # 固定测试用户配置
        self.test_users = {
            "nutrition": {
                "email": "nutrition.test@example.com",
                "password": "NutritionTest123!",
                "username": "nutritiontest",
            },
            "default": {
                "email": "test.user@example.com",
                "password": "TestPassword123!",
                "username": "testuser",
            },
        }

        self.current_user = "nutrition"
        self._token = None

    def ensure_test_user(self):
        """确保测试用户存在（一次性创建）"""
        print("确保测试用户存在...")

        user_config = self.test_users[self.current_user]

        # 尝试直接注册用户
        register_url = f"{self.base_url}/api/v1/auth/register"
        register_data = {
            "email": user_config["email"],
            "username": user_config["username"],
            "password": user_config["password"],
            "confirm_password": user_config["password"],
            "full_name": f"Test User {self.current_user.capitalize()}",
            "age": 25,
            "height": 170,
            "initial_weight": 70000,
            "target_weight": 65000,
            "activity_level": "moderate",
        }

        try:
            response = requests.post(register_url, json=register_data, timeout=10)
            if response.status_code == 200:
                print(f"✅ 创建测试用户: {user_config['email']}")
            elif (
                response.status_code == 400
                and "already registered" in response.text.lower()
            ):
                print(f"✅ 测试用户已存在: {user_config['email']}")
            else:
                print(f"⚠️  用户注册状态: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
        except Exception as e:
            print(f"⚠️  用户注册检查: {e}")

    def get_token_directly(self) -> str:
        """直接获取令牌（最简单的方式）"""
        print("获取认证令牌...")

        user_config = self.test_users[self.current_user]
        login_url = f"{self.base_url}/api/v1/auth/login"
        login_data = {
            "username": user_config["email"],  # FastAPI通常使用email作为username
            "password": user_config["password"],
        }

        try:
            response = requests.post(login_url, data=login_data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                if token:
                    print(f"✅ 获取令牌成功 (长度: {len(token)})")
                    return token
                else:
                    print(f"❌ 响应中没有access_token字段")
                    print(f"   响应: {result}")
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 登录请求失败: {e}")

        # 如果获取失败，尝试使用token端点
        print("尝试使用token端点...")
        token_url = f"{self.base_url}/api/v1/auth/token"

        try:
            response = requests.post(token_url, data=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                if token:
                    print(f"✅ 通过token端点获取成功")
                    return token
        except:
            pass

        raise ValueError("无法获取认证令牌")

    def setup_once(self):
        """一次性设置（创建用户+获取令牌）"""
        print("=" * 50)
        print("一次性测试环境设置")
        print("=" * 50)

        # 1. 确保测试用户存在
        self.ensure_test_user()

        # 2. 获取令牌
        self._token = self.get_token_directly()

        print("✅ 测试环境设置完成!")
        return True

    def get_headers(self) -> Dict[str, str]:
        """获取带认证头的headers"""
        if not self._token:
            raise ValueError("未设置令牌，请先调用setup_once()")

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def test_api(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """测试API端点"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.get_headers(), timeout=10)
            elif method.upper() == "POST":
                response = requests.post(
                    url, headers=self.get_headers(), json=data, timeout=10
                )
            else:
                print(f"不支持的HTTP方法: {method}")
                return {}

            print(f"{method} {endpoint}: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"   错误: {response.text[:200]}")
                return {}

        except Exception as e:
            print(f"请求失败: {e}")
            return {}

    def run_quick_test(self):
        """运行快速测试"""
        print("\n" + "=" * 50)
        print("运行快速API测试")
        print("=" * 50)

        # 测试健康端点
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"后端健康: {response.status_code}")
        except:
            print("❌ 后端不可用")
            return

        # 测试需要认证的端点
        tests = [
            ("GET", "/api/v1/users/me", "获取用户信息"),
            ("GET", "/api/v1/nutrition/recommendations", "获取营养建议"),
            ("GET", "/api/v1/dashboard/summary", "获取仪表板摘要"),
        ]

        for method, endpoint, description in tests:
            print(f"\n测试: {description}")
            result = self.test_api(method, endpoint)
            if result:
                print(f"   ✅ 成功")
            else:
                print(f"   ❌ 失败")

    def test_photo_analysis_simple(self):
        """简单测试照片分析"""
        print("\n" + "=" * 50)
        print("测试照片分析（简单版）")
        print("=" * 50)

        # 使用一个简单的base64测试图像
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        result = self.test_api(
            "POST",
            "/api/v1/nutrition/analyze-food-image",
            {"image": test_image, "date": "2024-01-01"},
        )

        if result:
            print(f"分析结果:")
            print(f"  餐次类型: {result.get('meal_type', 'N/A')}")
            print(f"  总热量: {result.get('total_calories', 'N/A')}")
            print(f"  食材数量: {len(result.get('items', []))}")

            notes = result.get("notes", "")
            if "模拟" in notes or "未设置API Key" in notes:
                print(f"  ⚠️  返回模拟数据: {notes}")
            else:
                print(f"  🎉 真实AI分析!")

        return result


def main():
    """主函数"""
    print("简单高效测试工具 - 避免所有重复流程")
    print("=" * 60)

    tester = SimpleEfficientTester()

    try:
        # 一次性设置（创建用户+获取令牌）
        if not tester.setup_once():
            return 1

        # 运行测试
        tester.run_quick_test()

        # 测试照片分析
        tester.test_photo_analysis_simple()

        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print("\n使用说明:")
        print("1. 此工具一次性创建测试用户并获取令牌")
        print("2. 所有后续测试使用相同的令牌")
        print("3. 避免重复注册和无效的token获取流程")
        print("4. 令牌有效期为30分钟，过期后需要重新运行setup_once()")

        # 保存令牌供后续使用
        token_file = "/tmp/test_token.txt"
        with open(token_file, "w") as f:
            f.write(tester._token)
        print(f"\n令牌已保存到: {token_file}")
        print(f"下次测试可直接使用: Bearer {tester._token[:30]}...")

        return 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
