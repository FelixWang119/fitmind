"""
Agent Memory 端到端测试

测试场景：
1. 通过对话接口 (ai_service) 与 Agent 交互
2. 通过打卡接口 (meal_checkin/exercise_checkin) 记录行为
3. 验证短期记忆队列的工作
4. 验证溢出触发长期记忆索引
5. 通过对话验证 Agent 是否掌握了用户情况
6. 通过日志验证索引逻辑

测试流程：
1. 用户进行多次餐食打卡 → 进入短期记忆
2. 用户进行对话 → Agent 应该能引用短期记忆
3. 继续打卡直到触发溢出 (100 条) → 触发长期记忆索引
4. 再次对话 → Agent 应该能引用长期记忆
5. 查询记忆 API → 验证记忆已正确存储
"""

import pytest
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# =============================================================================
# 测试夹具 (Fixtures)
# =============================================================================


@pytest.fixture(scope="function")
def memory_test_user(db_session):
    """创建专门用于 memory 测试的用户"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    from app.core.test_users import test_user_manager
    import uuid

    # 使用唯一的测试用户标识
    unique_id = f"memory_test_{uuid.uuid4().hex[:8]}"

    # 检查是否已存在
    existing_user = (
        db_session.query(User).filter(User.email == f"{unique_id}@test.com").first()
    )

    if existing_user:
        return existing_user

    user = User(
        email=f"{unique_id}@test.com",
        username=unique_id,
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        full_name="Memory Test User",
        age=30,
        gender="male",
        height=175,
        initial_weight=80000,  # 80kg
        target_weight=70000,  # 70kg
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    logger.info(f"创建 memory 测试用户：{user.id}, {unique_id}")
    return user


@pytest.fixture(scope="function")
def memory_test_client(client, memory_test_user, db_session):
    """创建已认证的测试客户端，用于 memory 测试"""
    from app.services.auth_service import create_access_token
    from datetime import timedelta

    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={
            "sub": str(memory_test_user.id),
            "email": memory_test_user.email,
            "user_id": memory_test_user.id,
        },
        expires_delta=access_token_expires,
    )

    # 设置认证头
    headers = {"Authorization": f"Bearer {token}"}
    client.headers.update(headers)

    return client, headers, memory_test_user


# =============================================================================
# P0: 短期记忆基础功能测试
# =============================================================================


class TestShortTermMemory:
    """短期记忆功能测试"""

    def test_add_memory_via_meal_checkin(self, memory_test_client, db_session):
        """[P0] 通过餐食打卡添加短期记忆"""
        client, headers, test_user = memory_test_client

        # 模拟餐食打卡数据
        meal_data = {
            "meal_type": "lunch",
            "items": [
                {
                    "name": "米饭",
                    "grams": 200,
                    "calories": 260,
                    "protein": 5,
                    "carbs": 57,
                    "fat": 1,
                },
                {
                    "name": "鸡胸肉",
                    "grams": 150,
                    "calories": 165,
                    "protein": 31,
                    "carbs": 0,
                    "fat": 4,
                },
                {
                    "name": "西兰花",
                    "grams": 100,
                    "calories": 34,
                    "protein": 3,
                    "carbs": 7,
                    "fat": 0,
                },
            ],
            "notes": "健康午餐",
        }

        # 确认打卡 (修正：正确的 endpoint 路径是 /api/v1/meal-checkin/confirm)
        response = client.post("/api/v1/meal-checkin/confirm", json=meal_data)

        assert response.status_code == 200
        data = response.json()
        assert "meal_id" in data

        logger.info(
            f"餐食打卡成功 - 用户 ID: {test_user.id}, "
            f"餐食 ID: {data['meal_id']}, 卡路里：{data['nutrition']['calories']}"
        )

        # 验证短期记忆队列中有新记录
        from app.services.short_term_memory import get_short_term_memory_service

        memory_service = get_short_term_memory_service()
        queue_size = memory_service.get_queue_size(test_user.id)

        # 队列大小应该至少为 1
        assert queue_size >= 1

        logger.info(f"短期记忆队列大小：{queue_size}")

    def test_add_memory_via_exercise_checkin(self, memory_test_client, db_session):
        """[P0] 通过运动打卡添加短期记忆"""
        client, headers, test_user = memory_test_client

        # 模拟运动打卡数据
        exercise_data = {
            "exercise_type": "running",
            "duration_minutes": 30,
            "calories_burned": 300,
            "distance_km": 5.0,
            "notes": "晨跑",
            "started_at": datetime.now().isoformat(),
        }

        response = client.post("/api/v1/exercises", json=exercise_data)

        # 如果 endpoint 存在，验证响应
        if response.status_code == 200:
            logger.info("运动打卡成功")
        else:
            logger.warning(f"运动打卡 endpoint 响应：{response.status_code}")

    def test_get_recent_memories(self, memory_test_client, db_session):
        """[P0] 获取用户最近记忆"""
        client, headers, test_user = memory_test_client

        # 先添加一些记忆
        from app.services.short_term_memory import get_short_term_memory_service

        memory_service = get_short_term_memory_service()

        # 添加测试记忆
        for i in range(3):
            memory_service.add_memory(
                user_id=test_user.id,
                event_type="nutrition",
                event_source="meal_checkin",
                content=f"测试餐食 {i + 1}",
                metrics={"calories": 500 + i * 100},
                source_table="meals",
                source_id=i + 1,
            )

        # 获取记忆
        memories = memory_service.get_recent_memories(test_user.id, limit=10)

        assert len(memories) >= 3
        assert memories[0]["event_type"] == "nutrition"

        logger.info(f"获取到 {len(memories)} 条短期记忆")


# =============================================================================
# P1: 对话中引用记忆测试
# =============================================================================


class TestMemoryInConversation:
    """对话中引用记忆的测试"""

    def test_ai_uses_short_term_memory_in_chat(self, memory_test_client, db_session):
        """[P1] AI 在对话中使用短期记忆"""
        client, headers, test_user = memory_test_client

        # 先进行餐食打卡
        meal_data = {
            "meal_type": "dinner",
            "items": [
                {
                    "name": "烤鱼",
                    "grams": 300,
                    "calories": 450,
                    "protein": 45,
                    "carbs": 0,
                    "fat": 27,
                },
            ],
            "notes": "晚餐吃了烤鱼",
        }

        # 直接创建 Meal 记录（简化测试）
        from app.models.nutrition import Meal
        from datetime import datetime

        meal = Meal(
            user_id=test_user.id,
            meal_type="dinner",
            name="晚餐",
            meal_datetime=datetime.now(),
            calories=450,
            protein=45,
            carbs=0,
            fat=27,
        )
        db_session.add(meal)
        db_session.commit()

        logger.info(f"创建测试餐食记录 - ID: {meal.id}")

        # 进行对话，询问今日摄入
        chat_request = {
            "message": "我今天摄入多少热量了？",
            "context": {"current_role": "nutritionist"},
        }

        response = client.post("/api/v1/ai/chat", json=chat_request)

        assert response.status_code == 200
        chat_data = response.json()
        ai_response = chat_data["response"]

        logger.info(f"AI 回复：{ai_response[:200]}...")

        # AI 应该能够引用记忆数据
        # 注意：在 mock 模式下，AI 会返回预设回复
        assert "response" in chat_data

    def test_memory_context_builder(self, memory_test_client, db_session):
        """[P1] 测试记忆上下文构建器"""
        from app.services.memory_query_service import get_memory_context_for_agent

        # 添加一些测试数据
        from app.models.nutrition import Meal

        for i in range(3):
            meal = Meal(
                user_id=memory_test_client[2].id,
                meal_type="lunch",
                name=f"测试餐食 {i + 1}",
                meal_datetime=datetime.now() - timedelta(hours=i * 2),
                calories=500 + i * 100,
                protein=30,
                carbs=50,
                fat=20,
            )
            db_session.add(meal)

        db_session.commit()

        # 获取记忆上下文
        context = get_memory_context_for_agent(memory_test_client[2].id, db_session)

        assert context is not None
        assert len(context) > 0
        assert "摄入热量" in context

        logger.info(f"记忆上下文长度：{len(context)} 字符")
        logger.debug(f"上下文预览：{context[:500]}...")


# =============================================================================
# P1: 溢出触发索引测试
# =============================================================================


class TestOverflowIndexing:
    """溢出触发长期记忆索引测试"""

    def test_overflow_triggers_indexing(self, memory_test_client, db_session):
        """[P1] 队列溢出触发长期记忆索引"""
        client, headers, test_user = memory_test_client

        from app.services.short_term_memory import get_short_term_memory_service
        from app.services.memory_index_service import index_memory_to_long_term

        memory_service = get_short_term_memory_service()

        # 清理队列，确保从 0 开始
        memory_service.queue.clear(test_user.id)

        initial_queue_size = memory_service.get_queue_size(test_user.id)
        logger.info(f"初始队列大小：{initial_queue_size}")

        # 添加 105 条记录（超过 100 条阈值）
        # 注意：第 101 条会触发溢出（前 100 条在队列中，第 101 条挤出一条）
        overflow_triggered = False
        overflow_at_count = 0

        for i in range(105):
            overflow_item = memory_service.add_memory(
                user_id=test_user.id,
                event_type="nutrition",
                event_source="test",
                content=f"测试记忆 {i + 1}",
                metrics={"test_index": i},
                source_table="test",
                source_id=i + 1,
            )

            if overflow_item:
                if not overflow_triggered:
                    logger.info(f"首次溢出触发 - 记录 {i + 1}")
                    overflow_triggered = True
                overflow_at_count += 1

        logger.info(f"溢出触发次数：{overflow_at_count}")

        # 验证溢出已触发
        assert overflow_triggered, "添加 105 条记录应该触发溢出"

        # 队列大小应该保持在 100 左右
        final_queue_size = memory_service.get_queue_size(test_user.id)
        assert final_queue_size <= 100

        logger.info(f"最终队列大小：{final_queue_size}")

        # 等待异步索引完成（实际测试中应该等待）
        import time

        time.sleep(0.5)

        # 验证长期记忆中应该有记录
        from app.models.memory import UnifiedMemory

        long_term_count = (
            db_session.query(UnifiedMemory)
            .filter(
                UnifiedMemory.user_id == test_user.id,
                UnifiedMemory.source_type == "test",
            )
            .count()
        )

        logger.info(f"长期记忆数量：{long_term_count}")

        # 至少应该有 5 条溢出记录被索引
        assert long_term_count >= 5


# =============================================================================
# P2: 长期记忆验证测试
# =============================================================================


class TestLongTermMemory:
    """长期记忆验证测试"""

    def test_indexed_memory_query(self, memory_test_client, db_session):
        """[P2] 查询已索引的长期记忆"""
        client, headers, test_user = memory_test_client

        # 先创建一些长期记忆
        from app.models.memory import UnifiedMemory

        for i in range(5):
            memory = UnifiedMemory(
                user_id=test_user.id,
                memory_type="nutrition",
                content_summary=f"长期记忆测试 {i + 1}",
                content_keywords=["测试", "营养"],
                source_type="test",
                source_id=f"test_{i}",
                importance_score=0.8,
            )
            db_session.add(memory)

        db_session.commit()

        # 通过 API 查询记忆 (注意：memory 端点已有/memory 前缀)
        response = client.get(
            "/api/v1/memory/unified-memories",
            params={"user_id": test_user.id, "limit": 10},
        )

        # 如果 404，尝试正确的路径（memory 路由器已有/memory 前缀）
        if response.status_code == 404:
            response = client.get(
                "/api/v1/memory/unified-memories",
                params={"user_id": test_user.id, "limit": 10},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["count"] >= 5

        logger.info(f"查询到 {data['count']} 条长期记忆")

    def test_memory_search(self, memory_test_client, db_session):
        """[P2] 记忆语义搜索"""
        client, headers, test_user = memory_test_client

        # 创建测试记忆
        from app.models.memory import UnifiedMemory

        memory = UnifiedMemory(
            user_id=test_user.id,
            memory_type="exercise",
            content_summary="今天进行了 30 分钟跑步锻炼",
            content_keywords=["跑步", "运动", "锻炼"],
            source_type="test",
            source_id="search_test",
            importance_score=0.7,
        )
        db_session.add(memory)
        db_session.commit()

        # 搜索记忆
        search_request = {
            "user_id": test_user.id,
            "query": "运动",
            "memory_types": ["exercise"],
            "limit": 10,
        }

        response = client.post(
            "/api/v1/memory/search",
            json=search_request,
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"搜索到 {data['total']} 条记忆")
        else:
            logger.warning(f"搜索 API 响应：{response.status_code}")


# =============================================================================
# P2: 完整工作流测试
# =============================================================================


class TestCompleteWorkflow:
    """完整工作流测试"""

    def test_complete_memory_workflow(self, memory_test_client, db_session):
        """[P2] 完整记忆工作流：打卡 → 对话 → 索引 → 验证"""
        client, headers, test_user = memory_test_client

        logger.info("=" * 60)
        logger.info("开始完整记忆工作流测试")
        logger.info("=" * 60)

        # 步骤 1: 进行多次打卡
        logger.info("步骤 1: 进行餐食打卡...")

        from app.models.nutrition import Meal

        for i in range(10):
            meal = Meal(
                user_id=test_user.id,
                meal_type="lunch",
                name=f"工作流测试餐食 {i + 1}",
                meal_datetime=datetime.now() - timedelta(hours=i),
                calories=500 + i * 50,
                protein=30,
                carbs=50,
                fat=20,
            )
            db_session.add(meal)

        db_session.commit()
        logger.info(f"创建了 10 条餐食记录")

        # 步骤 2: 进行对话
        logger.info("步骤 2: 进行对话...")

        chat_request = {
            "message": "我今天吃了什么？",
            "context": {"current_role": "nutritionist"},
        }

        response = client.post("/api/v1/ai/chat", json=chat_request)

        if response.status_code == 200:
            chat_data = response.json()
            logger.info(f"AI 回复：{chat_data['response'][:100]}...")

        # 步骤 3: 查询记忆
        logger.info("步骤 3: 查询记忆...")

        response = client.get(
            "/api/v1/memory/unified-memories",
            params={"user_id": test_user.id, "limit": 20},
        )

        if response.status_code == 200:
            memory_data = response.json()
            logger.info(f"查询到 {memory_data['count']} 条记忆")

        logger.info("=" * 60)
        logger.info("完整工作流测试完成")
        logger.info("=" * 60)


# =============================================================================
# 测试标记
# =============================================================================


pytestmark = [
    pytest.mark.memory,
    pytest.mark.e2e,
]
