"""
习惯管理 API 端点测试

覆盖功能：
- 习惯 CRUD 操作
- 习惯完成记录
- 连续记录跟踪
- 习惯类别过滤
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.models.habit import Habit, HabitCompletion, HabitCategory, HabitFrequency


class TestHabitEndpoints:
    """习惯管理端点测试"""

    def test_get_habits_requires_auth(self, client: TestClient):
        """测试获取习惯列表需要认证"""
        response = client.get("/api/v1/habits/")
        assert response.status_code == 401

    def test_get_habits_with_auth(self, authenticated_client):
        """测试获取习惯列表（已认证）"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/habits/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_habits_with_category_filter(self, authenticated_client, db_session):
        """测试按类别过滤习惯"""
        client, headers, user = authenticated_client

        # 创建测试习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            target_value=30,
            target_unit="分钟",
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()

        # 按类别过滤
        response = client.get("/api/v1/habits/?category=exercise", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_create_habit(self, authenticated_client):
        """测试创建新习惯"""
        client, headers, user = authenticated_client

        habit_data = {
            "name": "每日喝水",
            "description": "每天喝足够的水",
            "category": "health",
            "frequency": "daily",
            "target_value": 2000,
            "target_unit": "毫升",
            "preferred_time": "09:00",
            "reminder_enabled": True,
            "reminder_time": "08:30",
        }

        response = client.post("/api/v1/habits/", json=habit_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "每日喝水"
        assert data["target_value"] == 2000

    def test_get_single_habit(self, authenticated_client, db_session):
        """测试获取单个习惯"""
        client, headers, user = authenticated_client

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)

        # 获取习惯
        response = client.get(f"/api/v1/habits/{habit.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "每日运动"

    def test_update_habit(self, authenticated_client, db_session):
        """测试更新习惯"""
        client, headers, user = authenticated_client

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            target_value=30,
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)

        # 更新习惯
        update_data = {
            "name": "每日晨跑",
            "target_value": 45,
        }

        response = client.put(
            f"/api/v1/habits/{habit.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "每日晨跑"
        assert data["target_value"] == 45

    def test_delete_habit(self, authenticated_client, db_session):
        """测试删除习惯"""
        client, headers, user = authenticated_client

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)
        habit_id = habit.id

        # 删除习惯
        response = client.delete(f"/api/v1/habits/{habit_id}", headers=headers)
        assert response.status_code == 200

        # 验证习惯已删除
        response = client.get(f"/api/v1/habits/{habit_id}", headers=headers)
        assert response.status_code == 404

    def test_record_habit_completion(self, authenticated_client, db_session):
        """测试记录习惯完成"""
        client, headers, user = authenticated_client

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            target_value=30,
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)

        # 记录完成
        completion_data = {
            "completed_value": 30,
            "notes": "完成晨跑",
        }

        response = client.post(
            f"/api/v1/habits/{habit.id}/complete", json=completion_data, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["habit_id"] == habit.id

    def test_get_habit_statistics(self, authenticated_client, db_session):
        """测试获取习惯统计"""
        client, headers, user = authenticated_client

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name="每日运动",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            target_value=30,
            is_active=True,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)

        # 获取统计
        response = client.get(f"/api/v1/habits/{habit.id}/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data
        assert "total_completions" in data

    def test_cannot_access_other_users_habit(self, authenticated_client, db_session):
        """测试不能访问其他用户的习惯"""
        from app.models.user import User
        from app.services.auth_service import get_password_hash

        client, headers, user = authenticated_client

        # 创建另一个用户和习惯
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        other_habit = Habit(
            user_id=other_user.id,
            name="其他用户习惯",
            category=HabitCategory.EXERCISE,
            frequency=HabitFrequency.DAILY,
            is_active=True,
        )
        db_session.add(other_habit)
        db_session.commit()
        db_session.refresh(other_habit)

        # 尝试访问其他用户的习惯
        response = client.get(f"/api/v1/habits/{other_habit.id}", headers=headers)
        assert response.status_code == 404

    def test_get_habits_inactive_filter(self, authenticated_client, db_session):
        """测试获取非活跃习惯"""
        client, headers, user = authenticated_client

        # 创建非活跃习惯
        habit = Habit(
            user_id=user.id,
            name="暂停的习惯",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            is_active=False,
        )
        db_session.add(habit)
        db_session.commit()

        # 获取非活跃习惯
        response = client.get("/api/v1/habits/?active_only=false", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # 应该包含所有习惯（活跃和非活跃）
        assert isinstance(data, list)
