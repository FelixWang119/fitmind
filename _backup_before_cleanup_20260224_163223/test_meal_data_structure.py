#!/usr/bin/env python3
"""测试餐食数据结构，查看为什么items为空"""

import sqlite3
import json


def check_meal_data_structure():
    print("检查餐食数据结构...")
    print("=" * 60)

    db_path = "/Users/felix/bmad/backend/weight_management.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 检查最近的一条餐食记录
        print("1. 检查最近的餐食记录:")
        cursor.execute("""
            SELECT m.id, m.name, m.meal_type, m.calories, m.protein, m.carbs, m.fat, 
                   m.meal_datetime, m.user_id
            FROM meals m
            ORDER BY m.id DESC
            LIMIT 1
        """)

        meal = cursor.fetchone()
        if meal:
            print(f"   餐食ID: {meal[0]}")
            print(f"   名称: {meal[1]}")
            print(f"   类型: {meal[2]}")
            print(f"   热量: {meal[3]}")
            print(f"   蛋白质: {meal[4]}")
            print(f"   碳水: {meal[5]}")
            print(f"   脂肪: {meal[6]}")
            print(f"   时间: {meal[7]}")
            print(f"   用户ID: {meal[8]}")

            # 2. 检查这条餐食的items
            print(f"\n2. 检查餐食ID={meal[0]}的items:")
            cursor.execute(
                """
                SELECT mi.id, mi.name, mi.serving_size, mi.serving_unit, mi.quantity,
                       mi.calories_per_serving, mi.protein_per_serving, 
                       mi.carbs_per_serving, mi.fat_per_serving
                FROM meal_items mi
                WHERE mi.meal_id = ?
                ORDER BY mi.id
            """,
                (meal[0],),
            )

            items = cursor.fetchall()
            print(f"   找到 {len(items)} 个items")

            for item in items:
                print(f"   - Item ID: {item[0]}, 名称: {item[1]}")
                print(f"     份量: {item[2]}{item[3]} × {item[4]}")
                print(
                    f"     热量: {item[5]}, 蛋白质: {item[6]}, 碳水: {item[7]}, 脂肪: {item[8]}"
                )

        # 3. 检查数据库表结构
        print(f"\n3. 检查数据库表结构:")

        # meals表结构
        cursor.execute("PRAGMA table_info(meals)")
        print("   meals表字段:")
        for col in cursor.fetchall():
            print(f"     {col[1]} ({col[2]})")

        # meal_items表结构
        cursor.execute("PRAGMA table_info(meal_items)")
        print("\n   meal_items表字段:")
        for col in cursor.fetchall():
            print(f"     {col[1]} ({col[2]})")

        # 4. 检查所有餐食的items统计
        print(f"\n4. 所有餐食的items统计:")
        cursor.execute("""
            SELECT m.id, m.name, COUNT(mi.id) as item_count
            FROM meals m
            LEFT JOIN meal_items mi ON m.id = mi.meal_id
            GROUP BY m.id
            ORDER BY m.id DESC
            LIMIT 5
        """)

        print("   最近5条餐食的items数量:")
        for row in cursor.fetchall():
            print(f"     餐食ID {row[0]}: {row[1]} - {row[2]}个items")

        conn.close()

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    check_meal_data_structure()
