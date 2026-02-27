"""记忆提取器 - 从原始数据中提取关键信息"""

import logging
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime

from app.services.ai_service import AIService
from app.models.memory import UnifiedMemory

logger = logging.getLogger(__name__)


def _extract_keywords_and_summary(
    text: str, ai_service: AIService
) -> Tuple[str, List[str]]:
    """
    使用AI服务提取摘要和关键词

    Args:
        text: 原始文本
        ai_service: AI服务实例

    Returns:
        (摘要, 关键词列表)
    """
    # 生成提示给AI
    prompt = f"""
    请分析以下文本，提取最重要的信息：
    
    {text}
    
    返回格式：
    1. 内容摘要（一句话概括核心内容）
    2. 关键信息（3-5个关键词或短语，用逗号分隔）
    """

    try:
        # 调用AI服务
        result = ai_service.call_model(
            system_prompt="你是专业的数据分析师，擅长从杂乱数据中提取核心信息。",
            user_query=prompt,
        )

        # 解析AI返回结果，简单地提取摘要和关键词
        # 这里需要根据AI返回的实际格式来调整解析逻辑
        lines = result.split("\n")
        summary = ""
        keywords = []

        for line in lines:
            line = line.strip()
            if line.startswith("1.") or line.startswith("-") or line.startswith("*"):
                if not summary:
                    # 尝试找到摘要
                    if ":" in line:
                        summary = line.split(":", 1)[1].strip()
                    else:
                        summary = (
                            line.replace("1.", "")
                            .replace("-", "")
                            .replace("*", "")
                            .strip()
                        )
            elif line.startswith("2."):
                # 提取关键词
                keywords_str = line.replace("2.", "").strip()
                keywords = [kw.strip() for kw in keywords_str.split(",") if kw.strip()]

        # 如果AI没有返回理想的格式，则使用整个返回作为摘要
        if not summary:
            summary = result[:200]  # 限制长度

        return summary, keywords if keywords else [summary[:50]]  # 至少有一个关键词

    except Exception as e:
        logger.error(f"Failed to extract summary and keywords: {e}")
        # 降级处理：返回简化版本
        summary = text[:200] if len(text) > 200 else text
        return summary, [summary[:50]]


