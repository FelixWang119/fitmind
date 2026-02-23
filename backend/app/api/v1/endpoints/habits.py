from datetime import date, datetime, timedelta
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.habit import Habit, HabitCompletion, HabitFrequency, HabitCategory
from app.models.user import User as UserModel
from app.schemas.habit import (
    HabitCreate,
    HabitInDB,
    HabitUpdate,  # FIXED: Missing import
    HabitStats,  # FIXED: Was HabitStatistics
    HabitCompletionCreate,
    HabitCompletionInDB,
    HabitRecommendation,
    DailyHabitChecklist,
    StreakInfo,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/", response_model=List[HabitInDB])
async def get_habits(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="过滤类别"),
    active_only: bool = Query(True, description="只返回活跃状态"),
):
    """获取用户的所有习惯"""
    query = db.query(Habit).filter(Habit.user_id == current_user.id)

    if active_only:
        query = query.filter(Habit.is_active == True)

    if category:
        habit_category = HabitCategory(category)
        query = query.filter(Habit.category == habit_category)

    habits = query.all()

    logger.info(
        "Fetched habits",
        user_id=current_user.id,
        habit_count=len(habits),
        category=category,
        active_only=active_only,
    )

    return habits


@router.post("/", response_model=HabitInDB)
async def create_habit(
    habit_create: HabitCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建新习惯"""
    habit = Habit(
        name=habit_create.name,
        description=habit_create.description,
        category=habit_create.category,
        frequency=habit_create.frequency,
        target_value=habit_create.target_value,
        target_unit=habit_create.target_unit,
        preferred_time=habit_create.preferred_time,
        reminder_enabled=habit_create.reminder_enabled,
        reminder_time=habit_create.reminder_time,
        user_id=current_user.id,
        is_active=True,
    )

    db.add(habit)
    db.commit()
    db.refresh(habit)

    logger.info(
        "Habit created",
        user_id=current_user.id,
        habit_id=habit.id,
        habit_name=habit.name,
    )

    return habit


@router.get("/{habit_id}", response_model=HabitInDB)
async def get_habit(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定习惯详情"""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logger.info("Habit retrieved", user_id=current_user.id, habit_id=habit_id)

    return habit


@router.put("/{habit_id}", response_model=HabitInDB)
async def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新习惯"""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # 更新允许的字段
    update_data = habit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(habit, field, value)

    db.commit()
    db.refresh(habit)

    logger.info("Habit updated", user_id=current_user.id, habit_id=habit_id)

    return habit


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除习惯"""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    db.delete(habit)
    db.commit()

    logger.info("Habit deleted", user_id=current_user.id, habit_id=habit_id)

    return {"message": "Habit deleted successfully"}


@router.get("/{habit_id}/completions", response_model=List[HabitCompletionInDB])
async def get_habit_completions(
    habit_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯完成记录"""
    # 验证习惯属于当前用户
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # 查询完成记录
    query = db.query(HabitCompletion).filter(HabitCompletion.habit_id == habit_id)

    if start_date:
        query = query.filter(func.date(HabitCompletion.completion_date) >= start_date)
    if end_date:
        query = query.filter(func.date(HabitCompletion.completion_date) <= end_date)

    completions = query.order_by(HabitCompletion.completion_date.desc()).all()

    logger.info(
        "Habit completions retrieved",
        user_id=current_user.id,
        habit_id=habit_id,
        completion_count=len(completions),
    )

    return completions


@router.post("/{habit_id}/complete", response_model=HabitCompletionInDB)
async def complete_habit(
    habit_id: int,
    completion_data: HabitCompletionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """标记习惯完成"""
    # 验证习惯是否存在并属于当前用户
    habit = (
        db.query(Habit)
        .filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id,
            Habit.is_active == True,
        )
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Active habit not found")

    # 检查今天是否已经完成
    today_start = datetime.combine(
        completion_data.completion_date.date(), datetime.min.time()
    )
    today_end = datetime.combine(
        completion_data.completion_date.date() + timedelta(days=1), datetime.min.time()
    )

    existing_completion = (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date >= today_start,
            HabitCompletion.completion_date < today_end,
        )
        .first()
    )

    if existing_completion:
        raise HTTPException(status_code=400, detail="Habit already completed today")

    # 创建完成记录
    completion = HabitCompletion(
        habit_id=habit_id,
        completion_date=completion_data.completion_date,
        actual_value=completion_data.actual_value,
        notes=completion_data.notes,
        mood_rating=completion_data.mood_rating,
        difficulty_rating=completion_data.difficulty_rating,
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    logger.info(
        "Habit completed",
        user_id=current_user.id,
        habit_id=habit_id,
        completion_date=completion_data.completion_date,
    )

    return completion


@router.delete("/{habit_id}/completion/{completion_id}")
async def delete_completion(
    habit_id: int,
    completion_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除特定的完成记录"""
    # 验证习惯和完成记录归属
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    completion = (
        db.query(HabitCompletion)
        .join(Habit)
        .filter(HabitCompletion.id == completion_id, Habit.user_id == current_user.id)
        .first()
    )

    if not completion:
        raise HTTPException(status_code=404, detail="Completion not found")

    db.delete(completion)
    db.commit()

    logger.info(
        "Habit completion removed",
        user_id=current_user.id,
        habit_id=habit_id,
        completion_id=completion_id,
    )

    return {"message": "Completion removed successfully"}


@router.get("/statistics", response_model=HabitStats)
async def get_habit_statistics(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户习惯统计数据"""
    from collections import defaultdict

    # Total habits
    total_habits_query = db.query(Habit).filter(Habit.user_id == current_user.id)
    total_habits = total_habits_query.count()

    # Active habits
    active_habits_query = db.query(Habit).filter(
        Habit.user_id == current_user.id, Habit.is_active == True
    )
    active_habits = active_habits_query.count()

    # Total completions
    total_completions = (
        db.query(HabitCompletion)
        .join(Habit)
        .filter(Habit.user_id == current_user.id)
        .count()
    )

    # Category statistics
    category_stats = (
        db.query(Habit.category, func.count(Habit.id))
        .filter(Habit.user_id == current_user.id)
        .group_by(Habit.category)
        .all()
    )

    category_counts = {}
    for category, count in category_stats:
        category_counts[category.value] = count

    # Weekly completions for the past 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=6)  # 7 days including today
    week_start = seven_days_ago.date()

    weekly_completions_raw = (
        db.query(
            func.date(HabitCompletion.completion_date).label("date"),
            func.count(HabitCompletion.id).label("completions"),
        )
        .join(Habit)
        .filter(
            Habit.user_id == current_user.id,
            func.date(HabitCompletion.completion_date) >= week_start,
        )
        .group_by(func.date(HabitCompletion.completion_date))
        .order_by(func.date(HabitCompletion.completion_date))
        .all()
    )

    # Create a map of date to completion count
    daily_completions_map = {row[0]: row[1] for row in weekly_completions_raw}

    # Generate last 7 days data ensuring all dates appear
    weekly_completions = []
    for i in range(7):
        check_date = (datetime.utcnow() - timedelta(days=i)).date()
        weekly_completions.append(daily_completions_map.get(check_date, 0))
    weekly_completions.reverse()  # Oldest to newest

    # Completion rate calculation - for simplicity, calculating based on active habits this week
    recent_completions = (
        db.query(
            Habit.name,
            func.date(HabitCompletion.completion_date).label("date"),
            func.count(HabitCompletion.id).label("count"),
        )
        .join(HabitCompletion, Habit.id == HabitCompletion.habit_id)
        .filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True,
            func.date(HabitCompletion.completion_date) >= week_start,
        )
        .group_by(Habit.name, func.date(HabitCompletion.completion_date))
        .subquery()
    )

    # Calculate total possible completions based on habit frequency
    active_habits_data = active_habits_query.all()
    possible_completions = 0
    for habit in active_habits_data:
        # Calculate based on habit frequency and date range
        if habit.frequency == HabitFrequency.DAILY:
            days_since_creation = (
                min((datetime.utcnow().date() - habit.created_at.date()).days, 7) + 1
            )
            possible_completions += days_since_creation
        elif habit.frequency == HabitFrequency.WEEKLY:
            possible_completions += 1  # One weekly habit attempt possible each week
        else:  # Monthly
            possible_completions += (
                1  # One monthly habit attempt per month (simplified)
            )

    completion_rate = (
        (total_completions / possible_completions * 100)
        if possible_completions > 0
        else 0
    )

    # Create response statistics
    stats = HabitStats(  # Fixed: Was HabitStatistics
        total_habits=total_habits,
        active_habits=active_habits,
        total_completions=total_completions,
        current_streak=0,  # Placeholder, would need actual calculation
        completion_rate=min(completion_rate, 100.0),  # Cap at 100%
        category_stats=category_counts,
        weekly_completions=weekly_completions,
    )

    logger.info(
        "Habit Statistics retrieved",
        user_id=current_user.id,
        total_habits=total_habits,
        active_habits=active_habits,
        total_completions=total_completions,
    )

    return stats


@router.get("/{habit_id}/streak-info", response_model=StreakInfo)
async def get_habit_streak_info(
    habit_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取习惯的连续打卡信息"""
    # 验证习惯归属
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # 获取该习惯的完成记录
    completions = (
        db.query(HabitCompletion)
        .filter(HabitCompletion.habit_id == habit_id)
        .order_by(HabitCompletion.completion_date.asc())
        .all()
    )

    # Calculate current streak
    current_streak = 0
    longest_streak = 0
    streak_start_date = None
    last_completion_date = None

    if completions:
        # Convert all completions to just date portion and create a set
        from collections import defaultdict

        daily_completions = defaultdict(int)
        for comp in completions:
            comp_date = comp.completion_date.date()
            daily_completions[comp_date] += (
                1  # Count how many times a habit was completed on a day (for cases where user completes habit multiple times a day)
            )

        # Create array of completion dates to calculate streaks
        if daily_completions:
            dates = sorted(daily_completions.keys(), reverse=True)

            # Determine streak information
            if dates:
                # Check if today's date is one of the completion dates
                today = datetime.now().date()
                if dates[0] == today:
                    # If user completed today, start with current streak = 1
                    current_streak = 1

                    # Count backwards day-by-day
                    current_date = today
                    for i in range(1, len(dates)):
                        check_date = current_date - timedelta(days=i)
                        if check_date in daily_completions:
                            current_streak += 1
                        else:
                            break  # Broken streak

                # Find the longest streak among all dates
                if dates:
                    # Iterate through the dates to find the longest consecutive streak
                    consecutive_days = 1
                    temp_longest_streak = 1

                    for i in range(
                        1, len(dates)
                    ):  # Skip first as we start counting from second
                        prev_date = dates[i - 1]
                        curr_date = dates[i]

                        if (prev_date - curr_date).days == 1:  # Consecutive days
                            consecutive_days += 1
                        else:  # Gap between dates
                            temp_longest_streak = max(
                                temp_longest_streak, consecutive_days
                            )
                            consecutive_days = 1  # Reset current streak counter

                    # Update max considering the last sequence
                    longest_streak = max(temp_longest_streak, consecutive_days)

                    # Set last completion date
                    last_completion_date = dates[
                        0
                    ]  # First in reversed list is the most recent date

            # Calculate streak start date
            if current_streak > 0 and last_completion_date:
                # Calculate start date based on current streak length
                streak_start_date = last_completion_date - timedelta(
                    days=current_streak - 1
                )

    streak_info = StreakInfo(
        current_streak=current_streak,
        longest_streak=longest_streak,
        streak_start_date=streak_start_date,
        last_completion_date=last_completion_date,
        is_streak_active=(current_streak > 0),
    )

    logger.info(
        "Habit streak info retrieved",
        user_id=current_user.id,
        habit_id=habit_id,
        current_streak=current_streak,
        longest_streak=longest_streak,
    )

    return streak_info


@router.get("/daily-checklist", response_model=DailyHabitChecklist)
async def get_daily_habit_checklist(
    target_date: date = Query(None, description="目标日期，默认为 today"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取每日习惯清单"""
    if target_date is None:
        target_date = datetime.utcnow().date()

    # Get all active habits for user
    active_habits = (
        db.query(Habit)
        .filter(Habit.user_id == current_user.id, Habit.is_active == True)
        .all()
    )

    # Get any completions for today
    today_start = datetime.combine(target_date, datetime.min.time())
    today_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    completed_ids = set()
    todays_completions = (
        db.query(HabitCompletion)
        .join(Habit)
        .filter(
            Habit.user_id == current_user.id,
            HabitCompletion.completion_date >= today_start,
            HabitCompletion.completion_date < today_end,
        )
        .all()
    )

    for comp in todays_completions:
        completed_ids.add(comp.habit_id)

    # Build habit checklist
    habits_list = []
    total_count = len(active_habits)
    completed_count = 0

    for habit in active_habits:
        is_completed = habit.id in completed_ids
        if is_completed:
            completed_count += 1

        habits_list.append(
            {
                "id": habit.id,
                "name": habit.name,
                "description": habit.description,
                "category": habit.category.value,
                "target_value": habit.target_value,
                "target_unit": habit.target_unit,
                "completed": is_completed,
            }
        )

    checklist = DailyHabitChecklist(
        date=target_date.isoformat(),
        habits=habits_list,
        completed_count=completed_count,
        total_count=total_count,
        completion_percentage=round(
            (completed_count / total_count * 100) if total_count > 0 else 0, 2
        ),
    )

    logger.info(
        "Daily habit checklist retrieved",
        user_id=current_user.id,
        date=target_date,
        total=total_count,
        completed=completed_count,
    )

    return checklist


# Habit Templates / Recommendations
@router.get("/templates")
async def get_habit_templates():
    """获取习惯模板列表"""
    templates = [
        {
            "name": "每日喝水8杯",
            "category": "hydration",
            "frequency": "daily",
            "target_value": 8,
            "target_unit": "cups",
            "description": "保持身体水分平衡，促进新陈代谢",
        },
        {
            "name": "每周运动3次",
            "category": "exercise",
            "frequency": "weekly",
            "target_value": 3,
            "target_unit": "times",
            "description": "增强体质，提高免疫力",
        },
        {
            "name": "每晚10点前入睡",
            "category": "sleep",
            "frequency": "daily",
            "description": "保证充足睡眠，促进身体恢复",
        },
        {
            "name": "每日冥想10分钟",
            "category": "mental_health",
            "frequency": "daily",
            "target_value": 10,
            "target_unit": "minutes",
            "description": "减轻压力，提高专注力",
        },
        {
            "name": "每天吃早餐",
            "category": "diet",
            "frequency": "daily",
            "description": "均衡营养摄入，开启活力一天",
        },
        {
            "name": "每日步行10000步",
            "category": "exercise",
            "frequency": "daily",
            "target_value": 10000,
            "target_unit": "steps",
            "description": "保持活力，促进心血管健康",
        },
    ]
    return templates
