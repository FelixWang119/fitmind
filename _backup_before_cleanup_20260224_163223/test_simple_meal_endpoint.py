#!/usr/bin/env python3
"""Simple test to check if meals endpoint exists"""

import requests
import json


def test_meals_endpoint():
    """Test if meals endpoint exists and returns proper status"""
    print("Testing meals endpoint...")

    # Test 1: Check if endpoint exists (should return 401 without auth)
    print("\n1. Testing meals endpoint (no auth)...")
    try:
        response = requests.get("http://localhost:8000/api/v1/meals")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")

        if response.status_code == 401:
            print("   ✅ Good! Endpoint exists and requires authentication")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found - route issue")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Check OpenAPI docs
    print("\n2. Checking OpenAPI docs...")
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"   Docs status: {response.status_code}")

        # Check if meals endpoint is in docs
        response = requests.get("http://localhost:8000/openapi.json")
        openapi = response.json()

        # Look for meals endpoints
        meals_paths = [path for path in openapi.get("paths", {}) if "/meals" in path]
        print(f"   Found {len(meals_paths)} meals endpoints:")
        for path in meals_paths[:5]:  # Show first 5
            print(f"     - {path}")

        # Check for POST /api/v1/meals
        if "/api/v1/meals" in openapi.get("paths", {}):
            print("   ✅ POST /api/v1/meals endpoint found in OpenAPI!")
        else:
            print("   ❌ POST /api/v1/meals NOT found in OpenAPI")

    except Exception as e:
        print(f"   ❌ Error checking docs: {e}")

    # Test 3: Try to get the actual route structure
    print("\n3. Checking route structure...")
    try:
        # Check what the actual full path is
        response = requests.options("http://localhost:8000/api/v1/meals")
        print(f"   OPTIONS status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_meals_endpoint()
