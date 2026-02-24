import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate

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
        # 特殊情況驗證
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

        # 更新允许更改的字段
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        logger.info(
            "User profile updated",
            user_id=current_user.id,
            fields_updated=list(user_update.model_dump(exclude_unset=True).keys()),
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
