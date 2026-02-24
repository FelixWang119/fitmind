#!/usr/bin/env python3
"""Test meal creation API directly"""

import requests
import json
from datetime import datetime


def test_meal_creation():
    """Test creating a meal via API"""
    print("Testing meal creation API...")

    # First, try to login (we need a token)
    print("\n1. Attempting to login...")

    # Try with test credentials
    login_data = {"username": "test@example.com", "password": "password123"}

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Login status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

        if response.status_code != 200:
            print("   ❌ Login failed. Need valid credentials to test.")
            print("\n   To test meal creation:")
            print("   1. Create a user first via frontend")
            print("   2. Get authentication token")
            print("   3. Use token to call API")
            return False

        # If login successful, get token
        token = response.json().get("access_token")
        print(f"   ✅ Got token: {token[:20]}...")

        # Now test meal creation
        print("\n2. Testing meal creation...")

        meal_data = {
            "meal_type": "lunch",
            "name": "Test Meal from API",
            "meal_datetime": datetime.now().isoformat(),
            "notes": "Test meal created via API",
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
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Failed to create meal: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ Exception: {type(e).__name__}: {e}")
        return False


def check_database_schema():
    """Check database schema issues"""
    print("\n" + "=" * 60)
    print("Checking database schema...")
    print("=" * 60)

    # Check if we can query meals
    try:
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

        from app.db.session import SessionLocal
        from app.models.nutrition import Meal

        db = SessionLocal()
        try:
            count = db.query(Meal).count()
            print(f"   Total meals in database: {count}")

            # Check table structure
            from sqlalchemy import inspect

            inspector = inspect(db.bind)
            columns = inspector.get_columns("meals")
            print(f"\n   Meal table columns:")
            for col in columns:
                print(f"     - {col['name']} ({col['type']})")

            return True
        finally:
            db.close()

    except Exception as e:
        print(f"   ❌ Database error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("Meal Creation API Test")
    print("=" * 60)

    # Check database first
    db_ok = check_database_schema()

    if not db_ok:
        print("\n⚠️  Database issues detected. This may cause meal creation to fail.")

    # Test API
    api_ok = test_meal_creation()

    print("\n" + "=" * 60)
    if api_ok:
        print("✅ Meal creation API test successful!")
    else:
        print("❌ Meal creation API test failed")
        print("\nPossible issues:")
        print("1. Authentication required (need valid user)")
        print("2. Database schema issues")
        print("3. API endpoint errors")

        print("\nTo debug further:")
        print("1. Check backend logs for errors")
        print("2. Verify database tables exist")
        print("3. Create a test user first")


if __name__ == "__main__":
    main()
