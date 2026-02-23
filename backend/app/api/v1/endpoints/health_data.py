from datetime import date, datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.health_record import HealthRecord
from app.models.user import User as UserModel
from app.schemas.health import HealthRecord as HealthRecordSchema
from app.schemas.health import HealthRecordCreate, HealthRecordList, HealthRecordUpdate

logger = structlog.get_logger()

router = APIRouter()


@router.get("/records", response_model=HealthRecordList)
async def get_health_records(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康记录列表"""
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)

    # 日期过滤
    if start_date:
        query = query.filter(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.filter(HealthRecord.record_date <= end_date)

    # 获取总数
    total = query.count()

    # 获取记录
    records = (
        query.order_by(desc(HealthRecord.record_date)).offset(skip).limit(limit).all()
    )

    return HealthRecordList(records=records, total=total, skip=skip, limit=limit)


@router.get("/records/{record_id}", response_model=HealthRecordSchema)
async def get_health_record(
    record_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取特定健康记录"""
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == record_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found"
        )

    return record


@router.post(
    "/records", response_model=HealthRecordSchema, status_code=status.HTTP_201_CREATED
)
async def create_health_record(
    record_data: HealthRecordCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建健康记录"""
    # 检查是否已有当天的记录
    existing_record = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date.date() == record_data.record_date.date(),
        )
        .first()
    )

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Health record already exists for this date",
        )

    # 创建记录
    record = HealthRecord(user_id=current_user.id, **record_data.dict())

    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(
        "Health record created",
        record_id=record.id,
        user_id=current_user.id,
        record_date=record.record_date,
    )

    return record


@router.put("/records/{record_id}", response_model=HealthRecordSchema)
async def update_health_record(
    record_id: int,
    record_update: HealthRecordUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新健康记录"""
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == record_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found"
        )

    # 更新字段
    update_data = record_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    logger.info("Health record updated", record_id=record.id, user_id=current_user.id)

    return record


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_record(
    record_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除健康记录"""
    record = (
        db.query(HealthRecord)
        .filter(HealthRecord.id == record_id, HealthRecord.user_id == current_user.id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found"
        )

    db.delete(record)
    db.commit()

    logger.info("Health record deleted", record_id=record_id, user_id=current_user.id)


@router.get("/records/summary")
async def get_health_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康数据摘要"""
    # 获取最近30天的记录
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)

    records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= thirty_days_ago,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    if not records:
        return {"message": "No health records found", "summary": {}}

    # 计算统计数据
    weights = [r.weight for r in records if r.weight]
    blood_sugars = [r.blood_sugar for r in records if r.blood_sugar]
    heart_rates = [r.heart_rate for r in records if r.heart_rate]
    sleep_hours = [r.sleep_hours for r in records if r.sleep_hours]

    def safe_average(values):
        return sum(values) / len(values) if values else None

    summary = {
        "total_records": len(records),
        "date_range": {
            "start": records[0].record_date.date().isoformat(),
            "end": records[-1].record_date.date().isoformat(),
        },
        "averages": {
            "weight": safe_average(weights),
            "blood_sugar": safe_average(blood_sugars),
            "heart_rate": safe_average(heart_rates),
            "sleep_hours": safe_average(sleep_hours),
        },
        "trends": {
            "weight": calculate_trend(weights),
            "blood_sugar": calculate_trend(blood_sugars),
            "heart_rate": calculate_trend(heart_rates),
            "sleep_hours": calculate_trend(sleep_hours),
        },
    }

    return {"message": "Health summary generated", "summary": summary}


def calculate_trend(values: List[float]) -> str:
    """计算趋势（上升、下降、稳定）"""
    if len(values) < 2:
        return "insufficient_data"

    # 简单趋势计算：比较前三分之一和后三分之一
    n = len(values)
    start_avg = sum(values[: n // 3]) / (n // 3)
    end_avg = sum(values[-(n // 3) :]) / (n // 3)

    if end_avg > start_avg * 1.05:
        return "increasing"
    elif end_avg < start_avg * 0.95:
        return "decreasing"
    else:
        return "stable"


# 添加定时导入
from datetime import timedelta
