"""Admin authentication and authorization"""

import structlog
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User as UserModel
from app.services.auth_service import verify_token, create_access_token

logger = structlog.get_logger()

router = APIRouter()

# OAuth2 scheme for admin
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/admin/auth/login")


# Response Models
class AdminUser(BaseModel):
    """Admin user response"""

    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    is_superuser: bool
    is_active: bool


class AdminToken(BaseModel):
    """Admin login token response"""

    access_token: str
    token_type: str
    user: AdminUser


class AdminMenuItem(BaseModel):
    """Admin menu item"""

    id: str
    name: str
    path: str
    icon: Optional[str] = None
    children: Optional[List["AdminMenuItem"]] = None


class AdminMenusResponse(BaseModel):
    """Admin menus response"""

    menus: List[AdminMenuItem]


# Admin role permissions
ADMIN_ROLES = {
    "super_admin": [
        "admin:dashboard",
        "admin:feature-flags",
        "admin:ai-prompts",
        "admin:notifications",
        "admin:system-config",
        "admin:business-rules",
        "admin:audit-logs",
        "admin:users",
    ],
    "admin": [
        "admin:dashboard",
        "admin:notifications",
        "admin:business-rules",
    ],
}


def get_admin_menus(user: UserModel) -> List[AdminMenuItem]:
    """根据用户角色获取可访问的菜单"""
    if user.is_superuser:
        permissions = ADMIN_ROLES["super_admin"]
    else:
        permissions = ADMIN_ROLES.get("admin", [])

    # 定义所有可用菜单
    all_menus = [
        AdminMenuItem(
            id="dashboard", name="仪表盘", path="/admin", icon="LayoutDashboard"
        ),
        AdminMenuItem(
            id="feature-flags",
            name="功能开关",
            path="/admin/feature-flags",
            icon="ToggleLeft",
        ),
        AdminMenuItem(
            id="ai-prompts", name="AI 提示词", path="/admin/ai-prompts", icon="Brain"
        ),
        AdminMenuItem(
            id="notifications",
            name="通知模板",
            path="/admin/notifications",
            icon="Bell",
        ),
        AdminMenuItem(
            id="system-config",
            name="系统配置",
            path="/admin/system-config",
            icon="Settings",
        ),
        AdminMenuItem(
            id="business-rules",
            name="业务规则",
            path="/admin/business-rules",
            icon="BookOpen",
        ),
        AdminMenuItem(
            id="audit-logs", name="审计日志", path="/admin/audit-logs", icon="FileText"
        ),
    ]

    # 根据权限过滤菜单
    # 简化处理：super_admin可以看到所有菜单
    if user.is_superuser:
        return all_menus

    # 普通管理员只看到部分菜单
    allowed_paths = {
        "admin:dashboard": "dashboard",
        "admin:notifications": "notifications",
        "admin:business-rules": "business-rules",
    }

    filtered_menus = []
    for menu in all_menus:
        perm = f"admin:{menu.id}"
        if perm in permissions:
            filtered_menus.append(menu)

    return filtered_menus


# ========== Admin Authentication Dependencies ==========


async def get_current_admin_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    """获取当前认证的管理员用户"""
    from app.services.auth_service import verify_token

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

    if not user.is_active:
        logger.warning("User inactive", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # 检查是否是管理员
    if not user.is_superuser:
        logger.warning("Non-admin user attempted access", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return user


# ========== Admin Authentication Endpoints ==========


@router.post("/auth/login", response_model=AdminToken)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """管理员登录 - 使用邮箱和密码"""
    # 查询用户
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码 (复用 auth_service 的验证逻辑)
    from app.services.auth_service import authenticate_user

    authenticated = authenticate_user(db, form_data.username, form_data.password)

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查是否是管理员
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    # 创建 token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AdminToken(
        access_token=access_token,
        token_type="bearer",
        user=AdminUser(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        ),
    )


@router.get("/auth/me", response_model=AdminUser)
async def get_admin_me(current_user: UserModel = Depends(get_current_admin_user)):
    """获取当前管理员信息"""
    return AdminUser(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_superuser=current_user.is_superuser,
        is_active=current_user.is_active,
    )


@router.get("/auth/menus", response_model=AdminMenusResponse)
async def get_admin_menus_endpoint(
    current_user: UserModel = Depends(get_current_admin_user),
):
    """获取当前管理员可访问的菜单"""
    menus = get_admin_menus(current_user)
    return AdminMenusResponse(menus=menus)
