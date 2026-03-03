"""
Notification API Tests

Tests for Epic 8: Notification System Integration
Priority: P0 (Critical)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification, UserNotificationSetting
from app.core.security import create_access_token

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_notifications.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create test database session."""
    # Create tables
    from app.models import Base

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        from app.models import Base

        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(db_session):
    """Create authenticated user and return headers."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create access token
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}, user.id


class TestNotificationAPI:
    """Test notification API endpoints."""

    def test_get_notifications_requires_auth(self, client):
        """P0: Should reject unauthenticated requests."""
        response = client.get("/api/v1/notifications")
        assert response.status_code == 401

    def test_get_notifications_success(self, client, auth_headers):
        """P0: Should return notification list for authenticated user."""
        headers, user_id = auth_headers

        response = client.get("/api/v1/notifications", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "unread_count" in data

    def test_get_notifications_pagination(self, client, auth_headers, db_session):
        """P1: Should support pagination parameters."""
        headers, user_id = auth_headers

        # Create test notifications
        for i in range(25):
            notification = Notification(
                user_id=user_id,
                title=f"Test Notification {i}",
                content=f"Content {i}",
                notification_type="system",
                is_read=False,
            )
            db_session.add(notification)
        db_session.commit()

        response = client.get(
            "/api/v1/notifications?page=1&page_size=10", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 25

    def test_get_notifications_unread_only(self, client, auth_headers, db_session):
        """P1: Should filter by unread status."""
        headers, user_id = auth_headers

        # Create mixed notifications
        for i in range(5):
            notification = Notification(
                user_id=user_id,
                title=f"Unread {i}",
                content=f"Content {i}",
                notification_type="system",
                is_read=False,
            )
            db_session.add(notification)
        for i in range(3):
            notification = Notification(
                user_id=user_id,
                title=f"Read {i}",
                content=f"Content {i}",
                notification_type="system",
                is_read=True,
            )
            db_session.add(notification)
        db_session.commit()

        response = client.get("/api/v1/notifications?unread_only=true", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should only return unread notifications
        for item in data["items"]:
            assert item["is_read"] is True or item.get("is_read") == True

    def test_get_unread_count(self, client, auth_headers, db_session):
        """P0: Should return correct unread count."""
        headers, user_id = auth_headers

        # Create notifications
        for i in range(7):
            notification = Notification(
                user_id=user_id,
                title=f"Test {i}",
                content=f"Content {i}",
                notification_type="system",
                is_read=False,
            )
            db_session.add(notification)
        db_session.commit()

        response = client.get("/api/v1/notifications/unread-count", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] >= 7

    def test_mark_as_read(self, client, auth_headers, db_session):
        """P0: Should mark notification as read."""
        headers, user_id = auth_headers

        # Create notification
        notification = Notification(
            user_id=user_id,
            title="Test Notification",
            content="Test Content",
            notification_type="system",
            is_read=False,
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        response = client.post(
            f"/api/v1/notifications/{notification.id}/read", headers=headers
        )

        assert response.status_code == 200

        # Verify notification is marked as read
        db_session.refresh(notification)
        assert notification.is_read is True

    def test_mark_all_as_read(self, client, auth_headers, db_session):
        """P0: Should mark all notifications as read."""
        headers, user_id = auth_headers

        # Create notifications
        for i in range(5):
            notification = Notification(
                user_id=user_id,
                title=f"Test {i}",
                content=f"Content {i}",
                notification_type="system",
                is_read=False,
            )
            db_session.add(notification)
        db_session.commit()

        response = client.post("/api/v1/notifications/mark-all-read", headers=headers)

        assert response.status_code == 200

        # Verify all notifications are read
        notifications = (
            db_session.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .all()
        )
        assert len(notifications) == 0

    def test_delete_notification(self, client, auth_headers, db_session):
        """P1: Should delete notification."""
        headers, user_id = auth_headers

        # Create notification
        notification = Notification(
            user_id=user_id,
            title="Test Notification",
            content="Test Content",
            notification_type="system",
            is_read=False,
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)
        notification_id = notification.id

        response = client.delete(
            f"/api/v1/notifications/{notification_id}", headers=headers
        )

        assert response.status_code == 200

        # Verify notification is deleted
        deleted = (
            db_session.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        assert deleted is None


class TestNotificationSettingsAPI:
    """Test notification settings API endpoints."""

    def test_get_settings_requires_auth(self, client):
        """P0: Should reject unauthenticated requests."""
        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 401

    def test_get_settings_success(self, client, auth_headers, db_session):
        """P1: Should return user notification settings."""
        headers, user_id = auth_headers

        # Create settings
        settings = UserNotificationSetting(
            user_id=user_id,
            enabled=True,
            notify_habit_reminder=True,
            notify_milestone=True,
            notify_care=True,
            notify_system=True,
        )
        db_session.add(settings)
        db_session.commit()

        response = client.get("/api/v1/notifications/settings", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "notify_habit_reminder" in data

    def test_update_settings(self, client, auth_headers, db_session):
        """P1: Should update notification settings."""
        headers, user_id = auth_headers

        response = client.put(
            "/api/v1/notifications/settings",
            headers=headers,
            json={"enabled": False, "notify_habit_reminder": False},
        )

        assert response.status_code == 200

        # Verify settings updated
        settings = (
            db_session.query(UserNotificationSetting)
            .filter(UserNotificationSetting.user_id == user_id)
            .first()
        )

        assert settings is not None
        assert settings.enabled is False
        assert settings.notify_habit_reminder is False
