#!/usr/bin/env python3
"""Test meal save fix with actual frontend data format"""

import requests
import json
from datetime import datetime


def test_with_actual_frontend_format():
    """Test with the exact format frontend sends"""
    print("Testing meal save with frontend data format...")

    # First create a test user
    print("\n1. Creating test user...")
    user_data = {
        "email": "test_meal@example.com",
        "username": "testmealuser",
        "password": "TestPassword123!",
        "full_name": "Test Meal User",
    }

    try:
        # Try to register user
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Register status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ User created")
            # Login to get token
            login_data = {"username": "testmealuser", "password": "TestPassword123!"}
        elif (
            response.status_code == 400
            and "already registered" in response.text.lower()
        ):
            print("   ℹ️  User already exists, trying login...")
            login_data = {"username": "testmealuser", "password": "TestPassword123!"}
        else:
            print(f"   ❌ Failed to create user: {response.text[:200]}")
            # Try with different credentials
            login_data = {"username": "test@example.com", "password": "password123"}

        # Login
        print("\n2. Logging in...")
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Login status: {response.status_code}")

        if response.status_code != 200:
            print(f"   ❌ Login failed: {response.text[:200]}")
            print("\n   Note: You need to create a user first through the frontend.")
            print("   Steps:")
            print("   1. Go to http://localhost:3000")
            print("   2. Click '注册' (Register)")
            print("   3. Create an account")
            print("   4. Then try saving meals again")
            return False

        token = response.json().get("access_token")
        print(f"   ✅ Got token: {token[:20]}...")

        # Test meal creation with frontend format
        print("\n3. Testing meal creation with frontend format...")

        # This is the exact format frontend sends (from DietTracking.tsx)
        meal_data = {
            "meal_type": "lunch",
            "name": "AI Analyzed Lunch",
            "meal_datetime": datetime.now().isoformat(),
            "notes": "AI analyzed lunch with detailed ingredients",
            "items": [
                {
                    "name": "面条",
                    "serving_size": 150,
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": 570,
                    "protein_per_serving": 15,
                    "carbs_per_serving": 120,
                    "fat_per_serving": 1,
                },
                {
                    "name": "牛肉片",
                    "serving_size": 80,
                    "serving_unit": "g",
                    "quantity": 1,
                    "calories_per_serving": 160,
                    "protein_per_serving": 30,
                    "carbs_per_serving": 0,
                    "fat_per_serving": 2,
                },
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        response = requests.post(
            "http://localhost:8000/api/v1/meals", json=meal_data, headers=headers
        )

        print(f"   Create meal status: {response.status_code}")

        if response.status_code == 201:
            print(f"   ✅ Meal created successfully!")
            result = response.json()
            print(f"   Meal ID: {result.get('id')}")
            print(f"   Meal name: {result.get('name')}")
            print(f"   Total calories: {result.get('calories')}")
            print(f"   Items: {len(result.get('items', []))}")

            # Also test getting meals
            print("\n4. Testing get meals...")
            response = requests.get(
                "http://localhost:8000/api/v1/meals", headers=headers
            )

            if response.status_code == 200:
                meals = response.json()
                print(f"   ✅ Got {len(meals)} meals")
                return True
            else:
                print(f"   ❌ Failed to get meals: {response.status_code}")
                return False

        else:
            print(f"   ❌ Failed to create meal: {response.text[:500]}")

            # Try to parse error
            try:
                error_data = response.json()
                if "detail" in error_data:
                    print(f"   Error detail: {error_data['detail']}")
            except:
                pass

            return False

    except Exception as e:
        print(f"   ❌ Exception: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_backend_logs():
    """Check backend logs for errors"""
    print("\n" + "=" * 60)
    print("Checking backend logs...")
    print("=" * 60)

    try:
        # Check if backend is running
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        print(f"   Backend health: {response.status_code}")

        # Check meals endpoint without auth (should fail)
        response = requests.get("http://localhost:8000/api/v1/meals", timeout=5)
        print(f"   Meals endpoint (no auth): {response.status_code}")

        return True
    except Exception as e:
        print(f"   ❌ Backend check failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Meal Save Fix Test")
    print("=" * 60)

    print("\nThis test simulates what the frontend does when saving a meal.")
    print("It uses the exact data format from DietTracking.tsx")

    # Check backend
    backend_ok = check_backend_logs()

    if not backend_ok:
        print("\n⚠️  Backend issues detected.")
        return

    # Test meal save
    success = test_with_actual_frontend_format()

    print("\n" + "=" * 60)
    if success:
        print("✅ MEAL SAVE FIX TEST SUCCESSFUL!")
        print("\nThe meal save issue should now be fixed.")
        print("Frontend can now save meals successfully.")
    else:
        print("❌ Meal save test failed")
        print("\nPossible issues:")
        print("1. Need valid user credentials")
        print("2. Database schema issues (CalorieGoal table)")
        print("3. API validation errors")

        print("\nTo fix in browser:")
        print("1. Make sure you're logged in")
        print("2. Try saving a meal again")
        print("3. Check browser console for errors (F12 → Console)")


if __name__ == "__main__":
    main()
