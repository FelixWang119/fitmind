from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion


def get_health_advice_from_ai(
    db: Session, user: User, context: Dict[str, Any] = None
) -> str:
    """
    基于用户健康数据生成AI个性化健康建议

    参数:
        db: 数据库会话
        user: 用户对象
        context: 额外的上下文信息

    返回:
        str: AI生成的健康建议
    """
    # 获取用户基本信息
    user_info = {
        "age": user.age,
        "gender": user.gender,
        "height": user.height,
        "initial_weight": user.initial_weight,
        "target_weight": user.target_weight,
    }

    # 获取最近的健康记录
    recent_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == user.id,
            HealthRecord.record_date >= datetime.utcnow() - timedelta(days=30),
        )
        .order_by(HealthRecord.record_date.desc())
        .limit(10)
        .all()
    )

    # 获取活跃习惯
    active_habits = (
        db.query(Habit).filter(Habit.user_id == user.id, Habit.is_active == True).all()
    )

    # 获取最近的习惯完成情况
    # 通过habit表连接查询用户的习惯完成记录
    recent_completions = []
    if active_habits:
        habit_ids = [habit.id for habit in active_habits]
        recent_completions = (
            db.query(HabitCompletion)
            .filter(
                HabitCompletion.habit_id.in_(habit_ids),
                HabitCompletion.completion_date
                >= datetime.utcnow() - timedelta(days=7),
            )
            .all()
        )

    # 分析用户数据
    analysis = analyze_user_health_data(
        user_info, recent_records, active_habits, recent_completions
    )

    # 生成个性化建议
    advice = generate_personalized_advice(analysis, user_info)

    return advice


def analyze_user_health_data(
    user_info: Dict[str, Any],
    recent_records: List[HealthRecord],
    active_habits: List[Habit],
    recent_completions: List[HabitCompletion],
) -> Dict[str, Any]:
    """
    分析用户健康数据

    返回:
        Dict[str, Any]: 分析结果
    """
    analysis = {
        "weight_trend": "stable",
        "sleep_quality": "average",
        "activity_level": "moderate",
        "nutrition_balance": "balanced",
        "habit_consistency": "good",
        "stress_level": "medium",
    }

    # 分析体重趋势
    if recent_records and len(recent_records) >= 2:
        weights = [r.weight for r in recent_records if r.weight is not None]
        if len(weights) >= 2:
            weight_change = weights[0] - weights[-1]
            if weight_change > 0.5:
                analysis["weight_trend"] = "increasing"
            elif weight_change < -0.5:
                analysis["weight_trend"] = "decreasing"

    # 分析睡眠质量
    sleep_hours = [r.sleep_hours for r in recent_records if r.sleep_hours is not None]
    if sleep_hours:
        avg_sleep = sum(sleep_hours) / len(sleep_hours)
        if avg_sleep < 6:
            analysis["sleep_quality"] = "poor"
        elif avg_sleep > 8:
            analysis["sleep_quality"] = "excellent"

    # 分析活动水平
    steps = [r.steps_count for r in recent_records if r.steps_count is not None]
    if steps:
        avg_steps = sum(steps) / len(steps)
        if avg_steps < 5000:
            analysis["activity_level"] = "low"
        elif avg_steps > 10000:
            analysis["activity_level"] = "high"

    # 分析习惯一致性
    if active_habits and recent_completions:
        completion_rate = len(recent_completions) / (
            len(active_habits) * 7
        )  # 7天内的完成率
        if completion_rate < 0.5:
            analysis["habit_consistency"] = "poor"
        elif completion_rate > 0.8:
            analysis["habit_consistency"] = "excellent"

    return analysis


