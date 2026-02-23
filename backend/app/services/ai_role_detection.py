"""Enhanced AI Role Detection Service

Provides intelligent role switching based on:
- Content analysis (keywords, topics)
- Sentiment detection
- Intent classification
- Context window analysis
- Multi-domain detection (role fusion)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()


class RoleType(str, Enum):
    """Available AI roles"""

    NUTRITIONIST = "nutritionist"
    BEHAVIOR_COACH = "behavior_coach"
    EMOTIONAL_COMPANION = "emotional_companion"
    GENERAL = "general"


class TriggerType(str, Enum):
    """Role switch trigger types"""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    FUSION = "fusion"


@dataclass
class RoleDetectionResult:
    """Result of role detection analysis"""

    detected_role: str
    confidence: float
    is_fusion: bool
    detected_domains: List[str]
    switch_recommended: bool
    reason: str


# Extended role keywords mapping
ROLE_KEYWORDS = {
    RoleType.NUTRITIONIST: [
        "食物",
        "吃",
        "饮食",
        "营养",
        "热量",
        "卡路里",
        "蛋白质",
        "碳水",
        "脂肪",
        "维生素",
        "矿物质",
        "膳食纤维",
        "食谱",
        "早餐",
        "午餐",
        "晚餐",
        "零食",
        "健康",
        "减肥",
        "增重",
        "BMI",
        "BMR",
        "TDEE",
        "代谢",
        "消化",
        "吸收",
        "GI值",
        "果腹",
        "饱腹",
        "进食",
        "食材",
        "做法",
        "烹饪",
        "外卖",
        "餐厅",
        "外卖",
        "节食",
        "暴食",
        "食欲",
        "胃口",
        "蔬菜",
        "水果",
        "肉类",
        "鱼类",
        "豆制品",
        "奶制品",
        "坚果",
        "主食",
    ],
    RoleType.BEHAVIOR_COACH: [
        "运动",
        "锻炼",
        "跑步",
        "步行",
        "健身",
        "习惯",
        "坚持",
        "目标",
        "计划",
        "打卡",
        "自律",
        "动力",
        "激励",
        "改变",
        "行为",
        "养成",
        "放弃",
        "偷懒",
        "拖延",
        "效率",
        "时间管理",
        "习惯养成",
        "小目标",
        "进度",
        "完成",
        "训练",
        "瑜伽",
        "拉伸",
        "力量训练",
        "有氧",
        "无氧",
        "健身计划",
        "运动强度",
        "心率",
        "步数",
        "站立",
        "久坐",
        "休息",
        "恢复",
        "睡眠",
        "作息",
    ],
    RoleType.EMOTIONAL_COMPANION: [
        "情绪",
        "心情",
        "感受",
        "压力",
        "焦虑",
        "抑郁",
        "沮丧",
        "难过",
        "伤心",
        "开心",
        "快乐",
        "愤怒",
        "恐惧",
        "担心",
        "害怕",
        "孤独",
        "寂寞",
        "累",
        "疲惫",
        "想放弃",
        "没动力",
        "鼓励",
        "支持",
        "倾诉",
        "倾听",
        "理解",
        "陪伴",
        "烦恼",
        "困扰",
        "迷茫",
        "无助",
        "绝望",
        "失落",
        "自责",
        "后悔",
        "生气",
        "烦躁",
        "不安",
        "紧张",
        "害怕失败",
        "自我怀疑",
    ],
}

# Role switch explicit request patterns
ROLE_SWITCH_PATTERNS = {
    RoleType.NUTRITIONIST: [
        "营养师",
        "营养咨询",
        "和营养师",
        "要营养师",
        "切换到营养",
        "我要营养",
        " dietitian",
        "帮我算热量",
        "饮食建议",
    ],
    RoleType.BEHAVIOR_COACH: [
        "行为教练",
        "教练",
        "和教练",
        "要教练",
        "切换到教练",
        "我要运动",
        "习惯养成",
        "帮我制定计划",
        "行为改变",
        "behavior coach",
        "motivation",
        "坚持",
    ],
    RoleType.EMOTIONAL_COMPANION: [
        "情感陪伴",
        "情绪支持",
        "和情感",
        "要陪伴",
        "切换到情感",
        "心情不好",
        "压力大",
        "想倾诉",
        "emotional",
        "support",
        "陪我聊聊",
        "好累啊",
        "心情烦",
        "郁闷",
    ],
}

# Capability inquiry patterns
CAPABILITY_PATTERNS = {
    "general": [
        "你能做什么",
        "你有什么功能",
        "你会什么",
        "你能帮我什么",
        "介绍一下自己",
        "你是谁",
        "有什么能力",
        "有哪些功能",
    ],
    RoleType.NUTRITIONIST: [
        "营养师能做什么",
        "营养师帮我",
        "营养师能帮我什么",
        " nutritionist ",
        "饮食方面",
        "食物方面",
    ],
    RoleType.BEHAVIOR_COACH: [
        "教练能做什么",
        "教练帮我",
        "教练能帮我什么",
        " behavior ",
        "习惯方面",
        "运动方面",
    ],
    RoleType.EMOTIONAL_COMPANION: [
        "情感陪伴能做什么",
        "情感支持",
        "情绪方面",
        "心理方面",
        " emotional ",
        "心情方面",
        "倾诉",
    ],
    "comparison": [
        "有什么区别",
        "有什么不同",
        "差异",
        "对比",
    ],
}


def detect_role_from_content(
    message: str, conversation_context: Optional[List[str]] = None
) -> RoleDetectionResult:
    """
    Detect the appropriate role based on message content and conversation context.

    Args:
        message: The user's message
        conversation_context: Optional list of recent messages for context

    Returns:
        RoleDetectionResult with detected role and metadata
    """
    message_lower = message.lower()

    # Check for explicit role switch requests first
    explicit_role = _check_explicit_role_request(message_lower)
    if explicit_role:
        return RoleDetectionResult(
            detected_role=explicit_role,
            confidence=1.0,
            is_fusion=False,
            detected_domains=[explicit_role],
            switch_recommended=True,
            reason="explicit_role_request",
        )

    # Check for capability inquiry
    if _is_capability_inquiry(message_lower):
        return RoleDetectionResult(
            detected_role="capability_inquiry",
            confidence=1.0,
            is_fusion=False,
            detected_domains=[],
            switch_recommended=False,
            reason="capability_inquiry",
        )

    # Analyze current message for keywords
    domain_scores = _calculate_domain_scores(message_lower)

    # Include conversation context for better detection
    if conversation_context:
        context_scores = _calculate_context_scores(conversation_context)
        # Weight current message more heavily
        for domain in domain_scores:
            domain_scores[domain] = (
                domain_scores[domain] * 0.7 + context_scores.get(domain, 0) * 0.3
            )

    # Determine if this is a multi-domain query (role fusion)
    active_domains = [domain for domain, score in domain_scores.items() if score > 0]

    if len(active_domains) >= 2:
        # Multi-domain detected - enable role fusion
        primary_role = max(domain_scores, key=domain_scores.get)
        confidence = (
            domain_scores[primary_role] / sum(domain_scores.values())
            if sum(domain_scores.values()) > 0
            else 0
        )

        return RoleDetectionResult(
            detected_role=primary_role,
            confidence=confidence,
            is_fusion=True,
            detected_domains=active_domains,
            switch_recommended=True,
            reason="multi_domain_detected",
        )

    # Single domain detected
    if active_domains:
        primary_role = active_domains[0]
        confidence = domain_scores[primary_role]

        return RoleDetectionResult(
            detected_role=primary_role,
            confidence=confidence,
            is_fusion=False,
            detected_domains=active_domains,
            switch_recommended=confidence >= 1,  # Only switch with clear signal
            reason=f"single_domain_{primary_role}",
        )

    # No clear domain detected
    return RoleDetectionResult(
        detected_role=RoleType.GENERAL,
        confidence=0.0,
        is_fusion=False,
        detected_domains=[],
        switch_recommended=False,
        reason="no_clear_domain",
    )


def _check_explicit_role_request(message: str) -> Optional[str]:
    """Check if message contains explicit role switch request"""
    for role, patterns in ROLE_SWITCH_PATTERNS.items():
        for pattern in patterns:
            if pattern in message:
                return role.value
    return None


def _is_capability_inquiry(message: str) -> bool:
    """Check if message is asking about capabilities"""
    for patterns in CAPABILITY_PATTERNS.values():
        for pattern in patterns:
            if pattern in message:
                return True
    return False


def _calculate_domain_scores(message: str) -> Dict[str, int]:
    """Calculate scores for each role domain based on keyword matching"""
    scores = {
        RoleType.NUTRITIONIST.value: 0,
        RoleType.BEHAVIOR_COACH.value: 0,
        RoleType.EMOTIONAL_COMPANION.value: 0,
    }

    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in message)
        scores[role.value] = score

    return scores


def _calculate_context_scores(context_messages: List[str]) -> Dict[str, int]:
    """Calculate domain scores based on recent conversation context"""
    combined_context = " ".join(context_messages).lower()
    return _calculate_domain_scores(combined_context)


def suggest_role_switch(
    current_role: str,
    new_message: str,
    context: Dict,
    conversation_context: Optional[List[str]] = None,
) -> Tuple[str, bool, str, bool]:
    """
    Determine if role switch is needed.

    Args:
        current_role: Current active role
        new_message: New user message
        context: Additional context including conversation state
        conversation_context: Recent messages for context

    Returns:
        Tuple of (new_role, should_switch, reason, is_fusion)
    """
    # Check if manual override is active
    if context.get("manual_mode_override", False):
        message_count = context.get("manual_mode_message_count", 0)
        # Keep manual role for at least 3 messages
        if message_count < 3:
            return current_role, False, "manual_mode_active", False
        else:
            # After 3 messages, allow auto-switching
            pass

    # Check for explicit role request in the message
    explicit_role = _check_explicit_role_request(new_message.lower())
    if explicit_role:
        logger.info(
            "Explicit role switch requested",
            requested_role=explicit_role,
            current_role=current_role,
        )
        return explicit_role, True, "explicit_request", False

    # Check for capability inquiry
    if _is_capability_inquiry(new_message.lower()):
        return "capability_inquiry", False, "capability_inquiry", False

    # Perform content analysis
    detection_result = detect_role_from_content(new_message, conversation_context)

    # Handle capability inquiry result
    if detection_result.detected_role == "capability_inquiry":
        return "capability_inquiry", False, "capability_inquiry", False

    # If fusion is detected, enable fusion mode
    if detection_result.is_fusion:
        logger.info(
            "Multi-domain query detected - enabling role fusion",
            domains=detection_result.detected_domains,
        )
        return (
            detection_result.detected_role,
            True,
            "fusion_mode",
            True,
        )

    # Only switch if confidence is high enough and role is different
    if (
        detection_result.switch_recommended
        and detection_result.detected_role != current_role
    ):
        logger.info(
            "Role switch recommended",
            old_role=current_role,
            new_role=detection_result.detected_role,
            confidence=detection_result.confidence,
        )
        return (
            detection_result.detected_role,
            True,
            detection_result.reason,
            False,
        )

    # No switch needed
    return current_role, False, "no_change", False


def get_capability_response(role: Optional[str] = None) -> str:
    """
    Get the capability response for capability inquiries.

    Args:
        role: Optional specific role to get capabilities for

    Returns:
        Formatted capability response message
    """
    if role == RoleType.NUTRITIONIST.value:
        return """🥗 **营养师模式** - 可以帮您：
