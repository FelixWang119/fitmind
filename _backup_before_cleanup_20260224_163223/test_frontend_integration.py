#!/usr/bin/env python3
"""Test frontend-backend integration for diet tracking"""

import requests
import json
import base64


def test_nutrition_endpoint():
    """Test the nutrition analysis endpoint with authentication"""

    # First, try to login or get a token
    print("Testing frontend-backend integration...")

    # Test without authentication (should fail)
    print("\n1. Testing without authentication (should fail):")
    response = requests.post(
        "http://localhost:8000/api/v1/nutrition/analyze-food-image",
        json={"image_data": "test_base64_string", "meal_type": "lunch"},
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}...")

    # Test health endpoint (should work without auth)
    print("\n2. Testing health endpoint (no auth required):")
    response = requests.get("http://localhost:8000/api/v1/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Test login endpoint
    print("\n3. Testing login endpoint:")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "test@example.com", "password": "password123"},
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   Got token: {token[:20]}...")

            # Now test with authentication
            print("\n4. Testing nutrition endpoint WITH authentication:")
            response = requests.post(
                "http://localhost:8000/api/v1/nutrition/analyze-food-image",
                json={"image_data": "test_base64_string", "meal_type": "lunch"},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
            )
            print(f"   Status: {response.status_code}")
            print(
                f"   Response keys: {list(response.json().keys()) if response.status_code == 200 else 'N/A'}"
            )
        else:
            print(f"   Login failed: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    test_nutrition_endpoint()
    print("\n" + "=" * 50)
    print("Integration test complete!")
    print("Note: If login fails, you may need to create a test user first.")
