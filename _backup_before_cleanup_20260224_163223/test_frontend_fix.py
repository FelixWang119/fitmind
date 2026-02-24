#!/usr/bin/env python3
"""
测试前端修复后的效果

模拟前端修复后的行为：
1. 读取图片文件
2. 转换为data URL（模拟FileReader.readAsDataURL()）
3. 提取纯base64部分（修复后的前端代码）
4. 发送给后端API
5. 验证是否返回真实分析结果，而不是模拟数据
"""

import base64
import requests
import json
from pathlib import Path

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_TOKEN_FILE = "/Users/felix/bmad/test_token.txt"

def read_token():
    """读取测试token"""
    if Path(TEST_TOKEN_FILE).exists():
        with open(TEST_TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def simulate_frontend_behavior(image_path):
    """模拟前端行为：读取图片并转换为base64"""
    
    # 1. 读取图片文件（模拟前端File对象）
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 2. 转换为base64（模拟btoa或类似操作）
    base64_string = base64.b64encode(image_data).decode('utf-8')
    
    # 3. 创建data URL（模拟FileReader.readAsDataURL()的结果）
    data_url = f"data:image/jpeg;base64,{base64_string}"
    
    print(f"   📁 图片文件: {image_path}")
    print(f"   📊 文件大小: {len(image_data):,} 字节")
    print(f"   🔤 Base64长度: {len(base64_string):,} 字符")
    print(f"   🌐 Data URL长度: {len(data_url):,} 字符")
    print(f"   🌐 Data URL前缀: {data_url[:50]}...")
    
    return {
        "original_base64": base64_string,
        "data_url": data_url,
        "pure_base64": base64_string  # 修复后的前端会提取纯base64
    }

def test_api_with_base64(base64_image, token, description):
    """测试API使用不同的base64格式"""
    print(f"\n  {description}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "image": base64_image,
        "date": "2026-02-24"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/nutrition/analyze-food-image",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"    状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            notes = result.get('notes', '')
            
            if "模拟数据" in notes:
                print(f"    ❌ 返回模拟数据")
                print(f"    原因: {notes[:100]}...")
                
                # 检查是否是红烧肉和米饭
                items = result.get('items', [])
                item_names = [item.get('name', '') for item in items]
                if "红烧肉" in item_names and "米饭" in item_names:
                    print(f"    🔍 找到红烧肉和米饭！")
                    return False, "模拟数据（红烧肉和米饭）"
                else:
                    return False, "模拟数据（其他）"
            else:
                print(f"    ✅ 真实千问分析")
                print(f"    餐型: {result.get('meal_type')}, 食材数: {len(result.get('items', []))}")
                return True, "真实分析"
        else:
            print(f"    ❌ 请求失败: {response.status_code}")
            print(f"    响应: {response.text[:200]}")
            return False, f"失败 {response.status_code}"
            
    except Exception as e:
        print(f"    ❌ 异常: {e}")
        return False, f"异常: {str(e)[:100]}"

def main():
    """主函数"""
    print("=" * 70)
    print("测试前端修复后的效果")
    print("=" * 70)
    
    # 读取token
    token = read_token()
    if not token:
        print("❌ 没有找到测试token")
        print("   运行: python test_direct_token.py")
        return
    
    print(f"✅ 使用token: {token[:20]}...")
    
    # 使用测试图片
    test_image = "/Users/felix/bmad/backend/tests/mealimg/lunch.jpg"
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 模拟前端行为
    print("\n1. 模拟前端图片处理行为...")
    image_data = simulate_frontend_behavior(test_image)
    
    # 测试不同的格式
    print("\n2. 测试不同的base64格式...")
    
    test_cases = [
        {
            "name": "❌ 前端修复前：发送完整data URL",
            "data": image_data["data_url"],
            "expected": "模拟数据（红烧肉和米饭）"
        },
        {
            "name": "✅ 前端修复后：发送纯base64",
            "data": image_data["pure_base64"],
            "expected": "真实分析"
        },
        {
            "name": "✅ 直接使用原始base64",
            "data": image_data["original_base64"],
            "expected": "真实分析"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        success, result = test_api_with_base64(test_case['data'], token, test_case['name'])
        
        results.append({
            "test": test_case['name'],
            "success": success,
            "result": result,
            "expected": test_case['expected"],
            "match": result == test_case['expected']
        })
    
    # 总结
    print("\n" + "=" * 70)
    print("测试结果总结")
    print("=" * 70)
    
    print("\n📊 测试结果:")
    for i, result in enumerate(results):
        status = "✅" if result["match"] else "❌"
        print(f"  {i+1}. {result['test']}")
        print(f"     结果: {result['result']}")
        print(f"     预期: {result['expected']}")
        print(f"     匹配: {status}")
    
    # 分析
    print("\n🔍 分析:")
    print("  1. 前端修复前（发送data URL）会导致千问API错误，返回模拟数据")
    print("  2. 前端修复后（发送纯base64）应该返回真实千问分析")
    print("  3. 直接使用原始base64也能正常工作")
    
    print("\n🎯 结论:")
    if results[1]["success"] and results[1]["match"]:
        print("  ✅ 前端修复成功！发送纯base64可以正常工作")
        print("  ✅ 千问API能够正确分析图像")
    else:
        print("  ❌ 前端修复可能还有问题")
        print("  ❌ 需要进一步调试")
    
    print("\n🔧 前端代码更改总结:")
    print("  1. 在 handlePhotoUpload 函数中，从 data URL 提取纯base64:")
    print("     const pureBase64 = dataURL.split(',')[1];")
    print("     setSelectedPhoto(pureBase64);")
    print("  2. 在显示图片时，重新添加 data:image/jpeg;base64, 前缀:")
    print("     src={`data:image/jpeg;base64,${selectedPhoto}`}")

if __name__ == "__main__":
    main()