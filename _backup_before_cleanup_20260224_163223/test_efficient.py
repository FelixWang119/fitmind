#!/usr/bin/env python3
"""
高效测试工具 - 使用固定的测试用户和预获取的令牌
避免重复注册和无效的token获取流程
"""

import sys
import os
import requests
import json
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


class EfficientTester:
    """高效测试器 - 使用固定的测试用户"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_user_type = "nutrition"  # 固定使用营养测试用户
        self._token: Optional[str] = None
        self._user_data: Optional[Dict[str, Any]] = None

    def setup(self):
        """设置测试环境 - 获取固定用户的令牌"""
        print("设置高效测试环境...")
        print("=" * 50)

        try:
            from app.core.database import SessionLocal
            from app.core.test_users import test_user_manager

            db = SessionLocal()
            try:
                # 获取固定测试用户（如果不存在会自动创建）
                self._user_data = test_user_manager.get_or_create_test_user(
                    db, self.test_user_type
                )
                print(f"✅ 使用固定测试用户: {self._user_data['email']}")

                # 获取令牌（自动缓存和刷新）
                self._token = test_user_manager.get_test_user_token(
                    db, self.test_user_type
                )
                if self._token:
                    print(f"✅ 获取令牌成功 (长度: {len(self._token)})")
                    print(f"   令牌前30字符: {self._token[:30]}...")
                else:
                    print("❌ 无法获取令牌")
                    return False

            finally:
                db.close()

            return True

        except Exception as e:
            print(f"❌ 设置失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_headers(self) -> Dict[str, str]:
        """获取带认证头的headers"""
        if not self._token:
            raise ValueError("未设置令牌，请先调用setup()")

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def test_photo_analysis(self, image_base64: str) -> Dict[str, Any]:
        """测试照片分析API"""
        print("\n测试照片分析API...")
        print("-" * 30)

        url = f"{self.base_url}/api/v1/nutrition/analyze-food-image"
        payload = {
            "image": image_base64,
            "date": "2024-01-01",  # 固定测试日期
        }

        try:
            response = requests.post(
                url, headers=self.get_headers(), json=payload, timeout=30
            )
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 分析成功!")
                print(f"   餐次类型: {result.get('meal_type', 'N/A')}")
                print(f"   总热量: {result.get('total_calories', 'N/A')}")
                print(f"   食材数量: {len(result.get('items', []))}")

                # 检查是否是模拟数据
                notes = result.get("notes", "")
                if "模拟" in notes or "未设置API Key" in notes:
                    print(f"⚠️  注意: 返回的是模拟数据!")
                    print(f"   原因: {notes}")
                else:
                    print(f"🎉 成功调用真实AI分析!")

                return result
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {}

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {}

    def test_protected_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """测试受保护的端点"""
        print(f"\n测试受保护端点: {endpoint}")
        print("-" * 30)

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 端点访问成功")
                return result
            else:
                print(f"❌ 端点访问失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {}

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {}

    def run_comprehensive_test(self):
        """运行全面的API测试"""
        print("\n运行全面API测试")
        print("=" * 50)

        # 1. 测试健康端点（不需要认证）
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"✅ 后端健康: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   状态: {data.get('status', 'unknown')}")
        except:
            print("❌ 后端不可用")
            return

        # 2. 测试需要认证的端点
        endpoints = [
            "/api/v1/nutrition/recommendations",
            "/api/v1/users/me",
            "/api/v1/dashboard/summary",
        ]

        for endpoint in endpoints:
            self.test_protected_endpoint(endpoint)

    @staticmethod
    def create_test_script():
        """创建可重用的测试脚本"""
        script_content = '''#!/usr/bin/env python3
"""
高效测试脚本 - 使用固定的测试用户
避免重复注册和无效的token获取流程

使用方法:
    python test_api_efficient.py
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

class EfficientAPITester:
    """高效API测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_user_type = "nutrition"  # 固定使用营养测试用户
        self._token = None
        
    def setup(self):
        """设置测试环境"""
        from app.core.database import SessionLocal
        from app.core.test_users import test_user_manager
        
        db = SessionLocal()
        try:
            # 获取固定测试用户
            user_data = test_user_manager.get_or_create_test_user(db, self.test_user_type)
            print(f"使用测试用户: {user_data['email']}")
            
            # 获取令牌
            self._token = test_user_manager.get_test_user_token(db, self.test_user_type)
            if self._token:
                print(f"令牌获取成功")
                return True
            return False
        finally:
            db.close()
    
    def get_headers(self):
        """获取认证头"""
        if not self._token:
            raise ValueError("未设置令牌")
        
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
    
    def test_endpoint(self, method, endpoint, data=None):
        """测试API端点"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.get_headers(), timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.get_headers(), json=data, timeout=10)
            else:
                print(f"不支持的HTTP方法: {method}")
                return None
            
            print(f"{method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"错误: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"请求失败: {e}")
            return None

if __name__ == "__main__":
    tester = EfficientAPITester()
    
    if tester.setup():
        print("\\n测试需要认证的端点:")
        
        # 测试用户信息
        user_info = tester.test_endpoint("GET", "/api/v1/users/me")
        if user_info:
            print(f"  用户ID: {user_info.get('id')}")
            print(f"  邮箱: {user_info.get('email')}")
        
        # 测试营养建议
        recommendations = tester.test_endpoint("GET", "/api/v1/nutrition/recommendations")
        if recommendations:
            print(f"  营养建议获取成功")
        
        print("\\n✅ 测试完成!")
    else:
        print("❌ 测试设置失败")
'''

        script_path = "/Users/felix/bmad/test_api_efficient.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        print(f"✅ 已创建可重用测试脚本: {script_path}")
        os.chmod(script_path, 0o755)  # 添加执行权限


def main():
    """主函数"""
    print("高效测试工具 - 使用固定的测试用户")
    print("=" * 60)

    tester = EfficientTester()

    # 1. 设置测试环境（获取固定用户的令牌）
    if not tester.setup():
        print("❌ 测试环境设置失败")
        return 1

    # 2. 运行全面测试
    tester.run_comprehensive_test()

    # 3. 创建可重用的测试脚本
    tester.create_test_script()

    print("\n" + "=" * 60)
    print("✅ 高效测试模式已设置完成!")
    print("\n使用建议:")
    print("1. 所有测试使用固定的测试用户 (nutrition.test@example.com)")
    print("2. 令牌自动缓存和刷新，避免重复获取")
    print("3. 使用 test_api_efficient.py 进行快速测试")
    print("4. 在项目上下文中记录此模式")

    return 0


if __name__ == "__main__":
    sys.exit(main())
