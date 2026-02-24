#!/usr/bin/env python3
"""Test vision API endpoint directly"""

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


async def test_vision_api():
    """Test vision API endpoint"""
    print("Testing Vision API...")

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    # Simple test image (1x1 pixel)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    # Test different endpoints and formats
    endpoints = [
        {
            "name": "Vision API (multimodal-generation)",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            "payload": {
                "model": "qwen-vl-max",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": f"data:image/jpeg;base64,{test_image_base64}"
                                },
                                {"text": "描述这张图片"},
                            ],
                        }
                    ]
                },
            },
        },
        {
            "name": "Compatible mode with qwen-vl-max",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "payload": {
                "model": "qwen-vl-max",
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
                            {"type": "text", "text": "描述这张图片"},
                        ],
                    }
                ],
            },
        },
        {
            "name": "Compatible mode with qwen-vl-plus",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "payload": {
                "model": "qwen-vl-plus",
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
                            {"type": "text", "text": "描述这张图片"},
                        ],
                    }
                ],
            },
        },
    ]

    for endpoint in endpoints:
        print(f"\nTesting: {endpoint['name']}")
        print(f"  URL: {endpoint['url']}")
        print(f"  Model: {endpoint['payload']['model']}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    endpoint["url"], headers=headers, json=endpoint["payload"]
                )
                print(f"  Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ Success!")

                    # Try to extract response content
                    if "choices" in result:
                        content = result["choices"][0]["message"]["content"]
                        print(f"  Response: {content[:100]}...")
                    elif "output" in result and "choices" in result["output"]:
                        content = result["output"]["choices"][0]["message"]["content"]
                        print(f"  Response: {content[:100]}...")
                    else:
                        print(f"  Response format: {list(result.keys())}")
                else:
                    print(f"  ❌ Error: {response.text[:200]}")

        except Exception as e:
            print(f"  ❌ Exception: {str(e)[:100]}")


async def main():
    print("=" * 60)
    print("Vision API Test")
    print("=" * 60)

    print(f"\nAPI Key: {settings.QWEN_API_KEY[:10]}...")

    await test_vision_api()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nNote: If all vision models return 401, the API key may not have")
    print("      permission for vision models. Chat models work because")
    print("      they use different model (qwen-turbo).")


if __name__ == "__main__":
    asyncio.run(main())
