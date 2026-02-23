from datetime import datetime, date
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.health_record import HealthRecord
from app.models.user import User as UserModel
from app.schemas.exercise import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSession,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/exercise-sessions", response_model=List[WorkoutSession])
async def get_exercise_sessions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户的运动会话记录列表"""
    # 在健康记录中找到运动相关数据
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)

    # 日期过滤
    if start_date:
        query = query.filter(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.filter(HealthRecord.record_date <= end_date)

    # 查找包含运动数据的记录
    records_with_exercise = (
        query.filter(
            (HealthRecord.exercise_minutes != None)
            | (HealthRecord.exercise_type != None)
            | (HealthRecord.steps_count != None)
        )
        .order_by(HealthRecord.record_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 将装成运动会话模型
    sessions = []
    for record in records_with_exercise:
        session = WorkoutSession(
            id=record.id,  # Use HealthRecord ID as session ID
            user_id=record.user_id,
            date=record.record_date,
            exercise_type=record.exercise_type or "General Activity",
            duration_minutes=record.exercise_minutes or 0,
            steps_count=record.steps_count or 0,
            calories_burned=record.calories_intake
            if record.calories_intake
            else None,  # Calories burned if available
            notes=record.notes,
            created_at=record.created_at,
        )
        sessions.append(session)

    return sessions


@router.get("/exercise-sessions/{session_id}", response_model=WorkoutSession)
async def get_exercise_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定的运动会话记录"""
    # Find in health records that matches the session_id
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == session_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise session not found"
        )

    if (
        not record.exercise_type
        and not record.exercise_minutes
        and not record.steps_count
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record does not contain exercise data",
        )

    session = WorkoutSession(
        id=record.id,
        user_id=record.user_id,
        date=record.record_date,
        exercise_type=record.exercise_type or "General Activity",
        duration_minutes=record.exercise_minutes or 0,
        steps_count=record.steps_count or 0,
        calories_burned=record.calories_intake if record.calories_intake else None,
        notes=record.notes,
        created_at=record.created_at,
    )

    return session


@router.post(
    "/exercise-sessions",
    response_model=WorkoutSession,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise_session(
    session_data: WorkoutSessionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建运动会话记录"""
    # 使用 HealthRecord 模型存储运动数据
    new_record = HealthRecord(
        user_id=current_user.id,
        exercise_type=session_data.exercise_type,
        exercise_minutes=session_data.duration_minutes,
        steps_count=session_data.steps_count,
        # 计算大概卡路里燃烧，基于运动类型和时长
        calories_intake=session_data.calories_burned,  # Store as intake (negative balance)
        # 用备注字段存储额外信息
        notes=session_data.notes,
        # 设置记录日期为运动日期
        record_date=session_data.date,
        # 设置时间
        created_at=datetime.utcnow(),
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # 返回封装的会话对象
    session = WorkoutSession(
        id=new_record.id,
        user_id=new_record.user_id,
        date=new_record.record_date.isoformat() if new_record.record_date else None,
        exercise_type=new_record.exercise_type or "General Activity",
        duration_minutes=new_record.exercise_minutes or 0,
        steps_count=new_record.steps_count or 0,
        calories_burned=new_record.calories_intake,
        notes=new_record.notes,
        created_at=new_record.created_at.isoformat() if new_record.created_at else None,
    )

    logger.info(
        "Exercise session created",
        session_id=new_record.id,
        user_id=current_user.id,
        exercise_type=new_record.exercise_type,
        duration_minutes=new_record.exercise_minutes,
    )

    return session


@router.put("/exercise-sessions/{session_id}", response_model=WorkoutSession)
async def update_exercise_session(
    session_id: int,
    session_update: WorkoutSessionUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新运动会话记录"""
    # 获取健康记录
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == session_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise session not found"
        )

    # 更新字段
    update_fields = [
        "exercise_type",
        "exercise_minutes",
        "steps_count",
        "calories_intake",
        "notes",
    ]
    for field in update_fields:
        field_val = getattr(
            session_update, field.replace("calories_intake", "calories_burned")
        )
        if field_val is not None:
            # Special mapping for calories field
            if field == "calories_intake":
                setattr(record, field, session_update.calories_burned)
            else:
                setattr(record, field, field_val)

    db.commit()
    db.refresh(record)

    session = WorkoutSession(
        id=record.id,
        user_id=record.user_id,
        date=record.record_date,
        exercise_type=record.exercise_type or "General Activity",
        duration_minutes=record.exercise_minutes or 0,
        steps_count=record.steps_count or 0,
        calories_burned=record.calories_intake,
        notes=record.notes,
        created_at=record.created_at,
    )

    logger.info(
        "Exercise session updated", session_id=record.id, user_id=current_user.id
    )

    return session


@router.delete(
    "/exercise-sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除运动会话记录"""
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == session_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise session not found"
        )

    db.delete(record)
    db.commit()

    logger.info(
        "Exercise session deleted", session_id=session_id, user_id=current_user.id
    )


@router.get("/exercise-types", response_model=List[str])
async def get_exercise_types(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取运动类型列表（从用户数据中提取）"""
    # 从用户的运动数据中提取不重复的运动类型
    exercise_types = (
        db.query(HealthRecord.exercise_type)
        .filter(
            HealthRecord.user_id == current_user.id, HealthRecord.exercise_type != None
        )
        .distinct()
        .all()
    )

    types = [etype[0] for etype in exercise_types if etype[0]]
    # 默认选项
    defaults = [
        "Running",
        "Walking",
        "Cycling",
        "Swimming",
        "Strength Training",
        "Yoga",
        "Other",
    ]

    # 合并用户特定类型和默认类型
    all_types = list(set(types + defaults))

    return all_types


@router.get("/daily-exercise-summary", response_model=List[dict])
async def get_daily_exercise_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取日常运动摘要"""
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)

    # 日期过滤
    if start_date:
        query = query.filter(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.filter(HealthRecord.record_date <= end_date)

    # 查询包含运动数据的记录
    exercise_records = (
        query.filter(
            (HealthRecord.exercise_minutes != None) | (HealthRecord.steps_count != None)
        )
        .order_by(HealthRecord.record_date.desc())
        .all()
    )

    # 按日期聚合数据
    summary = {}
    for record in exercise_records:
        date_str = record.record_date.isoformat()
        if date_str not in summary:
            summary[date_str] = {
                "date": date_str,
                "total_duration": 0,
                "total_steps": 0,
                "total_calories": 0,
                "exercise_types": [],
                "sessions_count": 0,
            }

        session_data = {
            "duration": record.exercise_minutes or 0,
            "type": record.exercise_type or "Activity",
            "steps": record.steps_count or 0,
            "calories": record.calories_intake or 0,
        }

        summary[date_str]["total_duration"] += session_data["duration"]
        summary[date_str]["total_steps"] += session_data["steps"]
        summary[date_str]["total_calories"] += session_data["calories"]

        if session_data["type"] not in summary[date_str]["exercise_types"]:
            summary[date_str]["exercise_types"].append(session_data["type"])

        summary[date_str]["sessions_count"] += 1

    # 转换为列表并按日期排序
    summary_list = list(summary.values())
    summary_list.sort(key=lambda x: x["date"], reverse=True)

    return summary_list
