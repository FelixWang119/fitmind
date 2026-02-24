#!/usr/bin/env python3
"""Check backend startup errors"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

print("Checking for import errors...")

# 逐个导入模块来查找错误
modules_to_check = [
    "app.core.database",
    "app.models.user",
    "app.models.nutrition",
    "app.models.calorie_goal",
    "app.api.v1.endpoints.meals",
    "app.main",
]

for module_name in modules_to_check:
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
    except Exception as e:
        print(f"❌ {module_name}: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        print()

print("\nChecking FastAPI app creation...")
try:
    from app.main import app

    print("✅ FastAPI app created")

    # 检查路由
    print(f"\nRoutes found: {len(app.routes)}")
    for route in app.routes:
        if hasattr(route, "path"):
            print(
                f"  - {route.path} ({route.methods if hasattr(route, 'methods') else 'N/A'})"
            )
except Exception as e:
    print(f"❌ App creation failed: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
