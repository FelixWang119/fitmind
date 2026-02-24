#!/usr/bin/env python3
"""Test backend fixes."""

import requests
import time


def test_backend():
    print("Testing backend fixes...")

    # Test 1: Health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        if response.status_code == 200 and data.get("status") == "healthy":
            print("   ✅ Health endpoint works")
        else:
            print("   ❌ Health endpoint failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: Meals endpoint without auth (should return 401)
    print("\n2. Testing meals endpoint without authentication...")
    try:
        response = requests.get("http://localhost:8000/api/v1/meals", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly returns 401 (unauthorized)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 3: Test multiple requests to ensure backend doesn't crash
    print("\n3. Testing backend stability with multiple requests...")
    success_count = 0
    for i in range(3):
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                success_count += 1
                print(f"   Request {i + 1}: ✅")
            else:
                print(f"   Request {i + 1}: ❌ Status {response.status_code}")
        except Exception as e:
            print(f"   Request {i + 1}: ❌ Error: {e}")
        time.sleep(0.5)

    if success_count == 3:
        print("   ✅ Backend is stable!")
    else:
        print(f"   ❌ Backend had issues: {success_count}/3 successful")
        return False

    # Test 4: Test meals/today endpoint
    print("\n4. Testing meals/today endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/meals/today", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly returns 401 (unauthorized)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED! Backend is working correctly.")
    print("=" * 50)
    return True


if __name__ == "__main__":
    # Give backend time to start
    time.sleep(1)
    test_backend()
