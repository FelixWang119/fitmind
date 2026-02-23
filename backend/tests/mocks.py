"""
测试模拟框架
用于模拟外部服务和依赖
"""

from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any, Dict, Optional
import json


class MockQwenAI:
    """模拟通义千问AI服务"""

    def __init__(self):
        self.responses = {
            "health_advice": "Based on your current weight of 75kg and target of 70kg, I recommend focusing on a balanced diet with moderate exercise. Aim for 30 minutes of daily activity and reduce processed foods.",
            "nutrition_advice": "As a nutritionist, I suggest increasing your protein intake to support muscle maintenance during weight loss. Include lean proteins like chicken, fish, and legumes in your meals.",
            "coach_advice": "As your behavior coach, let's work on establishing consistent habits. Start with a daily 10-minute walk and track your progress in the app.",
            "companion_support": "I understand weight management can be challenging. Remember to celebrate small victories and be kind to yourself throughout this journey.",
            "trend_analysis": "Your weight has been decreasing steadily over the past 2 weeks. The trend shows a healthy rate of weight loss at about 0.5kg per week.",
            "general_chat": "I'm here to help you with your weight management goals. How can I assist you today?",
        }

    def get_response(self, prompt: str, role: Optional[str] = None) -> str:
        """根据提示和角色获取模拟响应"""
        prompt_lower = prompt.lower()

        if role == "nutritionist":
            return self.responses["nutrition_advice"]
        elif role == "coach":
            return self.responses["coach_advice"]
        elif role == "companion":
            return self.responses["companion_support"]
        elif any(
            keyword in prompt_lower
            for keyword in ["weight", "diet", "exercise", "health"]
        ):
            return self.responses["health_advice"]
        elif any(
            keyword in prompt_lower for keyword in ["trend", "progress", "analysis"]
        ):
            return self.responses["trend_analysis"]
        else:
            return self.responses["general_chat"]

    async def get_response_async(self, prompt: str, role: Optional[str] = None) -> str:
        """异步获取模拟响应"""
        return self.get_response(prompt, role)


class MockDatabase:
    """模拟数据库会话"""

    def __init__(self):
        self.data = {}
        self.query_results = {}
        self.committed = False
        self.rolled_back = False

    def add(self, obj):
        """模拟添加对象"""
        obj_type = type(obj).__name__
        if obj_type not in self.data:
            self.data[obj_type] = []
        self.data[obj_type].append(obj)

    def commit(self):
        """模拟提交"""
        self.committed = True

    def rollback(self):
        """模拟回滚"""
        self.rolled_back = True

    def refresh(self, obj):
        """模拟刷新对象"""
        pass

    def query(self, model):
        """模拟查询"""
        return MockQuery(self, model)

    def execute(self, *args, **kwargs):
        """模拟执行"""
        return MockResult()


class MockQuery:
    """模拟查询对象"""

    def __init__(self, mock_db, model):
        self.mock_db = mock_db
        self.model = model
        self.filters = []
        self.order_by_clause = None
        self.limit_value = None
        self.offset_value = None

    def filter(self, *args):
        """模拟过滤"""
        self.filters.extend(args)
        return self

    def filter_by(self, **kwargs):
        """模拟按条件过滤"""
        self.filters.append(kwargs)
        return self

    def order_by(self, clause):
        """模拟排序"""
        self.order_by_clause = clause
        return self

    def limit(self, value):
        """模拟限制"""
        self.limit_value = value
        return self

    def offset(self, value):
        """模拟偏移"""
        self.offset_value = value
        return self

    def first(self):
        """模拟获取第一个结果"""
        model_name = self.model.__name__
        if model_name in self.mock_db.data and self.mock_db.data[model_name]:
            return self.mock_db.data[model_name][0]
        return None

    def all(self):
        """模拟获取所有结果"""
        model_name = self.model.__name__
        if model_name in self.mock_db.data:
            return self.mock_db.data[model_name]
        return []

    def count(self):
        """模拟计数"""
        model_name = self.model.__name__
        if model_name in self.mock_db.data:
            return len(self.mock_db.data[model_name])
        return 0

    def delete(self):
        """模拟删除"""
        model_name = self.model.__name__
        if model_name in self.mock_db.data:
            self.mock_db.data[model_name] = []
        return MockDeleteResult()


class MockResult:
    """模拟结果对象"""

    def fetchone(self):
        """模拟获取一行"""
        return None

    def fetchall(self):
        """模拟获取所有行"""
        return []


class MockDeleteResult:
    """模拟删除结果"""

    def rowcount(self):
        """模拟受影响的行数"""
        return 1


