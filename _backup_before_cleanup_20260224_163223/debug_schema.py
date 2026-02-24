#!/usr/bin/env python3
"""Debug the schema issue"""

import sys

sys.path.insert(0, "./backend")

from app.schemas.meal_models import DailyNutritionSummary, Meal, MealItem
from datetime import datetime

# Test creating a DailyNutritionSummary with minimal data
print("Testing DailyNutritionSummary schema...")

# Create a simple MealItem
meal_item = MealItem(
    name="Test Food",
    serving_size=100.0,
    serving_unit="g",
    quantity=1.0,
    calories_per_serving=100.0,
    protein_per_serving=10.0,
    carbs_per_serving=20.0,
    fat_per_serving=5.0,
)

# Create a simple Meal
meal = Meal(
    id=1,
    user_id=1,
    calories=100.0,
    protein=10.0,
    carbs=20.0,
    fat=5.0,
    created_at=datetime.now(),
    items=[meal_item],
)

# Create DailyNutritionSummary
summary = DailyNutritionSummary(
    date="2026-02-24",
    total_calories=100.0,
    total_protein=10.0,
    total_carbs=20.0,
    total_fat=5.0,
    meal_count=1,
    meals=[meal],
)

print("✅ Schema test successful!")
print(f"Summary: {summary}")
