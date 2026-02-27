#!/usr/bin/env python3
"""测试图片识别 API 是否正常工作"""

import asyncio
import httpx
import base64


async def test_image_recognition():
    # 1. 先登录获取 token
    async with httpx.AsyncClient() as client:
        # 登录
        login_data = {"username": "test@example.com", "password": "test123"}

        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/login", data=login_data
            )

            if response.status_code != 200:
                print(f"❌ 登录失败：{response.status_code}")
                print(f"响应：{response.text}")
                return

            token = response.json().get("access_token")
            print(f"✅ 登录成功，token: {token[:20]}...")

        except Exception as e:
            print(f"❌ 登录异常：{e}")
            print("提示：请确保测试用户存在，或先注册一个用户")
            return

        # 2. 创建一张测试图片（简单的 base64 图片）
        # 使用一个 1x1 的红色像素图片作为测试
        test_image = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        ).decode("utf-8")

        print(f"\n📷 测试图片大小：{len(test_image)} bytes")

        # 3. 调用图片识别 API
        headers = {"Authorization": f"Bearer {token}"}

        # 创建 FormData
        import io
        from PIL import Image

        # 创建一个简单的测试图片
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

        try:
            print("\n🔄 调用图片识别 API...")
            response = await client.post(
                "http://localhost:8000/api/v1/meal-checkin/upload",
                files=files,
                headers=headers,
            )

            print(f"📊 响应状态码：{response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 识别成功！")
                print(f"\n结果:")
                print(f"  餐次类型：{result.get('meal_type')}")
                print(f"  食材数量：{len(result.get('items', []))}")
                print(f"  总热量：{result.get('total_calories')}")

                # 检查是否是模拟数据
                notes = result.get("notes", "")
                if "模拟" in notes or "mock" in notes.lower():
                    print(f"\n⚠️  警告：返回的是模拟数据！")
                    print(f"  notes 字段：{notes}")
                else:
                    print(f"\n✅ 返回的是真实 AI 识别结果")
                    if notes:
                        print(f"  AI 评价：{notes[:100]}...")

                if result.get("items"):
                    print(f"\n  食材列表:")
                    for item in result["items"]:
                        print(
                            f"    - {item.get('name')}: {item.get('grams')}g, {item.get('calories')}kcal"
                        )

            else:
                print(f"❌ API 调用失败：{response.status_code}")
                print(f"响应：{response.text}")

        except Exception as e:
            print(f"❌ 调用异常：{e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_image_recognition())
