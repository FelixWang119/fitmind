#!/usr/bin/env python3
"""Test vision API with a real food image (simulated)"""

import asyncio
import httpx
import sys
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings


def create_test_image():
    """Create a simple 100x100 test image (red square)"""
    # Create a simple PNG image using PIL
    try:
        from PIL import Image, ImageDraw

        # Create a 100x100 red image
        img = Image.new("RGB", (100, 100), color="red")
        draw = ImageDraw.Draw(img)
        # Draw a green rectangle in the middle
        draw.rectangle([20, 20, 80, 80], fill="green")

        # Save to bytes
        import io

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Encode to base64
        return base64.b64encode(img_bytes.read()).decode("utf-8")
    except ImportError:
        # Fallback: create a simple base64 encoded 100x100 red image
        # This is a minimal 100x100 red PNG
        return "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABLSURBVHic7cExAQAAAMKg9U9tCj8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgNwH3AAH0T4qTAAAAAElFTkSuQmCC"


async def test_food_analysis():
    """Test food analysis with a real image"""
    print("Testing Food Analysis with Real Image...")

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    # Create a test image
    test_image_base64 = create_test_image()
    print(f"Created test image (base64 length: {len(test_image_base64)})")

    # Use the compatible mode endpoint with qwen-vl-plus
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    payload = {
        "model": "qwen-vl-plus",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_base64}"
                        },
                    },
                    {
                        "type": "text",
                        "text": """这是一张食物图片的测试。请假设这是一张食物图片，并按照以下JSON格式返回模拟的营养分析结果：
{
    "meal_type": "lunch",
    "items": [
        {
            "name": "番茄",
            "grams": 150,
            "calories": 27,
            "protein": 1.3,
            "carbs": 5.8,
            "fat": 0.2
        },
        {
            "name": "鸡蛋",
            "grams": 100,
            "calories": 155,
            "protein": 13,
            "carbs": 1.1,
            "fat": 11
        }
    ],
    "notes": "这是一份番茄炒蛋，营养均衡，富含蛋白质和维生素。"
}

请只返回JSON格式，不要有其他文本。""",
                    },
                ],
            }
        ],
        "temperature": 0.1,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Sending request to vision API...")
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Success! Response received.")

                # Extract content
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    print(f"\nResponse content:")
                    print(content)

                    # Try to parse as JSON
                    import json

                    try:
                        # Find JSON in response
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        if start != -1 and end != 0:
                            json_str = content[start:end]
                            parsed = json.loads(json_str)
                            print(f"\n✅ Successfully parsed JSON!")
                            print(f"Meal type: {parsed.get('meal_type')}")
                            print(f"Number of items: {len(parsed.get('items', []))}")
                            for item in parsed.get("items", []):
                                print(f"  - {item.get('name')}: {item.get('grams')}g")
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  Could not parse JSON: {e}")
                        print(f"Raw content: {content[:200]}...")
                else:
                    print(f"\nUnexpected response format: {list(result.keys())}")

                return True
            else:
                print(f"\n❌ Error: {response.text[:500]}")
                return False

    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("Food Analysis with Real Image Test")
    print("=" * 60)

    print(f"\nAPI Key: {settings.QWEN_API_KEY[:10]}...")
    print(f"Model: qwen-vl-plus")

    success = await test_food_analysis()

    print("\n" + "=" * 60)
    if success:
        print("✅ Test successful! Vision API is working.")
        print("\nNext steps:")
        print("1. Update food_image_analyzer.py to use correct format")
        print("2. Test with actual food photos")
    else:
        print("❌ Test failed!")
        print("\nPossible issues:")
        print("1. Image format/size issues")
        print("2. API permissions")
        print("3. Request format")


if __name__ == "__main__":
    asyncio.run(main())
