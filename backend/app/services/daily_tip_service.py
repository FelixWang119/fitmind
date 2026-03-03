"""
科普内容生成服务
Story 9.1: 科普内容生成服务
"""

import json
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any

import httpx
import structlog

from app.core.config import settings
from app.core.qwen_config import qwen_config
from app.models.daily_tip import DailyTip, TipTopic
from app.models.user import User

logger = structlog.get_logger()


# 主题配置
TOPICS = [
    TipTopic.NUTRITION.value,  # 营养
    TipTopic.EXERCISE.value,  # 运动
    TipTopic.SLEEP.value,  # 睡眠
    TipTopic.PSYCHOLOGY.value,  # 心理
]

# 主题中文名称映射
TOPIC_NAMES = {
    TipTopic.NUTRITION.value: "营养健康",
    TipTopic.EXERCISE.value: "科学运动",
    TipTopic.SLEEP.value: "优质睡眠",
    TipTopic.PSYCHOLOGY.value: "心理健康",
}

# 医学免责声明
DEFAULT_DISCLAIMER = "本内容仅供参考，不能替代专业医疗建议。如有健康问题，请咨询医生。"


class DailyTipService:
    """科普内容生成服务"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=qwen_config.CHAT_TIMEOUT)
        self.mock_mode = (
            settings.ENVIRONMENT == "development" and not qwen_config.QWEN_API_KEY
        )

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    def get_current_topic(self, target_date: Optional[date] = None) -> str:
        """
        获取指定日期的主题（每周轮换）
        AC #2: 每周一个主题（营养/运动/睡眠/心理）

        使用 ISO 周数来确定主题，确保同一周内主题一致
        """
        if target_date is None:
            target_date = date.today()

        # 获取一年的第几周
        week_number = target_date.isocalendar()[1]
        # 每周轮换主题
        topic_index = (week_number - 1) % len(TOPICS)
        return TOPICS[topic_index]

    def get_topic_name(self, topic: str) -> str:
        """获取主题的中文名称"""
        return TOPIC_NAMES.get(topic, topic)

    def build_prompt(self, topic: str) -> str:
        """
        构建科普内容生成 Prompt 模板
        AC #1, #3, #4: 生成当日科普内容，正文 300-500 字，添加医学免责声明
        """
        topic_name = self.get_topic_name(topic)

        prompt = f"""你是一位专业的健康科普作家。请为体重管理 AI 助手的用户生成一篇今日科普文章。

## 要求
1. 主题：{topic_name}
2. 摘要：不超过 50 字，简洁概括文章要点
3. 正文：300-500 字，内容专业、实用、易懂
4. 必须包含医学免责声明

## 格式要求
请严格按照以下 JSON 格式输出，不要包含任何其他内容：
{{
    "title": "文章标题（20字以内）",
    "summary": "摘要（50字以内）",
    "content": "正文内容（300-500字）",
    "disclaimer": "医学免责声明"
}}

## 注意事项
- 内容要结合生活实际，提供可操作的建议
- 语言亲切友好，适合普通用户阅读
- 不要使用过于专业的医学术语，如需使用请解释
- 确保内容科学准确

请生成今日的科普内容："""

        return prompt

    async def generate_tip_content(self, topic: Optional[str] = None) -> Dict[str, str]:
        """
        生成科普内容
        AC #1: 每日凌晨生成当日科普内容
        """
        if topic is None:
            topic = self.get_current_topic()

        prompt = self.build_prompt(topic)

        if self.mock_mode:
            return self._get_mock_content(topic)

        try:
            return await self._generate_from_ai(prompt)
        except Exception as e:
            logger.error("Failed to generate tip content from AI", error=str(e))
            # 返回模拟内容作为后备
            return self._get_mock_content(topic)

    async def _generate_from_ai(self, prompt: str) -> Dict[str, str]:
        """调用 AI 生成内容"""
        headers = qwen_config.get_headers()

        messages = [
            {
                "role": "system",
                "content": "你是一位专业的健康科普作家，擅长用通俗易懂的语言解释健康知识。",
            },
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": qwen_config.QWEN_CHAT_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500,
        }

        response = await self.client.post(
            qwen_config.QWEN_API_URL, headers=headers, json=payload
        )

        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 响应
        try:
            # 尝试提取 JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error("Failed to parse AI response", error=str(e), content=content)
            raise

    def _get_mock_content(self, topic: str) -> Dict[str, str]:
        """
        获取模拟内容（开发环境使用）
        """
        topic_name = self.get_topic_name(topic)

        mock_contents = {
            TipTopic.NUTRITION.value: {
                "title": "健康饮水指南",
                "summary": "每日适量饮水对健康至关重要，建议成年人每天饮用约2000毫升水。",
                "content": """健康的饮水习惯对人体至关重要。建议成年人每天饮用约2000毫升的水，分为多次饮用。早晨起床后喝一杯温水有助于唤醒身体机能，餐前半小时适量饮水可以增加饱腹感。运动前后补充适量水分有助于维持身体水合状态。

