#!/usr/bin/env python3
"""Test ORM conversion for Meal to MealSchema"""

import sys

sys.path.insert(0, "./backend")

from datetime import datetime, timezone
from app.schemas.meal_models import Meal as MealSchema, MealItem
from app.models.nutrition import Meal as MealModel, MealItem as MealItemModel


# Create a mock MealItem SQLAlchemy-like object
class MockMealItem:
    def __init__(self):
        self.id = 1
        self.meal_id = 1
        self.food_item_id = None
        self.name = "Test Food"
        self.serving_size = 100.0
        self.serving_unit = "g"
        self.quantity = 1.0
        self.notes = None
        self.calories_per_serving = 100.0
        self.protein_per_serving = 10
        self.carbs_per_serving = 20
        self.fat_per_serving = 5
        self.created_at = datetime.now(timezone.utc)


# Create a mock Meal SQLAlchemy-like object
class MockMeal:
    def __init__(self):
        self.id = 1
        self.user_id = 1
        self.meal_type = "lunch"
        self.name = "Test Meal"
        self.notes = None
        self.photo_url = None
        self.calories = 100
        self.protein = 10
        self.carbs = 20
        self.fat = 5
        self.fiber = None
        self.sugar = None
        self.sodium = None
        self.meal_datetime = datetime.now(timezone.utc)
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = None
        self.meal_items = [MockMealItem()]  # SQLAlchemy uses meal_items, not items


print("Testing MealSchema.from_orm() with mock objects...")
try:
    mock_meal = MockMeal()
    # Use model_validate instead of from_orm (deprecated)
    meal_schema = MealSchema.model_validate(mock_meal)
    print("✅ Success! MealSchema created from ORM")
    print(f"  Meal has {len(meal_schema.items)} items")
    print(
        f"  First item name: {meal_schema.items[0].name if meal_schema.items else 'None'}"
    )
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
