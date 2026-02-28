# 导入所有模型
from app.models.conversation import Conversation, Message, MessageRole
from app.models.habit import Habit, HabitCategory, HabitCompletion, HabitFrequency
from app.models.health_record import HealthRecord
from app.models.health_assessment import HealthAssessment
from app.models.user import User
from app.models.memory import (
    UserLongTermMemory,
    HabitPattern,
    ContextSummary,
    DataAssociation,
)
from app.models.gamification import (
    UserBadge,
    UserPoints,
    PointsTransaction,
    UserLevel,
    Achievement,
    Challenge,
    StreakRecord,
    LeaderboardEntry,
)
from app.models.nutrition import Meal, MealItem, FoodItem, WaterIntake
from app.models.calorie_goal import CalorieGoal
from app.models.password_reset import PasswordResetToken
from app.models.rewards import Reward, RewardRedemption
from app.models.notification import (
    Notification,
    NotificationTemplate,
    UserNotificationSetting,
    EventLog,
)
from app.models.memory import UnifiedMemory
from app.models.exercise_checkin import ExerciseCheckIn

# 导出所有模型
__all__ = [
    "User",
    "HealthRecord",
    "HealthAssessment",
    "Conversation",
    "Message",
    "MessageRole",
    "Habit",
    "HabitCompletion",
    "HabitFrequency",
    "HabitCategory",
    "UserLongTermMemory",
    "HabitPattern",
    "ContextSummary",
    "DataAssociation",
    "UserBadge",
    "UserPoints",
    "PointsTransaction",
    "UserLevel",
    "Achievement",
    "Challenge",
    "StreakRecord",
    "LeaderboardEntry",
    "Meal",
    "MealItem",
    "FoodItem",
    "WaterIntake",
    "CalorieGoal",
    "PasswordResetToken",
    "Reward",
    "RewardRedemption",
    "Notification",
    "NotificationTemplate",
    "UserNotificationSetting",
    "EventLog",
    "UnifiedMemory",
    "ExerciseCheckIn",
]
