#!/usr/bin/env python3
"""Test to reproduce the 422 error in daily-nutrition-summary"""

import requests
import json
from datetime import datetime


def test_with_auth():
    """Test the endpoint with authentication"""
    print("Testing /meals/daily-nutrition-summary with auth")
    print("=" * 60)

    # First, login to get token
    print("\n1. Logging in...")
    login_data = {"username": "test@example.com", "password": "testpassword"}

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login", data=login_data
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Login successful, token: {token[:20]}...")

            headers = {"Authorization": f"Bearer {token}"}

            # Test daily summary
            today = datetime.now().date().isoformat()
            print(f"\n2. Testing daily summary (date={today})...")
            response = requests.get(
                f"http://localhost:8000/api/v1/meals/daily-nutrition-summary?target_date={today}",
                headers=headers,
            )

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")

            if response.status_code == 422:
                print("\n   ❌ Got 422 Unprocessable Entity error!")
                print(f"   Error detail: {response.text}")

        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_with_auth()