• 分析饮食营养成分
• 推荐健康食谱
• 计算热量摄入（卡路里）
• 根据您的BMI/BMR制定营养计划
• 解答营养学问题
• 推荐健康饮食习惯

请告诉我您今天吃了什么，或者有什么营养问题想咨询？"""

    elif role == RoleType.BEHAVIOR_COACH.value:
        return """🏃 **行为教练模式** - 可以帮您：
• 制定运动计划
• 养成健康习惯
• 设定可实现的目标
• 保持动力和激励
• 克服拖延和懈怠
• 跟踪习惯养成进度

请告诉我您想培养什么习惯，或者需要什么运动建议？"""

    elif role == RoleType.EMOTIONAL_COMPANION.value:
        return """💬 **情感陪伴模式** - 可以帮您：
• 倾听您的感受和烦恼
• 提供情感支持
• 帮助缓解压力和焦虑
• 给予鼓励和肯定
• 陪伴您度过难关

有什么想说的，我随时在这里倾听。"""

    else:
        # General capability overview
        return """您好！我是您的AI健康助手，有三种专业模式：

🥗 **营养师模式** - 帮您分析饮食、推荐食谱、计算热量
🏃 **行为教练模式** - 帮您制定计划、养成习惯、保持动力
💬 **情感陪伴模式** - 倾听您的心声、提供情感支持

您可以：
• 直接点击切换按钮选择模式
• 说"切换到XX模式"让我改变角色
• 问我"你能做什么"了解详细功能

我会根据对话内容自动切换到最合适的模式。现在您想和哪位助手交流呢？"""


def get_role_display_name(role: str) -> str:
    """Get display name for role"""
    role_names = {
        "nutritionist": "营养师",
        "behavior_coach": "行为教练",
        "emotional_companion": "情感陪伴",
        "general": "AI助手",
        "capability_inquiry": "功能查询",
    }
    return role_names.get(role, role)


def get_role_emoji(role: str) -> str:
    """Get emoji for role"""
    role_emojis = {
        "nutritionist": "🥗",
        "behavior_coach": "🏃",
        "emotional_companion": "💬",
        "general": "🤖",
        "capability_inquiry": "❓",
    }
    return role_emojis.get(role, "🤖")


def determine_role_by_content(content: str) -> str:
    """
    Legacy function for backward compatibility.
    Uses the new enhanced detection.
    """
    result = detect_role_from_content(content)
    return result.detected_role