class MemoryExtractor:
    """记忆提取器 - 从原始数据中提取关键信息"""

    def __init__(self, ai_service: "AIService"):
        """
        初始化记忆提取器

        Args:
            ai_service: AI 服务实例
        """
        self.ai_service = ai_service

    def extract_from_habit(self, habit_record: Dict) -> Dict:
        """
        从习惯记录中提取记忆

        Args:
            habit_record: 习惯记录数据 {
                "user_id": int,
                "id": int,
                "name": str,
                "completed": bool,
                "date": str,
                "notes": str,
                "created_at": datetime
            }

        Returns:
            提取的记忆信息 {
                "memory_type": str,
                "content_summary": str,
                "keywords": List[str],
                "importance": float,
                "metadata": Dict
            }
        """
        try:
            # 构建要分析的文本
            habit_text = f"习惯名称: {habit_record['name']}\n"
            habit_text += (
                f"完成情况: {'是' if habit_record.get('completed') else '否'}\n"
            )
            habit_text += f"日期: {habit_record['date']}\n"

            if habit_record.get("notes"):
                habit_text += f"备注: {habit_record['notes']}\n"

            # 使用AI提取分析
            summary, keywords = _extract_keywords_and_summary(
                habit_text, self.ai_service
            )

            # 计算重要性分数（已完成的重要习惯、带有特殊备注的等）
            importance = 5.0  # 默认

            # 完成习惯给予正向影响
            if habit_record.get("completed"):
                importance += 1.0
            else:
                # 未完成的重要习惯给予更高重视
                importance -= 0.5

            # 特殊备注（如困难、意外情况）增加重要性
            notes = habit_record.get("notes", "")
            if notes and any(
                keyword in notes.lower()
                for keyword in ["困难", "挑战", "很难", "挫折", "受伤", "不适"]
            ):
                importance += 2.0
            elif notes and any(
                keyword in notes.lower() for keyword in ["很好", "顺利", "坚持", "开心"]
            ):
                importance += 1.0

            # 重要性的最大和最小范围
            importance = max(0, min(10, importance))

            return {
                "memory_type": "习惯打卡"
                if habit_record.get("completed")
                else "习惯中断",
                "content_summary": summary,
                "keywords": keywords,
                "importance": importance,
                "metadata": {
                    "source": "habit",
                    "original_id": habit_record["id"],
                    "date": habit_record["date"],
                    "completed": habit_record.get("completed", False),
                    "notes": habit_record.get("notes", ""),
                },
            }
        except Exception as e:
            logger.error(f"Failed to extract memory from habit: {e}")
            # 降级处理
            return {
                "memory_type": "习惯",
                "content_summary": f"习惯打卡记录: {habit_record.get('name', '未知')}",
                "keywords": [habit_record.get("name", "习惯")],
                "importance": 5.0,
                "metadata": {"source": "habit", "original_id": habit_record.get("id")},
            }

    def extract_from_health_record(self, health_record: Dict) -> Dict:
        """
        从健康记录中提取记忆

        Args:
            health_record: 健康记录数据 {
                "user_id": int,
                "id": int,
                "weight_grams": int,
                "date": str,
                "notes": str,
                "created_at": datetime
            }

        Returns:
            提取的记忆信息
        """
        try:
            # 构建要分析的文本
            weight_kg = (
                health_record["weight_grams"] / 1000
                if health_record.get("weight_grams")
                else 0
            )
            health_text = f"体重记录: {weight_kg:.1f}kg\n"
            health_text += f"测量日期: {health_record['date']}\n"

            if health_record.get("notes"):
                health_text += f"备注: {health_record['notes']}\n"

            # 使用AI提取分析
            summary, keywords = _extract_keywords_and_summary(
                health_text, self.ai_service
            )

            # 计算重要性分数（体重变化较大时提升重要性）
            importance = 5.0  # 默认

            # 如果之前有体重记录，可以比较变化，这里简化处理
            notes = health_record.get("notes", "")
            if notes and any(
                keyword in notes.lower()
                for keyword in ["下降", "上升", "波动", "异常", "注意"]
            ):
                importance += 2.0
            elif notes and any(
                keyword in notes.lower() for keyword in ["稳定", "正常", "平稳"]
            ):
                importance += 1.0

            importance = max(0, min(10, importance))

            return {
                "memory_type": "体重趋势",
                "content_summary": summary,
                "keywords": keywords,
                "importance": importance,
                "metadata": {
                    "source": "health",
                    "original_id": health_record["id"],
                    "date": health_record["date"],
                    "weight_kg": weight_kg,
                    "notes": health_record.get("notes", ""),
                },
            }
        except Exception as e:
            logger.error(f"Failed to extract memory from health record: {e}")
            return {
                "memory_type": "健康",
                "content_summary": f"体重记录: {health_record.get('weight_grams', 0) / 1000:.1f}kg",
                "keywords": ["体重", "健康"],
                "importance": 5.0,
                "metadata": {
                    "source": "health",
                    "original_id": health_record.get("id"),
                },
            }

    def extract_from_nutrition(self, meal_record: Dict) -> Dict:
        """
        从营养餐食记录中提取记忆

        Args:
            meal_record: 餐食记录数据 {
                "user_id": int,
                "id": int,
                "meal_type": str,
                "food_items": str,
                "calories": int,
                "date": str,
                "notes": str,
                "created_at": datetime
            }
        """
        try:
            # 提取关键信息
            meal_type = meal_record.get("meal_type", "未知")
            calories = meal_record.get("calories", 0)
            created_at = meal_record.get("created_at")
            date_str = created_at.strftime("%Y-%m-%d") if created_at else "未知日期"

            # 构建描述文本
            description_parts = [
                f"用户在{date_str}记录了{meal_type}，",
                f"摄入热量约{calories}千卡",
            ]

            notes = meal_record.get("notes")
            if notes:
                description_parts.append(f"备注：{notes}")

            description = "".join(description_parts)

            # 提取摘要和关键词
            summary, keywords = _extract_keywords_and_summary(
                description, self.ai_service
            )

            # 计算重要性
            importance = 5.0
            if calories > 800:
                importance += 1.5  # 高热量餐食更重要

            return {
                "user_id": meal_record.get("user_id"),
                "memory_type": "nutrition",
                "content": description,
                "summary": summary or f"{meal_type}摄入{calories}千卡",
                "keywords": keywords or [meal_type, "饮食", "热量"],
                "importance": importance,
                "metadata": {
                    "source": "nutrition",
                    "original_id": meal_record.get("id"),
                },
            }
        except Exception as e:
            logger.error(f"提取营养记忆失败：{e}")
            return None

    def extract_from_exercise(self, exercise_record: Dict) -> Dict:
        """
        从运动打卡记录中提取记忆

        Args:
            exercise_record: 运动打卡记录数据 {
                "user_id": int,
                "id": int,
                "exercise_type": str,
                "category": str,
                "duration_minutes": int,
                "intensity": str,
                "distance_km": float,
                "heart_rate_avg": int,
                "calories_burned": int,
                "notes": str,
                "started_at": datetime,
                "created_at": datetime
            }
        """
        try:
            # 提取关键信息
            exercise_type = exercise_record.get("exercise_type", "未知运动")
            category = exercise_record.get("category", "")
            duration = exercise_record.get("duration_minutes", 0)
            intensity = exercise_record.get("intensity", "中等")
            distance = exercise_record.get("distance_km")
            calories = exercise_record.get("calories_burned", 0)
            heart_rate = exercise_record.get("heart_rate_avg")
            started_at = exercise_record.get("started_at")
            date_str = started_at.strftime("%Y-%m-%d") if started_at else "未知日期"
            time_str = started_at.strftime("%H:%M") if started_at else ""

            # 构建描述文本
            description_parts = [
                f"用户在{date_str}进行了{exercise_type}运动",
            ]

            if time_str:
                description_parts[0] = (
                    f"用户在{date_str} {time_str}进行了{exercise_type}运动"
                )

            if duration > 0:
                description_parts.append(f"时长{duration}分钟")

            if intensity:
                description_parts.append(f"强度{intensity}")

            if distance and distance > 0:
                description_parts.append(f"距离{distance}公里")

            if calories > 0:
                description_parts.append(f"消耗约{calories}千卡")

            if heart_rate and heart_rate > 0:
                description_parts.append(f"平均心率{heart_rate}次/分")

            notes = exercise_record.get("notes")
            if notes:
                description_parts.append(f"备注：{notes}")

            description = "，".join(description_parts) + "。"

            # 提取摘要和关键词
            summary, keywords = _extract_keywords_and_summary(
                description, self.ai_service
            )

            # 计算重要性
            importance = 5.0
            if duration >= 60:
                importance += 2.0  # 长时间运动更重要
            elif duration >= 30:
                importance += 1.0

            if intensity == "高强度":
                importance += 1.0

            if calories >= 500:
                importance += 1.0

            return {
                "user_id": exercise_record.get("user_id"),
                "memory_type": "exercise",
                "content": description,
                "summary": summary
                or f"进行了{duration}分钟{exercise_type}运动，消耗{calories}千卡",
                "keywords": keywords
                or [exercise_type, "运动", "锻炼", category if category else "健身"],
                "importance": min(importance, 10.0),  # 最高10分
                "metadata": {
                    "source": "exercise",
                    "original_id": exercise_record.get("id"),
                    "exercise_type": exercise_type,
                    "duration_minutes": duration,
                    "calories_burned": calories,
                },
            }
        except Exception as e:
            logger.error(f"提取运动记忆失败: {e}")
            return None
        try:
            # 构建要分析的文本
            nutrition_text = f"餐食: {meal_record.get('meal_type', '')}\n"
            nutrition_text += f"食物内容: {meal_record.get('food_items', '')}\n"
            nutrition_text += f"热量: {meal_record.get('calories', 0)}卡\n"
            nutrition_text += f"用餐日期: {meal_record['date']}\n"

            if meal_record.get("notes"):
                nutrition_text += f"备注: {meal_record['notes']}\n"

            # 使用AI提取分析
            summary, keywords = _extract_keywords_and_summary(
                nutrition_text, self.ai_service
            )

            # 计算重要性分数
            importance = 5.0

            # 高热量餐食或有特殊备注提高重要性
            if meal_record.get("calories", 0) > 800:
                importance += 1.5  # 高热量
            elif meal_record.get("calories", 0) < 200:
                importance += 1.0  # 低热量

            notes = meal_record.get("notes", "")
            if notes and any(
                keyword in notes.lower() for keyword in ["大餐", "外卖", "聚餐", "特殊"]
            ):
                importance += 1.5
            elif notes and any(
                keyword in notes.lower() for keyword in ["清淡", "健康", "养生"]
            ):
                importance += 1.0

            importance = max(0, min(10, importance))

            return {
                "memory_type": "餐食习惯",
                "content_summary": summary,
                "keywords": keywords,
                "importance": importance,
                "metadata": {
                    "source": "nutrition",
                    "original_id": meal_record["id"],
                    "date": meal_record["date"],
                    "meal_type": meal_record.get("meal_type", ""),
                    "calories": meal_record.get("calories", 0),
                    "notes": meal_record.get("notes", ""),
                },
            }
        except Exception as e:
            logger.error(f"Failed to extract memory from nutrition record: {e}")
            return {
                "memory_type": "饮食",
                "content_summary": f"餐食记录: {meal_record.get('meal_type', '餐')}",
                "keywords": ["饮食", "餐食"]
                + (
                    [meal_record.get("meal_type", "")]
                    if meal_record.get("meal_type")
                    else []
                ),
                "importance": 5.0,
                "metadata": {
                    "source": "nutrition",
                    "original_id": meal_record.get("id"),
                },
            }

    def extract_from_conversation(self, conversation_messages: List[Dict]) -> Dict:
        """
        从对话中提取记忆

        Args:
            conversation_messages: 消息列表 [{
                "id": int,
                "role": str,
                "content": str,
                "created_at": datetime
            }]
        """
        try:
            # 构建对话文本
            dialog_text = "\n".join(
                [
                    f"[{msg['role'].upper()}]: {msg['content'][:500]}"  # 限制每条消息长度
                    for msg in conversation_messages[-5:]  # 只分析最后5条消息
                ]
            )

            if not dialog_text.strip():
                return None  # 没有有效对话

            # 使用AI提取分析
            summary, keywords = _extract_keywords_and_summary(
                dialog_text, self.ai_service
            )

            # 计算重要性分数（根据用户表达的情绪、目标设定等）
            importance = 5.0

            combined_text = " ".join(
                [msg.get("content", "") for msg in conversation_messages]
            )
            if any(
                x in combined_text.lower() for x in ["目标", "计划", "打算", "决定"]
            ):
                importance += 2.0
            elif any(
                x in combined_text.lower() for x in ["困难", "难", "挫折", "不想"]
            ):
                importance += 1.5
            elif any(x in combined_text.lower() for x in ["谢谢", "好的", "继续"]):
                importance += 0.5

            importance = max(0, min(10, importance))

            return {
                "memory_type": "对话洞察",
                "content_summary": summary,
                "keywords": keywords,
                "importance": importance,
                "metadata": {
                    "source": "conversation",
                    "message_count": len(conversation_messages),
                    "recent_messages": [
                        msg["id"] for msg in conversation_messages[-3:]
                    ],  # 记录最后3条消息ID
                    "contains_goals": any(
                        x in combined_text.lower()
                        for x in ["目标", "计划", "打算", "决定"]
                    ),
                    "contains_difficulties": any(
                        x in combined_text.lower()
                        for x in ["困难", "难", "挫折", "不想"]
                    ),
                },
            }
        except Exception as e:
            logger.error(f"Failed to extract memory from conversation: {e}")
            return {
                "memory_type": "对话",
                "content_summary": "用户与AI的互动对话",
                "keywords": ["对话", "交流"],
                "importance": 3.0,
                "metadata": {
                    "source": "conversation",
                    "message_count": len(conversation_messages),
                },
            }
