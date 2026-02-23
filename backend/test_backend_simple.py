#!/usr/bin/env python3
"""Simple backend test with real AI integration"""

import asyncio
import time

import httpx


async def test_backend():
    """Test the full backend API"""
    print("Testing backend with real AI integration...")

    # Base URL
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Health check
        print("\n1. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 2: Register user
        print("\n2. Testing user registration...")
        test_email = f"test_{int(time.time())}@example.com"
        test_password = "TestPassword123!"

        try:
            user_data = {
                "email": test_email,
                "password": test_password,
                "nickname": "Test User",
            }
            response = await client.post(
                f"{base_url}/api/v1/auth/register", json=user_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_response = response.json()
                print(f"   Success: {user_response.get('message')}")
                print(f"   User ID: {user_response.get('user_id')}")
                user_id = user_response.get("user_id")
            else:
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   Error: {e}")
            return

        # Test 3: Login
        print("\n3. Testing user login...")
        try:
            login_data = {"username": test_email, "password": test_password}
            response = await client.post(
                f"{base_url}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                login_response = response.json()
                access_token = login_response.get("access_token")
                print(f"   Login successful!")
                print(f"   Token: {access_token[:20]}...")
            else:
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   Error: {e}")
            return

        # Test 4: AI Chat
        print("\n4. Testing AI chat with real QWen API...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            chat_data = {
                "message": "你好，我最近体重增加了2公斤，感觉有点沮丧。我应该怎么办？",
                "role": "nutritionist",
            }
            print(f"   Sending message: {chat_data['message']}")
            response = await client.post(
                f"{base_url}/api/v1/ai/chat",
                json=chat_data,
                headers=headers,
                timeout=30.0,
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                chat_response = response.json()
                print(f"   AI Response received!")
                print(f"   Model: {chat_response.get('model')}")
                print(f"   Response time: {chat_response.get('response_time')}s")
                print(f"   Tokens used: {chat_response.get('tokens_used')}")

                # Show first 300 chars of response
                response_text = chat_response.get("response", "")
                if len(response_text) > 300:
                    print(f"   Preview: {response_text[:300]}...")
                else:
                    print(f"   Preview: {response_text}")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 5: Health data
        print("\n5. Testing health data recording...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            health_data = {
                "weight": 75000,  # 75kg in grams
                "height": 175,  # 175cm
                "notes": "Test recording",
            }
            response = await client.post(
                f"{base_url}/api/v1/health-data/record",
                json=health_data,
                headers=headers,
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                health_response = response.json()
                print(f"   Health data recorded!")
                print(f"   BMI: {health_response.get('bmi')}")
                print(f"   Weight: {health_response.get('weight')}g")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")

        print("\n" + "=" * 60)
        print("✅ Backend testing completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    print("Starting backend tests...")
    print("Make sure backend is running on http://127.0.0.1:8000")
    print("Waiting 2 seconds...")
    time.sleep(2)

    asyncio.run(test_backend())
