#!/usr/bin/env python3
"""
测试Qwen API是否工作
"""

import os
import httpx
import asyncio
import json


async def test_qwen_api():
    """测试Qwen API"""

    api_key = os.environ.get("QWEN_API_KEY", "sk-14e3024216784670afe00fc2b5d79861")

    print("测试Qwen API...")
    print("=" * 60)
    print(f"API密钥: {api_key[:10]}...")

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 尝试一个简单的文本请求（不使用图像）
    payload = {
        "model": "qwen-turbo",  # 使用文本模型
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "temperature": 0.1,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n发送请求到: {url}")
            print(f"使用模型: {payload['model']}")

            response = await client.post(url, headers=headers, json=payload)

            print(f"\n响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ API调用成功!")
                print(
                    f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}..."
                )
            else:
                print(f"\n❌ API调用失败!")
                print(f"错误响应: {response.text[:500]}")

    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 设置环境变量
    os.environ["QWEN_API_KEY"] = "sk-14e3024216784670afe00fc2b5d79861"
    asyncio.run(test_qwen_api())
