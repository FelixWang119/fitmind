from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import rate_limit_registration, rate_limit_login
from app.models.user import User as UserModel
from app.schemas.user import (
    Token,
    User,
    UserCreate,
    UserUpdate,
    PasswordResetRequest,
    PasswordReset,
)
from app.services.email_service import email_service
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user_password,
    verify_token,
)

logger = structlog.get_logger()

router = APIRouter()

# OAuth2方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# 依赖项：获取当前用户
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None:
        logger.warning("Invalid token")
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.id == token_data.user_id).first()
    if user is None:
        logger.warning("User not found", user_id=token_data.user_id)
        raise credentials_exception

    if not user.is_active:  # type: ignore
        logger.warning("User inactive", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """获取当前活跃用户"""
    if not current_user.is_active:  # type: ignore
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request, user_data: UserCreate, db: Session = Depends(get_db)
):
    """用户注册

    接收用户注册信息，创建新用户账户。

    Args:
        request: FastAPI 请求对象（包含 IP 地址）
        user_data: 用户注册数据（邮箱、密码等）
        db: 数据库会话

    Returns:
        User: 创建的用户对象（不含密码）

    Raises:
        HTTPException: 400 - 邮箱已注册/验证失败
        HTTPException: 429 - 超过速率限制
        HTTPException: 500 - 服务器内部错误
    """
    # 获取客户端 IP 地址
    client_ip = request.client.host if request.client else "unknown"
    timestamp = datetime.utcnow().isoformat()

    # 速率限制检查
    await rate_limit_registration(request)

    logger.info(
        "User registration request",
        email=user_data.email,
        ip=client_ip,
        timestamp=timestamp,
        username=user_data.username,
    )

    try:
        user = create_user(db, user_data.model_dump())
        logger.info(
            "User registered successfully",
            user_id=user.id,
            email=user.email,
            ip=client_ip,
            timestamp=timestamp,
        )
        return user
    except ValueError as e:
        logger.warning(
            "Registration failed",
            email=user_data.email,
            ip=client_ip,
            error=str(e),
            field="email" if "email" in str(e).lower() else "general",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": str(e),
                "field": "email" if "email" in str(e).lower() else "general",
            },
        )
    except Exception as e:
        logger.error(
            "Registration error",
            email=user_data.email,
            ip=client_ip,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "服务器内部错误，请稍后重试"},
        )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """用户登录"""
    # 速率限制检查
    await rate_limit_login(request)

    logger.info("Login attempt", username=form_data.username)

    user = None  # 初始化变量以满足静态分析要求
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except ValueError as e:
        error_message = str(e)
        logger.warning("Login failed", username=form_data.username, error=error_message)

        # 根据错误类型返回不同的消息
        if error_message == "邮箱未注册":
            detail_message = "邮箱未注册，请先注册账户"
        elif error_message == "密码错误":
            detail_message = "邮箱或密码错误"
        elif error_message == "账户已被禁用":
            detail_message = "账户已被禁用，请联系管理员"
        else:
            detail_message = "邮箱或密码错误"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "authentication_error", "message": detail_message},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 确保user不是None - 如果authenticate_user函数正常，它应当返回有效的用户对象
    # 或在认证失败的情况下抛出ValueError异常
    if user is None:
        # 这种情况在正常的业务逻辑下不应该出现
        logger.error(
            "Unexpected None user returned from authenticate_user",
            username=form_data.username,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "内部服务错误"},
        )

    # 将用户信息提取到局部变量，以便类型检查器能够正确推导类型
    user_id = str(user.id)
    user_email = str(user.email)

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": user_email},
        expires_delta=access_token_expires,
    )

    logger.info("Login successful", user_id=user_id, email=user_email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新用户信息"""
    logger.info("Updating user", user_id=current_user.id)

    update_data = user_update.dict(exclude_unset=True)

    # 检查用户名是否已被使用
    if "username" in update_data and update_data["username"] != current_user.username:
        existing_user = (
            db.query(UserModel)
            .filter(UserModel.username == update_data["username"])
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    # 检查邮箱是否已被使用
    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = (
            db.query(UserModel).filter(UserModel.email == update_data["email"]).first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # 处理饮食偏好列表
    if "dietary_preferences" in update_data and update_data["dietary_preferences"]:
        update_data["dietary_preferences"] = ",".join(
            update_data["dietary_preferences"]
        )

    # 更新用户信息
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    logger.info("User updated successfully", user_id=current_user.id)
    return current_user


@router.post("/logout")
async def logout(current_user: UserModel = Depends(get_current_active_user)):
    """用户登出（客户端应删除令牌）"""
    logger.info("User logout", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    logger.info("Changing password", user_id=current_user.id)

    # 验证旧密码
    from app.services.auth_service import verify_password

    if not verify_password(old_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    # 更新密码
    update_user_password(db, current_user, new_password)

    logger.info("Password changed successfully", user_id=current_user.id)
    return {"message": "Password updated successfully"}


@router.post("/password-reset-request")
async def password_reset_request(
    password_reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """请求密码重置"""
    logger.info("Password reset request", email=password_reset_request.email)

    # 验证是否使用了现有的用户模型导入

    user = (
        db.query(UserModel)
        .filter(
            UserModel.email == password_reset_request.email, UserModel.is_active == True
        )
        .first()
    )

    if not user:
        # 为安全原因返回成功信息以防止用户探测
        logger.info(
            "Password reset request processed", email=password_reset_request.email
        )
        return {"message": "如果邮箱地址有效，我们已向您发送密码重置邮件"}

    # 撤销现有未使用的重置令牌
    from app.models.password_reset import PasswordResetToken

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow(),
    ).delete()

    # 创建新的重置令牌
    import secrets

    token = secrets.token_urlsafe(32)  # 生成安全的随机令牌

    # 令牌有效期为 24 小时
    expires_at = datetime.utcnow() + timedelta(hours=24)

    reset_token = PasswordResetToken(
        user_id=user.id, token=token, expires_at=expires_at, used=False
    )
    db.add(reset_token)
    db.commit()

    # 发送密码重置邮件
    await email_service.send_password_reset_email(user.email, token)

    logger.info("Password reset token generated and email sent", user_id=user.id)
    return {"message": "如果邮箱地址有效，我们已向您发送密码重置邮件"}


@router.post("/password-reset")
async def password_reset(
    password_reset: PasswordReset,
    db: Session = Depends(get_db),
):
    """重置密码"""
    logger.info("Password reset attempt", token_used=True)

    from app.models.password_reset import PasswordResetToken
    from app.services.auth_service import get_password_hash
    import hashlib

    # 查找有效的未使用令牌
    reset_token_record = (
        db.query(PasswordResetToken)
        .join(UserModel, UserModel.id == PasswordResetToken.user_id)
        .filter(
            PasswordResetToken.token == password_reset.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow(),
            UserModel.is_active == True,
        )
        .first()
    )

    if not reset_token_record:
        logger.warning("Invalid or expired password reset token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无效或过期的重置令牌"
        )

    # 更新用户密码
    user = reset_token_record.user
    hashed_password = get_password_hash(password_reset.new_password)
    user.hashed_password = hashed_password

    # 标记令牌为已使用
    reset_token_record.used = True
    db.commit()

    logger.info("Password reset successful", user_id=user.id)
    return {"message": "密码重置成功"}
