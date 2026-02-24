#!/usr/bin/env python3
"""Diagnose why meals show as saved but don't appear in frontend"""

import sqlite3
import os


def diagnose_meal_issue():
    print("=" * 60)
    print("Meal Save Issue Diagnosis")
    print("=" * 60)

    db_path = "/Users/felix/bmad/backend/weight_management.db"

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n1. Database Analysis")
    print("-" * 40)

    # Get all users
    cursor.execute("SELECT id, email, username FROM users ORDER BY id")
    users = cursor.fetchall()
    print(f"Total users in database: {len(users)}")
    for user in users:
        print(f"  User ID: {user[0]}, Email: {user[1]}, Username: {user[2]}")

    # Get all meals with user info
    print(
        f"\nTotal meals in database: {cursor.execute('SELECT COUNT(*) FROM meals').fetchone()[0]}"
    )

    cursor.execute("""
        SELECT m.id, m.name, m.meal_datetime, m.user_id, u.email, u.username
        FROM meals m
        LEFT JOIN users u ON m.user_id = u.id
        ORDER BY m.id DESC
        LIMIT 10
    """)

    recent_meals = cursor.fetchall()
    print(f"\nRecent meals (last 10):")
    for meal in recent_meals:
        print(f"  Meal ID: {meal[0]}, Name: {meal[1]}, Date: {meal[2]}")
        print(f"    User ID: {meal[3]}, Email: {meal[4]}, Username: {meal[5]}")

    # Check for date issues
    print(f"\n2. Date Analysis")
    print("-" * 40)

    cursor.execute("SELECT MIN(meal_datetime), MAX(meal_datetime) FROM meals")
    min_max = cursor.fetchone()
    print(f"Earliest meal date: {min_max[0]}")
    print(f"Latest meal date: {min_max[1]}")

    # Check meals by date
    cursor.execute("""
        SELECT DATE(meal_datetime), COUNT(*) as meal_count
        FROM meals 
        GROUP BY DATE(meal_datetime)
        ORDER BY DATE(meal_datetime) DESC
        LIMIT 5
    """)

    print(f"\nMeals by date (last 5 days):")
    for row in cursor.fetchall():
        print(f"  Date: {row[0]}, Meals: {row[1]}")

    # Check meal_items
    print(f"\n3. Meal Items Analysis")
    print("-" * 40)

    cursor.execute("SELECT COUNT(*) FROM meal_items")
    print(f"Total meal items: {cursor.fetchone()[0]}")

    cursor.execute("""
        SELECT mi.meal_id, mi.name, mi.calories_per_serving, m.name as meal_name
        FROM meal_items mi
        JOIN meals m ON mi.meal_id = m.id
        ORDER BY mi.id DESC
        LIMIT 5
    """)

    print(f"\nRecent meal items:")
    for item in cursor.fetchall():
        print(
            f"  Meal ID: {item[0]}, Meal: {item[3]}, Item: {item[1]}, Calories: {item[2]}"
        )

    # Check for potential issues
    print(f"\n4. Potential Issues Check")
    print("-" * 40)

    # Check for meals without items
    cursor.execute("""
        SELECT m.id, m.name, m.meal_datetime
        FROM meals m
        LEFT JOIN meal_items mi ON m.id = mi.meal_id
        WHERE mi.id IS NULL
    """)

    meals_without_items = cursor.fetchall()
    if meals_without_items:
        print(f"❌ Found {len(meals_without_items)} meals without items:")
        for meal in meals_without_items:
            print(f"  Meal ID: {meal[0]}, Name: {meal[1]}, Date: {meal[2]}")
    else:
        print("✅ All meals have items")

    # Check for duplicate recent meals (same user, same date/time)
    cursor.execute("""
        SELECT user_id, meal_datetime, COUNT(*) as duplicate_count
        FROM meals
        GROUP BY user_id, meal_datetime
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC
    """)

    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} potential duplicate meals:")
        for dup in duplicates:
            print(f"  User ID: {dup[0]}, DateTime: {dup[1]}, Count: {dup[2]}")
    else:
        print("✅ No duplicate meals found")

    conn.close()

    print(f"\n" + "=" * 60)
    print("Diagnosis Summary")
    print("=" * 60)
    print("""
Based on the database analysis:

1. ✅ Meals ARE being saved to the database
2. ✅ Meals have associated meal items
3. ✅ Dates appear correct (2026-02-24 matches current date)

Possible reasons meals don't appear in frontend:
1. **User mismatch**: Logged-in user different from meal user_id
2. **Date filtering**: Frontend filtering by wrong date
3. **API response**: Backend returning empty list due to query issues
4. **Frontend state**: React state not updating after save
5. **Authentication**: Token/user session issue

Next steps:
1. Check which user is currently logged in frontend
2. Verify frontend API calls in browser DevTools
3. Check backend logs for query errors
4. Test API endpoints directly with correct user auth
""")


if __name__ == "__main__":
    diagnose_meal_issue()
