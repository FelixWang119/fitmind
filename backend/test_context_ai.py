#!/usr/bin/env python3
"""测试带上下文的真实AI对话"""

import asyncio

from app.services.ai_service import AIService


async def test_context_ai():
    """测试AI的上下文记忆能力"""
    print("测试带上下文的AI对话...")
    print("=" * 60)

    ai_service = AIService()

    # 模拟一个连续对话
    conversation_history = []

    # 第一轮：用户介绍
    print("【第一轮】用户介绍自己")
    user_message_1 = "你好，我是李四，28岁女性，身高165cm，体重68公斤。我想健康减肥。"
    print(f"用户: {user_message_1}")

    # AI回复（无上下文）
    response_1 = await ai_service.get_response(user_message_1)
    print(f"AI回复: {response_1.response[:100]}...")
    print(f"模型: {response_1.model}, Token使用: {response_1.tokens_used}")

    # 保存到历史
    conversation_history.append({"role": "user", "content": user_message_1})
    conversation_history.append({"role": "assistant", "content": response_1.response})

    print("\n" + "=" * 60)
    print("【第二轮】基于上下文的连续对话")

    # 第二轮：基于上下文的提问
    user_message_2 = "根据我的情况，每天应该吃多少卡路里？"
    print(f"用户: {user_message_2}")
    print("期望: AI应该记得我是李四，28岁女性，165cm，68kg")

    # AI回复（带上下文）
    context = {"history": conversation_history}
    print(f"传递给AI的上下文: {len(conversation_history)}条历史消息")
    response_2 = await ai_service.get_response(user_message_2, context)
    print(f"AI回复: {response_2.response[:150]}...")
    print(f"模型: {response_2.model}, Token使用: {response_2.tokens_used}")

    # 保存到历史
    conversation_history.append({"role": "user", "content": user_message_2})
    conversation_history.append({"role": "assistant", "content": response_2.response})

    print("\n" + "=" * 60)
    print("【第三轮】更深度的上下文对话")

    # 第三轮：更具体的提问
    user_message_3 = "那我应该多吃蛋白质还是碳水化合物？"
    print(f"用户: {user_message_3}")
    print("期望: AI应该记得所有历史：个人信息、体重目标、卡路里建议")

    # AI回复（带完整上下文）
    context = {"history": conversation_history}
    response_3 = await ai_service.get_response(user_message_3, context)
    print(f"AI回复: {response_3.response[:200]}...")
    print(f"模型: {response_3.model}, Token使用: {response_3.tokens_used}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print(f"总对话轮数: 3轮")
    print(
        f"总Token使用: {response_1.tokens_used + response_2.tokens_used + response_3.tokens_used}"
    )
    print(f"AI模型: {response_3.model}")

    print("\n" + "=" * 60)
    print("上下文验证：")
    print("1. AI是否记得用户基本信息？")
    print("2. AI是否参考了之前的对话？")
    print("3. 建议是否具有连续性？")

    await ai_service.close()


if __name__ == "__main__":
    print("启动带上下文的AI测试...")
    asyncio.run(test_context_ai())
