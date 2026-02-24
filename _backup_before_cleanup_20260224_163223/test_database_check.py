#!/usr/bin/env python3
"""直接检查数据库，看看食材是否保存了"""

import sys

sys.path.insert(0, "/Users/felix/bmad/backend")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.nutrition import Meal, MealItem
from app.core.database import Base

# 创建数据库连接
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bmad"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_database():
    """检查数据库中的餐食和食材"""
    db = SessionLocal()

    try:
        # 获取所有餐食
        meals = db.query(Meal).all()
        print(f"数据库中有 {len(meals)} 条餐食记录")

        for meal in meals:
            print(f"\n餐食ID: {meal.id}")
            print(f"  名称: {meal.name}")
            print(f"  用户ID: {meal.user_id}")
            print(f"  餐型: {meal.meal_type}")

            # 直接访问meal_items关系
            print(f"  meal_items关系类型: {type(meal.meal_items)}")
            print(f"  meal_items数量: {len(meal.meal_items)}")

            if meal.meal_items:
                print("  ✅ 数据库中有食材记录:")
                for item in meal.meal_items:
                    print(
                        f"    食材ID: {item.id}, 名称: {item.name}, 份量: {item.serving_size}{item.serving_unit}"
                    )
            else:
                print("  ❌ 数据库中没有食材记录")

                # 检查meal_items表
                items = db.query(MealItem).filter(MealItem.meal_id == meal.id).all()
                print(f"  直接查询meal_items表: {len(items)} 条记录")
                for item in items:
                    print(f"    食材ID: {item.id}, 名称: {item.name}")

        # 检查meal_items表的所有记录
        print("\n" + "=" * 60)
        print("检查meal_items表的所有记录:")
        all_items = db.query(MealItem).all()
        print(f"meal_items表总记录数: {len(all_items)}")

        for item in all_items:
            print(f"  食材ID: {item.id}, 餐食ID: {item.meal_id}, 名称: {item.name}")

    finally:
        db.close()


if __name__ == "__main__":
    check_database()
