"""
餐饮和营养 API 端点测试

覆盖功能：
- 餐饮记录 CRUD
- 营养跟踪
- 卡路里计算
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient


class TestMealEndpoints:
    """餐饮端点测试"""

    def test_get_meals_requires_auth(self, client: TestClient):
        """测试获取餐饮记录需要认证"""
        response = client.get("/api/v1/meals/")
        assert response.status_code == 401

    def test_get_meals_with_auth(self, authenticated_client):
        """测试获取餐饮记录列表（已认证）"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/meals/", headers=headers)
        assert response.status_code == 200

    def test_create_meal_record(self, authenticated_client):
        """测试创建餐饮记录"""
        client, headers, user = authenticated_client

        meal_data = {
            "meal_type": "breakfast",
            "food_items": [
                {
                    "name": "燕麦片",
                    "quantity": 100,
                    "unit": "克",
                    "calories": 380,
                    "protein": 13,
                    "carbs": 68,
                    "fat": 7,
                }
            ],
            "total_calories": 380,
            "notes": "健康早餐",
        }

        response = client.post("/api/v1/meals/", json=meal_data, headers=headers)
        assert response.status_code == 200

    def test_get_meal_by_id(self, authenticated_client):
        """测试获取单个餐饮记录"""
        client, headers, user = authenticated_client

        # 先创建一条记录
        meal_data = {
            "meal_type": "lunch",
            "food_items": [
                {
                    "name": "鸡胸肉",
                    "quantity": 200,
                    "unit": "克",
                    "calories": 330,
                    "protein": 62,
                    "carbs": 0,
                    "fat": 7,
                }
            ],
            "total_calories": 330,
        }

        create_response = client.post("/api/v1/meals/", json=meal_data, headers=headers)
        meal_id = create_response.json()["id"]

        # 获取单条记录
        response = client.get(f"/api/v1/meals/{meal_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["meal_type"] == "lunch"


class TestNutritionEndpoints:
    """营养端点测试"""

    def test_get_nutrition_summary_requires_auth(self, client: TestClient):
        """测试获取营养摘要需要认证"""
        response = client.get("/api/v1/nutrition/summary")
        assert response.status_code == 401

    def test_get_nutrition_summary_with_auth(self, authenticated_client):
        """测试获取营养摘要"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/nutrition/summary", headers=headers)
        assert response.status_code == 200

    def test_get_daily_nutrition(self, authenticated_client):
        """测试获取每日营养"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/nutrition/daily", headers=headers)
        assert response.status_code == 200

    def test_get_nutrition_goals(self, authenticated_client):
        """测试获取营养目标"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/nutrition/goals", headers=headers)
        assert response.status_code == 200


class TestExerciseEndpoints:
    """锻炼端点测试"""

    def test_get_exercises_requires_auth(self, client: TestClient):
        """测试获取锻炼记录需要认证"""
        response = client.get("/api/v1/exercises/")
        assert response.status_code == 401

    def test_get_exercises_with_auth(self, authenticated_client):
        """测试获取锻炼记录列表"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/exercises/", headers=headers)
        assert response.status_code == 200

    def test_create_exercise_record(self, authenticated_client):
        """测试创建锻炼记录"""
        client, headers, user = authenticated_client

        exercise_data = {
            "exercise_type": "running",
            "duration_minutes": 30,
            "intensity": "moderate",
            "calories_burned": 300,
            "heart_rate_avg": 140,
            "notes": "户外跑步",
        }

        response = client.post(
            "/api/v1/exercises/", json=exercise_data, headers=headers
        )
        assert response.status_code == 200

    def test_get_exercise_statistics(self, authenticated_client):
        """测试获取锻炼统计"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/exercises/stats", headers=headers)
        assert response.status_code == 200
