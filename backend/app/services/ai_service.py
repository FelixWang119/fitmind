import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import structlog
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.ai import AIResponse
from app.services.ai_role_detection import determine_role_by_content
from app.services.ai_role_services import (
    BehaviorCoachRole,
    EmotionalSupportRole,
    NutritionistRole,
    get_role_service,
)

logger = structlog.get_logger()


class AIService:
    """AI服务基类"""

    def __init__(self, db: Optional[Session] = None, user_id: Optional[int] = None):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.mock_mode = (
            settings.ENVIRONMENT == "development" and not settings.QWEN_API_KEY
        )
        self.db = db
        self.user_id = user_id

    def _get_user_progress_data(self) -> Dict[str, Any]:
        """获取用户进度数据用于个性化回复"""
        if not self.db or not self.user_id:
            return {}

        try:
            from app.models.user import User
            from app.services.gamification_service import get_gamification_service
            from app.services.user_experience_service import get_user_experience_service

            user = self.db.query(User).filter(User.id == self.user_id).first()
            if not user:
                return {}

            gamification_service = get_gamification_service(self.db)
            experience_service = get_user_experience_service(self.db)

            progress_data = {}

            try:
                gamification_overview = gamification_service.get_gamification_overview(
                    user
                )
                progress_data[
                    "streak_days"
                ] = gamification_overview.gamification_stats.longest_streak
                progress_data[
                    "total_points"
                ] = gamification_overview.user_points.total_points
                progress_data[
                    "current_level"
                ] = gamification_overview.user_level.current_level
                progress_data[
                    "badges_earned"
                ] = gamification_overview.gamification_stats.total_badges
            except Exception as e:
                logger.warning("Failed to get gamification data", error=str(e))

            try:
                progress_summary = experience_service.get_progress_summary(user)
                progress_data["weight_progress"] = progress_summary.get(
                    "weight_progress", 0
                )
                progress_data["habit_completion"] = progress_summary.get(
                    "habit_completion", 0
                )
            except Exception as e:
                logger.warning("Failed to get progress summary", error=str(e))

            return progress_data

        except Exception as e:
            logger.warning("Failed to get user progress data", error=str(e))
            return {}

    async def get_response(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """获取AI回复"""
        if self.mock_mode:
            return await self._get_mock_response(message, context)
        else:
            return await self._get_qwen_response(message, context)

    async def _get_mock_response(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """获取模拟回复（开发环境使用）- 支持角色专业化回复"""
        start_time = time.time()

        # 检测当前角色
        current_role = context.get("current_role", "general") if context else "general"

        # 根据角色提供专业化回复
        if current_role == "nutritionist":
            response_text = self._get_nutritionist_response(message, context)
        elif current_role == "behavior_coach":
            response_text = self._get_behavior_coach_response(message, context)
        elif current_role == "emotional_support":
            response_text = self._get_emotional_support_response(message, context)
        else:
            response_text = self._get_general_response(message)

        response_time = time.time() - start_time

        return AIResponse(
            response=response_text,
            model="mock",
            tokens_used=len(response_text.split()),
            response_time=response_time,
            timestamp=datetime.utcnow(),
            metadata={"role": current_role},
        )

    def _get_nutritionist_response(self, message: str, context: Optional[Dict]) -> str:
        """获取营养师角色回复"""
        # 分析饮食
        if any(kw in message for kw in ["吃", "喝", "早餐", "午餐", "晚餐", "食谱"]):
            # 提取食物关键词（简化版）
            food_keywords = []
            for kw in ["肉", "菜", "饭", "面", "蛋", "奶", "果", "鱼"]:
                if kw in message:
                    food_keywords.append(kw)

            if food_keywords:
                advice = NutritionistRole.analyze_diet(food_keywords, {})
                return f"🍽️ **饮食分析**\n\n{advice}\n\n💡 需要我为您推荐具体的食谱吗？"

            return NutritionistRole.get_recipe_recommendation({})

        # 计算营养目标
        if any(kw in message for kw in ["卡路里", "热量", "营养", "BMI", "BMR"]):
            goals = NutritionistRole.calculate_nutrition_goals(
                {"weight": 70, "height": 175, "age": 30, "gender": "male"}
            )
            return (
                f"📊 **营养目标建议**\n\n"
                f"基础代谢率 (BMR): {goals['bmr']} 卡路里/天\n"
                f"每日总消耗 (TDEE): {goals['tdee']} 卡路里/天\n"
                f"蛋白质：{goals['protein_g']}g/天\n"
                f"脂肪：{goals['fat_g']}g/天\n"
                f"碳水：{goals['carbs_g']}g/天\n"
                f"水分：{goals['water_ml']}ml/天"
            )

        return "您好！我是您的营养师，可以为您提供饮食分析、营养计算和食谱推荐。请告诉我您的饮食情况或营养问题！"

    def _get_behavior_coach_response(
        self, message: str, context: Optional[Dict]
    ) -> str:
        """获取行为教练角色回复"""
        # 习惯建议
        if any(kw in message for kw in ["习惯", "坚持", "运动", "减肥", "计划"]):
            habit_type = "general"
            if "运动" in message or "锻炼" in message:
                habit_type = "exercise"
            elif "吃" in message or "饮食" in message:
                habit_type = "diet"
            elif "睡" in message:
                habit_type = "sleep"

            advice = BehaviorCoachRole.get_habit_advice(habit_type, message)
            return f"🎯 **习惯建议**\n\n{advice}"

        # 鼓励
        if any(kw in message for kw in ["放弃", "难", "累", "坚持不"]):
            encouragement = BehaviorCoachRole.handle_setback(message)
            return f"💪 **教练说**\n\n{encouragement}"

        # 目标分解
        if any(kw in message for kw in ["目标", "怎么开始", "第一步"]):
            goals = BehaviorCoachRole.set_micro_goals(message)
            return "📋 **目标分解计划**\n\n" + "\n".join(goals)

        return "您好！我是您的行为教练，专注于帮助您建立健康习惯。告诉我您想培养什么习惯，我会帮您制定可行的计划！"

    def _get_emotional_support_response(
        self, message: str, context: Optional[Dict]
    ) -> str:
        """获取情感陪伴角色回复 - 集成用户进度数据和 EmotionalSupportService"""
        emotion = "default"
        if any(kw in message for kw in ["难过", "伤心", "哭", "痛苦"]):
            emotion = "sad"
        elif any(kw in message for kw in ["焦虑", "紧张", "担心", "害怕"]):
            emotion = "anxious"
        elif any(kw in message for kw in ["生气", "沮丧", "挫败", "烦"]):
            emotion = "frustrated"
        elif any(kw in message for kw in ["累", "疲惫", "困"]):
            emotion = "tired"

        user_context = message[:100] if len(message) > 100 else message

        progress_data = self._get_user_progress_data()

        if self.db and self.user_id:
            try:
                from app.models.user import User
                from app.services.emotional_support_service import (
                    get_emotional_support_service,
                )

                user = self.db.query(User).filter(User.id == self.user_id).first()
                if user:
                    emotional_service = get_emotional_support_service(self.db)

                    from app.models.emotional_support import EmotionType

                    emotion_type_map = {
                        "sad": EmotionType.SAD,
                        "anxious": EmotionType.ANXIOUS,
                        "frustrated": EmotionType.FRUSTRATED,
                        "tired": EmotionType.TIRED,
                        "default": EmotionType.NEUTRAL,
                    }
                    mapped_emotion = emotion_type_map.get(emotion, EmotionType.NEUTRAL)

                    support_rec = emotional_service.provide_emotional_support(
                        user=user,
                        emotion_type=mapped_emotion,
                        intensity=5,
                        context=user_context,
                    )

                    progress_mention = ""
                    if progress_data.get("streak_days", 0) > 0:
                        progress_mention += (
                            f"\n\n🌟 **你的进步:** 已经坚持了 {progress_data['streak_days']} 天！"
                        )
                    if progress_data.get("badges_earned", 0) > 0:
                        progress_mention += (
                            f" 已获得 {progress_data['badges_earned']} 枚徽章！"
                        )

                    if progress_mention:
                        return (
                            f"💝 **陪伴**\n\n{support_rec.message}\n{progress_mention}\n\n💡 **建议行动:**\n"
                            + "\n".join(
                                [
                                    f"- {action}"
                                    for action in support_rec.suggested_actions
                                ]
                            )
                        )
                    else:
                        return (
                            f"💝 **陪伴**\n\n{support_rec.message}\n\n💡 **建议行动:**\n"
                            + "\n".join(
                                [
                                    f"- {action}"
                                    for action in support_rec.suggested_actions
                                ]
                            )
                        )

            except Exception as e:
                logger.warning("Failed to use EmotionalSupportService", error=str(e))

        support = EmotionalSupportRole.provide_support(emotion, user_context)

        progress_mention = ""
        if progress_data:
            if progress_data.get("streak_days", 0) > 0:
                progress_mention += (
                    f"\n\n🌟 我看到你已经很努力了！已经坚持了 {progress_data['streak_days']} 天，"
                )
            if progress_data.get("current_level", 0) > 1:
                progress_mention += f"等级达到了 {progress_data['current_level']}！"
            if progress_mention:
                progress_mention += " 这些都是你的进步，继续加油！"

        return f"💝 **陪伴**\n\n{support}{progress_mention}"

    def _get_general_response(self, message: str) -> str:
        """获取通用回复"""
        # 简单的关键词匹配
        if "体重" in message or "减肥" in message:
            return "体重管理需要耐心和坚持。建议您每天记录体重变化，保持均衡饮食，适量运动。我可以帮您制定个性化的计划。"
        elif "饮食" in message or "吃饭" in message:
            return "健康的饮食应该包含足够的蛋白质、蔬菜和全谷物。建议控制碳水化合物摄入，增加蔬菜比例。"
        elif "运动" in message or "锻炼" in message:
            return "每周至少 150 分钟中等强度有氧运动，加上 2-3 次力量训练。可以从快走开始，逐渐增加强度。"
        elif "压力" in message or "焦虑" in message:
            return "体重管理过程中有压力是正常的。尝试深呼吸、冥想或与朋友交流。记住，进步比完美更重要。"
        else:
            return "感谢您与我交流！我是您的体重管理 AI 助手，可以为您提供营养建议、运动指导和情感支持。请告诉我您今天的情况如何？"

    async def _get_qwen_response(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """获取通义千问回复 - 支持角色专业化"""
        start_time = time.time()

        # 检测当前角色
        current_role = context.get("current_role", "general") if context else "general"

        try:
            # 构建请求
            headers = {
                "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                "Content-Type": "application/json",
            }

            # 获取角色提示词
            role_prompt = self._get_role_system_prompt(current_role)

            # 构建消息历史
            messages = []
            if role_prompt:
                messages.append({"role": "system", "content": role_prompt})

            if context and "history" in context:
                messages.extend(context["history"])

            messages.append({"role": "user", "content": message})

            payload = {
                "model": settings.QWEN_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            # 发送请求
            response = await self.client.post(
                settings.QWEN_API_URL, headers=headers, json=payload
            )

            response.raise_for_status()
            result = response.json()

            # 解析响应
            ai_response = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)

            response_time = time.time() - start_time

            logger.info(
                "Qwen API call successful",
                tokens_used=tokens_used,
                response_time=response_time,
                role=current_role,
            )

            return AIResponse(
                response=ai_response,
                model=settings.QWEN_MODEL,
                tokens_used=tokens_used,
                response_time=response_time,
                timestamp=datetime.utcnow(),
                metadata={"role": current_role},
            )

        except httpx.HTTPError as e:
            logger.error("Qwen API error", error=str(e))
            # 失败时返回模拟回复
            return await self._get_mock_response(message, context)
        except Exception as e:
            logger.error("Unexpected AI service error", error=str(e))
            return await self._get_mock_response(message, context)

    def _get_role_system_prompt(self, role: str) -> str:
        """获取角色系统提示词"""
        role_prompts = {
            "nutritionist": NutritionistRole.ROLE_PROMPT,
            "behavior_coach": BehaviorCoachRole.ROLE_PROMPT,
            "emotional_support": EmotionalSupportRole.ROLE_PROMPT,
        }
        return role_prompts.get(role, "")

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局AI服务实例
_ai_service: Optional[AIService] = None
_db_instance: Optional[Session] = None
_user_id_instance: Optional[int] = None


async def get_ai_service(
    db: Optional[Session] = None, user_id: Optional[int] = None
) -> AIService:
    """获取AI服务实例"""
    global _ai_service, _db_instance, _user_id_instance

    if db != _db_instance or user_id != _user_id_instance or _ai_service is None:
        _ai_service = AIService(db=db, user_id=user_id)
        _db_instance = db
        _user_id_instance = user_id

    return _ai_service


async def get_ai_response(
    message: str,
    user_id: int,
    context: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None,
) -> AIResponse:
    """获取AI回复（主要入口点）"""
    logger.info("Getting AI response", user_id=user_id, message_length=len(message))

    # 获取AI服务，传入数据库连接和用户ID用于获取用户进度数据
    ai_service = await get_ai_service(db=db, user_id=user_id)

    # 获取回复
    response = await ai_service.get_response(message, context)

    return response


async def close_ai_service():
    """关闭AI服务"""
    global _ai_service
    if _ai_service:
        await _ai_service.close()
        _ai_service = None
