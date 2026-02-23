from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import structlog
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.user import TokenData

logger = structlog.get_logger()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error("Password verification failed", error=str(e))
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    # bcrypt has a 72-byte limit, so we need to check
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # Truncate to 72 bytes if necessary
        password_bytes = password_bytes[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.debug("Access token created", user_id=data.get("sub"), expires=expire)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """验证令牌"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None or email is None:
            logger.warning(
                "Token missing required fields", user_id=user_id, email=email
            )
            return None

        return TokenData(user_id=int(user_id), email=str(email))
    except JWTError as e:
        logger.warning("Token verification failed", error=str(e))
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """认证用户"""
    logger.debug("Authenticating user", email=email)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning("User not found", email=email)
        raise ValueError("邮箱未注册")

    if not verify_password(password, str(user.hashed_password)):
        logger.warning("Invalid password", email=email)
        raise ValueError("密码错误")

    if not user.is_active:  # type: ignore
        logger.warning("User inactive", email=email)
        raise ValueError("账户已被禁用")

    # 更新最后登录时间
    from datetime import datetime

    user.last_login = datetime.utcnow()  # type: ignore
    db.commit()

    logger.info("User authenticated successfully", user_id=user.id, email=email)
    return user


def create_user(db: Session, user_data: dict) -> User:
    """创建新用户"""
    logger.debug("Creating new user", email=user_data.get("email"))

    # 检查用户是否已存在
    existing_user = (
        db.query(User)
        .filter(
            (User.email == user_data["email"])
            | (User.username == user_data["username"])
        )
        .first()
    )

    if existing_user:
        if existing_user.email == user_data["email"]:
            logger.warning("Email already exists", email=user_data["email"])
            raise ValueError("Email already registered")
        else:
            logger.warning("Username already exists", username=user_data["username"])
            raise ValueError("Username already taken")

    # 移除确认密码字段（不存储）
    if "confirm_password" in user_data:
        user_data.pop("confirm_password")

    # 创建用户
    hashed_password = get_password_hash(user_data.pop("password"))
    user_data["hashed_password"] = hashed_password

    # 处理饮食偏好列表
    if "dietary_preferences" in user_data and user_data["dietary_preferences"]:
        user_data["dietary_preferences"] = ",".join(user_data["dietary_preferences"])

    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User created successfully", user_id=user.id, email=user.email)
    return user


def update_user_password(db: Session, user: User, new_password: str) -> None:
    """更新用户密码"""
    logger.debug("Updating user password", user_id=user.id)

    user.hashed_password = get_password_hash(new_password)  # type: ignore
    db.commit()

    logger.info("User password updated", user_id=user.id)
