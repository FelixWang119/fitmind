"""
通知系统 API 测试

测试通知系统的所有 API 端点
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.notification import Notification
from datetime import datetime


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestNotificationAPI:
    """通知 API 测试类"""

    def test_get_notifications_requires_auth(self, client):
        """测试获取通知列表需要认证"""
        response = client.get("/api/v1/notifications")
        assert response.status_code == 401

    def test_get_unread_count_requires_auth(self, client):
        """测试获取未读数量需要认证"""
        response = client.get("/api/v1/notifications/unread-count")
        assert response.status_code == 401

    def test_get_notification_settings_requires_auth(self, client):
        """测试获取通知设置需要认证"""
        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 401

    def test_update_settings_requires_auth(self, client):
        """测试更新设置需要认证"""
        response = client.put("/api/v1/notifications/settings", json={})
        assert response.status_code == 401


class TestNotificationAPIWithAuth:
    """带认证的通知 API 测试"""

    @pytest.fixture
    def auth_client(self, authenticated_client):
        """创建认证客户端"""
        client, headers, user = authenticated_client
        return client, headers, user

    def test_get_notifications_empty(self, auth_client):
        """测试获取空通知列表"""
        client, headers, user = auth_client

        response = client.get(
            "/api/v1/notifications", params={"page": 1, "page_size": 20}
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "unread_count" in data

    def test_get_unread_count(self, auth_client):
        """测试获取未读数量"""
        client, headers, user = auth_client

        response = client.get("/api/v1/notifications/unread-count")

        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)

    def test_get_notification_settings(self, auth_client):
        """测试获取通知设置"""
        client, headers, user = auth_client

        response = client.get("/api/v1/notifications/settings")

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "do_not_disturb_enabled" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
