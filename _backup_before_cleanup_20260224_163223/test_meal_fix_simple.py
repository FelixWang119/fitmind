#!/usr/bin/env python3
"""
Simple test to verify meal creation returns items
"""

import sys
import os
import json
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

BASE_URL = "http://localhost:8000"


def get_token():
    """Get test token"""
    token_file = "/Users/felix/bmad/test_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return None


def test_meal_creation():
    """Test meal creation with items"""
    token = get_token()
    if not token:
        print("❌ No token")
        return

    print(f"✅ Token: {token[:20]}...")

    # Create meal with items
    meal_data = {
        "meal_type": "lunch",
        "name": "Test Meal with Items",
        "meal_datetime": datetime.now(timezone.utc).isoformat(),
        "notes": "Test meal to verify items are returned",
        "items": [
            {
                "name": "Test Rice",
                "serving_size": 100,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 130,
                "protein_per_serving": 2,
                "carbs_per_serving": 28,
                "fat_per_serving": 0.3,
            },
            {
                "name": "Test Chicken",
                "serving_size": 100,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 165,
                "protein_per_serving": 31,
                "carbs_per_serving": 0,
                "fat_per_serving": 3.6,
            },
        ],
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("\n🍽️ Creating meal...")
    response = requests.post(
        f"{BASE_URL}/api/v1/meals", json=meal_data, headers=headers
    )

    if response.status_code == 201:
        result = response.json()
        print(f"✅ Meal created! ID: {result.get('id')}")
        print(f"   Response keys: {list(result.keys())}")

        # Check for items
        if "items" in result:
            print(f"✅ Found 'items' field with {len(result['items'])} items")
            for i, item in enumerate(result["items"]):
                print(
                    f"   Item {i + 1}: {item.get('name')} - {item.get('calories_per_serving')} cal"
                )
        elif "meal_items" in result:
            print(
                f"⚠️ Found 'meal_items' field (not 'items') with {len(result['meal_items'])} items"
            )
            for i, item in enumerate(result["meal_items"]):
                print(
                    f"   Item {i + 1}: {item.get('name')} - {item.get('calories_per_serving')} cal"
                )
        else:
            print("❌ No items field found in response")
            print(f"   Full response: {json.dumps(result, indent=2)}")

        # Test retrieving the meal
        meal_id = result.get("id")
        print(f"\n🔍 Retrieving meal {meal_id}...")
        response = requests.get(f"{BASE_URL}/api/v1/meals/{meal_id}", headers=headers)

        if response.status_code == 200:
            meal = response.json()
            print(f"✅ Meal retrieved!")
            if "items" in meal:
                print(
                    f"✅ Retrieved meal has 'items' field with {len(meal['items'])} items"
                )
            elif "meal_items" in meal:
                print(f"⚠️ Retrieved meal has 'meal_items' field (not 'items')")
            else:
                print("❌ Retrieved meal has no items field")
        else:
            print(f"❌ Failed to retrieve meal: {response.status_code}")
            print(f"   {response.text}")

        # Test getting all meals
        print(f"\n📋 Getting all meals...")
        response = requests.get(f"{BASE_URL}/api/v1/meals", headers=headers)

        if response.status_code == 200:
            meals = response.json()
            print(f"✅ Got {len(meals)} meals")
            if meals:
                first_meal = meals[0]
                if "items" in first_meal:
                    print(
                        f"✅ First meal has 'items' field with {len(first_meal['items'])} items"
                    )
                elif "meal_items" in first_meal:
                    print(f"⚠️ First meal has 'meal_items' field (not 'items')")
                else:
                    print("❌ First meal has no items field")
        else:
            print(f"❌ Failed to get meals: {response.status_code}")

    else:
        print(f"❌ Failed to create meal: {response.status_code}")
        print(f"   {response.text}")


if __name__ == "__main__":
    test_meal_creation()
