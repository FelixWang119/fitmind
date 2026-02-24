#!/usr/bin/env python3
"""Minimal test to check backend connectivity"""

import requests
import time

print("Testing backend connectivity...")

# Test 1: Health endpoint
print("\n1. Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Health endpoint works")
    else:
        print(f"   ❌ Health endpoint failed: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Auth endpoint (public)
print("\n2. Testing auth endpoint...")
try:
    response = requests.get("http://localhost:8000/api/v1/auth/me", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:  # Expected - needs auth
        print(f"   ✅ Auth endpoint works (401 as expected)")
    else:
        print(f"   ⚠️ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Try with token
print("\n3. Testing with token...")
try:
    with open("/Users/felix/bmad/test_token.txt", "r") as f:
        token = f.read().strip()

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/auth/me", headers=headers, timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Auth with token works")
        print(f"   User: {response.json().get('email')}")
    else:
        print(f"   ❌ Auth with token failed: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("Connectivity test complete")
