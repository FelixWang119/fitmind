from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


# 基础模式
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)  # 可选字段
    full_name: Optional[str] = None

    # 用户信息
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[int] = Field(None, ge=50, le=250)  # 厘米
    initial_weight: Optional[int] = Field(None, ge=20000, le=300000)  # 克
    target_weight: Optional[int] = Field(None, ge=20000, le=300000)  # 克
    activity_level: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None


# 创建用户
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password_strength(cls, v):
        """验证密码强度 - 要求：至少 8 位，包含大小写字母和数字"""
        if len(v) < 8:
            raise ValueError("密码至少需要 8 个字符")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("密码不能超过 72 字节，请使用较短的密码")
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not has_upper:
            raise ValueError("密码必须包含至少一个大写字母")
        if not has_lower:
            raise ValueError("密码必须包含至少一个小写字母")
        if not has_digit:
            raise ValueError("密码必须包含至少一个数字")
        return v

    @validator("confirm_password")
    def validate_passwords_match(cls, v, values):
        """验证密码和确认密码是否匹配"""
        if "password" in values and v != values["password"]:
            raise ValueError("密码和确认密码不匹配")
        return v


# 更新用户
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[int] = Field(None, ge=50, le=250)
    initial_weight: Optional[int] = Field(None, ge=20000, le=300000)
    target_weight: Optional[int] = Field(None, ge=20000, le=300000)
    activity_level: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None


# 数据库中的用户
class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# 响应给客户端的用户
class User(UserInDB):
    pass


# 用户登录
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 令牌
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# 令牌数据
class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# 密码重置
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def validate_password_strength(cls, v):
        """验证密码强度 - 要求：至少 8 位，包含大小写字母和数字"""
        if len(v) < 8:
            raise ValueError("密码至少需要 8 个字符")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("密码不能超过 72 字节，请使用较短的密码")
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not has_upper:
            raise ValueError("密码必须包含至少一个大写字母")
        if not has_lower:
            raise ValueError("密码必须包含至少一个小写字母")
        if not has_digit:
            raise ValueError("密码必须包含至少一个数字")
        return v
