#!/usr/bin/env python3
"""
Test script to directly test the backend query logic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime, date, timedelta, timezone
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, joinedload
from app.models.nutrition import Meal as MealModel, MealItem
from app.schemas.meal_models import Meal as MealSchema


def test_backend_query():
    """Test the backend query logic directly."""

    print("Testing backend query logic...")
    print("=" * 60)

    # Connect to the actual database
    db_path = "backend/weight_management.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # First, let's find a meal that we know has items
        print("1. Finding a meal with items...")

        # Query for meals with items
        meals_with_items = (
            db.query(MealModel)
            .join(MealItem)
            .group_by(MealModel.id)
            .having(func.count(MealItem.id) > 0)
            .limit(3)
            .all()
        )

        print(f"   Found {len(meals_with_items)} meals with items")

        for i, meal in enumerate(meals_with_items):
            print(f"\n   Meal {i + 1}:")
            print(f"     ID: {meal.id}")
            print(f"     Name: {meal.name}")
            print(f"     Type: {meal.meal_type}")
            print(f"     Date: {meal.meal_datetime}")

            # Check if meal_items is loaded
            print(f"     Has meal_items attribute: {hasattr(meal, 'meal_items')}")

            # Try to access meal_items
            if hasattr(meal, "meal_items"):
                # Check if it's a relationship proxy
                print(f"     meal_items type: {type(meal.meal_items)}")

                # Try to get the items
                try:
                    items = meal.meal_items
                    print(
                        f"     meal_items count (direct access): {len(items) if items else 0}"
                    )
                except Exception as e:
                    print(f"     Error accessing meal_items directly: {e}")

        # Now test with joinedload
        print("\n2. Testing with joinedload...")

        # Get a specific meal ID that we know has items (from earlier database query)
        meal_id = 2  # From earlier test, meal ID 2 has 2 items

        meal_with_join = (
            db.query(MealModel)
            .options(joinedload(MealModel.meal_items))
            .filter(MealModel.id == meal_id)
            .first()
        )

        if meal_with_join:
            print(f"   Found meal ID {meal_with_join.id}")
            print(f"   Name: {meal_with_join.name}")

            # Check meal_items
            print(
                f"   Has meal_items attribute: {hasattr(meal_with_join, 'meal_items')}"
            )

            if hasattr(meal_with_join, "meal_items"):
                try:
                    items = meal_with_join.meal_items
                    print(f"   meal_items count: {len(items) if items else 0}")

                    if items:
                        print(f"   First 2 items:")
                        for j, item in enumerate(items[:2]):
                            print(f"     Item {j + 1}: {item.name}")
                            print(
                                f"       Serving: {item.serving_size}{item.serving_unit}"
                            )
                            print(f"       Calories: {item.calories_per_serving}")
                except Exception as e:
                    print(f"   Error accessing meal_items: {e}")

            # Now test Pydantic conversion
            print("\n3. Testing Pydantic conversion...")
            try:
                meal_schema = MealSchema.model_validate(meal_with_join)
                print(f"   Pydantic conversion successful!")
                print(f"   Has items attribute: {hasattr(meal_schema, 'items')}")
                print(
                    f"   Items count: {len(meal_schema.items) if meal_schema.items else 0}"
                )

                if meal_schema.items:
                    print(f"   First item name: {meal_schema.items[0].name}")

                    # Convert to dict to see what would be returned by API
                    meal_dict = meal_schema.model_dump()
                    print(f"\n4. Converted to dict:")
                    print(f"   Keys: {list(meal_dict.keys())}")
                    print(f"   Has 'items' key: {'items' in meal_dict}")
                    if "items" in meal_dict:
                        print(f"   Items in dict: {len(meal_dict['items'])}")
                        print(f"   First item in dict: {meal_dict['items'][0]['name']}")
            except Exception as e:
                print(f"   Pydantic conversion error: {e}")
                import traceback

                traceback.print_exc()
        else:
            print(f"   Meal ID {meal_id} not found")

    finally:
        db.close()


if __name__ == "__main__":
    test_backend_query()
