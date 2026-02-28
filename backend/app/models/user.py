from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)  # 可选字段
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 用户信息
    age = Column(Integer)
    gender = Column(String(10))  # male, female, other
    height = Column(Integer)  # 厘米
    initial_weight = Column(Integer)  # 克
    target_weight = Column(Integer)  # 克
    activity_level = Column(
        String(50)
    )  # sedentary, light, moderate, active, very_active
    dietary_preferences = Column(Text)  # JSON字符串存储饮食偏好

    # 用户信息扩展 - 新增 11 字段 (Story 1.1)
    current_weight = Column(Integer, comment="当前体重 (单位：克)")  # 当前体重，克
    waist_circumference = Column(Integer, comment="腰围 (单位：厘米)")  # 腰围，厘米
    hip_circumference = Column(Integer, comment="臀围 (单位：厘米)")  # 臀围，厘米
    body_fat_percentage = Column(Float, comment="体脂率 (单位：百分比)")  # 体脂率，%
    muscle_mass = Column(Integer, comment="肌肉量 (单位：克)")  # 肌肉量，克
    bone_density = Column(Float, comment="骨密度 (单位：克/平方厘米)")  # 骨密度，g/cm²
    metabolism_rate = Column(
        Integer, comment="基础代谢率 (单位：kcal/day)"
    )  # 基础代谢率，kcal/day
    health_conditions = Column(JSON, comment="健康状况 (JSON 格式)")  # 健康状况
    medications = Column(JSON, comment="用药情况 (JSON 格式)")  # 用药情况
    allergies = Column(JSON, comment="过敏信息 (JSON 格式)")  # 过敏信息
    sleep_quality = Column(Integer, comment="睡眠质量 (1-10 分)")  # 睡眠质量，1-10

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # 关系
    health_records = relationship(
        "HealthRecord", back_populates="user", cascade="all, delete-orphan"
    )
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    habit_goals = relationship(
        "HabitGoal", back_populates="user", cascade="all, delete-orphan"
    )
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    water_intakes = relationship(
        "WaterIntake", back_populates="user", cascade="all, delete-orphan"
    )
    health_assessments = relationship(
        "HealthAssessment", back_populates="user", cascade="all, delete-orphan"
    )

    # 记忆系统关系
    long_term_memories = relationship(
        "UserLongTermMemory", back_populates="user", cascade="all, delete-orphan"
    )
    unified_memories = relationship(
        "UnifiedMemory", back_populates="user", cascade="all, delete-orphan"
    )
    context_summaries = relationship(
        "ContextSummary", back_populates="user", cascade="all, delete-orphan"
    )
    habit_patterns = relationship(
        "HabitPattern", back_populates="user", cascade="all, delete-orphan"
    )
    data_associations = relationship(
        "DataAssociation", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    reward_redemptions = relationship(
        "RewardRedemption", back_populates="user", cascade="all, delete-orphan"
    )
    calorie_goals = relationship(
        "CalorieGoal", back_populates="user", cascade="all, delete-orphan"
    )
    exercise_checkins = relationship(
        "ExerciseCheckIn", back_populates="user", cascade="all, delete-orphan"
    )

    # 目标系统关系 (Story 1.6)
    goals = relationship(
        "UserGoal", back_populates="user", cascade="all, delete-orphan"
    )

    # 通知系统关系
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    notification_settings = relationship(
        "UserNotificationSetting",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