class MockRedis:
    """模拟Redis客户端"""

    def __init__(self):
        self.data = {}
        self.expirations = {}

    def get(self, key):
        """模拟获取值"""
        return self.data.get(key)

    def set(self, key, value, ex=None):
        """模拟设置值"""
        self.data[key] = value
        if ex:
            self.expirations[key] = ex
        return True

    def delete(self, key):
        """模拟删除键"""
        if key in self.data:
            del self.data[key]
        if key in self.expirations:
            del self.expirations[key]
        return 1

    def exists(self, key):
        """模拟检查键是否存在"""
        return key in self.data

    def incr(self, key):
        """模拟递增"""
        if key not in self.data:
            self.data[key] = "0"
        self.data[key] = str(int(self.data[key]) + 1)
        return int(self.data[key])

    def expire(self, key, time):
        """模拟设置过期时间"""
        self.expirations[key] = time
        return True


class MockRequest:
    """模拟HTTP请求"""

    def __init__(self, client_host="127.0.0.1", headers=None):
        self.client = MockClientHost(client_host)
        self.headers = headers or {}
        self.cookies = {}

    def get(self, key, default=None):
        """模拟获取头部值"""
        return self.headers.get(key, default)


class MockClientHost:
    """模拟客户端主机"""

    def __init__(self, host):
        self.host = host


class MockResponse:
    """模拟HTTP响应"""

    def __init__(self, status_code=200, json_data=None, text=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._text = text or json.dumps(json_data) if json_data else ""

    def json(self):
        """模拟JSON响应"""
        return self._json_data

    @property
    def text(self):
        """模拟文本响应"""
        return self._text

    def raise_for_status(self):
        """模拟检查状态"""
        if 400 <= self.status_code < 600:
            raise Exception(f"HTTP Error: {self.status_code}")


# 常用的模拟装饰器和上下文管理器
def mock_qwen_ai():
    """模拟Qwen AI服务的装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch("app.services.ai_service.QwenAI", MockQwenAI):
                with patch("app.api.v1.endpoints.ai.QwenAI", MockQwenAI):
                    return func(*args, **kwargs)

        return wrapper

    return decorator


def mock_database():
    """模拟数据库的装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch("app.core.database.get_db") as mock_get_db:
                mock_db = MockDatabase()
                mock_get_db.return_value = mock_db
                return func(*args, **kwargs, mock_db=mock_db)

        return wrapper

    return decorator


def mock_redis():
    """模拟Redis的装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch("app.core.redis.get_redis_client") as mock_get_redis:
                mock_redis = MockRedis()
                mock_get_redis.return_value = mock_redis
                return func(*args, **kwargs, mock_redis=mock_redis)

        return wrapper

    return decorator


def mock_request(client_host="127.0.0.1"):
    """模拟请求的装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            mock_req = MockRequest(client_host=client_host)
            return func(*args, **kwargs, mock_request=mock_req)

        return wrapper

    return decorator


# 预配置的模拟数据
class MockData:
    """预配置的模拟数据"""

    @staticmethod
    def get_user_data(user_id=1):
        """获取用户模拟数据"""
        return {
            "id": user_id,
            "email": f"user{user_id}@example.com",
            "username": f"testuser{user_id}",
            "full_name": f"Test User {user_id}",
            "age": 30,
            "height": 175,
            "initial_weight": 80000,
            "target_weight": 70000,
            "activity_level": "moderate",
            "is_active": True,
        }

    @staticmethod
    def get_health_record_data(user_id=1, record_id=1):
        """获取健康记录模拟数据"""
        return {
            "id": record_id,
            "user_id": user_id,
            "weight": 75000,
            "date": "2026-02-22",
            "notes": "Test health record",
            "blood_pressure": "120/80",
            "heart_rate": 72,
            "sleep_hours": 7.5,
            "step_count": 8542,
            "calorie_intake": 1850,
            "water_intake": 2000,
        }

    @staticmethod
    def get_habit_data(user_id=1, habit_id=1):
        """获取习惯模拟数据"""
        return {
            "id": habit_id,
            "user_id": user_id,
            "name": "晨跑",
            "description": "每天早上跑步30分钟",
            "category": "fitness",
            "frequency": "daily",
            "target_count": 1,
            "reminder_time": "07:00",
            "is_active": True,
        }

    @staticmethod
    def get_ai_request_data():
        """获取AI请求模拟数据"""
        return {"message": "我需要减肥建议", "role": "nutritionist"}

    @staticmethod
    def get_emotional_state_data(user_id=1):
        """获取情感状态模拟数据"""
        return {
            "user_id": user_id,
            "mood": "happy",
            "energy_level": "high",
            "stress_level": 3,
            "notes": "今天感觉很好",
        }
