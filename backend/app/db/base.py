# 导入所有模型，确保它们被注册到 Base.metadata
from app.db.session import Base
from app.models.conversation import Conversation
from app.models.habit import Habit, HabitCompletion
from app.models.health_record import HealthRecord
from app.models.user import User

# 导出 Base，用于创建表
__all__ = ["Base"]
