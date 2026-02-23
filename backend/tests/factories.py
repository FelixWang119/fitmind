"""
测试数据工厂
用于生成测试数据的工厂模式实现
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import random

from app.models.user import User
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.conversation import Conversation, Message
from app.models.emotional_support import EmotionalState, EmotionalSupport

# Note: ExerciseSession model may not exist, we'll handle it gracefully
try:
    from app.models.exercise import ExerciseSession
except ImportError:
    # Create a mock class if the model doesn't exist
    class ExerciseSession:
        pass


from app.models.meal import Meal
from app.models.gamification import (
    UserPoints,
    Badge,
    UserBadge,
    Achievement,
    UserAchievement,
    Challenge,
    UserChallenge,
)
from app.core.security import get_password_hash


class TestDataFactory:
    """测试数据工厂基类"""

    @staticmethod
    def create_user(
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: str = "TestPass123!",
        full_name: Optional[str] = None,
        age: Optional[int] = 30,
        height: Optional[int] = 175,
        initial_weight: Optional[int] = 80000,
        **kwargs,
    ) -> Dict[str, Any]:
        """创建用户测试数据"""
        if email is None:
            email = f"test{random.randint(1000, 9999)}@example.com"
        if username is None:
            username = f"testuser{random.randint(1000, 9999)}"
        if full_name is None:
            full_name = f"Test User {random.randint(1000, 9999)}"

        return {
            "email": email,
            "username": username,
            "password": password,
            "confirm_password": password,
            "full_name": full_name,
            "age": age,
            "height": height,
            "initial_weight": initial_weight,
            "target_weight": initial_weight - 10000,  # 减10kg
            "activity_level": "moderate",
            "dietary_preferences": "balanced",
            **kwargs,
        }

    @staticmethod
    def create_health_record(
        user_id: int,
        weight: Optional[int] = None,
        date: Optional[datetime] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """创建健康记录测试数据"""
        if weight is None:
            weight = random.randint(70000, 90000)
        if date is None:
            date = datetime.now() - timedelta(days=random.randint(0, 30))

        return {
            "user_id": user_id,
            "weight": weight,
            "date": date,
            "notes": "Test health record",
            "blood_pressure": "120/80",
            "heart_rate": random.randint(60, 100),
            "sleep_hours": random.uniform(6.0, 9.0),
            "step_count": random.randint(5000, 15000),
            "calorie_intake": random.randint(1500, 2500),
            "water_intake": random.randint(1500, 3000),
            **kwargs,
        }

    @staticmethod
    def create_habit(
        user_id: int, name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """创建习惯测试数据"""
        if name is None:
            habits = ["晨跑", "冥想", "喝水", "早睡", "健康饮食", "阅读", "锻炼"]
            name = random.choice(habits)

        return {
            "user_id": user_id,
            "name": name,
            "description": f"Test habit: {name}",
            "category": random.choice(
                ["health", "fitness", "mindfulness", "nutrition"]
            ),
            "frequency": random.choice(["daily", "weekly", "custom"]),
            "target_count": random.randint(1, 7),
            "reminder_time": "08:00",
            "is_active": True,
            **kwargs,
        }

    @staticmethod
    def create_habit_completion(
        habit_id: int, completion_date: Optional[datetime] = None, **kwargs
    ) -> Dict[str, Any]:
        """创建习惯完成记录测试数据"""
        if completion_date is None:
            completion_date = datetime.now() - timedelta(days=random.randint(0, 7))

        return {
            "habit_id": habit_id,
            "completion_date": completion_date,
            "notes": "Test completion",
            **kwargs,
        }

    @staticmethod
    def create_emotional_state(user_id: int, **kwargs) -> Dict[str, Any]:
        """创建情感状态测试数据"""
        moods = ["happy", "neutral", "sad", "anxious", "energetic", "calm"]
        energy_levels = ["low", "medium", "high"]

        return {
            "user_id": user_id,
            "mood": random.choice(moods),
            "energy_level": random.choice(energy_levels),
            "stress_level": random.randint(1, 10),
            "notes": "Test emotional state",
            **kwargs,
        }

    @staticmethod
    def create_exercise_session(user_id: int, **kwargs) -> Dict[str, Any]:
        """创建运动记录测试数据"""
        exercise_types = ["running", "cycling", "swimming", "weightlifting", "yoga"]

        return {
            "user_id": user_id,
            "exercise_type": random.choice(exercise_types),
            "duration_minutes": random.randint(20, 120),
            "calories_burned": random.randint(200, 800),
            "date": datetime.now() - timedelta(days=random.randint(0, 7)),
            "notes": "Test exercise session",
            **kwargs,
        }

    @staticmethod
    def create_meal(user_id: int, **kwargs) -> Dict[str, Any]:
        """创建餐饮记录测试数据"""
        meal_types = ["breakfast", "lunch", "dinner", "snack"]

        return {
            "user_id": user_id,
            "meal_type": random.choice(meal_types),
            "calories": random.randint(300, 800),
            "protein_g": random.randint(10, 40),
            "carbs_g": random.randint(20, 80),
            "fat_g": random.randint(5, 30),
            "date": datetime.now() - timedelta(hours=random.randint(1, 12)),
            "notes": "Test meal",
            **kwargs,
        }

    @staticmethod
    def create_conversation(user_id: int, **kwargs) -> Dict[str, Any]:
        """创建对话测试数据"""
        return {
            "user_id": user_id,
            "title": "Test Conversation",
            "role": random.choice(["nutritionist", "coach", "companion"]),
            **kwargs,
        }

    @staticmethod
    def create_message(
        conversation_id: int, is_user: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """创建消息测试数据"""
        if is_user:
            content = "Hello, I need help with my weight management."
        else:
            content = "I'd be happy to help you with your weight management goals. Let's start by understanding your current situation."

        return {
            "conversation_id": conversation_id,
            "content": content,
            "is_user": is_user,
            **kwargs,
        }


class DatabaseFactory:
    """数据库对象工厂"""

    def __init__(self, db):
        self.db = db
        self.data_factory = TestDataFactory()

    def create_user(self, **kwargs) -> User:
        """在数据库中创建用户"""
        user_data = self.data_factory.create_user(**kwargs)
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            age=user_data.get("age"),
            height=user_data.get("height"),
            initial_weight=user_data.get("initial_weight"),
            target_weight=user_data.get("target_weight"),
            activity_level=user_data.get("activity_level"),
            dietary_preferences=user_data.get("dietary_preferences"),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_health_record(self, user_id: int, **kwargs) -> HealthRecord:
        """在数据库中创建健康记录"""
        record_data = self.data_factory.create_health_record(user_id, **kwargs)
        record = HealthRecord(**record_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_habit(self, user_id: int, **kwargs) -> Habit:
        """在数据库中创建习惯"""
        habit_data = self.data_factory.create_habit(user_id, **kwargs)
        habit = Habit(**habit_data)
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        return habit

    def create_habit_completion(self, habit_id: int, **kwargs) -> HabitCompletion:
        """在数据库中创建习惯完成记录"""
        completion_data = self.data_factory.create_habit_completion(habit_id, **kwargs)
        completion = HabitCompletion(**completion_data)
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        return completion

    def create_emotional_state(self, user_id: int, **kwargs) -> EmotionalState:
        """在数据库中创建情感状态"""
        state_data = self.data_factory.create_emotional_state(user_id, **kwargs)
        state = EmotionalState(**state_data)
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        return state

    def create_exercise_session(self, user_id: int, **kwargs) -> ExerciseSession:
        """在数据库中创建运动记录"""
        session_data = self.data_factory.create_exercise_session(user_id, **kwargs)
        session = ExerciseSession(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def create_meal(self, user_id: int, **kwargs) -> Meal:
        """在数据库中创建餐饮记录"""
        meal_data = self.data_factory.create_meal(user_id, **kwargs)
        meal = Meal(**meal_data)
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)
        return meal

    def create_conversation(self, user_id: int, **kwargs) -> Conversation:
        """在数据库中创建对话"""
        conv_data = self.data_factory.create_conversation(user_id, **kwargs)
        conversation = Conversation(**conv_data)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def create_message(self, conversation_id: int, **kwargs) -> Message:
        """在数据库中创建消息"""
        msg_data = self.data_factory.create_message(conversation_id, **kwargs)
        message = Message(**msg_data)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def create_user_with_data(self, **kwargs) -> tuple:
        """创建用户及其相关数据"""
        user = self.create_user(**kwargs)

        # 创建一些健康记录
        for _ in range(3):
            self.create_health_record(user.id)

        # 创建一些习惯
        habits = []
        for _ in range(2):
            habit = self.create_habit(user.id)
            habits.append(habit)

            # 为习惯创建一些完成记录
            for _ in range(5):
                self.create_habit_completion(habit.id)

        # 创建情感状态
        self.create_emotional_state(user.id)

        # 创建运动记录
        self.create_exercise_session(user.id)

        # 创建餐饮记录
        self.create_meal(user.id)

        # 创建对话和消息
        conversation = self.create_conversation(user.id)
        self.create_message(conversation.id, is_user=True)
        self.create_message(conversation.id, is_user=False)

        return user, habits
