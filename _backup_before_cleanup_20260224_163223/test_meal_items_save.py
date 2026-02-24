#!/usr/bin/env python3
"""
Test script to verify if meal_items are being saved to the database.
This script simulates the create_meal endpoint logic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.nutrition import Meal, MealItem
from app.schemas.meal_models import MealCreate, MealItemCreate


def test_meal_creation():
    """Test meal creation with items"""
    db = SessionLocal()

    try:
        # Create a test meal with items
        meal_data = MealCreate(
            meal_type="lunch",
            name="Test Lunch",
            meal_datetime=datetime.now(timezone.utc),
            notes="Test meal with items",
            items=[
                MealItemCreate(
                    name="Rice",
                    serving_size=100,
                    serving_unit="g",
                    quantity=1,
                    calories_per_serving=130,
                    protein_per_serving=2,
                    carbs_per_serving=28,
                    fat_per_serving=0.3,
                ),
                MealItemCreate(
                    name="Chicken",
                    serving_size=100,
                    serving_unit="g",
                    quantity=1,
                    calories_per_serving=165,
                    protein_per_serving=31,
                    carbs_per_serving=0,
                    fat_per_serving=3.6,
                ),
            ],
        )

        # Simulate create_meal endpoint logic
        total_calories = 0
        total_proteins = 0
        total_carbs = 0
        total_fat = 0

        for item in meal_data.items:
            if item.calories_per_serving:
                if item.quantity:
                    total_calories += item.calories_per_serving * item.quantity
                else:
                    total_calories += item.calories_per_serving
            if item.protein_per_serving:
                if item.quantity:
                    total_proteins += item.protein_per_serving * item.quantity
                else:
                    total_proteins += item.protein_per_serving
            if item.carbs_per_serving:
                if item.quantity:
                    total_carbs += item.carbs_per_serving * item.quantity
                else:
                    total_carbs += item.carbs_per_serving
            if item.fat_per_serving:
                if item.quantity:
                    total_fat += item.fat_per_serving * item.quantity
                else:
                    total_fat += item.fat_per_serving

        # Create meal (using user_id=1 for testing)
        meal = Meal(
            user_id=1,
            meal_type=meal_data.meal_type,
            name=meal_data.name,
            meal_datetime=meal_data.meal_datetime,
            notes=meal_data.notes,
            calories=int(total_calories) if total_calories else 0,
            protein=int(total_proteins) if total_proteins else 0,
            carbs=int(total_carbs) if total_carbs else 0,
            fat=int(total_fat) if total_fat else 0,
        )

        db.add(meal)
        db.flush()  # Get meal.id but don't commit

        # Create meal items
        if meal_data.items:
            for item_data in meal_data.items:
                meal_item = MealItem(
                    meal_id=meal.id,
                    name=item_data.name,
                    serving_size=item_data.serving_size,
                    serving_unit=item_data.serving_unit,
                    quantity=item_data.quantity,
                    notes=item_data.notes,
                    calories_per_serving=item_data.calories_per_serving,
                    protein_per_serving=item_data.protein_per_serving,
                    carbs_per_serving=item_data.carbs_per_serving,
                    fat_per_serving=item_data.fat_per_serving,
                )
                db.add(meal_item)

        db.commit()
        db.refresh(meal)

        print(f"✅ Meal created with ID: {meal.id}")
        print(f"   Meal calories: {meal.calories}")
        print(f"   Meal protein: {meal.protein}")

        # Now query the meal with its items
        meal_with_items = db.query(Meal).filter(Meal.id == meal.id).first()

        print(f"\n🔍 Checking meal items relationship...")
        print(f"   Has meal_items attribute: {hasattr(meal_with_items, 'meal_items')}")
        if hasattr(meal_with_items, "meal_items"):
            print(f"   Number of meal_items: {len(meal_with_items.meal_items)}")
            for item in meal_with_items.meal_items:
                print(f"   - {item.name}: {item.calories_per_serving} cal")

        # Also query MealItem table directly
        meal_items = db.query(MealItem).filter(MealItem.meal_id == meal.id).all()
        print(f"\n🔍 Direct query of MealItem table:")
        print(f"   Found {len(meal_items)} meal items")
        for item in meal_items:
            print(f"   - ID: {item.id}, Name: {item.name}, Meal ID: {item.meal_id}")

        # Clean up
        db.query(MealItem).filter(MealItem.meal_id == meal.id).delete()
        db.query(Meal).filter(Meal.id == meal.id).delete()
        db.commit()
        print(f"\n🧹 Cleaned up test meal {meal.id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("🧪 Testing meal creation with items...")
    test_meal_creation()
