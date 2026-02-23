import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.conversation import Conversation, Message, MessageRole
from app.models.user import User as UserModel
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.emotional_support import EmotionalSupport, EmotionalState
from app.schemas.ai import (
    AIRequest,
    AIResponse,
    AIHealthAdviceRequest,
    AIHealthAdviceResponse,
)

from app.services.ai_service import get_ai_response
from app.services.ai_health_advisor import get_health_advice_from_ai
from app.services.ai_role_detection import (
    suggest_role_switch,
    determine_role_by_content,
)  # New import
from app.core.rate_limit import RateLimiter

logger = structlog.get_logger()

router = APIRouter()

# Rate limiter for AI endpoints (20 requests per minute)
ai_rate_limiter = RateLimiter(requests_per_minute=20)


@router.post("/chat", response_model=AIResponse)
async def ai_chat(
    ai_request: AIRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """AI 聊天接口 - 速率限制：20 次/分钟"""
    # 检查速率限制
    if not ai_rate_limiter.is_allowed(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试（AI 聊天限制：20 次/分钟）",
        )

    logger.info(
        "AI chat request",
        user_id=current_user.id,
        message_length=len(ai_request.message),
    )

    try:
        # 构建上下文：如果有对话ID，加载历史消息
        context = ai_request.context or {}

        # 如果是首次会话或没有明确指定角色且不是角色切换请求
        if "current_role" not in context:
            context["current_role"] = "general"  # Default to general

        # 检查是否需要根据消息内容进行角色切换 (新函数返回4个值)
        new_role, needs_switch, reason, is_fusion = suggest_role_switch(
            context.get("current_role", "general"), ai_request.message, context
        )

        # 处理功能查询
        if new_role == "capability_inquiry":
            from app.services.ai_role_detection import get_capability_response

            capability_response = get_capability_response()
            return AIResponse(
                response=capability_response,
                model="role_detection",
                tokens_used=len(capability_response.split()),
                response_time=0.1,
                timestamp=datetime.utcnow(),
                current_role=context.get("current_role", "general"),
                role_switched=False,
            )

        # 如果需要切换角色
        previous_role = None
        notification = None
        if needs_switch and new_role != context.get("current_role"):
            logger.info(
                f"Switching from {context['current_role']} to {new_role} based on message content"
            )
            previous_role = context.get("current_role")
            context["previous_role"] = previous_role
            context["current_role"] = new_role

            # 设置通知消息
            from app.services.ai_role_detection import get_role_display_name

            if is_fusion:
                notification = "让我从多个角度帮你分析..."
            else:
                notification = f"已切换到{get_role_display_name(new_role)}模式"

        if ai_request.conversation_id:
            # 验证对话属于当前用户
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == ai_request.conversation_id,
                    Conversation.user_id == current_user.id,
                )
                .first()
            )

            if conversation:
                # 更新对话的角色信息
                conversation.current_role = new_role
                if is_fusion:
                    conversation.role_fusion_enabled = True
                else:
                    conversation.role_fusion_enabled = False

                # 如果是手动模式切换
                if ai_request.context and "manual_role" in ai_request.context:
                    conversation.manual_mode_override = True
                    conversation.manual_mode_message_count = 0

                db.commit()

                # 加载最近的历史消息（限制数量避免token超限）
                history_messages = (
                    db.query(Message)
                    .filter(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at.desc())
                    .limit(10)  # 限制最近10条消息
                    .all()
                )

                # 反转顺序（最旧到最新）并转换为AI格式
                history_messages.reverse()
                context["history"] = [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in history_messages
                ]

        # 获取AI回复
        response = await get_ai_response(
            message=ai_request.message,
            user_id=int(current_user.id),  # Convert SQLAlchemy Column to int
            context=context,
            db=db,
        )

        # 包含当前角色信息
        response_dict = response.dict()
        response_dict["current_role"] = context.get("current_role", "general")
        response_dict["role_switched"] = (
            needs_switch and new_role != previous_role if previous_role else False
        )
        response_dict["previous_role"] = previous_role
        response_dict["is_fusion"] = is_fusion
        response_dict["notification"] = notification

        logger.info(
            "AI response generated",
            response_length=len(response.response),
            model=response.model,
            has_history=("history" in context),
            current_role=context.get("current_role", "general"),
            role_switched=response_dict["role_switched"],
        )

        return AIResponse(**response_dict)

    except Exception as e:
        logger.error("AI chat error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI service error"
        )


