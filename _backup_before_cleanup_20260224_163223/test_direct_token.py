#!/usr/bin/env python3
"""
Direct test token acquisition - simplest possible approach.

This script demonstrates the most efficient way to get a test user token
without any unnecessary steps or complexity.
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_USER_EMAIL = "nutrition.test@example.com"
TEST_USER_PASSWORD = "NutritionTest123!"


def get_direct_token():
    """Get authentication token directly - simplest approach."""
    print(f"Getting token for test user: {TEST_USER_EMAIL}")

    # Direct login request
    login_data = {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Success! Got token: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")

            # Try to register user first
            print("\nTrying to register user first...")
            register_user()

            # Try login again
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(
                    f"✅ Success after registration! Got token: {access_token[:20]}..."
                )
                return access_token
            else:
                print(f"❌ Still failed after registration: {response.status_code}")
                return None

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Is the backend running?")
        print("   Run: cd /Users/felix/bmad && ./restart_efficient.sh")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def register_user():
    """Register test user if not exists."""
    print(f"Registering test user: {TEST_USER_EMAIL}")

    user_data = {
        "email": TEST_USER_EMAIL,
        "username": "nutritiontest",
        "password": TEST_USER_PASSWORD,
        "confirm_password": TEST_USER_PASSWORD,
        "full_name": "Nutrition Test User",
        "age": 25,
        "height": 170,
        "initial_weight": 70000,
        "target_weight": 65000,
        "activity_level": "moderate",
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)

        if response.status_code in [200, 201]:
            print(f"✅ User registered successfully")
        else:
            print(f"⚠️  Registration response: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")


def test_api_with_token(token):
    """Test API with acquired token."""
    if not token:
        print("❌ No token available for testing")
        return False

    print(f"\nTesting API with token...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test a simple endpoint
    try:
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ API test successful!")
            print(f"   User: {user_data.get('email')}")
            print(f"   ID: {user_data.get('id')}")
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False


def save_token_to_file(token):
    """Save token to file for reuse."""
    if not token:
        return

    token_file = Path(__file__).parent / "test_token.txt"
    with open(token_file, "w") as f:
        f.write(token)

    print(f"\n✅ Token saved to: {token_file}")
    print(f"   Use: export TEST_TOKEN='{token[:20]}...'")


def main():
    """Main function."""
    print("=" * 60)
    print("DIRECT TEST TOKEN ACQUISITION")
    print("=" * 60)
    print("\nGoal: Get test user token in the most efficient way possible")
    print("      No unnecessary steps, no complexity")
    print()

    # Step 1: Get token
    token = get_direct_token()

    if token:
        # Step 2: Test API with token
        test_api_with_token(token)

        # Step 3: Save token for reuse
        save_token_to_file(token)

        print("\n" + "=" * 60)
        print("✅ EFFICIENT WORKFLOW COMPLETE")
        print("=" * 60)
        print("\nYou now have a working token for all testing.")
        print("No need to register users repeatedly.")
        print("No need to test API without token first.")
        print("\nUse this token for ALL your tests!")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED TO GET TOKEN")
        print("=" * 60)
        print("\nCheck if backend is running:")
        print("  cd /Users/felix/bmad && ./restart_backend.sh")
        print("\nOr check server logs for errors.")


if __name__ == "__main__":
    main()
