import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate


# 允许更新的字段白名单 (P0-4 安全修复)


def convert_weight_kg_to_g(weight_kg: float) -> int:
    """体重单位转换：kg → g (四舍五入)"""
    return round(weight_kg * 1000)


ALLOWED_UPDATE_FIELDS = {
    "age",
    "gender",
    "height",
    "initial_weight",
    "target_weight",
    "activity_level",
    "dietary_preferences",
    "current_weight",
    "waist_circumference",
    "hip_circumference",
    "body_fat_percentage",
    "muscle_mass",
    "bone_density",
    "metabolism_rate",
    "health_conditions",
    "medications",
    "allergies",
    "sleep_quality",
    "username",
    "full_name",
}

logger = structlog.get_logger()

router = APIRouter()


@router.get("/profile", response_model=User)
async def get_user_profile(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的个人资料"""
    return current_user


@router.put("/profile", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新当前用户的个人资料"""
    try:
        # P0-3: 必填字段验证 (如果是首次设置)
        if not current_user.age and user_update.age is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age is required for profile completion",
            )

        if not current_user.height and user_update.height is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Height is required for profile completion",
            )

        if not current_user.initial_weight and user_update.initial_weight is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial weight is required for profile completion",
            )

        if not current_user.target_weight and user_update.target_weight is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target weight is required for profile completion",
            )

        # 原有字段验证
        if user_update.age is not None and user_update.age <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Age must be positive"
            )

        if user_update.height is not None and user_update.height <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Height must be positive",
            )

        if user_update.initial_weight is not None and user_update.initial_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial weight must be positive",
            )

        if user_update.target_weight is not None and user_update.target_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target weight must be positive",
            )

        # 新增字段验证 - Story 1.3
        if user_update.current_weight is not None and user_update.current_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current weight must be positive",
            )

        if (
            user_update.waist_circumference is not None
            and user_update.waist_circumference <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Waist circumference must be positive",
            )

        if (
            user_update.hip_circumference is not None
            and user_update.hip_circumference <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hip circumference must be positive",
            )

        if user_update.body_fat_percentage is not None and (
            user_update.body_fat_percentage < 3.0
            or user_update.body_fat_percentage > 70.0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Body fat percentage must be between 3.0 and 70.0",
            )

        if user_update.muscle_mass is not None and user_update.muscle_mass <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Muscle mass must be positive",
            )

        if user_update.bone_density is not None and (
            user_update.bone_density < 0.5 or user_update.bone_density > 2.5
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bone density must be between 0.5 and 2.5 g/cm²",
            )

        if user_update.metabolism_rate is not None and (
            user_update.metabolism_rate < 800 or user_update.metabolism_rate > 4000
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metabolism rate must be between 800 and 4000 kcal/day",
            )

        if user_update.sleep_quality is not None and (
            user_update.sleep_quality < 1 or user_update.sleep_quality > 10
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sleep quality must be between 1 and 10",
            )

        # 更新允许更改的字段
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ALLOWED_UPDATE_FIELDS:  # P0-4: 白名单验证
                setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        # Story 5.1: 自动同步档案到记忆系统
        try:
            from app.services.profile_memory_service import get_profile_memory_service

            profile_service = get_profile_memory_service(db)
            profile_service.sync_profile_to_memory(current_user)
            logger.info("Profile auto-synced to memory", user_id=current_user.id)
        except Exception as e:
            # 不阻塞档案更新流程
            logger.warning(f"Auto-sync to memory failed: {e}")

        logger.info(
            "User profile updated",
            user_id=current_user.id,
            fields_updated=list(update_data.keys()),
        )

        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update user profile", user_id=current_user.id, error=str(e)
        )

        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


# ========== Story 5.1: 档案记忆同步 ==========


@router.post("/profile/sync-to-memory")
async def sync_profile_to_memory(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """同步用户档案到记忆系统 (Story 5.1)"""
    from app.services.profile_memory_service import get_profile_memory_service

    try:
        profile_service = get_profile_memory_service(db)
        result = profile_service.sync_profile_to_memory(current_user)

        return {
            "success": True,
            "user_id": current_user.id,
            "synced_memories": result,
            "message": f"成功同步 {len(result)} 种档案类型到记忆系统",
        }

    except Exception as e:
        logger.error(
            "Failed to sync profile to memory", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync profile to memory",
        )


@router.post("/profile/sync-to-memory/batch")
async def batch_sync_profiles_to_memory(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """批量同步所有用户档案到记忆系统 (仅管理员, Story 5.1)"""
    # 仅允许超级管理员执行批量操作
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can perform batch sync",
        )

    from app.services.profile_memory_service import get_profile_memory_service

    try:
        profile_service = get_profile_memory_service(db)
        result = profile_service.batch_migrate_existing_profiles()

        return {
            "success": True,
            "stats": result,
            "message": f"批量同步完成：成功 {result['success']}, 跳过 {result['skipped']}, 失败 {result['failed']}",
        }

    except Exception as e:
        logger.error("Batch profile sync failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to batch sync profiles to memory",
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户信息（仅限当前用户或管理员）"""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.get("", response_model=list[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户列表（仅限管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users
