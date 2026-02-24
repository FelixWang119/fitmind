#!/usr/bin/env python3
"""
Test FastAPI serialization behavior.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from pydantic import BaseModel, Field
from typing import List


# Create a test schema with alias
class Item(BaseModel):
    id: int
    name: str


class TestModel(BaseModel):
    id: int
    name: str
    items: List[Item] = Field(default_factory=list, alias="test_items")

    class Config:
        from_attributes = True
        populate_by_name = True


def test_serialization():
    """Test how Pydantic serializes models with aliases."""

    print("Testing Pydantic serialization with aliases...")
    print("=" * 60)

    # Create a test instance
    test_data = {
        "id": 1,
        "name": "Test",
        "test_items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
    }

    # Create model instance
    model = TestModel(**test_data)

    print("1. Model instance created")
    print(f"   Has items attribute: {hasattr(model, 'items')}")
    print(f"   Items count: {len(model.items)}")

    # Test model_dump() without by_alias
    print("\n2. model_dump() without by_alias:")
    dump_default = model.model_dump()
    print(f"   Keys: {list(dump_default.keys())}")
    print(f"   Has 'items' key: {'items' in dump_default}")
    print(f"   Has 'test_items' key: {'test_items' in dump_default}")

    # Test model_dump() with by_alias=True
    print("\n3. model_dump() with by_alias=True:")
    dump_with_alias = model.model_dump(by_alias=True)
    print(f"   Keys: {list(dump_with_alias.keys())}")
    print(f"   Has 'items' key: {'items' in dump_with_alias}")
    print(f"   Has 'test_items' key: {'test_items' in dump_with_alias}")

    # Test model_dump_json() without by_alias
    print("\n4. model_dump_json() without by_alias:")
    json_default = model.model_dump_json()
    print(f"   JSON (first 100 chars): {json_default[:100]}...")

    # Test model_dump_json() with by_alias=True
    print("\n5. model_dump_json() with by_alias=True:")
    json_with_alias = model.model_dump_json(by_alias=True)
    print(f"   JSON (first 100 chars): {json_with_alias[:100]}...")

    # Now test what happens when we create with 'items' instead of 'test_items'
    print("\n6. Testing with 'items' field instead of 'test_items':")
    test_data_with_items = {
        "id": 2,
        "name": "Test 2",
        "items": [{"id": 3, "name": "Item 3"}, {"id": 4, "name": "Item 4"}],
    }

    model2 = TestModel(**test_data_with_items)
    print(f"   Model created successfully")
    print(f"   Items count: {len(model2.items)}")

    dump2 = model2.model_dump()
    print(f"   Has 'items' key in dump: {'items' in dump2}")
    print(f"   Has 'test_items' key in dump: {'test_items' in dump2}")


if __name__ == "__main__":
    test_serialization()
