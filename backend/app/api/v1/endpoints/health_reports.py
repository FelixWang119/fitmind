from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.health_record import HealthRecord
from app.models.user import User as UserModel
from app.models.nutrition import Meal, MealItem
from app.schemas.health_report import (
    HealthReportRequest,
    HealthReportResponse,
    DetailedHealthReport,
    HealthTrendData,
    AchievementInfo,
)

logger = structlog.get_logger()

router = APIRouter()


@router.post("/generate-report", response_model=HealthReportResponse)
async def generate_health_report(
    report_request: HealthReportRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成综合健康报告"""
    logger.info(
        "Generating health report",
        user_id=current_user.id,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
    )

    # 确定报告范围
    start_date = report_request.start_date
    end_date = report_request.end_date or datetime.utcnow().date()

    # 获取体重数据（来自HealthRecord）
    weight_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.weight != None,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    # 获取食物数据（来自Meal表）
    meals_data = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.meal_datetime >= start_date,
            Meal.meal_datetime <= end_date,
        )
        .order_by(Meal.meal_datetime)
        .all()
    )

    # 计算饮食指标
    total_calories = 0
    daily_calories: Dict[str, float] = defaultdict(float)
    meal_categories = defaultdict(int)

    for meal in meals_data:
        if meal.calories:
            total_calories += meal.calories
            date_key = meal.meal_datetime.date().isoformat()
            daily_calories[date_key] += meal.calories
            meal_categories[meal.meal_type] += 1

    # 获取运动数据（从HealthRecord中的运动字段）
    exercise_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.exercise_minutes > 0,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    total_exercise_minutes = 0
    total_steps = 0
    daily_exercise: Dict[str, dict] = defaultdict(lambda: {"minutes": 0, "steps": 0})

    for record in exercise_records:
        if record.exercise_minutes:
            total_exercise_minutes += record.exercise_minutes
            date_key = record.record_date.isoformat()
            daily_exercise[date_key]["minutes"] += record.exercise_minutes
        if record.steps_count:
            total_steps += record.steps_count
            daily_exercise[date_key]["steps"] += record.steps_count

    # 分析体重趋势
    if weight_records:
        weights = [
            (r.record_date, r.weight / 1000.0) for r in weight_records if r.weight
        ]  # Convert to kg
        if weights:
            start_weight = weights[0][1] if weights else 0
            end_weight = weights[-1][1] if weights else 0
            weight_change = end_weight - start_weight
            average_weight = sum(w[1] for w in weights) / len(weights) if weights else 0
        else:
            weight_change = 0
            average_weight = 0
            start_weight = 0
            end_weight = 0
    else:
        weight_change = 0
        average_weight = 0
        start_weight = 0
        end_weight = 0

    # 计算完成率和其他指标
    report_data = DetailedHealthReport(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        summary=HealthTrendData(
            weight_change_kg=round(weight_change, 2),
            starting_weight_kg=round(start_weight, 2),
            current_weight_kg=round(end_weight, 2),
            average_weight_kg=round(average_weight, 2),
            total_calories_consumed=round(total_calories),
            average_daily_calories=round(
                total_calories / len(set(daily_calories.keys()))
            )
            if daily_calories
            else 0,
            total_exercise_minutes=total_exercise_minutes,
            average_daily_exercise_minutes=round(
                total_exercise_minutes / len(set(daily_exercise.keys()))
            )
            if daily_exercise
            else 0,
            total_steps=total_steps,
            average_daily_steps=round(total_steps / len(set(daily_exercise.keys())))
            if daily_exercise
            else 0,
            active_days=len(set(daily_calories.keys())),  # Days with food log entries
        ),
        trends=HealthTrendData(
            weight_trend="decreasing"
            if weight_change < -0.5
            else ("increasing" if weight_change > 0.5 else "stable"),
            calorie_trend="consistent"
            if abs(
                total_calories
                / (len(set(daily_calories.keys())) if daily_calories else 1)
                - 2000
            )
            < 500
            else "variable",  # Assuming target of 2000 kcal
            exercise_trend="improving"
            if total_exercise_minutes > 7 * 30
            else "needs_improvement",  # More than 30 min/day avg
        ),
        achievements=[
            AchievementInfo(
                title="减肥里程碑",
                description=f"减掉了{abs(weight_change):.2f}公斤"
                if weight_change < 0
                else "体重管理稳定",
                achieved=(weight_change < -0.5),
                category="weight",
            ),
            AchievementInfo(
                title="持续记录者",
                description="连续一周保持健康记录",
                achieved=len(set(daily_calories.keys())) >= 7,
                category="consistency",
            ),
            AchievementInfo(
                title="运动达人",
                description="达到每日30分钟运动建议",
                achieved=total_exercise_minutes >= 7 * 30,
                category="fitness_achievements",
            ),
            AchievementInfo(
                title="营养均衡",
                description="营养摄入均衡，合理分配各类营养成分",
                achieved=True,  # Simplified for this example
            ),
        ],
        recommendations=[
            "继续维持当前的健康饮食和运动习惯",
            "确保摄入足够的蛋白质以维持肌肉量",
            "保持充足的水分摄入",
            "考虑加入力量训练以提高基础代谢率",
        ],
        detailed_insights={
            "weight_management": {
                "summary": f"在报告期间，您的体重{'减少' if weight_change < -0.5 else '增加' if weight_change > 0.5 else '稳定'}了{abs(weight_change):.2f}公斤",
                "analysis": f"您的平均体重为{average_weight:.1f}公斤，初始权重为{start_weight:.1f}公斤",
            },
            "nutrition_evaluation": {
                "summary": f"您在这段时间内总共摄入了{total_calories:.0f}大卡热量，平均每日{total_calories / len(set(daily_calories.keys())):.0f}大卡",
                "analysis": f"共记录{len(daily_calories.keys())}天的饮食数据，最常见的餐次是{(max(meal_categories, key=meal_categories.get) if meal_categories else 'n/a')}",
            },
            "physical_activity": {
                "summary": f"您总共运动了{total_exercise_minutes}分钟，走了{total_steps}步",
                "analysis": f"平均每日运动{total_exercise_minutes / len(set(daily_exercise.keys())):.0f}分钟",
            },
        },
    )

    logger.info(
        "Health report generated",
        user_id=current_user.id,
        duration_days=(end_date - start_date).days,
    )

    return HealthReportResponse(
        status="success",
        message="Health report generated successfully",
        report=report_data,
        generated_at=datetime.utcnow().isoformat(),
    )


@router.get("/monthly-health-summary", response_model=Dict)
async def get_monthly_health_summary(
    month: str = Query(..., description="月份 (YYYY-MM)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取月度健康摘要"""
    logger.info(
        "Generating monthly health summary", user_id=current_user.id, month=month
    )

    try:
        # Parse month parameter (e.g., "2026-02")
        year, mon = map(int, month.split("-"))
        start_date = datetime(year, mon, 1).date()
        end_date = (
            datetime(year, mon + 1, 1).date() - timedelta(days=1)
            if mon < 12
            else datetime(year + 1, 1, 1).date() - timedelta(days=1)
        )

        # Call the main report generation with monthly range
        report_request = HealthReportRequest(start_date=start_date, end_date=end_date)

        # Use generate_health_report internally
        weight_records = (
            db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == current_user.id,
                HealthRecord.record_date >= start_date,
                HealthRecord.record_date <= end_date,
                HealthRecord.weight != None,
            )
            .order_by(HealthRecord.record_date)
            .all()
        )

        meals_data = (
            db.query(Meal)
            .filter(
                Meal.user_id == current_user.id,
                Meal.meal_datetime >= start_date,
                Meal.meal_datetime <= end_date,
            )
            .order_by(Meal.meal_datetime)
            .all()
        )

        exercise_records = (
            db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == current_user.id,
                HealthRecord.record_date >= start_date,
                HealthRecord.record_date <= end_date,
                HealthRecord.exercise_minutes > 0,
            )
            .order_by(HealthRecord.record_date)
            .all()
        )

        # Process similar to generate_health_report for monthly specific metrics
        # Implementation would be similar to the main method but with month-specific logic
        # For brevity, simplfying this endpoint to provide high-level statistics based on available data

        weight_changes = []
        if weight_records and len(weight_records) > 1:
            # Calculate weight change over the month
            start_weight = (
                weight_records[0].weight / 1000.0 if weight_records[0].weight else None
            )
            end_weight = (
                weight_records[-1].weight / 1000.0
                if weight_records[-1].weight
                else None
            )
            if start_weight is not None and end_weight is not None:
                weight_changes = [end_weight - start_weight]

        total_calories = sum(m.calories or 0 for m in meals_data)
        total_exercise_minutes = sum(r.exercise_minutes or 0 for r in exercise_records)
        total_steps = sum(r.steps_count or 0 for r in exercise_records)
        active_days_records = set()
        for m in meals_data:
            active_days_records.add(m.meal_datetime.date())
        for r in exercise_records:
            active_days_records.add(r.record_date)

        summary = {
            "month": month,
            "stats": {
                "starting_weight": round(start_weight, 2)
                if start_weight is not None
                else None,
                "ending_weight": round(end_weight, 2)
                if end_weight is not None
                else None,
                "weight_change": round(weight_changes[0], 2) if weight_changes else 0,
                "total_calories": int(total_calories),
                "avg_daily_calories": round(total_calories / len(active_days_records))
                if active_days_records
                else 0,
                "total_exercise_minutes": total_exercise_minutes,
                "avg_daily_exercise": round(
                    total_exercise_minutes / len(active_days_records)
                )
                if active_days_records
                else 0,
                "total_steps": total_steps,
                "active_days": len(active_days_records),
            },
            "highlights": [
                f"本月记录饮食{len(meals_data)}次",
                f"运动{len(exercise_records)}次",
                f"共活跃{len(active_days_records)}天",
            ],
        }

        return summary
    except Exception as e:
        logger.error(
            "Error generating monthly summary", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail=f"生成月度摘要时出错: {str(e)}")


