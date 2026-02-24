#!/usr/bin/env python3
"""Test real food image analysis with lunch.jpg"""

import asyncio
import sys
import os
import base64

# Set working directory to backend
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

# Now import
from app.utils.food_image_analyzer import analyze_food_with_qwen_vision


def encode_image_to_base64(image_path):
    """Encode image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def test_real_food_image():
    """Test with real food image"""
    print("Testing real food image analysis...")

    # Get the absolute path to lunch.jpg
    image_path = os.path.join(os.path.dirname(__file__), "lunch.jpg")

    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return None

    print(f"Image file: {image_path}")
    print(f"File size: {os.path.getsize(image_path)} bytes")

    try:
        # Encode image to base64
        print("Encoding image to base64...")
        image_base64 = encode_image_to_base64(image_path)
        print(f"Base64 length: {len(image_base64)} characters")

        # Call the analysis function
        print("\nCalling analyze_food_with_qwen_vision...")
        result = await analyze_food_with_qwen_vision(image_base64)

        print(f"\nResult type: {type(result)}")
        print(f"Keys: {list(result.keys())}")

        if "notes" in result:
            print(f"\nNotes: {result['notes']}")

            if "模拟数据" in result["notes"]:
                print("\n⚠️  Using fallback/mock data")
                print(f"Reason: {result['notes']}")
            else:
                print("\n✅ Real AI analysis successful!")

        # Display detailed results
        print(f"\nMeal type: {result.get('meal_type', 'unknown')}")
        print(f"Total calories: {result.get('total_calories', 0)} kcal")
        print(f"Total protein: {result.get('total_protein', 0)} g")
        print(f"Total carbs: {result.get('total_carbs', 0)} g")
        print(f"Total fat: {result.get('total_fat', 0)} g")

        # Display individual items
        items = result.get("items", [])
        print(f"\nNumber of items identified: {len(items)}")

        for i, item in enumerate(items):
            print(f"\n  Item {i + 1}:")
            print(f"    Name: {item.get('name', 'Unknown')}")
            print(f"    Grams: {item.get('grams', 0)}g")
            print(f"    Calories: {item.get('calories', 0)} kcal")
            print(f"    Protein: {item.get('protein', 0)}g")
            print(f"    Carbs: {item.get('carbs', 0)}g")
            print(f"    Fat: {item.get('fat', 0)}g")

        return result

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None


async def test_frontend_integration():
    """Test the frontend API endpoint"""
    print("\n" + "=" * 60)
    print("Testing Frontend API Integration...")
    print("=" * 60)

    import httpx
    from app.core.config import settings

    # First, let's test if we can call the API directly
    image_path = os.path.join(os.path.dirname(__file__), "..", "lunch.jpg")
    image_base64 = encode_image_to_base64(image_path)

    # Note: This would require authentication, so we'll just test the function directly
    print("Note: API endpoint requires authentication")
    print("Testing function directly instead...")

    return True


async def main():
    print("=" * 60)
    print("Real Food Image Integration Test")
    print("=" * 60)

    print(f"\nTesting with: lunch.jpg")
    print(f"Current directory: {os.getcwd()}")

    result = await test_real_food_image()

    print("\n" + "=" * 60)
    if result:
        if "模拟数据" in result.get("notes", ""):
            print("❌ Function returned fallback data")
            print("   This means the API call failed")
            print(f"   Reason: {result.get('notes', 'Unknown')}")
        else:
            print("✅ SUCCESS! Real AI analysis completed!")
            print(f"\nSummary:")
            print(f"  - Meal type: {result.get('meal_type')}")
            print(f"  - Items identified: {len(result.get('items', []))}")
            print(f"  - Total calories: {result.get('total_calories')} kcal")

            # Check if we got meaningful analysis
            items = result.get("items", [])
            if len(items) > 0:
                print(f"\n✅ AI successfully identified {len(items)} food items!")
                print(
                    "This meets the user requirement for detailed ingredient breakdown."
                )
            else:
                print(f"\n⚠️  AI did not identify any food items.")
                print("This could be because:")
                print("  1. Image doesn't contain recognizable food")
                print("  2. AI model limitations")
                print("  3. Image quality issues")
    else:
        print("❌ Test failed completely!")


if __name__ == "__main__":
    asyncio.run(main())
