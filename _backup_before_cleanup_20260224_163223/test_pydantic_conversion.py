#!/usr/bin/env python3
"""
Test script to check Pydantic schema conversion for meals.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime, timezone
from app.schemas.meal_models import Meal, MealItem
from pydantic import ValidationError


def test_pydantic_conversion():
    """Test Pydantic schema conversion."""

    print("Testing Pydantic schema conversion...")
    print("=" * 60)

    # Create a sample meal item
    meal_item_data = {
        "id": 1,
        "meal_id": 1,
        "name": "米饭",
        "serving_size": 150.0,
        "serving_unit": "g",
        "quantity": 1.0,
        "calories_per_serving": 174.0,
        "protein_per_serving": 3.0,
        "carbs_per_serving": 38.0,
        "fat_per_serving": 0.5,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        # Test MealItem schema
        print("1. Testing MealItem schema...")
        meal_item = MealItem(**meal_item_data)
        print(f"   MealItem created successfully")
        print(f"   Name: {meal_item.name}")
        print(f"   Serving: {meal_item.serving_size}{meal_item.serving_unit}")
        print(f"   Calories: {meal_item.calories_per_serving}")
    except ValidationError as e:
        print(f"   MealItem validation error: {e}")

    # Create a sample meal with items
    meal_data = {
        "id": 1,
        "user_id": 4,
        "name": "午餐餐食",
        "meal_type": "lunch",
        "meal_datetime": datetime.now(timezone.utc),
        "calories": 524.0,
        "protein": 15.0,
        "carbs": 46.0,
        "fat": 30.5,
        "notes": "测试餐食",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "meal_items": [meal_item_data],  # Note: using 'meal_items' not 'items'
    }

    try:
        # Test Meal schema with 'meal_items' field
        print("\n2. Testing Meal schema with 'meal_items' field...")
        meal_with_meal_items = Meal(**meal_data)
        print(f"   Meal created successfully with 'meal_items' field")
        print(f"   Has items field: {hasattr(meal_with_meal_items, 'items')}")
        print(
            f"   Items count: {len(meal_with_meal_items.items) if meal_with_meal_items.items else 0}"
        )
        if meal_with_meal_items.items:
            print(f"   First item name: {meal_with_meal_items.items[0].name}")
    except ValidationError as e:
        print(f"   Meal validation error with 'meal_items': {e}")

    # Now test with 'items' field instead
    meal_data_with_items = meal_data.copy()
    meal_data_with_items["items"] = meal_data_with_items.pop("meal_items")

    try:
        # Test Meal schema with 'items' field
        print("\n3. Testing Meal schema with 'items' field...")
        meal_with_items = Meal(**meal_data_with_items)
        print(f"   Meal created successfully with 'items' field")
        print(f"   Has items field: {hasattr(meal_with_items, 'items')}")
        print(
            f"   Items count: {len(meal_with_items.items) if meal_with_items.items else 0}"
        )
        if meal_with_items.items:
            print(f"   First item name: {meal_with_items.items[0].name}")
    except ValidationError as e:
        print(f"   Meal validation error with 'items': {e}")

    # Test the alias functionality
    print("\n4. Testing alias functionality...")
    print(
        f"   Meal schema field 'items' has alias 'meal_items': {Meal.model_fields['items'].alias == 'meal_items'}"
    )
    print(
        f"   Meal schema Config.populate_by_name: {Meal.model_config.get('populate_by_name', False)}"
    )

    # Test creating from dict with different field names
    test_data = {
        "id": 2,
        "user_id": 4,
        "name": "测试餐",
        "meal_type": "dinner",
        "meal_datetime": datetime.now(timezone.utc),
        "calories": 300.0,
        "created_at": datetime.now(timezone.utc),
    }

    # Test with meal_items
    test_with_meal_items = test_data.copy()
    test_with_meal_items["meal_items"] = [meal_item_data]

    try:
        meal1 = Meal(**test_with_meal_items)
        print(f"\n5. Created meal with 'meal_items' field:")
        print(f"   Items count: {len(meal1.items)}")
    except ValidationError as e:
        print(f"\n5. Failed to create meal with 'meal_items': {e}")

    # Test with items
    test_with_items = test_data.copy()
    test_with_items["items"] = [meal_item_data]

    try:
        meal2 = Meal(**test_with_items)
        print(f"\n6. Created meal with 'items' field:")
        print(f"   Items count: {len(meal2.items)}")
    except ValidationError as e:
        print(f"\n6. Failed to create meal with 'items': {e}")


if __name__ == "__main__":
    test_pydantic_conversion()
