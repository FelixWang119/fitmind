#!/usr/bin/env python3
"""
Test script to check if backend API correctly returns meal items in response.
Includes authentication simulation.
"""

import requests
import json
import sys


def test_meal_api_with_auth():
    """Test the meal API endpoints with authentication."""

    # Base URL for the backend API
    base_url = "http://localhost:8000/api/v1"

    print("Testing meal API endpoints with authentication...")
    print("=" * 60)

    try:
        # First, let's try to login to get a token
        print("1. Attempting to login...")
        login_data = {
            "username": "test@example.com",  # Common test email
            "password": "password123",  # Common test password
        }

        # Try login with form data
        response = requests.post(f"{base_url}/auth/login", data=login_data)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   Login successful, got access token")

            # Set up headers with token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Now let's get the list of meals
            print("\n2. Getting all meals with authentication...")
            response = requests.get(f"{base_url}/meals/", headers=headers)
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
                            print(f"   First item name: {items[0].get('name', 'N/A')}")
                            print(
                                f"   First item structure keys: {list(items[0].keys())}"
                            )
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
                        print(f"\n3. Getting specific meal ID {meal_id}...")
                        response = requests.get(
                            f"{base_url}/meals/{meal_id}", headers=headers
                        )
                        if response.status_code == 200:
                            meal_detail = response.json()
                            print(f"   Meal detail retrieved successfully")
                            print(f"   Has 'items' field: {'items' in meal_detail}")
                            print(
                                f"   Has 'meal_items' field: {'meal_items' in meal_detail}"
                            )

                            if "items" in meal_detail:
                                items = meal_detail["items"]
                                print(
                                    f"   Number of items: {len(items) if items else 0}"
                                )
                                if items:
                                    print(f"   First 2 items:")
                                    for i, item in enumerate(items[:2]):
                                        print(
                                            f"     Item {i + 1}: {item.get('name', 'N/A')}"
                                        )
                                        print(
                                            f"       Quantity: {item.get('quantity', 'N/A')}"
                                        )
                                        print(f"       Unit: {item.get('unit', 'N/A')}")
                                        print(
                                            f"       Calories: {item.get('calories', 'N/A')}"
                                        )
                            elif "meal_items" in meal_detail:
                                meal_items = meal_detail["meal_items"]
                                print(
                                    f"   Number of meal_items: {len(meal_items) if meal_items else 0}"
                                )
                                if meal_items:
                                    print(f"   First 2 meal_items:")
                                    for i, meal_item in enumerate(meal_items[:2]):
                                        print(f"     Meal item {i + 1}: {meal_item}")

                            # Print a sample of the response
                            print(
                                f"\n4. Sample response structure for meal ID {meal_id}:"
                            )
                            # Convert to JSON and print first 1500 chars
                            json_str = json.dumps(
                                meal_detail, indent=2, ensure_ascii=False
                            )
                            if len(json_str) > 1500:
                                print(json_str[:1500] + "...")
                            else:
                                print(json_str)
                        else:
                            print(
                                f"   Failed to get meal detail: {response.status_code}"
                            )
                            print(f"   Response: {response.text}")
                else:
                    print("   No meals found in database")
            else:
                print(f"   Failed to get meals: {response.status_code}")
                print(f"   Response: {response.text}")

        else:
            print(f"   Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            print(
                "\nTrying alternative approach: Check if we can access meals without auth..."
            )

            # Try without auth to see what happens
            response = requests.get(f"{base_url}/meals/")
            print(f"   GET /meals/ without auth: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend API. Is the backend server running?")
        print("Run: cd backend && uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_meal_api_with_auth()
