#!/usr/bin/env python3
"""
Basic QA test for API endpoints without authentication
"""

import sys
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, ".")

from app.main import app

client = TestClient(app)


def test_endpoint(endpoint: str, method: str = "GET", expected_status: int = 200):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json={})
        else:
            print(f"✗ {method} {endpoint}: SKIP (unsupported method)")
            return

        if response.status_code == expected_status:
            print(f"✓ {method} {endpoint}: PASS")
            return True
        else:
            print(
                f"✗ {method} {endpoint}: FAIL (expected {expected_status}, got {response.status_code})"
            )
            return False
    except Exception as e:
        print(f"✗ {method} {endpoint}: ERROR ({str(e)[:100]})")
        return False


print("=" * 80)
print("BASIC QA TEST FOR PUBLIC API ENDPOINTS")
print("=" * 80)

results = []

# Test health endpoints
print("\n1. Testing Health Endpoints...")
results.append(("GET /api/v1/health", test_endpoint("/api/v1/health", "GET", 200)))
results.append(
    ("GET /api/v1/health/ready", test_endpoint("/api/v1/health/ready", "GET", 200))
)

# Test authentication endpoints (registration should work)
print("\n2. Testing Authentication Endpoints...")
results.append(
    ("POST /api/v1/auth/register", test_endpoint("/api/v1/auth/register", "POST", 422))
)  # 422 expected due to missing data

# Test API documentation
print("\n3. Testing API Documentation...")
results.append(("GET /docs", test_endpoint("/docs", "GET", 200)))
results.append(("GET /redoc", test_endpoint("/redoc", "GET", 200)))
results.append(("GET /openapi.json", test_endpoint("/openapi.json", "GET", 200)))

# Print summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total = len(results)
passed = sum(1 for _, success in results if success)
failed = total - passed

print(f"Total tests: {total}")
print(f"Passed: {passed} ({passed / total * 100:.1f}%)")
print(f"Failed: {failed} ({failed / total * 100:.1f}%)")

if failed > 0:
    print("\nFAILED TESTS:")
    for endpoint, success in results:
        if not success:
            print(f"  {endpoint}")
