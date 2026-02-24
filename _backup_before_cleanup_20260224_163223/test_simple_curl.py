#!/usr/bin/env python3
"""最简单的测试"""

import subprocess
import time

print("测试后端连接...")

# 测试1: 使用curl测试health端点
print("\n1. 使用curl测试health端点...")
result = subprocess.run(
    ["curl", "-s", "http://localhost:8000/api/v1/health"],
    capture_output=True,
    text=True,
)
if result.returncode == 0:
    print(f"   ✅ 成功: {result.stdout[:100]}...")
else:
    print(f"   ❌ 失败: {result.stderr}")

# 测试2: 使用curl测试meals端点（无认证）
print("\n2. 使用curl测试meals端点（无认证）...")
result = subprocess.run(
    ["curl", "-s", "-v", "http://localhost:8000/api/v1/meals"],
    capture_output=True,
    text=True,
)
print(f"   返回码: {result.returncode}")
print(f"   输出: {result.stdout[:200]}...")
if result.stderr:
    print(f"   错误: {result.stderr[:200]}...")

# 测试3: 检查进程
print("\n3. 检查后端进程...")
result = subprocess.run(
    ["ps", "aux", "|", "grep", "uvicorn", "|", "grep", "-v", "grep"],
    shell=True,
    capture_output=True,
    text=True,
)
if result.stdout:
    print(f"   ✅ 找到uvicorn进程")
    print(f"   {result.stdout}")
else:
    print("   ❌ 没有找到uvicorn进程")

# 测试4: 检查端口
print("\n4. 检查端口8000...")
result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True)
if result.stdout:
    print(f"   ✅ 端口8000被占用")
    print(f"   {result.stdout}")
else:
    print("   ❌ 端口8000没有被占用")
