#!/usr/bin/env python3
"""测试导入meals模块"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

print("测试导入meals模块...")

try:
    from app.api.v1.endpoints import meals

    print("✅ 成功导入meals模块")

    # 检查router是否定义
    if hasattr(meals, "router"):
        print("✅ meals模块有router属性")
    else:
        print("❌ meals模块没有router属性")

except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback

    traceback.print_exc()
