"""
档案记忆服务 - 将用户档案数据同步到记忆系统
Story 5.1: 档案数据转入记忆
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.memory import UnifiedMemory

logger = logging.getLogger(__name__)


class ProfileMemoryService:
    """档案记忆服务 - 将用户档案数据同步到记忆系统"""

    def __init__(self, db: Session):
        self.db = db

    def sync_profile_to_memory(self, user: User) -> List[str]:
        """
        同步用户档案到记忆系统

        Args:
            user: 用户对象

        Returns:
            已创建的内存类型列表
        """
        created_memories = []

        # 1. 同步身体数据
        if self._has_profile_data(user):
            self._create_profile_memory(user, "profile_explicit")
            created_memories.append("profile_explicit")

        # 2. 同步目标数据
        if user.target_weight or user.initial_weight:
            self._create_goal_memory(user, "goal_explicit")
            created_memories.append("goal_explicit")

        # 3. 同步偏好数据
        if user.dietary_preferences or user.activity_level:
            self._create_preference_memory(user, "preference_inferred")
            created_memories.append("preference_inferred")

        logger.info(
            "Profile synced to memory",
            user_id=user.id,
            memories_created=created_memories,
        )

        return created_memories

    def _has_profile_data(self, user: User) -> bool:
        """检查用户是否有档案数据"""
        return any(
            [
                user.height,
                user.current_weight,
                user.body_fat_percentage,
                user.waist_circumference,
                user.hip_circumference,
            ]
        )

    def _create_profile_memory(
        self, user: User, memory_type: str
    ) -> Optional[UnifiedMemory]:
        """创建档案记忆"""
        # 检查是否已存在
        existing = self._get_existing_memory(user.id, memory_type, "profile")
        if existing:
            # 更新现有记忆
            existing = self._update_profile_memory(existing, user)
            return existing

        # 构建档案摘要
        content_summary = self._build_profile_summary(user)

        memory = UnifiedMemory(
            user_id=user.id,
            memory_type=memory_type,
            content_summary=content_summary,
            content_keywords=self._extract_profile_keywords(user),
            source_type="user_profile",
            source_id=f"profile_{user.id}",
            importance_score=8.0,  # 档案数据重要性较高
            is_active=True,
            is_indexed=True,
        )

        self.db.add(memory)
        self.db.commit()

        return memory

    def _create_goal_memory(
        self, user: User, memory_type: str
    ) -> Optional[UnifiedMemory]:
        """创建目标记忆"""
        # 检查是否已存在
        existing = self._get_existing_memory(user.id, memory_type, "goal")
        if existing:
            existing = self._update_goal_memory(existing, user)
            return existing

        # 构建目标摘要
        content_summary = self._build_goal_summary(user)

        memory = UnifiedMemory(
            user_id=user.id,
            memory_type=memory_type,
            content_summary=content_summary,
            content_keywords=["goal", "target", "weight", "health"],
            source_type="user_profile",
            source_id=f"goal_{user.id}",
            importance_score=9.0,  # 目标数据非常重要
            is_active=True,
            is_indexed=True,
        )

        self.db.add(memory)
        self.db.commit()

        return memory

    def _create_preference_memory(
        self, user: User, memory_type: str
    ) -> Optional[UnifiedMemory]:
        """创建偏好记忆"""
        # 检查是否已存在
        existing = self._get_existing_memory(user.id, memory_type, "preference")
        if existing:
            existing = self._update_preference_memory(existing, user)
            return existing

        # 构建偏好摘要
        content_summary = self._build_preference_summary(user)

        memory = UnifiedMemory(
            user_id=user.id,
            memory_type=memory_type,
            content_summary=content_summary,
            content_keywords=self._extract_preference_keywords(user),
            source_type="user_profile",
            source_id=f"preference_{user.id}",
            importance_score=7.0,
            is_active=True,
            is_indexed=True,
        )

        self.db.add(memory)
        self.db.commit()

        return memory

    def _get_existing_memory(
        self, user_id: int, memory_type: str, source_type_prefix: str
    ) -> Optional[UnifiedMemory]:
        """获取已存在的记忆"""
        return (
            self.db.query(UnifiedMemory)
            .filter(
                UnifiedMemory.user_id == user_id,
                UnifiedMemory.memory_type == memory_type,
                UnifiedMemory.source_type == "user_profile",
                UnifiedMemory.is_active == True,
            )
            .first()
        )

    def _update_profile_memory(
        self, memory: UnifiedMemory, user: User
    ) -> UnifiedMemory:
        """更新档案记忆"""
        memory.content_summary = self._build_profile_summary(user)
        memory.content_keywords = self._extract_profile_keywords(user)
        memory.updated_at = datetime.utcnow()
        self.db.commit()
        return memory

    def _update_goal_memory(self, memory: UnifiedMemory, user: User) -> UnifiedMemory:
        """更新目标记忆"""
        memory.content_summary = self._build_goal_summary(user)
        memory.updated_at = datetime.utcnow()
        self.db.commit()
        return memory

    def _update_preference_memory(
        self, memory: UnifiedMemory, user: User
    ) -> UnifiedMemory:
        """更新偏好记忆"""
        memory.content_summary = self._build_preference_summary(user)
        memory.content_keywords = self._extract_preference_keywords(user)
        memory.updated_at = datetime.utcnow()
        self.db.commit()
        return memory

    def _build_profile_summary(self, user: User) -> str:
        """构建档案摘要"""
        parts = []

        if user.height:
            parts.append(f"身高{user.height}厘米")
        if user.current_weight:
            parts.append(f"当前体重{user.current_weight / 1000:.1f}公斤")
        if user.initial_weight:
            parts.append(f"初始体重{user.initial_weight / 1000:.1f}公斤")
        if user.body_fat_percentage:
            parts.append(f"体脂率{user.body_fat_percentage}%")
        if user.waist_circumference:
            parts.append(f"腰围{user.waist_circumference}厘米")
        if user.hip_circumference:
            parts.append(f"臀围{user.hip_circumference}厘米")

        if not parts:
            return "用户尚未完善身体档案数据"

        return f"用户身体档案：{', '.join(parts)}"

    def _build_goal_summary(self, user: User) -> str:
        """构建目标摘要"""
        parts = []

        if user.target_weight:
            parts.append(f"目标体重{user.target_weight / 1000:.1f}公斤")
        if user.initial_weight:
            parts.append(f"起始体重{user.initial_weight / 1000:.1f}公斤")

        weight_diff = None
        if user.target_weight and user.current_weight:
            weight_diff = (user.current_weight - user.target_weight) / 1000
            if weight_diff > 0:
                parts.append(f"还需减重{weight_diff:.1f}公斤")
            elif weight_diff < 0:
                parts.append(f"还需增重{abs(weight_diff):.1f}公斤")
            else:
                parts.append("已达到目标体重")

        if not parts:
            return "用户尚未设置健康目标"

        return f"用户健康目标：{', '.join(parts)}"

    def _build_preference_summary(self, user: User) -> str:
        """构建偏好摘要"""
        parts = []

        if user.dietary_preferences:
            parts.append(f"饮食偏好：{user.dietary_preferences}")

        activity_map = {
            "sedentary": "久坐不动",
            "light": "轻度活动",
            "moderate": "中等活动量",
            "active": "活跃",
            "very_active": "非常活跃",
        }
        if user.activity_level:
            activity_cn = activity_map.get(user.activity_level, user.activity_level)
            parts.append(f"活动水平：{activity_cn}")

        if not parts:
            return "用户尚未设置饮食偏好"

        return f"用户偏好：{', '.join(parts)}"

    def _extract_profile_keywords(self, user: User) -> List[str]:
        """提取档案关键词"""
        keywords = ["profile", "body", "weight", "height"]

        if user.body_fat_percentage:
            keywords.append("body_fat")
        if user.waist_circumference:
            keywords.append("waist")
        if user.hip_circumference:
            keywords.append("hip")

        return keywords

    def _extract_preference_keywords(self, user: User) -> List[str]:
        """提取偏好关键词"""
        keywords = ["preference", "diet", "activity"]

        if user.dietary_preferences:
            keywords.append("food")
        if user.activity_level:
            keywords.append(user.activity_level)

        return keywords

    def batch_migrate_existing_profiles(self) -> Dict[str, int]:
        """
        批量迁移现有用户档案

        Returns:
            迁移结果统计
        """
        users = self.db.query(User).all()

        stats = {
            "total": len(users),
            "success": 0,
            "skipped": 0,
            "failed": 0,
        }

        for user in users:
            try:
                result = self.sync_profile_to_memory(user)
                if result:
                    stats["success"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                logger.error(f"迁移用户 {user.id} 档案失败: {e}")
                stats["failed"] += 1

        logger.info("Batch profile migration completed", stats=stats)
        return stats


def get_profile_memory_service(db: Session) -> ProfileMemoryService:
    """获取档案记忆服务实例"""
    return ProfileMemoryService(db)