过量饮水可能导致电解质失衡，应根据个人体重和活动量调整饮水量。养成健康的饮水习惯可以改善皮肤状态、提高免疫力、促进新陈代谢。每个人的饮水量可能因年龄、体重、运动量和气候条件而有所不同，建议根据自身情况调整饮水计划。

除了白开水，也可以适量饮用淡茶、蜂蜜水等，但应避免含糖饮料和酒精。特殊人群如孕妇、哺乳期妇女、肾病患者等应在医生指导下调整饮水量。合理饮水，从今天开始！

水的温度也很重要。过冷的水会刺激胃肠道，温水更适合日常饮用。睡前避免大量饮水，以免影响睡眠质量。""",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
            TipTopic.EXERCISE.value: {
                "title": "科学运动指南",
                "summary": "适量运动有助于健康，建议每周进行150分钟中等强度有氧运动。",
                "content": """运动是健康的基石。适量运动可以帮助控制体重、增强心肺功能、提高免疫力、缓解压力。建议每周进行至少150分钟中等强度有氧运动，如快走、慢跑、游泳等。

运动时应注意循序渐进，避免过度运动造成损伤。开始新的运动计划前，建议咨询医生或专业教练。运动前后要做好热身和放松，保持正确的运动姿势。

对于体重管理来说，除了有氧运动，力量训练也很重要。它可以增加肌肉量，提高基础代谢率，帮助更有效地燃烧热量。每周进行2-3次力量训练，每次30-45分钟为宜。

坚持运动需要找到适合自己的方式。可以选择自己喜欢的运动项目，与朋友一起运动，或者设置可实现的小目标。保持运动的习惯比运动强度更重要。

运动时还要注意补充水分和电解质，特别是在炎热天气或长时间运动后。根据个人身体状况调整运动强度，如有不适及时停止并就医。""",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
            TipTopic.SLEEP.value: {
                "title": "优质睡眠指南",
                "summary": "良好的睡眠对健康至关重要，成年人每天需要7-9小时的睡眠。",
                "content": """睡眠是身体修复和恢复的重要时间。良好的睡眠有助于提高免疫力、维持健康体重、改善情绪、提高认知功能。成年人每天需要7-9小时的睡眠。

提高睡眠质量的方法包括：保持规律的作息时间，每天在同一时间睡觉和起床；创造舒适的睡眠环境，保持卧室安静、黑暗、凉爽；睡前避免使用电子设备和摄入咖啡因；进行适当的睡前放松活动。

睡眠不足可能导致食欲增加、注意力下降、免疫力降低、情绪问题等。长期睡眠不足还会增加肥胖、糖尿病、心血管疾病等慢性病的风险。

如果你有睡眠问题，建议先尝试改善睡眠习惯。如果问题持续，建议咨询医生或睡眠专家。良好的睡眠是健康生活的重要组成部分。

午睡时间不宜过长，20-30分钟为宜。避免在下午晚些时候小睡，以免影响夜间睡眠。建立睡前仪式有助于改善睡眠质量。""",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
            TipTopic.PSYCHOLOGY.value: {
                "title": "心理健康指南",
                "summary": "心理健康与身体健康同等重要，学会调节情绪有助于提升生活质量。",
                "content": """心理健康与身体健康同等重要。良好的心理状态可以帮助我们更好地应对压力、建立良好的人际关系、提高工作效率、生活更加充实。

保持心理健康的方法包括：学会放松和减压，如深呼吸、冥想、运动等；保持社交，与家人朋友保持联系；培养兴趣爱好，丰富生活；学会接受自己和他人；及时寻求帮助。

体重管理过程中可能会遇到挫折和困难，保持积极的心态很重要。不要过分追求完美，接受自己的不完美，享受进步的过程。遇到问题时，可以寻求朋友、家人或专业人士的支持。

如果出现焦虑、抑郁等心理问题，应及时寻求专业帮助。心理健康是整体健康的重要组成部分，值得我们重视和关注。

建议每天留出时间进行自我关怀，做一些让自己放松和快乐的事情。保持好奇心和学习热情，让生活充满意义和目标。""",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
        }

        return mock_contents.get(topic, mock_contents[TipTopic.NUTRITION.value])


# 全局服务实例
_daily_tip_service: Optional[DailyTipService] = None


def get_daily_tip_service() -> DailyTipService:
    """获取科普内容生成服务实例"""
    global _daily_tip_service

    if _daily_tip_service is None:
        _daily_tip_service = DailyTipService()

    return _daily_tip_service


async def close_daily_tip_service():
    """关闭科普内容生成服务"""
    global _daily_tip_service

    if _daily_tip_service:
        await _daily_tip_service.close()
        _daily_tip_service = None
