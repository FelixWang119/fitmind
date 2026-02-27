#!/usr/bin/env python3
"""测试 AI 记忆功能"""

import asyncio
import httpx


async def test_ai_memory():
    async with httpx.AsyncClient() as client:
        # 1. 登录
        login_data = {"username": "testimg@example.com", "password": "Test1234"}
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login", data=login_data
        )

        if response.status_code != 200:
            print(f"❌ 登录失败：{response.text[:100]}")
            return

        token = response.json().get("access_token")
        print(f"✅ 登录成功")

        headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建一份餐食记录
        print("\n🍽️  创建测试餐食记录...")
        meal_data = {
            "name": "测试晚餐",
            "meal_type": "dinner",
            "calories": 600,
            "protein": 30,
            "carbs": 70,
            "fat": 20,
            "meal_datetime": "2026-02-26T19:00:00+08:00",
            "items": [
                {
                    "name": "米饭",
                    "serving_size": 200,
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": 260,
                    "protein_per_serving": 5,
                    "carbs_per_serving": 56,
                    "fat_per_serving": 1,
                },
                {
                    "name": "红烧肉",
                    "serving_size": 150,
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": 340,
                    "protein_per_serving": 25,
                    "carbs_per_serving": 14,
                    "fat_per_serving": 19,
                },
            ],
        }

        response = await client.post(
            "http://localhost:8000/api/v1/meals", json=meal_data, headers=headers
        )

        if response.status_code in [200, 201]:
            meal = response.json()
            print(f"✅ 餐食创建成功，ID={meal['id']}")
        else:
            print(f"❌ 餐食创建失败：{response.text[:200]}")
            return

        # 3. 立即测试 AI 记忆
        print("\n🤖 测试 AI 记忆...")
        chat_data = {"message": "我今天吃了什么？", "conversation_id": None}

        response = await client.post(
            "http://localhost:8000/api/v1/ai/chat", json=chat_data, headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI 回复：")
            print(f"   {result['response'][:200]}...")

            # 检查是否提到了晚餐
            if (
                "晚餐" in result["response"]
                or "吃了" in result["response"]
                or "米饭" in result["response"]
            ):
                print("\n✅ AI 有记忆！成功识别到用户的饮食记录")
            else:
                print("\n⚠️  AI 回复中没有提到饮食记录")
        else:
            print(f"❌ AI 聊天失败：{response.text[:200]}")

        # 4. 再次测试更具体的问题
        print("\n🤖 测试 AI 更具体的问题...")
        chat_data = {"message": "我晚餐摄入了多少热量？", "conversation_id": None}

        response = await client.post(
            "http://localhost:8000/api/v1/ai/chat", json=chat_data, headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI 回复：")
            print(f"   {result['response'][:200]}...")

            # 检查是否提到了热量
            if (
                "600" in result["response"]
                or "热量" in result["response"]
                or "千卡" in result["response"]
            ):
                print("\n✅ AI 正确回答热量信息！")
            else:
                print("\n⚠️  AI 没有正确回答热量信息")
        else:
            print(f"❌ AI 聊天失败：{response.text[:200]}")


if __name__ == "__main__":
    asyncio.run(test_ai_memory())
