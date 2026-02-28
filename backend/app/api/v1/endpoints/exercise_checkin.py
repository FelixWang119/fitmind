from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.exercise_checkin import ExerciseCheckIn
from app.models.user import User as UserModel
from app.schemas.exercise_checkin import (
    DailySummaryResponse,
    ExerciseCheckInCreate,
    ExerciseCheckInResponse,
    ExerciseCheckInUpdate,
    ExerciseTypeResponse,
)
from app.services.exercise_calorie_service import get_exercise_calorie_service

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/",
    response_model=ExerciseCheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise_checkin(
    checkin_data: ExerciseCheckInCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    创建运动打卡记录

    - 自动估算卡路里燃烧
    - 使用用户体重数据 (如果缺失使用默认值)
    """
    calorie_service = get_exercise_calorie_service(db)

    # 获取用户体重
    weight_kg = calorie_service.get_user_weight_kg(current_user.id)

    # 估算卡路里
    calorie_result = calorie_service.estimate_calories(
        exercise_type=checkin_data.exercise_type,
        duration_minutes=checkin_data.duration_minutes,
        intensity=checkin_data.intensity,
        weight_kg=weight_kg,
    )

    # 创建打卡记录
    db_checkin = ExerciseCheckIn(
        user_id=current_user.id,
        exercise_type=checkin_data.exercise_type,
        category=checkin_data.category,
        duration_minutes=checkin_data.duration_minutes,
        intensity=checkin_data.intensity,
        distance_km=checkin_data.distance_km,
        heart_rate_avg=checkin_data.heart_rate_avg,
        notes=checkin_data.notes,
        rating=checkin_data.rating,
        calories_burned=calorie_result["calories_burned"],
        is_estimated=calorie_result["is_estimated"],
        started_at=(
            datetime.fromisoformat(checkin_data.started_at)
            if checkin_data.started_at
            else datetime.utcnow()
        ),
    )

    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)

    logger.info(
        "Exercise checkin created",
        checkin_id=db_checkin.id,
        user_id=current_user.id,
        exercise_type=db_checkin.exercise_type,
        calories_burned=db_checkin.calories_burned,
    )

    # 添加到短期记忆队列
    try:
        from app.services.short_term_memory import get_short_term_memory_service

        content = f"进行了{db_checkin.exercise_type}运动"
        if db_checkin.duration_minutes:
            content += f"时长{db_checkin.duration_minutes}分钟"
        if db_checkin.calories_burned:
            content += f"，消耗{db_checkin.calories_burned}千卡"

        get_short_term_memory_service().add_memory(
            user_id=current_user.id,
            event_type="exercise",
            event_source=db_checkin.exercise_type,
            content=content,
            metrics={
                "duration": db_checkin.duration_minutes,
                "calories": db_checkin.calories_burned,
                "distance": db_checkin.distance_km,
                "heart_rate": db_checkin.heart_rate_avg,
            },
            context={
                "category": db_checkin.category,
                "intensity": db_checkin.intensity,
            },
            source_table="exercise_checkins",
            source_id=db_checkin.id,
        )
        logger.info(f"运动打卡已添加到短期记忆队列: {db_checkin.id}")
    except Exception as e:
        logger.error(f"添加运动打卡到短期记忆失败: {e}")

    # ===== Story 4.2: 更新运动成就 =====
    try:
        from app.services.gamification_service import get_gamification_service

        gamification_service = get_gamification_service(db)

        # 处理运动成就
        duration_minutes = db_checkin.duration_minutes or 0
        distance_meters = int((db_checkin.distance_km or 0) * 1000)  # 转换为米

        gamification_service.process_exercise_checkin_achievements(
            user=current_user,
            exercise_type=db_checkin.exercise_type,
            duration_minutes=duration_minutes,
            distance_meters=distance_meters,
        )

        logger.info("Exercise achievements updated", user_id=current_user.id)
    except Exception as e:
        logger.error(f"更新运动成就失败：{e}")
        # 不阻塞运动打卡流程

    # 构建响应 (包含估算详情)
    response = ExerciseCheckInResponse.model_validate(db_checkin)
    response.estimation_details = calorie_result["estimation_details"]

    return response


@router.get("/", response_model=List[ExerciseCheckInResponse])
def get_exercise_checkins(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(None, description="开始日期 (ISO 8601)"),
    end_date: Optional[str] = Query(None, description="结束日期 (ISO 8601)"),
    exercise_type: Optional[str] = Query(None, description="运动类型过滤"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取用户运动打卡列表 (支持分页/过滤)
    """
    # 基础查询
    query = db.query(ExerciseCheckIn).filter(
        ExerciseCheckIn.user_id == current_user.id,
        ExerciseCheckIn.deleted_at.is_(None),  # 软删除过滤
    )

    # 日期过滤
    if start_date:
        query = query.filter(
            ExerciseCheckIn.started_at >= datetime.fromisoformat(start_date)
        )
    if end_date:
        query = query.filter(
            ExerciseCheckIn.started_at <= datetime.fromisoformat(end_date)
        )

    # 运动类型过滤
    if exercise_type:
        query = query.filter(ExerciseCheckIn.exercise_type == exercise_type)

    # 分页
    offset = (page - 1) * limit
    results = (
        query.order_by(ExerciseCheckIn.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    logger.info(
        "Exercise checkins retrieved",
        user_id=current_user.id,
        count=len(results),
        page=page,
    )

    return [ExerciseCheckInResponse.model_validate(checkin) for checkin in results]


@router.get("/daily-summary", response_model=DailySummaryResponse)
def get_daily_summary(
    date: Optional[str] = Query(None, description="日期 (ISO 8601)，默认今天"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取当日运动摘要

    返回总时长、总燃烧卡路里、打卡次数等聚合数据
    """
    from datetime import date as date_type

    # 解析日期
    if date:
        target_date = datetime.fromisoformat(date).date()
    else:
        target_date = datetime.utcnow().date()

    # 日期范围
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    # 聚合查询
    result = (
        db.query(
            func.sum(ExerciseCheckIn.duration_minutes).label("total_duration_minutes"),
            func.sum(ExerciseCheckIn.calories_burned).label("total_calories_burned"),
            func.count(ExerciseCheckIn.id).label("sessions_count"),
            func.avg(ExerciseCheckIn.heart_rate_avg).label("avg_heart_rate"),
        )
        .filter(
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.started_at >= start_datetime,
            ExerciseCheckIn.started_at < end_datetime,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .first()
    )

    # 获取运动类型列表
    types_result = (
        db.query(ExerciseCheckIn.exercise_type)
        .filter(
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.started_at >= start_datetime,
            ExerciseCheckIn.started_at < end_datetime,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    exercise_types = [t[0] for t in types_result]

    total_duration_minutes = result.total_duration_minutes or 0 if result else 0
    total_calories_burned = result.total_calories_burned or 0 if result else 0
    sessions_count = result.sessions_count or 0 if result else 0
    avg_heart_rate = (
        int(result.avg_heart_rate) if result and result.avg_heart_rate else None
    )

    return DailySummaryResponse(
        date=target_date.isoformat(),
        total_duration_minutes=int(total_duration_minutes),
        total_calories_burned=int(total_calories_burned),
        sessions_count=int(sessions_count),
        exercise_types=exercise_types,
        average_heart_rate=avg_heart_rate,
    )


@router.get("/exercise-types", response_model=List[ExerciseTypeResponse])
def get_exercise_types(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取运动类型列表 (包含 MET 值)
    """
    calorie_service = get_exercise_calorie_service(db)
    types = calorie_service.get_exercise_types()

    return [ExerciseTypeResponse(**t) for t in types]


@router.get("/{checkin_id}", response_model=ExerciseCheckInResponse)
def get_exercise_checkin(
    checkin_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取单条运动打卡记录
    """
    checkin = (
        db.query(ExerciseCheckIn)
        .filter(
            ExerciseCheckIn.id == checkin_id,
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .first()
    )

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise checkin not found",
        )

    return ExerciseCheckInResponse.model_validate(checkin)


@router.put("/{checkin_id}", response_model=ExerciseCheckInResponse)
def update_exercise_checkin(
    checkin_id: int,
    checkin_update: ExerciseCheckInUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    全量更新运动打卡记录
    """
    checkin = (
        db.query(ExerciseCheckIn)
        .filter(
            ExerciseCheckIn.id == checkin_id,
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .first()
    )

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise checkin not found",
        )

    # 更新字段
    update_data = checkin_update.model_dump(exclude_unset=True)

    # 如果需要重新计算卡路里
    if any(
        field in update_data
        for field in ["exercise_type", "duration_minutes", "intensity"]
    ):
        calorie_service = get_exercise_calorie_service(db)
        weight_kg = calorie_service.get_user_weight_kg(current_user.id)

        calorie_result = calorie_service.estimate_calories(
            exercise_type=update_data.get("exercise_type", checkin.exercise_type),
            duration_minutes=update_data.get(
                "duration_minutes", checkin.duration_minutes
            ),
            intensity=update_data.get("intensity", checkin.intensity),
            weight_kg=weight_kg,
        )
        update_data["calories_burned"] = calorie_result["calories_burned"]

    for field, value in update_data.items():
        if field == "started_at" and value:
            setattr(checkin, field, datetime.fromisoformat(value))
        else:
            setattr(checkin, field, value)

    db.commit()
    db.refresh(checkin)

    logger.info(
        "Exercise checkin updated",
        checkin_id=checkin_id,
        user_id=current_user.id,
    )

    return ExerciseCheckInResponse.model_validate(checkin)


@router.patch("/{checkin_id}", response_model=ExerciseCheckInResponse)
def patch_exercise_checkin(
    checkin_id: int,
    checkin_update: ExerciseCheckInUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    部分更新运动打卡记录 (F6 新增)
    """
    # 与 PUT 逻辑相同，Pydantic 已处理部分更新
    return update_exercise_checkin(
        checkin_id=checkin_id,
        checkin_update=checkin_update,
        current_user=current_user,
        db=db,
    )


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_checkin(
    checkin_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    删除运动打卡记录 (软删除)
    """
    checkin = (
        db.query(ExerciseCheckIn)
        .filter(
            ExerciseCheckIn.id == checkin_id,
            ExerciseCheckIn.user_id == current_user.id,
            ExerciseCheckIn.deleted_at.is_(None),
        )
        .first()
    )

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise checkin not found",
        )

    # 软删除
    checkin.deleted_at = datetime.utcnow()
    db.commit()

    logger.info(
        "Exercise checkin deleted (soft)",
        checkin_id=checkin_id,
        user_id=current_user.id,
    )
