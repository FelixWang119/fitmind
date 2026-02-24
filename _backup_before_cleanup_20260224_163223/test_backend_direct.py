#!/usr/bin/env python3
"""Test backend function directly"""

import asyncio
import sys
import os

# Set working directory to backend
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

# Now import
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision


async def test_direct():
    """Test the function directly"""
    print("Testing backend function directly...")

    # Create a test image (100x100)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABLSURBVHic7cExAQAAAMKg9U9tCj8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgNwH3AAH0T4qTAAAAAElFTkSuQmCC"

    try:
        print("Calling analyze_food_with_qwen_vision...")
        result = await analyze_food_with_qwen_vision(test_image_base64)

        print(f"\nResult type: {type(result)}")
        print(f"Keys: {list(result.keys())}")

        if "notes" in result:
            print(f"Notes: {result['notes']}")

            if "模拟数据" in result["notes"]:
                print("\n⚠️  Using fallback data")
                print(f"Reason: {result['notes']}")
            else:
                print("\n✅ Real AI analysis successful!")
                print(f"Meal type: {result.get('meal_type')}")
                print(f"Number of items: {len(result.get('items', []))}")

        return result

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None


async def main():
    print("=" * 60)
    print("Direct Backend Function Test")
    print("=" * 60)

    result = await test_direct()

    print("\n" + "=" * 60)
    if result:
        if "模拟数据" in result.get("notes", ""):
            print("❌ Function returned fallback data")
            print("   This means the API call failed (401 or other error)")
        else:
            print("✅ Function successful with real AI analysis!")
    else:
        print("❌ Function failed completely!")


if __name__ == "__main__":
    asyncio.run(main())
