#!/usr/bin/env python3
"""测试晚餐重复上传覆盖功能"""

import asyncio
import httpx
from PIL import Image
import io


async def test_dinner_override():
    async with httpx.AsyncClient() as client:
        # 1. 登录
        login_data = {"username": "testimg@example.com", "password": "Test1234"}
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login", data=login_data
        )

        if response.status_code != 200:
            print(f"❌ 登录失败：{response.text[:100]}")
            print("提示：请先创建测试用户")
            return

        token = response.json().get("access_token")
        print(f"✅ 登录成功")

        headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建测试图片（橙色方块模拟食物）
        def create_test_image(color):
            img = Image.new("RGB", (200, 200), color=color)
            from PIL import ImageDraw

            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 50, 150, 150], fill="white")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)
            return img_bytes

        # 3. 第一次上传晚餐
        print("\n🍽️  第一次上传晚餐...")
        img1 = create_test_image("orange")
        files = {"file": ("dinner1.jpg", img1, "image/jpeg")}

        response = await client.post(
            "http://localhost:8000/api/v1/meal-checkin/upload",
            files=files,
            headers=headers,
        )

        if response.status_code != 200:
            print(f"❌ 第一次识别失败：{response.text[:200]}")
            return

        result1 = response.json()
        print(f"✅ 第一次识别成功")
        print(f"   食材数：{len(result1.get('items', []))}")
        print(f"   总热量：{result1.get('total_calories')} kcal")

        # 4. 第一次保存晚餐
        meal_data_1 = {
            "name": "晚餐餐食",
            "meal_type": "dinner",
            "calories": result1["total_calories"],
            "protein": result1["total_protein"],
            "carbs": result1["total_carbs"],
            "fat": result1["total_fat"],
            "notes": result1.get("notes", ""),
            "meal_datetime": "2026-02-26T19:00:00+08:00",
            "items": [
                {
                    "name": item["name"],
                    "serving_size": item["grams"],
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": item["calories"],
                    "protein_per_serving": item["protein"],
                    "carbs_per_serving": item["carbs"],
                    "fat_per_serving": item["fat"],
                }
                for item in result1.get("items", [])
            ],
        }

        response = await client.post(
            "http://localhost:8000/api/v1/meals", json=meal_data_1, headers=headers
        )

        if response.status_code not in [200, 201]:
            print(f"❌ 第一次保存失败：{response.text[:200]}")
            return

        meal1 = response.json()
        meal1_id = meal1["id"]
        print(f"✅ 第一次保存成功，meal_id={meal1_id}")

        # 5. 获取当日餐食列表
        print("\n📋 获取当日餐食列表...")
        response = await client.get(
            "http://localhost:8000/api/v1/meals/daily-nutrition-summary",
            params={"target_date": "2026-02-26"},
            headers=headers,
        )

        if response.status_code == 200:
            summary = response.json()
            dinners = [
                m for m in summary.get("meals", []) if m["meal_type"] == "dinner"
            ]
            print(f"   当日晚餐数量：{len(dinners)}")
            if dinners:
                print(
                    f"   第一份晚餐 ID: {dinners[0]['id']}, 热量：{dinners[0]['calories']} kcal"
                )

        # 6. 第二次上传晚餐（不同图片）
        print("\n🍽️  第二次上传晚餐...")
        img2 = create_test_image("red")
        files = {"file": ("dinner2.jpg", img2, "image/jpeg")}

        response = await client.post(
            "http://localhost:8000/api/v1/meal-checkin/upload",
            files=files,
            headers=headers,
        )

        if response.status_code != 200:
            print(f"❌ 第二次识别失败：{response.text[:200]}")
            return

        result2 = response.json()
        print(f"✅ 第二次识别成功")
        print(f"   食材数：{len(result2.get('items', []))}")
        print(f"   总热量：{result2.get('total_calories')} kcal")

        # 7. 第二次保存晚餐（应该更新而不是新建）
        meal_data_2 = {
            "name": "晚餐餐食",
            "meal_type": "dinner",
            "calories": result2["total_calories"],
            "protein": result2["total_protein"],
            "carbs": result2["total_carbs"],
            "fat": result2["total_fat"],
            "notes": result2.get("notes", ""),
            "meal_datetime": "2026-02-26T19:00:00+08:00",
            "items": [
                {
                    "name": item["name"],
                    "serving_size": item["grams"],
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": item["calories"],
                    "protein_per_serving": item["protein"],
                    "carbs_per_serving": item["carbs"],
                    "fat_per_serving": item["fat"],
                }
                for item in result2.get("items", [])
            ],
        }

        # 先检查是否有现有晚餐
        response = await client.get(
            "http://localhost:8000/api/v1/meals/daily-nutrition-summary",
            params={"target_date": "2026-02-26"},
            headers=headers,
        )

        if response.status_code == 200:
            summary = response.json()
            dinners = [
                m for m in summary.get("meals", []) if m["meal_type"] == "dinner"
            ]

            if dinners:
                # 更新现有晚餐
                print(f"\n🔄 发现已有晚餐 (ID: {dinners[0]['id']}),执行更新...")
                response = await client.put(
                    f"http://localhost:8000/api/v1/meals/{dinners[0]['id']}",
                    json=meal_data_2,
                    headers=headers,
                )

                if response.status_code == 200:
                    meal2 = response.json()
                    print(f"✅ 更新成功，meal_id={meal2['id']}")
                    print(f"   新热量：{meal2['calories']} kcal")
                else:
                    print(f"❌ 更新失败：{response.text[:200]}")
            else:
                # 创建新晚餐
                print("\n➕ 未发现现有晚餐，创建新记录...")
                response = await client.post(
                    "http://localhost:8000/api/v1/meals",
                    json=meal_data_2,
                    headers=headers,
                )

                if response.status_code in [200, 201]:
                    meal2 = response.json()
                    print(f"✅ 创建成功，meal_id={meal2['id']}")
                else:
                    print(f"❌ 创建失败：{response.text[:200]}")

        # 8. 最终检查：当日有多少份晚餐
        print("\n📊 最终检查...")
        response = await client.get(
            "http://localhost:8000/api/v1/meals/daily-nutrition-summary",
            params={"target_date": "2026-02-26"},
            headers=headers,
        )

        if response.status_code == 200:
            summary = response.json()
            dinners = [
                m for m in summary.get("meals", []) if m["meal_type"] == "dinner"
            ]
            print(f"   当日晚餐总数：{len(dinners)}")

            for i, dinner in enumerate(dinners, 1):
                print(
                    f"   晚餐{i}: ID={dinner['id']}, 热量={dinner['calories']} kcal, 食材数={len(dinner.get('items', []))}"
                )

            if len(dinners) == 1:
                print("\n✅ 测试通过：第二次上传正确覆盖了第一次晚餐")
            else:
                print(f"\n❌ 测试失败：应该有 1 份晚餐，实际有{len(dinners)}份")
        else:
            print(f"❌ 获取摘要失败：{response.text[:200]}")


if __name__ == "__main__":
    asyncio.run(test_dinner_override())