def generate_personalized_advice(
    analysis: Dict[str, Any], user_info: Dict[str, Any]
) -> str:
    """
    基于分析结果生成个性化建议

    返回:
        str: 个性化健康建议
    """
    advice_parts = []

    # 体重管理建议
    if analysis["weight_trend"] == "increasing":
        advice_parts.append("您的体重呈现上升趋势，建议加强饮食控制和增加有氧运动。")
    elif analysis["weight_trend"] == "decreasing":
        advice_parts.append("恭喜！您的体重正在下降，继续保持良好的生活习惯。")
    else:
        advice_parts.append("您的体重保持稳定，这是健康管理的重要基础。")

    # 睡眠建议
    if analysis["sleep_quality"] == "poor":
        advice_parts.append(
            "您的睡眠时间偏少，建议每天保证7-8小时睡眠，这对新陈代谢和体重管理至关重要。"
        )
    elif analysis["sleep_quality"] == "excellent":
        advice_parts.append(
            "您的睡眠质量很好，充足的睡眠有助于控制食欲和维持健康体重。"
        )

    # 活动建议
    if analysis["activity_level"] == "low":
        advice_parts.append(
            "建议增加日常活动量，每天步行8000-10000步有助于提高新陈代谢。"
        )
    elif analysis["activity_level"] == "high":
        advice_parts.append("您的运动量充足，继续保持！")

    # 习惯建议
    if analysis["habit_consistency"] == "poor":
        advice_parts.append("习惯坚持度有待提高，建议从简单的习惯开始，逐步建立规律。")
    elif analysis["habit_consistency"] == "excellent":
        advice_parts.append("您的习惯坚持度很高，这是长期成功的关键！")

    # 个性化建议基于用户信息
    if user_info.get("age") and user_info["age"] > 40:
        advice_parts.append(
            "随着年龄增长，建议增加力量训练以维持肌肉量，这对新陈代谢很重要。"
        )

    if user_info.get("gender") == "female":
        advice_parts.append(
            "女性在生理周期不同阶段对饮食和运动的需求可能不同，建议根据自身感受调整。"
        )

    # 添加通用健康建议
    advice_parts.append("保持水分充足，每天饮用足够的水有助于新陈代谢和食欲控制。")
    advice_parts.append("均衡饮食，确保摄入足够的蛋白质、健康脂肪和复合碳水化合物。")

    # 组合建议
    if not advice_parts:
        advice_parts.append(
            "继续保持良好的健康习惯，定期记录数据以便获得更精准的建议。"
        )

    return " ".join(advice_parts)


def get_daily_tip() -> Dict[str, str]:
    """
    获取每日健康小贴士

    返回:
        Dict[str, str]: 包含标题和内容的每日小贴士
    """
    tips = [
        {
            "title": "早餐的重要性",
            "content": "营养丰富的早餐有助于启动新陈代谢，控制全天食欲。建议早餐包含蛋白质和复合碳水化合物。",
        },
        {
            "title": "水分与体重管理",
            "content": "充足的水分摄入有助于新陈代谢和食欲控制。建议每天饮用8杯水，饭前喝水可减少进食量。",
        },
        {
            "title": "睡眠与体重",
            "content": "充足的睡眠有助于调节饥饿激素，减少对高热量食物的渴望。建议每晚保证7-8小时睡眠。",
        },
        {
            "title": "力量训练的好处",
            "content": "力量训练增加肌肉量，提高基础代谢率。每周2-3次力量训练有助于长期体重管理。",
        },
        {
            "title": "压力管理",
            "content": "长期压力可能导致皮质醇升高，影响体重。建议通过冥想、深呼吸等方式管理压力。",
        },
        {
            "title": "膳食纤维的重要性",
            "content": "高纤维食物增加饱腹感，有助于控制食欲。建议多吃蔬菜、水果和全谷物。",
        },
        {
            "title": "有氧运动建议",
            "content": "中等强度的有氧运动如快走、游泳、骑自行车，每周150分钟有助于心血管健康和体重管理。",
        },
        {
            "title": "蛋白质摄入",
            "content": "充足的蛋白质摄入有助于维持肌肉量，增加饱腹感。建议每餐包含优质蛋白质来源。",
        },
    ]

    # 根据日期选择不同的提示（简单实现：按星期几选择）
    day_of_week = datetime.now().weekday()
    return tips[day_of_week % len(tips)]
