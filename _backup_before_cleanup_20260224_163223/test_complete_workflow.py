#!/usr/bin/env python3
"""
Test the complete workflow: image recognition → save meal → retrieve with ingredient details
"""

import sys
import os
import json
import base64
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import requests
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.nutrition import Meal, MealItem
from app.schemas.meal_models import MealCreate, MealItemCreate

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "/Users/felix/bmad/backend/tests/mealimg/lunch.jpg"


def get_auth_token():
    """Get authentication token for testing"""
    # Try to get token from test file
    token_file = "/Users/felix/bmad/test_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            token = f.read().strip()
            if token:
                return token

    # Try to get token from test script
    token_script = "/Users/felix/bmad/test_direct_token.py"
    if os.path.exists(token_script):
        with open(token_script, "r") as f:
            content = f.read()
            # Extract token from the file
            import re

            match = re.search(r"token\s*=\s*['\"]([^'\"]+)['\"]", content)
            if match:
                return match.group(1)

    # Fallback: try to login
    login_data = {
        "username": "nutrition.test@example.com",
        "password": "testpassword123",
    }
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass

    return None


def test_image_analysis(token):
    """Test image analysis endpoint"""
    print("📸 Testing image analysis...")

    # Read and encode image
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {"Authorization": f"Bearer {token}"}
    data = {"image_data": image_data}

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/analyze-food-image",
            json=data,
            headers=headers,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image analysis successful!")
            print(f"   Detected foods: {result.get('foods', [])}")
            print(f"   Has meal_items: {'meal_items' in result}")
            if "meal_items" in result:
                print(f"   Number of meal_items: {len(result['meal_items'])}")
                for item in result["meal_items"]:
                    print(
                        f"   - {item.get('name')}: {item.get('calories_per_serving')} cal"
                    )
            return result
        else:
            print(f"❌ Image analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during image analysis: {e}")
        return None


def test_meal_creation(token, analysis_result):
    """Test creating a meal from analysis results"""
    print("\n🍽️ Testing meal creation...")

    if not analysis_result or "meal_items" not in analysis_result:
        print("❌ No meal_items in analysis result")
        return None

    # Prepare meal data
    meal_data = {
        "meal_type": "lunch",
        "name": "Test Meal from Image",
        "meal_datetime": datetime.now(timezone.utc).isoformat(),
        "notes": "Created from image analysis test",
        "items": analysis_result["meal_items"],
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/meals", json=meal_data, headers=headers
        )

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Meal created successfully!")
            print(f"   Meal ID: {result.get('id')}")
            print(f"   Meal name: {result.get('name')}")
            print(f"   Has items field: {'items' in result}")
            if "items" in result:
                print(f"   Number of items: {len(result['items'])}")
                for item in result["items"]:
                    print(
                        f"   - {item.get('name')}: {item.get('calories_per_serving')} cal"
                    )
            else:
                print(f"   Checking for meal_items field: {'meal_items' in result}")
                if "meal_items" in result:
                    print(f"   Number of meal_items: {len(result['meal_items'])}")
            return result
        else:
            print(f"❌ Meal creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during meal creation: {e}")
        return None


def test_meal_retrieval(token, meal_id):
    """Test retrieving the created meal"""
    print(f"\n🔍 Testing meal retrieval (ID: {meal_id})...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test get_meal endpoint
        response = requests.get(f"{BASE_URL}/api/v1/meals/{meal_id}", headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Meal retrieved successfully!")
            print(f"   Meal ID: {result.get('id')}")
            print(f"   Has items field: {'items' in result}")
            if "items" in result:
                print(f"   Number of items: {len(result['items'])}")
                for item in result["items"]:
                    print(
                        f"   - {item.get('name')}: {item.get('calories_per_serving')} cal"
                    )
            else:
                print(f"   Checking for meal_items field: {'meal_items' in result}")
                if "meal_items" in result:
                    print(f"   Number of meal_items: {len(result['meal_items'])}")
            return result
        else:
            print(f"❌ Meal retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during meal retrieval: {e}")
        return None


def test_daily_summary(token):
    """Test daily nutrition summary"""
    print(f"\n📊 Testing daily nutrition summary...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/meals/daily-nutrition-summary", headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Daily summary retrieved!")
            print(f"   Date: {result.get('date')}")
            print(f"   Meal count: {result.get('meal_count')}")
            print(f"   Has meals field: {'meals' in result}")
            if "meals" in result:
                print(f"   Number of meals: {len(result['meals'])}")
                for i, meal in enumerate(result["meals"]):
                    print(f"   Meal {i + 1}: {meal.get('name')}")
                    print(f"     Has items: {'items' in meal}")
                    if "items" in meal:
                        print(f"     Items count: {len(meal['items'])}")
            return result
        else:
            print(f"❌ Daily summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during daily summary: {e}")
        return None


def test_get_all_meals(token):
    """Test getting all meals"""
    print(f"\n📋 Testing get all meals...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/v1/meals", headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Got {len(result)} meals")
            if result:
                print(f"   First meal: {result[0].get('name')}")
                print(f"   Has items: {'items' in result[0]}")
                if "items" in result[0]:
                    print(f"   Items count: {len(result[0]['items'])}")
            return result
        else:
            print(f"❌ Get all meals failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during get all meals: {e}")
        return None


def main():
    print("🧪 Testing complete workflow...")

    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Could not get authentication token")
        return

    print(f"✅ Got auth token: {token[:20]}...")

    # Test 1: Image analysis
    analysis_result = test_image_analysis(token)
    if not analysis_result:
        print("❌ Image analysis test failed, skipping remaining tests")
        return

    # Test 2: Meal creation
    meal_result = test_meal_creation(token, analysis_result)
    if not meal_result:
        print("❌ Meal creation test failed, skipping remaining tests")
        return

    meal_id = meal_result.get("id")

    # Test 3: Meal retrieval
    test_meal_retrieval(token, meal_id)

    # Test 4: Daily summary
    test_daily_summary(token)

    # Test 5: Get all meals
    test_get_all_meals(token)

    print("\n" + "=" * 50)
    print("✅ Complete workflow test finished!")
    print("=" * 50)


if __name__ == "__main__":
    main()
