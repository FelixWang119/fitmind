#!/usr/bin/env python3
"""
Test script to directly query the database and check meal items.
"""

import sqlite3
import json
from datetime import datetime


def test_database_query():
    """Query the database directly to check meal items."""

    db_path = "backend/weight_management.db"

    print("Testing database query for meal items...")
    print("=" * 60)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()

        # First, let's check how many meals we have
        cursor.execute("SELECT COUNT(*) as count FROM meals")
        meal_count = cursor.fetchone()["count"]
        print(f"1. Total meals in database: {meal_count}")

        # Get some sample meals
        cursor.execute("""
            SELECT id, name, meal_type, meal_datetime, calories, protein, carbs, fat
            FROM meals 
            ORDER BY meal_datetime DESC 
            LIMIT 5
        """)
        meals = cursor.fetchall()

        print(f"\n2. Sample meals (first {len(meals)}):")
        for i, meal in enumerate(meals):
            print(f"   Meal {i + 1}:")
            print(f"     ID: {meal['id']}")
            print(f"     Name: {meal['name']}")
            print(f"     Type: {meal['meal_type']}")
            print(f"     Date: {meal['meal_datetime']}")
            print(f"     Calories: {meal['calories']}")
            print(f"     Protein: {meal['protein']}")
            print(f"     Carbs: {meal['carbs']}")
            print(f"     Fat: {meal['fat']}")

            # Now check meal items for this meal
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM meal_items 
                WHERE meal_id = ?
            """,
                (meal["id"],),
            )
            item_count = cursor.fetchone()["count"]
            print(f"     Meal items count: {item_count}")

            if item_count > 0:
                cursor.execute(
                    """
                    SELECT id, name, serving_size, serving_unit, quantity,
                           calories_per_serving, protein_per_serving, 
                           carbs_per_serving, fat_per_serving
                    FROM meal_items 
                    WHERE meal_id = ?
                    LIMIT 3
                """,
                    (meal["id"],),
                )
                items = cursor.fetchall()
                print(f"     First {len(items)} items:")
                for j, item in enumerate(items):
                    print(f"       Item {j + 1}: {item['name']}")
                    print(
                        f"         Serving: {item['serving_size']} {item['serving_unit']}"
                    )
                    print(f"         Quantity: {item['quantity']}")
                    print(f"         Calories: {item['calories_per_serving']}")

        # Let's also check the user_id for these meals to understand which user they belong to
        print(f"\n3. Checking user associations:")
        cursor.execute("""
            SELECT DISTINCT user_id, COUNT(*) as meal_count
            FROM meals
            GROUP BY user_id
        """)
        user_meals = cursor.fetchall()
        for user_meal in user_meals:
            print(f"   User ID {user_meal['user_id']}: {user_meal['meal_count']} meals")

            # Get user email for this user_id
            cursor.execute(
                "SELECT email FROM users WHERE id = ?", (user_meal["user_id"],)
            )
            user = cursor.fetchone()
            if user:
                print(f"     User email: {user['email']}")

        # Let's check the most recent meal with items
        print(f"\n4. Most recent meal with items:")
        cursor.execute("""
            SELECT m.id, m.name, m.meal_type, m.meal_datetime,
                   COUNT(mi.id) as item_count
            FROM meals m
            LEFT JOIN meal_items mi ON m.id = mi.meal_id
            GROUP BY m.id
            HAVING item_count > 0
            ORDER BY m.meal_datetime DESC
            LIMIT 1
        """)
        recent_meal = cursor.fetchone()
        if recent_meal:
            print(f"   Meal ID: {recent_meal['id']}")
            print(f"   Name: {recent_meal['name']}")
            print(f"   Type: {recent_meal['meal_type']}")
            print(f"   Date: {recent_meal['meal_datetime']}")
            print(f"   Item count: {recent_meal['item_count']}")

            # Get all items for this meal
            cursor.execute(
                """
                SELECT name, serving_size, serving_unit, quantity,
                       calories_per_serving, protein_per_serving,
                       carbs_per_serving, fat_per_serving
                FROM meal_items
                WHERE meal_id = ?
            """,
                (recent_meal["id"],),
            )
            items = cursor.fetchall()
            print(f"   All items for this meal:")
            for item in items:
                print(
                    f"     - {item['name']}: {item['quantity']} x {item['serving_size']}{item['serving_unit']}"
                )
                print(
                    f"       Calories: {item['calories_per_serving']}, Protein: {item['protein_per_serving']}"
                )

        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_database_query()
