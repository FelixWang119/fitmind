#!/usr/bin/env python3
"""Test image response format"""

import asyncio
import httpx
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings


async def test_image_response():
    """Test image response and see the format"""
    print("Testing Image Response Format...")

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
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"\nFull response structure:")
                print(f"  Keys: {list(result.keys())}")

                if "choices" in result:
                    choice = result["choices"][0]
                    print(f"\nChoice keys: {list(choice.keys())}")

                    if "message" in choice:
                        message = choice["message"]
                        print(f"Message keys: {list(message.keys())}")

                        if "content" in message:
                            content = message["content"]
                            print(f"\nContent (first 500 chars):")
                            print(f"{content[:500]}...")

                # Also check for usage info
                if "usage" in result:
                    print(f"\nUsage: {result['usage']}")

                return result
            else:
                print(f"Error: {response.text[:500]}")
                return None
    except Exception as e:
        print(f"Exception: {e}")
        import traceback

        traceback.print_exc()
        return None


async def main():
    print("=" * 60)
    print("Image Response Format Test")
    print("=" * 60)

    result = await test_image_response()

    if result:
        print("\n" + "=" * 60)
        print("✅ Test successful!")
        print("Now we know the exact response format from the API.")
    else:
        print("\n" + "=" * 60)
        print("❌ Test failed!")


if __name__ == "__main__":
    asyncio.run(main())
