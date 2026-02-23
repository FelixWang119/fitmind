#!/usr/bin/env python3
"""测试记忆系统功能"""

import asyncio
import sys
from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, ".")

# 重要：按正确顺序导入模型
from app.core.database import Base
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.memory import (
    ContextSummary,
    DataAssociation,
    HabitPattern,
    UserLongTermMemory,
)
from app.models.user import User

# 数据库连接
DATABASE_URL = "sqlite:///./test_memory.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def test_memory_system_async():
    """测试记忆系统（异步版本）"""
    print("=" * 60)
    print("测试记忆系统...")
    print("=" * 60)

    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    # 创建会话
    db = SessionLocal()

    try:
        # 创建测试用户
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="测试用户",
            hashed_password="hashed",
            height=175,
            initial_weight=85000,  # 85kg
            target_weight=75000,  # 75kg
            activity_level="moderate",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"创建测试用户: ID={user.id}, 用户名={user.username}")

        # 导入并创建记忆管理器
        from app.services.memory_manager import MemoryManager

        manager = MemoryManager(db)

        # 测试1: 创建记忆
        print("\n1. 测试创建记忆...")
        memory = await manager.create_memory(
            user_id=user.id,
            memory_type="health_goal",
            memory_key="target_weight",
            memory_value={"target": 75, "unit": "kg", "deadline": "2026-06-01"},
            importance_score=8.0,
        )
        if memory:
            print(f"   ✅ 记忆创建成功: {memory.memory_key}")
        else:
            print("   ❌ 记忆创建失败")

        # 测试2: 获取记忆
        print("\n2. 测试获取记忆...")
        retrieved_memory = await manager.get_memory(
            user.id, "health_goal", "target_weight"
        )
        if retrieved_memory:
            print(
                f"   ✅ 记忆获取成功: {retrieved_memory.memory_key}, 重要性: {retrieved_memory.importance_score}"
            )
        else:
            print("   ❌ 记忆获取失败")

        # 测试3: 获取记忆列表
        print("\n3. 测试获取记忆列表...")
        memories = await manager.get_memories(user.id)
        print(f"   ✅ 记忆数量: {len(memories)}")

        # 测试4: 创建每日摘要
        print("\n4. 测试创建每日摘要...")
        summary = await manager.create_daily_summary(user.id, date.today())
        if summary:
            print(f"   ✅ 每日摘要创建成功: {summary.summary_type}")
        else:
            print("   ❌ 每日摘要创建失败")

        # 测试5: 获取近期摘要
        print("\n5. 测试获取近期摘要...")
        summaries = await manager.get_recent_summaries(user.id)
        print(f"   ✅ 近期摘要数量: {len(summaries)}")

        # 测试6: 构建上下文
        print("\n6. 测试构建上下文...")
        context = await manager.build_context(user.id)
        print(f"   ✅ 上下文长度: {len(context)} 字符")
        print(f"   上下文预览: {context[:200]}...")

        # 测试7: 获取记忆统计
        print("\n7. 测试获取记忆统计...")
        stats = await manager.get_memory_stats(user.id)
        print(f"   ✅ 记忆统计: {stats}")

        # 测试8: 创建习惯模式
        print("\n8. 测试创建习惯模式...")
        # 先创建习惯
        habit = Habit(
            user_id=user.id,
            name="每天运动30分钟",
            description="每天运动30分钟",
            category="EXERCISE",
            frequency="DAILY",
            target_value=30,
            target_unit="minutes",
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)

        pattern = await manager.create_habit_pattern(
            user_id=user.id,
            habit_id=habit.id,
            pattern_type="morning",
            pattern_data={"preferred_time": "07:00", "days_per_week": 5},
            confidence=0.8,
        )
        if pattern:
            print(f"   ✅ 习惯模式创建成功: {pattern.pattern_type}")
        else:
            print("   ❌ 习惯模式创建失败")

        # 测试9: 创建数据关联
        print("\n9. 测试创建数据关联...")
        association = await manager.create_association(
            user_id=user.id,
            source_type="habit",
            source_id=habit.id,
            target_type="health_record",
            target_id=1,
            association_type="causal",
            strength=0.7,
        )
        if association:
            print(
                f"   ✅ 数据关联创建成功: {association.source_type} -> {association.target_type}"
            )
        else:
            print("   ❌ 数据关联创建失败")

        # 测试10: 更新记忆重要性
        print("\n10. 测试更新记忆重要性...")
        success = await manager.update_memory_importance(user.id, "target_weight", 1.0)
        if success:
            updated = await manager.get_memory(user.id, "health_goal", "target_weight")
            print(f"   ✅ 重要性更新成功: {updated.importance_score}")
        else:
            print("   ❌ 重要性更新失败")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def test_memory_system():
    """测试记忆系统（同步包装）"""
    asyncio.run(test_memory_system_async())


if __name__ == "__main__":
    test_memory_system()
