"""Basic tests for the backend application."""

import warnings


def test_import():
    """Test that the app can be imported."""
    # 忽略SQLAlchemy 2.0警告
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)
        from app.main import app

        assert app is not None
        assert app.title == "Weight AI Backend"


def test_health_check():
    """Test the health check endpoint."""
    # 忽略SQLAlchemy 2.0警告
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


def test_root_endpoint():
    """Test the root endpoint."""
    # 忽略SQLAlchemy 2.0警告
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "environment" in data
