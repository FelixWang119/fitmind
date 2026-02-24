#!/usr/bin/env python3
"""Test to reproduce the exact 422 error from logs"""

import requests
import json
from datetime import datetime


def test_exact_scenario():
    """Test the exact scenario from logs"""
    print("Testing exact scenario from logs")
    print("=" * 60)

    # Based on logs, user ID 4 was authenticated
    # User 4 has email: 2293351092@qq.com
    # Let me try to login with this user

    print("\n1. Trying to login as user 4 (2293351092@qq.com)...")

    # First, let me check if I can get a token for any user
    # Try with test@example.com which we know exists
    login_data = {
        "username": "test@example.com",
        "password": "testpassword",  # Default password in many test systems
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login", data=login_data
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Login successful, token: {token[:20]}...")

            headers = {"Authorization": f"Bearer {token}"}

            # Test daily summary with the exact date from logs
            target_date = "2026-02-24"
            print(f"\n2. Testing daily summary (date={target_date})...")
            response = requests.get(
                f"http://localhost:8000/api/v1/meals/daily-nutrition-summary?target_date={target_date}",
                headers=headers,
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 422:
                print("\n   ❌ Got 422 Unprocessable Entity error!")
                try:
                    error_data = response.json()
                    print(f"   Error detail: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw response: {response.text[:500]}")
            elif response.status_code == 200:
                print("\n   ✅ Success!")
                try:
                    data = response.json()
                    print(f"   Response has {len(data.get('meals', []))} meals")
                    print(f"   Total calories: {data.get('total_calories')}")
                except:
                    print(f"   Raw response: {response.text[:500]}")
            else:
                print(f"   Response: {response.text[:500]}")

        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_exact_scenario()