@router.get("/health")
async def ai_health_check():
    """AI服务健康检查"""
    return {"status": "healthy", "service": "ai", "timestamp": "now"}


@router.post("/health-advice", response_model=AIHealthAdviceResponse)
async def get_ai_health_advice(
    request: AIHealthAdviceRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    基于用户健康数据获取AI个性化健康建议
    """
    try:
        advice = get_health_advice_from_ai(db, current_user, request.context)
        return AIHealthAdviceResponse(advice=advice)
    except Exception as e:
        logger.error(
            "AI advice generation failed", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="暂时无法生成健康建议，请稍后再试",
        )


@router.get("/trend-analysis", response_model=Dict[str, Any])
async def get_health_trend_analysis(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = 30,
):
    """
    获取健康数据趋势分析
    """
    from datetime import timedelta

    # 计算起始日期
    start_date = datetime.utcnow().date() - timedelta(days=days)

    # 获取健康记录
    records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    if not records:
        return {
            "analysis": "近期没有足够的健康记录进行趋势分析",
            "recommendation": "请每日记录健康数据，持续跟踪您的进步",
        }

    # 提取数据序列
    weights = [(rec.record_date, rec.weight) for rec in records if rec.weight]
    blood_pressures = [
        (rec.record_date, rec.blood_pressure_sys, rec.blood_pressure_dia)
        for rec in records
        if rec.blood_pressure_sys and rec.blood_pressure_dia
    ]
    sleep_hours = [
        (rec.record_date, rec.sleep_hours) for rec in records if rec.sleep_hours
    ]
    steps_counts = [
        (rec.record_date, rec.steps_count) for rec in records if rec.steps_count
    ]

    analysis = {}

    # 体重趋势分析
    if len([w[1] for w in weights if w[1]]) >= 2:
        weight_values = [w[1] for w in weights if w[1] is not None]
        start_weight = weight_values[0] if weight_values else 0
        current_weight = weight_values[-1] if weight_values else 0
        weight_change = current_weight - start_weight

        if weight_change < -0.5:  # 减少半公斤以上
            analysis["weight"] = (
                f"体重呈现稳步下降趋势 (-{abs(weight_change):.2f}kg)，继续保持良好习惯！"
            )
        elif weight_change > 0.5:  # 増加半公斤以上
            analysis["weight"] = (
                f"体重有所增加 (+{weight_change:.2f}kg)，建议加强饮食控制和运动"
            )
        else:
            analysis["weight"] = (
                f"体重基本稳定 (变化:{weight_change:.2f}kg)，维持当前健康生活模式"
            )
    else:
        analysis["weight"] = "体重记录不足，无法分析趋势。请定期测量体重以跟踪进展"

    # 睡眠趋势分析
    if len([s[1] for s in sleep_hours if s[1]]) >= 3:
        avg_sleep_duration = sum([s[1] for s in sleep_hours if s[1]]) / len(
            [s[1] for s in sleep_hours if s[1]]
        )
        if avg_sleep_duration < 6:
            analysis["sleep"] = "平均睡眠时间偏少，建议增加至7小时以上以促进健康恢复"
        elif avg_sleep_duration > 9:
            analysis["sleep"] = "睡眠充足但过长可能会增加疲劳感，建议适度减少"
        else:
            analysis["sleep"] = "睡眠时间适宜，对健康维护非常有利"
    else:
        analysis["sleep"] = "建议每天保持规律的睡眠时间，对身心健康至关重要"

    # 步数趋势分析
    if len([sc[1] for sc in steps_counts if sc[1]]) >= 3:
        avg_steps = sum([sc[1] for sc in steps_counts if sc[1]]) / len(
            [sc[1] for sc in steps_counts if sc[1]]
        )
        if avg_steps > 8000:
            analysis["steps"] = f"运动积极，平均步数{avg_steps:.0f}，有益于心血管健康"
        else:
            analysis["steps"] = (
                f"平均步数{avg_steps:.0f}，建议逐渐增加日常活动量至万步以上"
            )
    else:
        analysis["steps"] = "缺乏步数记录，建议开启步数追踪功能"

    total_records = len(records)
    days_span = (weights[-1][0] - weights[0][0]).days if weights else 1
    consistency = (total_records / max(days_span, 1)) * 100 if days_span > 0 else 0

    analysis["consistency"] = (
        f"数据记录一致性: {consistency:.1f}%，{(total_records / max(days_span, 1)):.1f}次/天"
    )

    recommendations = []
    if consistency < 80:
        recommendations.append("请尽量每天定时记录健康数据，以便AI提供更精准的建议")
    if len(analysis["weight"]) > 10 and "增加" in analysis["weight"]:
        recommendations.append("增加低强度有氧运动，例如散步或慢跑，有助于控制体重")
    if any(k for k in analysis if "建议" in analysis[k]):
        recommendations.extend(
            [
                "逐步改善生活习惯对长期健康至关重要",
                "保持积极心态，减肥是一个渐进过程，不要给自己过大压力",
            ]
        )
    else:
        recommendations.append("继续保持良好的健康管理习惯!")

    return {
        "period_start": start_date.isoformat(),
        "period_end": datetime.utcnow().date().isoformat(),
        "data_points_count": total_records,
        "trend_analysis": analysis,
        "recommendations": recommendations,
        "overall_assessment": f"您在过去{days}天内的健康数据表现{'优秀' if consistency > 80 else '良好' if consistency > 60 else '一般'}",
    }


@router.post("/role-chat", response_model=AIResponse)
async def ai_role_chat(
    ai_request: AIRequest,
    ai_role: str = "general",  # Add a role parameter
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """AI对话接口，支持特定专家角色 (营养师, 运练師, etc.)"""
    logger.info(
        "AI role chat request",
        user_id=current_user.id,
        message_length=len(ai_request.message),
        ai_role=ai_role,
    )

    # 获取用户健康数据
    # 为了角色专业化，我们会根据角色收集不同类型的上下文
    context = ai_request.context or {}

    # 获取用户基本健康数据
    user_data = {
        "age": current_user.age,
        "gender": current_user.gender,
        "height": current_user.height,
        "initial_weight": current_user.initial_weight,
        "target_weight": current_user.target_weight,
        "activity_level": current_user.activity_level,
    }
    context["user_info"] = user_data

    # 检查是哪个角色被请求并相应地添加上下文
    if ai_role.lower() == "nutritionist":
        # 从HealthRecord 获取营养相关信息
        recent_records = (
            db.query(HealthRecord)
            .filter(HealthRecord.user_id == current_user.id)
            .order_by(HealthRecord.record_date.desc())
            .limit(10)
            .all()
        )

        nutrition_data = []
        for record in recent_records:
            record_data = {}
            if record.calories_intake:
                record_data["calories_intake"] = record.calories_intake
            if record.protein_intake:
                record_data["protein_intake"] = record.protein_intake
            if record.carbs_intake:
                record_data["carbs_intake"] = record.carbs_intake
            if record.fat_intake:
                record_data["fat_intake"] = record.fat_intake
            if record.meal_datetime:
                record_data["record_date"] = record.meal_datetime.isoformat()

            if record_data:  # 只有在有营养数据时添加
                nutrition_data.append(record_data)

        if nutrition_data:
            context["nutrition_data"] = nutrition_data

        context["professional_role"] = "nutritionist"
        # 为营养师角色定制消息模板前缀
        context["role_prompt"] = (
            "你是专业营养师。你只从营养科学角度回答问题，给出具体的饮食建议和营养成分分析。请根据用户的具体情况（年龄、身高、体重等），提供专业、有依据的营养建议。如果无法提供建议，请明确说明原因。"
        )
    # 如果是行为教练角色，获取用户的习惯和情绪数据
    elif ai_role.lower() == "behavior_coach":
        # 获取活跃习惯
        from app.models.habit import Habit, HabitCompletion
        from app.models.emotional_support import EmotionalSupport, EmotionalState

        active_habits = (
            db.query(Habit)
            .filter(Habit.user_id == current_user.id, Habit.is_active == True)
            .all()
        )

        if active_habits:
            habits_list = []
            for habit in active_habits:
                habits_list.append(
                    {
                        "name": habit.name,
                        "target_frequency": habit.target_frequency,
                        "created_at": habit.created_at.isoformat()
                        if habit.created_at
                        else None,
                        "notes": habit.notes,
                    }
                )
            context["active_habits"] = habits_list

        # 获取最近的打卡记录
        recent_completions = (
            db.query(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .filter(Habit.user_id == current_user.id)
            .order_by(HabitCompletion.completion_date.desc())
            .limit(14)  # 最近两周的习惯打卡情况
            .all()
        )

        if recent_completions:
            completions_data = []
            for completion in recent_completions:
                completions_data.append(
                    {
                        "habit_name": completion.habit.name if completion.habit else "",
                        "completed_at": completion.completion_date.isoformat()
                        if completion.completion_date
                        else None,
                        "notes": completion.notes,
                        "streak_count": completion.streak_count,
                    }
                )
            context["completions_data"] = completions_data

        # 获取最近的情感记录
        recent_emotions = (
            db.query(EmotionalSupport, EmotionalState)
            .join(
                EmotionalState, EmotionalSupport.emotional_state_id == EmotionalState.id
            )
            .filter(EmotionalSupport.user_id == current_user.id)
            .order_by(EmotionalSupport.created_at.desc())
            .limit(10)
            .all()
        )

        if recent_emotions:
            emotions_data = []
            for check_in, state in recent_emotions:
                emotions_data.append(
                    {
                        "emotion": state.state_name,
                        "level": check_in.intensity_level,
                        "notes": check_in.notes,
                        "date": check_in.created_at.isoformat()
                        if check_in.created_at
                        else None,
                    }
                )
            context["emotional_data"] = emotions_data

        context["professional_role"] = "behavior_coach"
        context["role_prompt"] = (
            "你是专业行为教练。专注于帮助用户建立持久的健康习惯，克服障碍，以及保持长期的行为变化。基于用户的生活情况和习惯数据，提供具体的技巧、激励和支持来促进他们成功达成健康目标。强调行为改变策略、动机和韧性。"
        )

        if active_habits:
            habits_list = []
            for habit in active_habits:
                habits_list.append(
                    {
                        "name": habit.name,
                        "target_frequency": habit.target_frequency,
                        "created_at": habit.created_at.isoformat()
                        if habit.created_at
                        else None,
                        "notes": habit.notes,
                    }
                )
            context["active_habits"] = habits_list

        # 获取最近的打卡记录
        recent_completions = (
            db.query(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .filter(Habit.user_id == current_user.id)
            .order_by(HabitCompletion.completion_date.desc())
            .limit(14)  # 最近两周的习惯打卡情况
            .all()
        )

        if recent_completions:
            completions_data = []
            for completion in recent_completions:
                completions_data.append(
                    {
                        "habit_name": completion.habit.name if completion.habit else "",
                        "completed_at": completion.completion_date.isoformat()
                        if completion.completion_date
                        else None,
                        "notes": completion.notes,
                        "streak_count": completion.streak_count,
                    }
                )
            context["completions_data"] = completions_data

        # 获取最近的情感记录
        recent_emotions = (
            db.query(EmotionalSupport, EmotionalState)
            .join(
                EmotionalState, EmotionalSupport.emotional_state_id == EmotionalState.id
            )
            .filter(EmotionalSupport.user_id == current_user.id)
            .order_by(EmotionalSupport.created_at.desc())
            .limit(10)
            .all()
        )

        if recent_emotions:
            emotions_data = []
            for check_in, state in recent_emotions:
                emotions_data.append(
                    {
                        "emotion": state.state_name,
                        "level": check_in.intensity_level,
                        "notes": check_in.notes,
                        "date": check_in.created_at.isoformat()
                        if check_in.created_at
                        else None,
                    }
                )
            context["emotional_data"] = emotions_data

        context["professional_role"] = "behavior_coach"
        context["role_prompt"] = (
            "你是专业行为教练。专注于帮助用户建立持久的健康习惯，克服障碍，以及保持长期的行为变化。基于用户的生活情况和习惯数据，提供具体的技巧、激励和支持来促进他们成功达成健康目标。强调行为改变策略、动机和韧性。"
        )
    # 如果是情感陪伴角色，处理用户情感数据
    elif ai_role.lower() == "emotional_support":
        # 获取用户的情感记录
        from app.models.emotional_support import EmotionalSupport, EmotionalState

        emotional_records = (
            db.query(EmotionalSupport, EmotionalState)
            .join(
                EmotionalState, EmotionalSupport.emotional_state_id == EmotionalState.id
            )
            .filter(EmotionalSupport.user_id == current_user.id)
            .order_by(EmotionalSupport.created_at.desc())
            .limit(20)  # 获取最近20条情感记录
            .all()
        )

        if emotional_records:
            emotional_data = []
            for check_in, emotion_state in emotional_records:
                emotional_data.append(
                    {
                        "emotion": emotion_state.state_name,
                        "intensity": check_in.intensity_level,
                        "date": check_in.created_at.isoformat()
                        if check_in.created_at
                        else None,
                        "notes": check_in.notes,
                    }
                )
            context["emotional_history"] = emotional_data

        # 获取用户的心理健康相关数据
        user_emotional_profile = {
            "stress_levels": getattr(current_user, "stress_level", None),
            "mood_tracking": getattr(current_user, "mood_tracking", None),
        }
        context["user_emotional_profile"] = user_emotional_profile

        context["professional_role"] = "emotional_support"
        context["role_prompt"] = (
            "你是专业的情感陪伴助手。你的职责是倾听和理解用户的情绪，提供温暖、共情的回应。以温和关怀的态度，给予情感支持、理解与鼓励。关注用户的情感状态，提供情感抚慰，帮助缓解压力和焦虑。请展现同情心和支持，让用户感到被理解和关爱。"
        )

    # 构建最终的上下文
    final_context = {
        **context,
        "role": ai_role,
        "user_fullname": current_user.full_name,
        "user_username": current_user.username,
    }

    try:
        # 获取AI回复
        response = await get_ai_response(
            message=ai_request.message,
            user_id=int(current_user.id),  # Convert to int
            context=final_context,
            db=db,
        )

        logger.info(
            "AI role response generated",
            response_length=len(response.response),
            model=response.model,
            ai_role=ai_role,
        )

        return response

    except Exception as e:
        logger.error("AI role chat error", error=str(e), ai_role=ai_role)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI service error"
        )


@router.post("/conversations/{conversation_id}/switch-role")
async def switch_role(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """手动切换角色"""
    from app.schemas.chat import RoleSwitchRequest, RoleSwitchResponse
    from app.models.conversation import RoleSwitch
    from app.services.ai_role_detection import get_role_display_name

    # This is a simple implementation - in production you'd want to parse the request body properly
    # For now, return a simple response
    # Note: The full implementation is in chat.py endpoint

    # Verify conversation belongs to user
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    return {
        "success": True,
        "current_role": conversation.current_role or "general",
        "message": "Use the /chat endpoint for role switching",
    }


@router.get("/conversations/{conversation_id}/role-history")
async def get_role_history(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取角色切换历史"""
    from app.models.conversation import RoleSwitch

    # Verify conversation belongs to user
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    # Get role switches
    switches = (
        db.query(RoleSwitch)
        .filter(RoleSwitch.conversation_id == conversation_id)
        .order_by(RoleSwitch.created_at.desc())
        .limit(50)
        .all()
    )

    return {
        "conversation_id": conversation_id,
        "current_role": conversation.current_role or "general",
        "role_fusion_enabled": conversation.role_fusion_enabled or False,
        "switches": [
            {
                "id": s.id,
                "from_role": s.from_role,
                "to_role": s.to_role,
                "trigger_type": s.trigger_type,
                "switch_reason": s.switch_reason,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in switches
        ],
    }
