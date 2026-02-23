from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.dashboard import (
    DashboardOverview,
    QuickStats,
    OverviewData,
    ChartData,
    WeightTrend,
    NutritionBreakdown,
    EmotionalData,
    WeekOverviewItem,
    BadgeInfo,
)
from app.services.ai_health_advisor import get_daily_tip


def get_dashboard_overview(db: Session, user: User) -> DashboardOverview:
    """
    获取仪表板概览数据
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    from app.models.health_record import HealthRecord
    from app.models.habit import Habit, HabitCompletion

    # 计算BMI（如果用户有身高和初始体重）
    bmi = None
    # Check if values exist by comparing with None, avoiding column-object boolean checks
    if user.height is not None and user.initial_weight is not None:
        # 身高从厘米转换为米，体重从克转换为公斤
        height_m = float(user.height) / 100.0 if user.height is not None else 1.0
        weight_kg = (
            float(user.initial_weight) / 1000.0
            if user.initial_weight is not None
            else 1.0
        )
        bmi = weight_kg / (height_m * height_m)

    # 查询最近的健康记录
    recent_records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user.id)
        .order_by(HealthRecord.created_at.desc())
        .limit(30)
        .all()
    )

    # Get actual value properties to avoid column object comparison
    user_initial_weight = user.initial_weight
    records_exist = len(recent_records) > 0

    # 计算总减重（如果有初始体重和最近体重）
    total_weight_loss = 0
    if user_initial_weight is not None and records_exist:
        # 找到最近的体重记录
        recent_weight_record = next((r for r in recent_records if r.weight), None)
        if recent_weight_record and recent_weight_record.weight:
            # 体重从克转换为公斤
            initial_weight_kg = (user.initial_weight or 0) / 1000.0
            recent_weight_kg = (recent_weight_record.weight or 0) / 1000.0
            total_weight_loss = initial_weight_kg - recent_weight_kg

    # 查询活跃习惯数量
    active_habits_count = (
        db.query(Habit)
        .filter(and_(Habit.user_id == user.id, Habit.is_active == True))
        .count()
    )

    # 查询习惯打卡连续天数（简化实现）
    streak_days = 0
    habit_completions = (
        db.query(HabitCompletion)
        .join(Habit, Habit.id == HabitCompletion.habit_id)
        .filter(Habit.user_id == user.id)
        .order_by(HabitCompletion.completion_date.desc())
        .limit(30)
        .all()
    )

    if habit_completions:
        # 简单计算连续天数（实际应该检查日期连续性）
        streak_days = min(30, len(habit_completions))

    # 查询健康记录天数
    days_tracked_result = (
        db.query(func.count(func.distinct(func.date(HealthRecord.created_at))))
        .filter(HealthRecord.user_id == user.id)
        .scalar()
    )
    days_tracked = int(days_tracked_result) if days_tracked_result is not None else 0

    # 计算每周平均减重
    weekly_average = 0
    if days_tracked > 7 and total_weight_loss > 0:
        weekly_average = total_weight_loss / (days_tracked / 7)

    # 获取最近7天的体重趋势
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_weight_records = (
        db.query(HealthRecord)
        .filter(
            and_(
                HealthRecord.user_id == user.id,
                HealthRecord.weight.isnot(None),
                HealthRecord.created_at >= seven_days_ago,
            )
        )
        .order_by(HealthRecord.created_at)
        .all()
    )

    # 准备图表数据
    weight_dates = []
    weight_values = []

    if recent_weight_records:
        for record in recent_weight_records:
            # 简化：只显示日期部分
            date_str = (
                record.created_at.strftime("%m-%d") if record.created_at else "N/A"
            )
            weight_dates.append(date_str)
            weight_values.append(record.weight / 1000)  # 转换为公斤
    else:
        # 使用模拟数据
        weight_dates = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weight_values = [72.3, 72.1, 71.9, 71.8, 71.6, 71.5, 71.4]

    # 查询最近的营养数据
    recent_nutrition = (
        db.query(HealthRecord)
        .filter(
            and_(
                HealthRecord.user_id == user.id,
                HealthRecord.calories_intake.isnot(None),
            )
        )
        .order_by(HealthRecord.created_at.desc())
        .first()
    )

    # 准备概览数据
    total_weight_loss_float = (
        float(max(total_weight_loss, 0))
        if total_weight_loss is not None and hasattr(total_weight_loss, "__float__")
        else 0.0
    )
    bmi_float = round(float(bmi), 1) if bmi is not None else 22.4
    weekly_avg_float = (
        round(float(weekly_average), 1) if weekly_average is not None else 0.0
    )
    days_tracked_int = int(days_tracked) if days_tracked is not None else 0
    active_habits_int = active_habits_count if active_habits_count is not None else 0
    streak_days_int = streak_days if streak_days is not None else 0

    overview_data = OverviewData(
        total_weight_loss=total_weight_loss_float,
        bmi=bmi_float,
        weekly_average=weekly_avg_float,
        days_tracked=days_tracked_int,
        active_habits=active_habits_int,
        streak_days=streak_days_int,
        total_points=1250,  # 暂时使用模拟数据
    )

    chart_data = ChartData(
        weight_trend=WeightTrend(
            dates=weight_dates,
            weights=weight_values,
        ),
        nutrition_breakdown=NutritionBreakdown(
            carbs=float(recent_nutrition.carbs_intake)
            if recent_nutrition and recent_nutrition.carbs_intake is not None
            else 230.0,
            protein=float(recent_nutrition.protein_intake)
            if recent_nutrition and recent_nutrition.protein_intake is not None
            else 150.0,
            fat=float(recent_nutrition.fat_intake)
            if recent_nutrition and recent_nutrition.fat_intake is not None
            else 78.0,
        ),
    )

    emotional_data = EmotionalData(
        stress_level=6,  # 暂时使用模拟数据
        mood_score=8,  # 暂时使用模拟数据
        week_overview=[
            WeekOverviewItem(day="周一", mood=8, stress=5),
            WeekOverviewItem(day="周二", mood=7, stress=6),
            WeekOverviewItem(day="周三", mood=9, stress=4),
            WeekOverviewItem(day="周四", mood=6, stress=7),
            WeekOverviewItem(day="周五", mood=8, stress=5),
            WeekOverviewItem(day="周六", mood=9, stress=3),
            WeekOverviewItem(day="周日", mood=8, stress=4),
        ],
    )

    badges = [
        BadgeInfo(
            id=1, name="早起鸟", description="连续早起一周", earned=True, icon="🌅"
        ),
        BadgeInfo(
            id=2, name="水水水", description="每日八杯水", earned=True, icon="💧"
        ),
        BadgeInfo(
            id=3, name="夜宵戒断", description="21天不进夜宵", earned=False, icon="🌙"
        ),
        BadgeInfo(
            id=4, name="蔬果达人", description="每日蔬果5份", earned=True, icon="🥗"
        ),
        BadgeInfo(
            id=5, name="连续记录", description="健康记录不间断", earned=True, icon="📝"
        ),
        BadgeInfo(
            id=6, name="突破瓶颈", description="突破体重平台期", earned=False, icon="📈"
        ),
    ]

    # 获取每日小贴士
    daily_tip = get_daily_tip()

    return DashboardOverview(
        greeting=f"欢迎回来，{user.username}！",
        daily_tip=daily_tip,
        progress_summary={
            "weight_progress": 5.2,
            "habit_completion": 75,
            "current_level": 5,
            "total_points": 1250,
        },
        overview=overview_data,
        chart_data=chart_data,
        emotional_data=emotional_data,
        badges=badges,
    )


def get_quick_stats(db: Session, user: User) -> QuickStats:
    """
    获取快速统计数据
    """
    from datetime import datetime, date
    from sqlalchemy import and_
    from app.models.health_record import HealthRecord

    # 获取今天的健康记录
    today = date.today()
    today_record = (
        db.query(HealthRecord)
        .filter(
            and_(
                HealthRecord.user_id == user.id,
                func.date(HealthRecord.created_at) == today,
            )
        )
        .first()
    )

    # 使用实际数据或默认值
    if today_record:
        today_calories = today_record.calories_intake or 1850
        daily_step_count = today_record.steps_count or 8542
        water_intake = 1800  # 水摄入量需要单独的模型
        sleep_hours = today_record.sleep_hours or 7.5
    else:
        # 如果没有今天的记录，使用最近的数据或默认值
        recent_record = (
            db.query(HealthRecord)
            .filter(HealthRecord.user_id == user.id)
            .order_by(HealthRecord.created_at.desc())
            .first()
        )

        if recent_record:
            today_calories = recent_record.calories_intake or 1850
            daily_step_count = recent_record.steps_count or 8542
            sleep_hours = recent_record.sleep_hours or 7.5
        else:
            today_calories = 1850
            daily_step_count = 8542
            sleep_hours = 7.5

        water_intake = 1800  # 默认值

    return QuickStats(
        today_calories=today_calories,
        daily_step_count=daily_step_count,
        water_intake=water_intake,
        sleep_hours=sleep_hours,
    )
