#!/usr/bin/env python3
"""Test AI service integration with real QWen API"""

import asyncio
import os

from app.services.ai_service import AIService, get_ai_service


async def test_ai_service():
    """Test the AI service with real QWen API"""
    print("Testing AI service integration...")

    # Create AI service instance
    ai_service = AIService()

    # Test message
    test_message = "你好，我最近体重增加了2公斤，感觉有点沮丧。我应该怎么办？"

    print(f"Sending test message: {test_message}")

    try:
        # Get AI response
        response = await ai_service.get_response(test_message)

        print("\n=== AI Response ===")
        print(f"Response: {response.response}")
        print(f"Model: {response.model}")
        print(f"Tokens used: {response.tokens_used}")
        print(f"Response time: {response.response_time:.2f} seconds")
        print(f"Timestamp: {response.timestamp}")

        if response.model == "mock":
            print("\n⚠️ WARNING: Using mock response instead of real QWen API")
            print("Check if QWEN_API_KEY is set in .env file")
        else:
            print("\n✅ SUCCESS: Real QWen API response received!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        await ai_service.close()


if __name__ == "__main__":
    # Set environment variable for testing
    os.environ["QWEN_API_KEY"] = "sk-14e3024216784670afe00fc2b5d79861"

    # Run test
    asyncio.run(test_ai_service())
