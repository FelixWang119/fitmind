from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """健康检查端点"""
    # 检查数据库连接
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {"database": db_status, "api": "healthy"},
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """就绪检查端点"""
    # 检查数据库是否就绪
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}
