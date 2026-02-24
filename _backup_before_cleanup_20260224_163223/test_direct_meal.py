#!/usr/bin/env python3
"""Direct test of meal creation"""

import requests
import json
from datetime import datetime, timezone

# Get token
with open("/Users/felix/bmad/test_token.txt", "r") as f:
    token = f.read().strip()

print(f"Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Create meal
meal_data = {
    "meal_type": "lunch",
    "name": "Direct Test Meal",
    "meal_datetime": datetime.now(timezone.utc).isoformat(),
    "notes": "Direct test",
    "items": [
        {
            "name": "Test Food",
            "serving_size": 100,
            "serving_unit": "g",
            "quantity": 1,
            "calories_per_serving": 100,
        }
    ],
}

print("\nCreating meal...")
response = requests.post(
    "http://localhost:8000/api/v1/meals", json=meal_data, headers=headers, timeout=10
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    result = response.json()
    print(f"Success! Meal ID: {result.get('id')}")
    print(f"Response keys: {list(result.keys())}")

    if "items" in result:
        print(f"✅ Found 'items' field with {len(result['items'])} items")
    elif "meal_items" in result:
        print(f"⚠️ Found 'meal_items' field (not 'items')")
    else:
        print("❌ No items field found")
        print(f"Response: {json.dumps(result, indent=2)}")
else:
    print(f"Error: {response.text}")
