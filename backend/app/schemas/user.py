from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# 基础模式
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)  # 可选字段
    full_name: Optional[str] = None

    # 用户信息
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[int] = Field(None, ge=50, le=250)  # 厘米
    initial_weight: Optional[int] = Field(None, ge=10, le=300)  # 克
    target_weight: Optional[int] = Field(None, ge=10, le=300)  # 克
    activity_level: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None

    # 用户信息扩展 - 新增 11 字段 (Story 1.2)
    current_weight: Optional[int] = Field(
        None, ge=20000, le=300000, description="当前体重 (克)"
    )
    waist_circumference: Optional[int] = Field(
        None, ge=50, le=150, description="腰围 (厘米)"
    )
    hip_circumference: Optional[int] = Field(
        None, ge=50, le=150, description="臀围 (厘米)"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=3.0, le=70.0, description="体脂率 (%)"
    )
    muscle_mass: Optional[int] = Field(
        None, ge=10000, le=150000, description="肌肉量 (克)"
    )
    bone_density: Optional[float] = Field(
        None, ge=0.5, le=2.5, description="骨密度 (g/cm²)"
    )
    metabolism_rate: Optional[int] = Field(
        None, ge=800, le=4000, description="基础代谢率 (kcal/day)"
    )
    health_conditions: Optional[Dict[str, Any]] = Field(
        None, description="健康状况 (JSON)"
    )
    medications: Optional[Dict[str, Any]] = Field(None, description="用药情况 (JSON)")
    allergies: Optional[List[str]] = Field(None, description="过敏信息 (JSON)")
    sleep_quality: Optional[int] = Field(
        None, ge=1, le=10, description="睡眠质量 (1-10 分)"
    )


# 创建用户
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """验证密码强度 - 要求：至少 8 位，包含大小写字母和数字"""
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

    @field_validator("confirm_password")
    @classmethod
    def validate_passwords_match(cls, v, info):
        """验证密码和确认密码是否匹配"""
        if "password" in info.data and v != info.data["password"]:
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

    # 用户信息扩展 - 新增 11 字段 (Story 1.2)
    current_weight: Optional[int] = Field(None, ge=20000, le=300000)
    waist_circumference: Optional[int] = Field(None, ge=50, le=150)
    hip_circumference: Optional[int] = Field(None, ge=50, le=150)
    body_fat_percentage: Optional[float] = Field(None, ge=3.0, le=70.0)
    muscle_mass: Optional[int] = Field(None, ge=10000, le=150000)
    bone_density: Optional[float] = Field(None, ge=0.5, le=2.5)
    metabolism_rate: Optional[int] = Field(None, ge=800, le=4000)
    health_conditions: Optional[Dict[str, Any]] = None
    medications: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)


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

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        """验证密码强度 - 要求：至少 8 位，包含大小写字母和数字"""
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
