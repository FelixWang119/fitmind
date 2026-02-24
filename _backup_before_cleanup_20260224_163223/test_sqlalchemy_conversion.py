#!/usr/bin/env python3
"""
Test script to check SQLAlchemy to Pydantic conversion.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime, timezone
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, Field
from typing import List, Optional

# Create a simple test setup
Base = declarative_base()


class MealItemModel(Base):
    __tablename__ = "meal_items"

    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))
    name = Column(String(100))
    serving_size = Column(Integer)
    serving_unit = Column(String(10))
    quantity = Column(Integer)
    calories_per_serving = Column(Integer)


class MealModel(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String(100))
    meal_type = Column(String(20))
    calories = Column(Integer)
    meal_datetime = Column(DateTime)
    created_at = Column(DateTime)

    # Relationship
    meal_items = relationship("MealItemModel", backref="meal")


# Pydantic schemas
class MealItemSchema(BaseModel):
    id: int
    meal_id: int
    name: str
    serving_size: Optional[int] = None
    serving_unit: Optional[str] = None
    quantity: Optional[int] = None
    calories_per_serving: Optional[int] = None

    class Config:
        from_attributes = True


class MealSchema(BaseModel):
    id: int
    user_id: int
    name: str
    meal_type: str
    calories: Optional[int] = None
    meal_datetime: datetime
    created_at: datetime
    items: List[MealItemSchema] = Field(default_factory=list, alias="meal_items")

    class Config:
        from_attributes = True
        populate_by_name = True


def test_conversion():
    """Test SQLAlchemy to Pydantic conversion."""

    print("Testing SQLAlchemy to Pydantic conversion...")
    print("=" * 60)

    # Create an in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a test meal with items
    now = datetime.now(timezone.utc)

    meal = MealModel(
        id=1,
        user_id=4,
        name="午餐餐食",
        meal_type="lunch",
        calories=524,
        meal_datetime=now,
        created_at=now,
    )

    # Add meal items
    meal_item1 = MealItemModel(
        id=1,
        meal_id=1,
        name="米饭",
        serving_size=150,
        serving_unit="g",
        quantity=1,
        calories_per_serving=174,
    )

    meal_item2 = MealItemModel(
        id=2,
        meal_id=1,
        name="红烧肉",
        serving_size=100,
        serving_unit="g",
        quantity=1,
        calories_per_serving=350,
    )

    meal.meal_items = [meal_item1, meal_item2]

    # Add to session but don't commit (we're just testing in memory)
    session.add(meal)
    session.add(meal_item1)
    session.add(meal_item2)
    session.flush()

    print("1. SQLAlchemy meal object:")
    print(f"   ID: {meal.id}")
    print(f"   Name: {meal.name}")
    print(f"   Has meal_items attribute: {hasattr(meal, 'meal_items')}")
    print(f"   meal_items type: {type(meal.meal_items)}")
    print(f"   meal_items count: {len(meal.meal_items)}")

    # Try to convert using model_validate
    print("\n2. Converting using MealSchema.model_validate(meal):")
    try:
        meal_schema = MealSchema.model_validate(meal)
        print(f"   Success!")
        print(f"   Has items attribute: {hasattr(meal_schema, 'items')}")
        print(f"   Items count: {len(meal_schema.items) if meal_schema.items else 0}")
        if meal_schema.items:
            print(f"   First item name: {meal_schema.items[0].name}")

        # Convert back to dict to see field names
        meal_dict = meal_schema.model_dump()
        print(f"\n3. Converted to dict:")
        print(f"   Keys: {list(meal_dict.keys())}")
        print(f"   Has 'items' key: {'items' in meal_dict}")
        print(f"   Has 'meal_items' key: {'meal_items' in meal_dict}")
        if "items" in meal_dict:
            print(f"   Items in dict: {len(meal_dict['items'])}")

        # Also check model_dump with mode='json'
        print(f"\n4. Checking model_dump with by_alias=True:")
        meal_dict_by_alias = meal_schema.model_dump(by_alias=True)
        print(f"   Has 'items' key: {'items' in meal_dict_by_alias}")
        print(f"   Has 'meal_items' key: {'meal_items' in meal_dict_by_alias}")

    except Exception as e:
        print(f"   Error: {e}")
        import traceback

        traceback.print_exc()

    # Test with from_orm (deprecated in Pydantic v2)
    print("\n5. Testing with from_orm (deprecated):")
    try:
        # In Pydantic v2, from_orm is deprecated but might still work
        meal_schema_orm = MealSchema.from_orm(meal)
        print(f"   Success with from_orm!")
        print(
            f"   Items count: {len(meal_schema_orm.items) if meal_schema_orm.items else 0}"
        )
    except Exception as e:
        print(f"   Error with from_orm: {e}")

    session.close()


if __name__ == "__main__":
    test_conversion()