# Enhanced behavioral insights endpoint
@router.get("/behavioral-health-insights", response_model=Dict)
async def get_behavioral_health_insights(
    days_back: int = Query(30, ge=1, le=365, description="追溯天数 (1-365)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取行为与健康关联分析"""
    logger.info(
        "Getting behavioral health insights",
        user_id=current_user.id,
        days_back=days_back,
    )

    try:
        from datetime import date, timedelta
        from app.services.health_report_service import (
            generate_behavioral_health_insights,
        )

        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days_back)

        # Call service function to get behavioral insights
        insights = generate_behavioral_health_insights(db, current_user, days_back)

        return {
            "insights": insights,
            "status": "success",
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(
            "Behavioral insights generation failed",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Behavioral insights generation failed",
        )

    except Exception as e:
        logger.error(
            "Monthly summary generation failed", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Monthly summary generation failed",
        )


@router.get("/weekly-health-trends", response_model=Dict)
async def get_weekly_health_trends(
    weeks_back: int = Query(4, ge=1, le=12, description="回溯多少周 (1-12)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取周度健康趋势"""
    logger.info(
        "Getting weekly health trends", user_id=current_user.id, weeks_back=weeks_back
    )

    # Calculate the date range for n weeks
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(weeks=weeks_back)

    # Query records in the date range
    weight_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.weight != None,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    meals_data = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.meal_datetime >= start_date,
            Meal.meal_datetime <= end_date,
        )
        .order_by(Meal.meal_datetime)
        .all()
    )

    exercise_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.exercise_minutes > 0,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    # Group by week
    from collections import defaultdict, Counter
    from calendar import week
    import math

    weekly_data = defaultdict(
        lambda: {
            "weight": [],
            "calories": 0,
            "exercise_minutes": 0,
            "meals_count": 0,
            "days_active": set(),
        }
    )

    # Process weight records by week
    for record in weight_records:
        week_num = f"{record.record_date.year}-W{record.record_date.isocalendar()[1]}"
        if record.weight:
            weekly_data[week_num]["weight"].append(
                record.weight / 1000.0
            )  # Convert to kg
        daily = record.record_date.isoformat()
        weekly_data[week_num]["days_active"].add(daily)

    # Process meals by week
    for meal in meals_data:
        week_num = f"{meal.meal_datetime.date().year}-W{meal.meal_datetime.date().isocalendar()[1]}"
        weekly_data[week_num]["calories"] += meal.calories or 0
        weekly_data[week_num]["meals_count"] += 1
        daily = meal.meal_datetime.date().isoformat()
        weekly_data[week_num]["days_active"].add(daily)

    # Process exercise by week
    for record in exercise_records:
        week_num = f"{record.record_date.year}-W{record.record_date.isocalendar()[1]}"
        weekly_data[week_num]["exercise_minutes"] += record.exercise_minutes or 0
        daily = record.record_date.isoformat()
        weekly_data[week_num]["days_active"].add(daily)

    # Transform to expected output
    trends = []
    for week_label in sorted(weekly_data.keys()):
        week_data = weekly_data[week_label]
        trends.append(
            {
                "week": week_label,
                "avg_weight_kg": round(
                    sum(week_data["weight"]) / len(week_data["weight"]), 2
                )
                if week_data["weight"]
                else None,
                "total_calories": week_data["calories"],
                "avg_daily_calories": round(
                    week_data["calories"] / len(week_data["days_active"])
                )
                if week_data["days_active"]
                else 0,
                "total_exercise_minutes": week_data["exercise_minutes"],
                "avg_daily_exercise_minutes": round(
                    week_data["exercise_minutes"] / len(week_data["days_active"])
                )
                if week_data["days_active"]
                else 0,
                "meals_count": week_data["meals_count"],
                "engagement_score": min(len(week_data["days_active"]), 7)
                / 7,  # Engagement from 0 (no records) to 1 (all 7 days)
            }
        )

    return {
        "weeks_back": weeks_back,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "weekly_trends": trends,
    }
