#!/usr/bin/env python3
"""Test backend startup"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

try:
    print("Testing backend startup...")

    # Import app
    from app.main import app

    print("✅ App imported successfully")

    # Test database
    from app.core.database import engine

    print("✅ Database engine created")

    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✅ Database connection works: {result.scalar()}")

    # Test model imports
    from app.models.user import User

    print("✅ User model imported")

    from app.models.nutrition import Meal

    print("✅ Meal model imported")

    from app.models.calorie_goal import CalorieGoal

    print("✅ CalorieGoal model imported")

    print("\n✅ All imports successful!")

except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
