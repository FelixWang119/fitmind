#!/usr/bin/env python3
"""Test QwenConfig to see if it has Pydantic validation issues."""

import sys

sys.path.insert(0, "/Users/felix/bmad/backend")

try:
    from app.core.qwen_config import qwen_config

    print("✅ Successfully imported qwen_config")
    print(f"  QWEN_API_KEY configured: {bool(qwen_config.QWEN_API_KEY)}")
    print(f"  QWEN_TEXT_MODEL: {qwen_config.QWEN_TEXT_MODEL}")
    print(f"  QWEN_VISION_MODEL: {qwen_config.QWEN_VISION_MODEL}")
except Exception as e:
    print(f"❌ Error importing qwen_config: {e}")
    import traceback

    traceback.print_exc()

# Also test importing the main app
print("\n--- Testing main app import ---")
try:
    from app.main import app

    print("✅ Successfully imported main app")
except Exception as e:
    print(f"❌ Error importing main app: {e}")
    import traceback

    traceback.print_exc()
