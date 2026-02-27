"""
用户Profile上下文服务 - 管理用户个人资料作为对话上下文

职责：
1. 从数据库加载用户Profile信息
2. 格式化Profile为对话友好的文本
3. 计算衍生健康指标（BMR、TDEE、BMI等）
4. 管理Profile更新和缓存
5. 将Profile作为长期记忆存储和检索
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.memory import UserLongTermMemory, ContextSummary
from app.services.memory_query_service import MemoryQueryService

logger = logging.getLogger(__name__)


class ProfileContextService:
    """用户Profile上下文服务"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.memory_query = MemoryQueryService(db_session)

    def get_user_profile(self, user_id: int) -> Optional[User]:
        """获取用户Profile数据"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户 {user_id} 不存在")
                return None
            return user
        except Exception as e:
            logger.error(f"获取用户Profile失败: {e}")
            return None

    def calculate_bmr(self, user: User) -> float:
        """
        计算基础代谢率 (BMR)
        使用 Mifflin-St Jeor 公式
        """
        if not all([user.age, user.gender, user.height, user.initial_weight]):
            return 0.0

        weight_kg = user.initial_weight / 1000  # 克转千克
        height_cm = user.height

        if user.gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * user.age + 5
        else:  # female or other
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * user.age - 161

        return round(bmr, 1)

    def calculate_tdee(self, user: User) -> float:
        """
        计算每日总能量消耗 (TDEE)
        基于活动水平乘数
        """
        bmr = self.calculate_bmr(user)
        if bmr == 0:
            return 0.0

        activity_multipliers = {
            "sedentary": 1.2,  # 久坐（办公室工作，很少运动）
            "light": 1.375,  # 轻度活动（每周1-3天轻度运动）
            "moderate": 1.55,  # 中度活动（每周3-5天中度运动）
            "active": 1.725,  # 活跃（每周6-7天剧烈运动）
            "very_active": 1.9,  # 非常活跃（体力劳动或每天剧烈运动）
        }

        activity_level = user.activity_level or "sedentary"
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)

        return round(bmr * multiplier, 1)

    def calculate_bmi(self, user: User) -> float:
        """计算身体质量指数 (BMI)"""
        if not all([user.height, user.initial_weight]):
            return 0.0

        weight_kg = user.initial_weight / 1000  # 克转千克
        height_m = user.height / 100  # 厘米转米

        if height_m == 0:
            return 0.0

        bmi = weight_kg / (height_m**2)
        return round(bmi, 1)

    def get_bmi_category(self, bmi: float) -> str:
        """获取BMI分类"""
        if bmi == 0:
            return "未知"

        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"

    def calculate_daily_calorie_target(self, user: User) -> Dict[str, float]:
        """
        计算每日卡路里目标
        返回维持、减重、增重的目标
        """
        tdee = self.calculate_tdee(user)
        if tdee == 0:
            return {}

        # 减重：TDEE - 500卡（每周减0.5kg）
        # 增重：TDEE + 500卡（每周增0.5kg）
        return {
            "maintenance": round(tdee, 1),
            "weight_loss": round(tdee - 500, 1),
            "weight_gain": round(tdee + 500, 1),
        }

    def format_profile_for_conversation(self, user: User) -> str:
        """
        格式化用户Profile为对话友好的文本
        """
        profile_text = []

        # 基本信息
        if user.full_name:
            profile_text.append(f"👤 姓名: {user.full_name}")
        if user.age:
            profile_text.append(f"🎂 年龄: {user.age}岁")
        if user.gender:
            gender_map = {"male": "男", "female": "女", "other": "其他"}
            gender = gender_map.get(user.gender.lower(), user.gender)
            profile_text.append(f"⚧️ 性别: {gender}")

        # 身体指标
        if user.height:
            profile_text.append(f"📏 身高: {user.height}cm")
        if user.initial_weight:
            weight_kg = user.initial_weight / 1000
            profile_text.append(f"⚖️ 当前体重: {weight_kg}kg")
        if user.target_weight:
            target_kg = user.target_weight / 1000
            profile_text.append(f"🎯 目标体重: {target_kg}kg")

        # 健康指标计算
        bmi = self.calculate_bmi(user)
        if bmi > 0:
            bmi_category = self.get_bmi_category(bmi)
            profile_text.append(f"📊 BMI: {bmi} ({bmi_category})")

        bmr = self.calculate_bmr(user)
        if bmr > 0:
            profile_text.append(f"🔥 基础代谢率 (BMR): {bmr} 卡路里/天")

        tdee = self.calculate_tdee(user)
        if tdee > 0:
            profile_text.append(f"⚡ 每日总消耗 (TDEE): {tdee} 卡路里/天")

        # 活动水平
        if user.activity_level:
            activity_map = {
                "sedentary": "久坐",
                "light": "轻度活动",
                "moderate": "中度活动",
                "active": "活跃",
                "very_active": "非常活跃",
            }
            activity = activity_map.get(
                user.activity_level.lower(), user.activity_level
            )
            profile_text.append(f"🏃 活动水平: {activity}")

        # 饮食偏好
        if user.dietary_preferences:
            try:
                preferences = json.loads(user.dietary_preferences)
                if preferences:
                    pref_text = ", ".join([f"{k}: {v}" for k, v in preferences.items()])
                    profile_text.append(f"🍽️ 饮食偏好: {pref_text}")
            except (json.JSONDecodeError, TypeError):
                profile_text.append(f"🍽️ 饮食偏好: {user.dietary_preferences}")

        # 卡路里目标建议
        calorie_targets = self.calculate_daily_calorie_target(user)
        if calorie_targets:
            profile_text.append("\n📈 卡路里目标建议:")
            profile_text.append(f"  • 维持体重: {calorie_targets['maintenance']} 卡/天")
            profile_text.append(f"  • 健康减重: {calorie_targets['weight_loss']} 卡/天")
            profile_text.append(f"  • 健康增重: {calorie_targets['weight_gain']} 卡/天")

        return "\n".join(profile_text)

    def save_profile_as_memory(self, user_id: int) -> Optional[UserLongTermMemory]:
        """
        将用户Profile保存为长期记忆
        """
        try:
            user = self.get_user_profile(user_id)
            if not user:
                return None

            # 检查是否已存在Profile记忆
            existing_memory = (
                self.db.query(UserLongTermMemory)
                .filter(
                    UserLongTermMemory.user_id == user_id,
                    UserLongTermMemory.memory_type == "user_profile",
                    UserLongTermMemory.memory_key == "basic_profile",
                )
                .first()
            )

            # 准备记忆数据
            profile_data = {
                "basic_info": {
                    "age": user.age,
                    "gender": user.gender,
                    "height": user.height,
                    "initial_weight": user.initial_weight,
                    "target_weight": user.target_weight,
                    "activity_level": user.activity_level,
                },
                "calculated_metrics": {
                    "bmr": self.calculate_bmr(user),
                    "tdee": self.calculate_tdee(user),
                    "bmi": self.calculate_bmi(user),
                    "bmi_category": self.get_bmi_category(self.calculate_bmi(user)),
                    "calorie_targets": self.calculate_daily_calorie_target(user),
                },
                "preferences": json.loads(user.dietary_preferences)
                if user.dietary_preferences
                else {},
                "formatted_text": self.format_profile_for_conversation(user),
                "last_updated": datetime.now().isoformat(),
            }

            if existing_memory:
                # 更新现有记忆
                existing_memory.set_memory_value(profile_data)
                existing_memory.updated_at = datetime.now()
                existing_memory.last_accessed = datetime.now()
                logger.info(f"更新用户 {user_id} 的Profile记忆")
            else:
                # 创建新记忆
                existing_memory = UserLongTermMemory(
                    user_id=user_id,
                    memory_type="user_profile",
                    memory_key="basic_profile",
                    importance_score=10.0,  # Profile记忆非常重要
                    last_accessed=datetime.now(),
                )
                existing_memory.set_memory_value(profile_data)
                self.db.add(existing_memory)
                logger.info(f"创建用户 {user_id} 的Profile记忆")

            self.db.commit()
            return existing_memory

        except Exception as e:
            logger.error(f"保存Profile记忆失败: {e}")
            self.db.rollback()
            return None

    def get_profile_memory(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户Profile记忆
        """
        try:
            memory = (
                self.db.query(UserLongTermMemory)
                .filter(
                    UserLongTermMemory.user_id == user_id,
                    UserLongTermMemory.memory_type == "user_profile",
                    UserLongTermMemory.memory_key == "basic_profile",
                )
                .first()
            )

            if memory:
                # 更新访问时间
                memory.last_accessed = datetime.now()
                self.db.commit()

                memory_data = memory.get_memory_value()
                return memory_data
            else:
                # 如果不存在，创建新的Profile记忆
                new_memory = self.save_profile_as_memory(user_id)
                if new_memory:
                    return new_memory.get_memory_value()
                return None

        except Exception as e:
            logger.error(f"获取Profile记忆失败: {e}")
            return None

    def get_profile_context(self, user_id: int) -> str:
        """
        获取用户Profile上下文（用于对话）
        返回格式化的文本
        """
        profile_memory = self.get_profile_memory(user_id)
        if profile_memory and "formatted_text" in profile_memory:
            return profile_memory["formatted_text"]

        # 如果记忆不存在，直接格式化当前Profile
        user = self.get_user_profile(user_id)
        if user:
            return self.format_profile_for_conversation(user)

        return "用户Profile信息未设置"

    def update_profile_field(self, user_id: int, field: str, value: Any) -> bool:
        """
        更新用户Profile字段并同步更新记忆
        """
        try:
            user = self.get_user_profile(user_id)
            if not user:
                return False

            # 更新用户字段
            if hasattr(user, field):
                setattr(user, field, value)
                user.updated_at = datetime.now()

                # 同步更新记忆
                self.save_profile_as_memory(user_id)

                self.db.commit()
                logger.info(f"更新用户 {user_id} 的 {field} 为 {value}")
                return True
            else:
                logger.warning(f"用户模型没有字段: {field}")
                return False

        except Exception as e:
            logger.error(f"更新Profile字段失败: {e}")
            self.db.rollback()
            return False

    def get_profile_summary_for_context(self, user_id: int) -> Dict[str, Any]:
        """
        获取Profile摘要（用于上下文摘要）
        """
        profile_memory = self.get_profile_memory(user_id)
        if not profile_memory:
            return {}

        return {
            "user_id": user_id,
            "profile_snapshot": {
                "age": profile_memory.get("basic_info", {}).get("age"),
                "gender": profile_memory.get("basic_info", {}).get("gender"),
                "bmi": profile_memory.get("calculated_metrics", {}).get("bmi"),
                "bmi_category": profile_memory.get("calculated_metrics", {}).get(
                    "bmi_category"
                ),
                "tdee": profile_memory.get("calculated_metrics", {}).get("tdee"),
                "activity_level": profile_memory.get("basic_info", {}).get(
                    "activity_level"
                ),
            },
            "last_updated": profile_memory.get("last_updated"),
        }


# 全局单例
_profile_context_service: Optional[ProfileContextService] = None


def get_profile_context_service(db_session: Session) -> ProfileContextService:
    """获取Profile上下文服务单例"""
    global _profile_context_service
    if _profile_context_service is None:
        _profile_context_service = ProfileContextService(db_session)
    return _profile_context_service


def init_profile_context_service(db_session: Session) -> ProfileContextService:
    """初始化Profile上下文服务"""
    global _profile_context_service
    _profile_context_service = ProfileContextService(db_session)
    return _profile_context_service
