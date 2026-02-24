#!/usr/bin/env python3
"""Test the daily nutrition summary endpoint"""

import requests
import json
from datetime import datetime


def test_daily_summary():
    """Test the daily nutrition summary endpoint"""
    print("Testing /meals/daily-nutrition-summary endpoint")
    print("=" * 60)

    # Try without auth (should fail)
    print("\n1. Testing without authentication...")
    response = requests.get(
        "http://localhost:8000/api/v1/meals/daily-nutrition-summary"
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")

    # Try with a test date
    today = datetime.now().date().isoformat()
    print(f"\n2. Testing with date parameter (date={today})...")
    response = requests.get(
        f"http://localhost:8000/api/v1/meals/daily-nutrition-summary?target_date={today}"
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 401:
        print("   ✅ Expected: Requires authentication")
    else:
        print(f"   Response: {response.text[:200]}...")

    # Check what the endpoint expects
    print(f"\n3. Checking endpoint documentation...")
    try:
        # Try to get OpenAPI schema
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("   ✅ Docs available at http://localhost:8000/docs")
        else:
            print(f"   Docs status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    print(f"\n" + "=" * 60)
    print("Analysis:")
    print("=" * 60)
    print("""
The frontend calls:
  GET /api/v1/meals/daily-nutrition-summary?target_date=YYYY-MM-DD

This endpoint:
1. Requires authentication (returns 401 without auth)
2. Returns meals for the authenticated user for the given date
3. Should return structure: {date, total_calories, total_protein, meals: [...]}

If meals are saved but not showing:
1. Check browser DevTools → Network tab for API calls
2. Look for 401 errors (authentication issue)
3. Check if response has empty meals array
4. Verify date parameter matches saved meal dates

To debug:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Save a meal in frontend
4. Check API responses for errors
5. Look at response data for /meals/daily-nutrition-summary
""")


if __name__ == "__main__":
    test_daily_summary()
