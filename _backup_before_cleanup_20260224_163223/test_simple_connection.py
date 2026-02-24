#!/usr/bin/env python3
"""Simple connection test to debug issues."""

import requests
import time

print("Testing connection to backend...")

# Try multiple times with timeout
for i in range(5):
    try:
        print(f"Attempt {i + 1}: Connecting to http://127.0.0.1:8000/api/v1/health")
        response = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:100]}")
        break
    except requests.exceptions.ConnectionError as e:
        print(f"  Connection error: {e}")
        time.sleep(1)
    except Exception as e:
        print(f"  Other error: {e}")
        time.sleep(1)

print("\nTesting login endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        data={
            "username": "nutrition.test@example.com",
            "password": "NutritionTest123!",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text[:200]}")
except Exception as e:
    print(f"Login error: {e}")
