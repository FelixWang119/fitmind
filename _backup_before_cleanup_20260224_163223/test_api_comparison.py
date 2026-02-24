#!/usr/bin/env python3
"""Compare chat API and food analysis API requests"""

import asyncio
import httpx
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings


async def test_chat_api():
    """Test the chat API endpoint"""
    print("Testing Chat API...")

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": 0.7,
    }

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(
                    f"  Success! Response: {result['choices'][0]['message']['content'][:50]}..."
                )
                return True
            else:
                print(f"  Error: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


async def test_food_api():
    """Test the food analysis API endpoint"""
    print("\nTesting Food Analysis API...")

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    # Simple test image (1x1 pixel)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    payload = {
        "model": "qwen-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{test_image_base64}"
                        },
                    },
                    {"type": "text", "text": "请描述这张图片"},
                ],
            }
        ],
        "temperature": 0.1,
    }

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Success! Response length: {len(str(result))}")
                return True
            else:
                print(f"  Error: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


async def test_simple_food_api():
    """Test food API without image first"""
    print("\nTesting Food Analysis API (text only, no image)...")

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": "请分析一份番茄炒蛋的营养成分"}],
        "temperature": 0.1,
    }

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(
                    f"  Success! Response: {result['choices'][0]['message']['content'][:100]}..."
                )
                return True
            else:
                print(f"  Error: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


async def main():
    print("=" * 60)
    print("API Comparison Test")
    print("=" * 60)

    print(f"\nAPI Key: {settings.QWEN_API_KEY[:10]}...")
    print(f"API URL: {settings.QWEN_API_URL}")
    print(f"Model: {settings.QWEN_MODEL}")

    chat_ok = await test_chat_api()
    food_text_ok = await test_simple_food_api()
    food_image_ok = await test_food_api()

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Chat API: {'✅' if chat_ok else '❌'}")
    print(f"  Food API (text only): {'✅' if food_text_ok else '❌'}")
    print(f"  Food API (with image): {'✅' if food_image_ok else '❌'}")

    if not chat_ok:
        print("\n⚠️  Chat API failed - API key may be invalid")
    elif chat_ok and not food_text_ok:
        print(
            "\n⚠️  Chat works but food analysis (text) fails - different model/permissions?"
        )
    elif food_text_ok and not food_image_ok:
        print(
            "\n⚠️  Text analysis works but image analysis fails - model may not support images"
        )


if __name__ == "__main__":
    asyncio.run(main())
