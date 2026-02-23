"""
健康数据 API 端点测试

覆盖功能：
- 健康记录 CRUD 操作
- 健康数据摘要
- 日期过滤
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.models.health_record import HealthRecord
from app.models.user import User
from app.services.auth_service import get_password_hash


class TestHealthDataEndpoints:
    """健康数据端点测试"""

    def test_get_health_records_requires_auth(self, client: TestClient):
        """测试获取健康记录需要认证"""
        response = client.get("/api/v1/health/records")
        assert response.status_code == 401

    def test_get_health_records_with_auth(self, authenticated_client):
        """测试获取健康记录列表（已认证）"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/health/records", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data

    def test_get_health_records_with_date_filter(
        self, authenticated_client, db_session
    ):
        """测试按日期过滤健康记录"""
        client, headers, user = authenticated_client

        # 创建测试记录
        record = HealthRecord(
            user_id=user.id,
            weight=70000,
            record_date=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()

        # 测试日期过滤
        start_date = (datetime.utcnow() - timedelta(days=1)).date()
        end_date = (datetime.utcnow() + timedelta(days=1)).date()

        response = client.get(
            f"/api/v1/health/records?start_date={start_date}&end_date={end_date}",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "records" in data

    def test_create_health_record(self, authenticated_client):
        """测试创建健康记录"""
        client, headers, user = authenticated_client

        record_data = {
            "weight": 70000,
            "record_date": datetime.utcnow().isoformat(),
            "heart_rate": 75,
            "sleep_hours": 7.5,
        }

        response = client.post(
            "/api/v1/health/records", json=record_data, headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["weight"] == 70000
        assert data["heart_rate"] == 75

    def test_create_duplicate_date_record_fails(self, authenticated_client, db_session):
        """测试创建重复日期的健康记录应失败"""
        client, headers, user = authenticated_client
        now = datetime.utcnow()

        # 创建第一条记录
        record_data = {
            "weight": 70000,
            "record_date": now.isoformat(),
        }

        response = client.post(
            "/api/v1/health/records", json=record_data, headers=headers
        )
        assert response.status_code == 201

        # 尝试创建同一天的记录
        response = client.post(
            "/api/v1/health/records", json=record_data, headers=headers
        )
        assert response.status_code == 400

    def test_get_single_health_record(self, authenticated_client, db_session):
        """测试获取单个健康记录"""
        client, headers, user = authenticated_client

        # 创建记录
        record = HealthRecord(
            user_id=user.id,
            weight=70000,
            record_date=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        # 获取单条记录
        response = client.get(f"/api/v1/health/records/{record.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == 70000

    def test_get_nonexistent_record_fails(self, authenticated_client):
        """测试获取不存在的健康记录应失败"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/health/records/99999", headers=headers)
        assert response.status_code == 404

    def test_update_health_record(self, authenticated_client, db_session):
        """测试更新健康记录"""
        client, headers, user = authenticated_client

        # 创建记录
        record = HealthRecord(
            user_id=user.id,
            weight=70000,
            record_date=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        # 更新记录
        update_data = {
            "weight": 69000,
            "heart_rate": 72,
        }

        response = client.put(
            f"/api/v1/health/records/{record.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == 69000
        assert data["heart_rate"] == 72

    def test_delete_health_record(self, authenticated_client, db_session):
        """测试删除健康记录"""
        client, headers, user = authenticated_client

        # 创建记录
        record = HealthRecord(
            user_id=user.id,
            weight=70000,
            record_date=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        record_id = record.id

        # 删除记录
        response = client.delete(f"/api/v1/health/records/{record_id}", headers=headers)
        assert response.status_code == 204

        # 验证记录已删除
        response = client.get(f"/api/v1/health/records/{record_id}", headers=headers)
        assert response.status_code == 404

    def test_get_health_summary(self, authenticated_client, db_session):
        """测试获取健康数据摘要"""
        client, headers, user = authenticated_client

        # 创建多条记录
        for i in range(5):
            record = HealthRecord(
                user_id=user.id,
                weight=70000 + i * 100,
                record_date=datetime.utcnow() - timedelta(days=i),
                heart_rate=70 + i,
                sleep_hours=7.0 + i * 0.5,
            )
            db_session.add(record)
        db_session.commit()

        response = client.get("/api/v1/health/records/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        summary = data["summary"]
        assert summary["total_records"] == 5

    def test_cannot_access_other_users_record(self, authenticated_client, db_session):
        """测试不能访问其他用户的健康记录"""
        client, headers, user = authenticated_client

        # 创建另一个用户和记录
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        other_record = HealthRecord(
            user_id=other_user.id,
            weight=80000,
            record_date=datetime.utcnow(),
        )
        db_session.add(other_record)
        db_session.commit()
        db_session.refresh(other_record)

        # 尝试访问其他用户的记录
        response = client.get(
            f"/api/v1/health/records/{other_record.id}", headers=headers
        )
        assert response.status_code == 404
