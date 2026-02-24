#!/usr/bin/env python3
"""
Test script to check if backend API correctly returns meal items in response.
"""

import requests
import json
import sys


def test_meal_api():
    """Test the meal API endpoints to see if items are returned correctly."""

    # Base URL for the backend API
    base_url = "http://localhost:8000/api/v1"

    print("Testing meal API endpoints...")
    print("=" * 60)

    try:
        # First, let's get the list of meals
        print("1. Getting all meals...")
        response = requests.get(f"{base_url}/meals/")
        if response.status_code == 200:
            meals = response.json()
            print(f"   Found {len(meals)} meals")

            if meals:
                # Check the first meal's structure
                first_meal = meals[0]
                print(f"   First meal ID: {first_meal.get('id')}")
                print(f"   First meal type: {first_meal.get('meal_type')}")
                print(f"   First meal date: {first_meal.get('meal_date')}")
                print(f"   First meal has 'items' field: {'items' in first_meal}")
                print(
                    f"   First meal has 'meal_items' field: {'meal_items' in first_meal}"
                )

                if "items" in first_meal:
                    items = first_meal["items"]
                    print(f"   Number of items: {len(items) if items else 0}")
                    if items:
                        print(f"   First item: {items[0]}")
                elif "meal_items" in first_meal:
                    meal_items = first_meal["meal_items"]
                    print(
                        f"   Number of meal_items: {len(meal_items) if meal_items else 0}"
                    )
                    if meal_items:
                        print(f"   First meal_item: {meal_items[0]}")

                # Now let's get a specific meal by ID
                meal_id = first_meal.get("id")
                if meal_id:
                    print(f"\n2. Getting specific meal ID {meal_id}...")
                    response = requests.get(f"{base_url}/meals/{meal_id}")
                    if response.status_code == 200:
                        meal_detail = response.json()
                        print(f"   Meal detail retrieved successfully")
                        print(f"   Has 'items' field: {'items' in meal_detail}")
                        print(
                            f"   Has 'meal_items' field: {'meal_items' in meal_detail}"
                        )

                        if "items" in meal_detail:
                            items = meal_detail["items"]
                            print(f"   Number of items: {len(items) if items else 0}")
                            if items:
                                print(
                                    f"   Items structure: {json.dumps(items[:2], indent=2, ensure_ascii=False)}"
                                )
                        elif "meal_items" in meal_detail:
                            meal_items = meal_detail["meal_items"]
                            print(
                                f"   Number of meal_items: {len(meal_items) if meal_items else 0}"
                            )
                            if meal_items:
                                print(
                                    f"   Meal items structure: {json.dumps(meal_items[:2], indent=2, ensure_ascii=False)}"
                                )

                        # Print the full response to see structure
                        print(f"\n3. Full response structure for meal ID {meal_id}:")
                        print(
                            json.dumps(meal_detail, indent=2, ensure_ascii=False)[:1000]
                            + "..."
                        )
                    else:
                        print(f"   Failed to get meal detail: {response.status_code}")
                        print(f"   Response: {response.text}")
            else:
                print("   No meals found in database")
        else:
            print(f"   Failed to get meals: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend API. Is the backend server running?")
        print("Run: cd backend && uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_meal_api()
