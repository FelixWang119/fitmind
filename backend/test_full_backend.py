#!/usr/bin/env python3
"""Test the full backend with real AI integration"""

import asyncio
import json
import time

import httpx


async def test_backend():
    """Test the full backend API"""
    print("Testing full backend with real AI integration...")

    # Base URL
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        print("\n1. Testing health check endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: User registration
        print("\n3. Testing user registration...")
        try:
            user_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "nickname": "Test User",
            }
            response = await client.post(
                f"{base_url}/api/v1/auth/register", json=user_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_response = response.json()
                print(f"   User created: {user_response.get('email')}")
                user_id = user_response.get("user_id")
                print(f"   User ID: {user_id}")
                test_email = user_data["email"]
                test_password = user_data["password"]
            else:
                print(f"   Response: {response.text}")
                user_id = None
                test_email = None
                test_password = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            user_id = None
            test_email = None
            test_password = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            user_id = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            user_id = None

        # Test 4: User login
        print("\n4. Testing user login...")
        try:
            if test_email and test_password:
                # Use form data for login
                login_data = {
                    "username": test_email,
                    "password": test_password
                }
                response = await client.post(
                    f"{base_url}/api/v1/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    login_response = response.json()
                    access_token = login_response.get('access_token')
                    print(f"   Login successful")
                    print(f"   Token type: {login_response.get('token_type')}")
                else:
                    print(f"   Response: {response.text}")
                    access_token = None
            else:
                print("   Skipping login test - no user credentials")
                access_token = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            access_token = None
            else:
                print("   Skipping login test - no user created")
                access_token = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            access_token = None

        # Test 5: AI chat endpoint (requires authentication)
        print("\n5. Testing AI chat endpoint...")
        try:
            if access_token and user_id:
                headers = {"Authorization": f"Bearer {access_token}"}
                chat_data = {
                    "message": "你好，我最近体重增加了2公斤，感觉有点沮丧。我应该怎么办？",
                    "role": "nutritionist",  # 测试营养师角色
                }
                response = await client.post(
                    f"{base_url}/api/v1/ai/chat", json=chat_data, headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    chat_response = response.json()
                    print(f"   AI response received!")
                    print(f"   Model: {chat_response.get('model')}")
                    print(
                        f"   Response length: {len(chat_response.get('response', ''))} characters"
                    )
                    print(f"   Tokens used: {chat_response.get('tokens_used')}")
                    print(
                        f"   Response time: {chat_response.get('response_time')} seconds"
                    )

                    # Show first 200 characters of response
                    response_text = chat_response.get("response", "")
                    if len(response_text) > 200:
                        print(f"   Preview: {response_text[:200]}...")
                    else:
                        print(f"   Preview: {response_text}")
                else:
                    print(f"   Response: {response.text}")
            else:
                print("   Skipping AI chat test - no authentication token")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 6: Health data recording
        print("\n6. Testing health data recording...")
        try:
            if access_token:
                headers = {"Authorization": f"Bearer {access_token}"}
                health_data = {
                    "weight": 75000,  # 75kg in grams
                    "height": 175,  # 175cm
                    "notes": "Test recording",
                }
                response = await client.post(
                    f"{base_url}/api/v1/health/record",
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
            else:
                print("   Skipping health data test - no authentication token")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "=" * 60)
        print("Backend testing completed!")
        print("=" * 60)


if __name__ == "__main__":
    print("Starting backend tests...")
    print("Make sure the backend is running on http://127.0.0.1:8000")
    print("Waiting 2 seconds for server to be ready...")
    import time

    time.sleep(2)

    asyncio.run(test_backend())
