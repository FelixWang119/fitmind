#!/usr/bin/env python3
"""Test script for AI food image analysis with fixed code"""

import asyncio
import base64
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.utils.food_image_analyzer import analyze_food_with_qwen_vision


async def test_ai_analysis():
    """Test the AI analysis function"""
    print("Testing AI food image analysis...")

    # Create a simple base64 encoded test image (100x100 pixel)
    # This is a minimal 100x100 red PNG
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABLSURBVHic7cExAQAAAMKg9U9tCj8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgNwH3AAH0T4qTAAAAAElFTkSuQmCC"

    try:
        print("Calling analyze_food_with_qwen_vision...")
        result = await analyze_food_with_qwen_vision(test_image_base64)

        print(f"Result type: {type(result)}")
        print(f"Keys in result: {list(result.keys())}")

        if "items" in result:
            print(f"Number of items: {len(result['items'])}")
            for i, item in enumerate(result["items"]):
                print(
                    f"  Item {i + 1}: {item.get('name', 'Unknown')} - {item.get('grams', 0)}g"
                )

        print(f"Total calories: {result.get('total_calories', 0)}")
        print(f"Notes: {result.get('notes', 'No notes')}")

        return result

    except Exception as e:
        print(f"Error during AI analysis: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_ai_analysis())

    if result:
        print("\n✅ AI analysis test completed!")
        if "模拟数据" in result.get("notes", ""):
            print(
                "⚠️  Note: Using fallback/mock data (this is expected if API call fails)"
            )
    else:
        print("\n❌ AI analysis test failed!")
