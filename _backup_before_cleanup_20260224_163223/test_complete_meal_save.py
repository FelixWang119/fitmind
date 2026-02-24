#!/usr/bin/env python3
"""Complete test of meal save functionality with authentication"""

import requests
import json
from datetime import datetime, timezone, timedelta
import sys


def get_auth_token():
    """Get authentication token for testing"""
    # Try to login with test credentials
    # Use form data as required by OAuth2PasswordRequestForm
    login_data = {
        "username": "test@example.com",  # Try common test credentials
        "password": "test123",
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,  # Use data, not json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def test_meal_save_with_auth():
    """Test meal save with authentication"""
    print("=" * 60)
    print("Complete Meal Save Test with Authentication")
    print("=" * 60)

    # Get auth token
    print("\n1. Getting authentication token...")
    token = get_auth_token()

    if not token:
        print("   ❌ Could not get auth token")
        print("   Please create a test user first:")
        print("   1. Go to http://localhost:3000")
        print("   2. Register an account")
        print("   3. Use those credentials in this test")
        return False

    print(f"   ✅ Got auth token: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test 1: Get current meals
    print("\n2. Getting current meals...")
    response = requests.get("http://localhost:8000/api/v1/meals", headers=headers)
    print(f"   GET /meals: {response.status_code}")
    if response.status_code == 200:
        meals = response.json()
        print(f"   Found {len(meals)} existing meals")

    # Test 2: Create a test meal
    print("\n3. Creating test meal...")

    # Get current date in local timezone
    now = datetime.now()
    local_date = now.date()

    # Create meal data similar to frontend
    meal_data = {
        "name": "测试午餐",
        "meal_type": "lunch",
        "notes": "测试餐食记录",
        "meal_datetime": f"{local_date.isoformat()}T12:00:00+08:00",  # Beijing time
        "items": [
            {
                "name": "米饭",
                "serving_size": 200,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 260,
                "protein_per_serving": 5,
                "carbs_per_serving": 58,
                "fat_per_serving": 0.5,
            },
            {
                "name": "鸡胸肉",
                "serving_size": 150,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 165,
                "protein_per_serving": 31,
                "carbs_per_serving": 0,
                "fat_per_serving": 3.6,
            },
        ],
    }

    print(f"   Meal date: {local_date.isoformat()}")
    print(f"   Meal datetime: {meal_data['meal_datetime']}")

    response = requests.post(
        "http://localhost:8000/api/v1/meals", json=meal_data, headers=headers
    )

    print(f"   POST /meals: {response.status_code}")

    if response.status_code == 201:
        meal = response.json()
        print(f"   ✅ Meal created successfully!")
        print(f"   Meal ID: {meal.get('id')}")
        print(f"   Total calories: {meal.get('calories')}")

        # Test 3: Verify meal appears in daily summary
        print("\n4. Checking daily nutrition summary...")
        response = requests.get(
            f"http://localhost:8000/api/v1/meals/daily-nutrition-summary?target_date={local_date.isoformat()}",
            headers=headers,
        )

        if response.status_code == 200:
            summary = response.json()
            print(f"   Daily summary: {response.status_code}")
            print(f"   Date: {summary.get('date')}")
            print(f"   Total calories: {summary.get('total_calories')}")
            print(f"   Meal count: {summary.get('meal_count')}")

            if summary.get("meal_count", 0) > 0:
                print("   ✅ Meal appears in daily summary!")
            else:
                print("   ⚠️  Meal not found in daily summary (timezone issue?)")
        else:
            print(f"   ❌ Failed to get daily summary: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

        # Test 4: Get the meal directly
        print("\n5. Getting created meal directly...")
        meal_id = meal.get("id")
        response = requests.get(
            f"http://localhost:8000/api/v1/meals/{meal_id}", headers=headers
        )

        if response.status_code == 200:
            meal_details = response.json()
            print(f"   ✅ Meal retrieved: {meal_details.get('name')}")
            print(f"   Meal datetime: {meal_details.get('meal_datetime')}")
        else:
            print(f"   ❌ Failed to get meal: {response.status_code}")

        return True
    else:
        print(f"   ❌ Failed to create meal: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        return False


def check_backend_logs():
    """Check backend logs for errors"""
    print("\n" + "=" * 60)
    print("Checking Backend Status")
    print("=" * 60)

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Backend health: {response.status_code}")

        # Check meals endpoint (no auth)
        response = requests.get("http://localhost:8000/api/v1/meals")
        print(f"Meals endpoint (no auth): {response.status_code}")

        return True
    except Exception as e:
        print(f"Backend not reachable: {e}")
        return False


if __name__ == "__main__":
    # Check backend first
    if not check_backend_logs():
        print("\n❌ Backend is not running. Please start it with:")
        print(
            "cd /Users/felix/bmad/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
        )
        sys.exit(1)

    # Run the test
    success = test_meal_save_with_auth()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Meal save functionality is working!")
        print("\nIf meals still don't appear in the frontend:")
        print("1. Check browser console for errors (F12 → Console)")
        print("2. Verify you're logged in with the same account")
        print("3. Check network tab to see API responses")
    else:
        print("❌ TEST FAILED: Meal save still has issues")
        print("\nDebugging steps:")
        print("1. Check backend logs for errors")
        print("2. Verify database connection")
        print("3. Check if user exists and is authenticated")

    print("=" * 60)
