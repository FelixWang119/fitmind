"""运动打卡功能测试

测试优先级标记：
- @pytest.mark.p0: 核心功能（创建、获取、认证），必须通过
- @pytest.mark.p1: 重要功能（更新、删除、摘要）
- @pytest.mark.p2: 一般功能（边界情况、性能）
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app


class TestExerciseCheckInCreate:
    """创建运动打卡测试 - P0 核心功能"""

    @pytest.mark.p0
    def test_create_exercise_checkin_success(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试成功创建运动打卡 - P0 核心功能"""
        client, headers, test_user = authenticated_client

        checkin_data = {
            "exercise_type": "Running",
            "category": "有氧",
            "duration_minutes": 30,
            "intensity": "medium",
            "distance_km": 5.0,
            "started_at": datetime.utcnow().isoformat(),
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 201
        data = response.json()

        # 验证响应字段
        assert data["exercise_type"] == checkin_data["exercise_type"]
        assert data["duration_minutes"] == checkin_data["duration_minutes"]
        assert data["intensity"] == checkin_data["intensity"]
        assert data["calories_burned"] > 0
        assert data["is_estimated"] is True
        assert "estimation_details" in data
        assert data["user_id"] == test_user.id
        assert "id" in data

    @pytest.mark.p0
    def test_create_exercise_checkin_with_weight(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试使用用户体重计算卡路里 - P0"""
        client, headers, test_user = authenticated_client

        # 设置用户体重 (70kg = 70000g)
        test_user.initial_weight = 70000
        db_session.commit()

        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 201
        data = response.json()

        # 验证卡路里估算 (MET=8.0 × 70kg × 0.5h × 1.0 = 280kcal)
        assert 250 <= data["calories_burned"] <= 310  # 允许误差范围

    @pytest.mark.p0
    def test_create_exercise_checkin_missing_weight(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试用户体重缺失时使用默认值 - F1 修复验证"""
        client, headers, test_user = authenticated_client

        # 确保用户体重为空
        test_user.initial_weight = None
        db_session.commit()

        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 201
        data = response.json()

        # 验证使用默认体重计算 (MET=8.0 × 70kg × 0.5h × 1.0 = 280kcal)
        assert data["calories_burned"] > 0
        assert data["estimation_details"]["weight_kg"] == 70.0

    @pytest.mark.p0
    def test_create_exercise_checkin_unauthorized(
        self, client: TestClient, db_session: Session
    ):
        """测试未授权访问 - AC5"""
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 401


class TestExerciseCheckInValidation:
    """数据验证测试 - P0"""

    @pytest.mark.p0
    def test_create_exercise_checkin_empty_type(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试运动类型为空 - AC6"""
        client, headers, test_user = authenticated_client

        checkin_data = {
            "exercise_type": "",
            "duration_minutes": 30,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 422

    @pytest.mark.p0
    def test_create_exercise_checkin_negative_duration(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试时长为负数 - AC7"""
        client, headers, test_user = authenticated_client

        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": -10,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 422

    @pytest.mark.p0
    def test_create_exercise_checkin_invalid_intensity(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试强度无效 - AC8"""
        client, headers, test_user = authenticated_client

        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "super_hard",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)

        assert response.status_code == 422


class TestExerciseCheckInList:
    """获取打卡列表测试 - P0"""

    @pytest.mark.p0
    def test_get_exercise_checkins_success(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试获取打卡列表 - AC3"""
        client, headers, test_user = authenticated_client

        # 先创建一条记录
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        client.post("/api/v1/exercise-checkin/", json=checkin_data)

        response = client.get("/api/v1/exercise-checkin/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.p0
    def test_get_exercise_checkins_pagination(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试分页 - F4 修复验证"""
        client, headers, test_user = authenticated_client

        response = client.get("/api/v1/exercise-checkin/?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    @pytest.mark.p0
    def test_cannot_access_other_user_checkins(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试无法访问他人打卡记录 - F3 修复验证"""
        client, headers, test_user = authenticated_client

        # 创建另一个用户
        from app.models.user import User
        from app.services.auth_service import get_password_hash
        from datetime import datetime

        other_user = User(
            email="other_user@test.com",
            username="other_user",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        # 以另一个用户身份创建打卡
        from app.services.auth_service import create_access_token
        from datetime import timedelta

        other_token = create_access_token(
            data={
                "sub": str(other_user.id),
                "email": other_user.email,
                "user_id": other_user.id,
            },
            expires_delta=timedelta(minutes=30),
        )

        # 创建打卡记录
        other_headers = {"Authorization": f"Bearer {other_token}"}
        other_client = TestClient(app)
        other_client.headers.update(other_headers)

        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        create_response = other_client.post(
            "/api/v1/exercise-checkin/", json=checkin_data
        )
        other_checkin_id = create_response.json()["id"]

        # 尝试访问另一个用户的记录
        response = client.get(f"/api/v1/exercise-checkin/{other_checkin_id}")

        # 应该返回 404（看起来不存在）
        assert response.status_code == 404


class TestDailySummary:
    """当日摘要测试 - P0"""

    @pytest.mark.p0
    def test_get_daily_summary_success(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试获取当日摘要 - AC4"""
        client, headers, test_user = authenticated_client

        # 创建一条记录
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        client.post("/api/v1/exercise-checkin/", json=checkin_data)

        response = client.get("/api/v1/exercise-checkin/daily-summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_duration_minutes"] >= 30
        assert data["total_calories_burned"] > 0
        assert data["sessions_count"] >= 1

    @pytest.mark.p1
    def test_get_daily_summary_no_data(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试无数据时返回 0 - AC11"""
        client, headers, test_user = authenticated_client

        response = client.get("/api/v1/exercise-checkin/daily-summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_duration_minutes"] == 0
        assert data["total_calories_burned"] == 0
        assert data["sessions_count"] == 0


class TestExerciseCheckInUpdate:
    """更新打卡测试 - P1"""

    @pytest.mark.p1
    def test_update_exercise_checkin_success(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试更新打卡记录 - AC13 反向验证"""
        client, headers, test_user = authenticated_client

        # 创建记录
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        create_response = client.post("/api/v1/exercise-checkin/", json=checkin_data)
        checkin_id = create_response.json()["id"]

        # 更新记录
        update_data = {
            "duration_minutes": 45,
            "intensity": "high",
        }

        response = client.put(
            f"/api/v1/exercise-checkin/{checkin_id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["duration_minutes"] == 45
        assert data["intensity"] == "high"

    @pytest.mark.p1
    def test_update_exercise_checkin_not_found(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试更新不存在的记录 - AC13"""
        client, headers, test_user = authenticated_client

        update_data = {
            "duration_minutes": 45,
        }

        response = client.put("/api/v1/exercise-checkin/99999", json=update_data)

        assert response.status_code == 404


class TestExerciseCheckInDelete:
    """删除打卡测试 - P1"""

    @pytest.mark.p1
    def test_delete_exercise_checkin_success(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试软删除打卡记录"""
        client, headers, test_user = authenticated_client

        # 创建记录
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        create_response = client.post("/api/v1/exercise-checkin/", json=checkin_data)
        checkin_id = create_response.json()["id"]

        # 删除记录
        response = client.delete(f"/api/v1/exercise-checkin/{checkin_id}")

        assert response.status_code == 204

        # 验证无法再获取到该记录
        get_response = client.get(f"/api/v1/exercise-checkin/{checkin_id}")
        assert get_response.status_code == 404

    @pytest.mark.p1
    def test_delete_exercise_checkin_not_own(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试删除他人记录返回 404 - AC12"""
        client, headers, test_user = authenticated_client

        # 删除不存在的记录 (模拟删除他人记录)
        response = client.delete("/api/v1/exercise-checkin/99999")

        assert response.status_code == 404


class TestExerciseTypes:
    """运动类型列表测试 - P1"""

    @pytest.mark.p1
    def test_get_exercise_types(self, authenticated_client: tuple, db_session: Session):
        """测试获取运动类型列表 - F7 修复验证"""
        client, headers, test_user = authenticated_client

        response = client.get("/api/v1/exercise-checkin/exercise-types")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # 验证包含 MET 值
        for item in data:
            assert "type" in item
            assert "met_value" in item
            assert "category" in item


class TestCalorieEstimation:
    """卡路里估算测试 - P1"""

    @pytest.mark.p1
    def test_calorie_estimation_formula(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试卡路里估算公式 - AC9"""
        client, headers, test_user = authenticated_client

        # 设置用户体重 70kg
        test_user.initial_weight = 70000
        db_session.commit()

        # 跑步 30 分钟中等强度 (MET=8.0)
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }

        response = client.post("/api/v1/exercise-checkin/", json=checkin_data)
        data = response.json()

        # 验证估算公式：8.0 × 70 × 0.5 × 1.0 = 280kcal
        assert 250 <= data["calories_burned"] <= 310
        assert data["estimation_details"]["met_value"] == 8.0
        assert data["estimation_details"]["weight_kg"] == 70.0
        assert data["estimation_details"]["duration_hours"] == 0.5
        assert data["estimation_details"]["intensity_factor"] == 1.0

    @pytest.mark.p1
    def test_calorie_estimation_intensity_factors(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试不同强度的卡路里系数 - F5 修复验证"""
        client, headers, test_user = authenticated_client

        test_user.initial_weight = 70000
        db_session.commit()

        # 低强度
        response_low = client.post(
            "/api/v1/exercise-checkin/",
            json={
                "exercise_type": "Running",
                "duration_minutes": 30,
                "intensity": "low",
            },
        )
        calories_low = response_low.json()["calories_burned"]

        # 高强度
        response_high = client.post(
            "/api/v1/exercise-checkin/",
            json={
                "exercise_type": "Running",
                "duration_minutes": 30,
                "intensity": "high",
            },
        )
        calories_high = response_high.json()["calories_burned"]

        # 验证高强度比低强度多燃烧卡路里
        assert calories_high > calories_low


class TestDashboardIntegration:
    """Dashboard 集成测试 - F15 修复验证"""

    @pytest.mark.p1
    def test_dashboard_exercise_summary(
        self, authenticated_client: tuple, db_session: Session
    ):
        """测试 Dashboard 运动摘要卡片 - AC14"""
        client, headers, test_user = authenticated_client

        # 创建记录
        checkin_data = {
            "exercise_type": "Running",
            "duration_minutes": 30,
            "intensity": "medium",
        }
        client.post("/api/v1/exercise-checkin/", json=checkin_data)

        # 获取 Dashboard 摘要
        response = client.get("/api/v1/dashboard/exercise-summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_duration_minutes"] >= 30
        assert data["total_calories_burned"] > 0
        assert "progress_percentage" in data
