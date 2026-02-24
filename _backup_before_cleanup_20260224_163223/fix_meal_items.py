#!/usr/bin/env python3
"""
修复餐食记录中的食材详情问题

问题：数据库模型使用 meal_items，但schema使用 items
解决方案：在schema中添加别名映射
"""

import sys
from pathlib import Path

# 检查并修复schema文件
schema_file = "/Users/felix/bmad/backend/app/schemas/meal_models.py"

def check_and_fix_schema():
    """检查并修复schema文件"""
    print("检查schema文件...")
    
    if not Path(schema_file).exists():
        print(f"❌ schema文件不存在: {schema_file}")
        return False
    
    with open(schema_file, 'r') as f:
        content = f.read()
    
    # 检查Meal类定义
    if "class Meal(MealBase):" in content:
        print("✅ 找到Meal类定义")
        
        # 查找items字段
        if "items: List[MealItem] = Field(default_factory=list)" in content:
            print("✅ Meal类有items字段")
            
            # 检查是否有alias配置
            if "alias=" in content or "serialization_alias=" in content:
                print("✅ 已有alias配置")
                return True
            else:
                print("❌ 没有alias配置，需要修复")
                return False
        else:
            print("❌ Meal类没有items字段")
            return False
    else:
        print("❌ 没有找到Meal类定义")
        return False

def fix_schema_file():
    """修复schema文件"""
    print("\n修复schema文件...")
    
    with open(schema_file, 'r') as f:
        lines = f.readlines()
    
    # 找到Meal类定义
    meal_class_start = -1
    for i, line in enumerate(lines):
        if "class Meal(MealBase):" in line:
            meal_class_start = i
            break
    
    if meal_class_start == -1:
        print("❌ 找不到Meal类定义")
        return False
    
    # 找到items字段行
    items_field_line = -1
    for i in range(meal_class_start, len(lines)):
        if "items: List[MealItem]" in lines[i]:
            items_field_line = i
            break
    
    if items_field_line == -1:
        print("❌ 找不到items字段")
        return False
    
    # 修复items字段，添加alias
    old_line = lines[items_field_line]
    new_line = '    items: List[MealItem] = Field(default_factory=list, serialization_alias="meal_items", validation_alias="meal_items")\n'
    
    print(f"替换行 {items_field_line+1}:")
    print(f"  旧: {old_line.strip()}")
    print(f"  新: {new_line.strip()}")
    
    lines[items_field_line] = new_line
    
    # 写回文件
    with open(schema_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ schema文件修复完成")
    return True

def create_test_script():
    """创建测试脚本"""
    test_script = """
#!/usr/bin/env python3
"""
测试修复后的餐食API
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_TOKEN_FILE = "/Users/felix/bmad/test_token.txt"

def read_token():
    """读取测试token"""
    if Path(TEST_TOKEN_FILE).exists():
        with open(TEST_TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def test_meal_with_items():
    """测试包含食材的餐食"""
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 创建测试餐食
    meal_data = {
        "name": "修复测试午餐",
        "meal_type": "lunch",
        "calories": 715,
        "protein": 35,
        "carbs": 80,
        "fat": 25,
        "notes": "修复测试",
        "meal_datetime": "2026-02-24T12:00:00+08:00",
        "items": [
            {
                "name": "测试面条",
                "serving_size": 150,
                "serving_unit": "g",
                "quantity": 1,
                "calories_per_serving": 174,
                "protein_per_serving": 3,
                "carbs_per_serving": 38,
                "fat_per_serving": 0.5
            }
        ]
    }
    
    print("创建测试餐食...")
    response = requests.post(
        f"{BASE_URL}/meals",
        headers=headers,
        json=meal_data,
        timeout=30
    )
    
    print(f"创建响应: {response.status_code}")
    
    if response.status_code in [200, 201]:
        meal = response.json()
        print(f"✅ 餐食创建成功，ID: {meal.get('id')}")
        
        # 检查返回的items
        items = meal.get('items', [])
        print(f"返回的items数量: {len(items)}")
        
        if items:
            print("✅ 餐食包含食材详情!")
            for item in items:
                print(f"  食材: {item.get('name')}")
        else:
            print("❌ 餐食没有食材详情")
            
        # 获取今日餐食
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n获取 {today} 的餐食记录...")
        
        response = requests.get(
            f"{BASE_URL}/meals/daily-nutrition-summary",
            headers=headers,
            params={"target_date": today},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            meals = data.get('meals', [])
            print(f"获取到 {len(meals)} 条餐食记录")
            
            for meal in meals:
                items = meal.get('items', [])
                print(f"餐食ID {meal.get('id')} 有 {len(items)} 个食材")
                
                if items:
                    print("✅ 前端应该能显示食材详情了!")
                else:
                    print("❌ 仍然没有食材详情")
    else:
        print(f"❌ 创建失败: {response.text}")

if __name__ == "__main__":
    test_meal_with_items()
"""
    
    test_file = "/Users/felix/bmad/test_fix_verification.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    print(f"\n✅ 创建测试脚本: {test_file}")
    print("运行: python test_fix_verification.py")

def main():
    """主函数"""
    print("=" * 70)
    print("修复餐食记录中的食材详情问题")
    print("=" * 70)
    
    # 1. 检查schema
    needs_fix = not check_and_fix_schema()
    
    if needs_fix:
        # 2. 修复schema
        if fix_schema_file():
            # 3. 创建测试脚本
            create_test_script()
            
            print("\n" + "=" * 70)
            print("修复完成!")
            print("=" * 70)
            print("\n修复内容:")
            print("  1. 在MealSchema的items字段添加alias:")
            print('     serialization_alias="meal_items"')
            print('     validation_alias="meal_items"')
            print("\n  2. 这样Pydantic就能正确映射:")
            print("     数据库字段: meal_items → schema字段: items")
            print("\n  3. 前端API返回的数据将包含items字段")
            print("\n运行测试脚本验证修复:")
            print("  python test_fix_verification.py")
        else:
            print("\n❌ 修复失败")
    else:
        print("\n✅ schema文件已经正确配置")
        print("问题可能在其他地方")

if __name__ == "__main__":
    main()