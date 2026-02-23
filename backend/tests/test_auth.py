"""用户认证测试

测试优先级标记：
- @pytest.mark.p0: 核心功能（注册、登录、认证），必须通过
- @pytest.mark.p1: 重要功能（个人资料、密码更新）
- @pytest.mark.p2: 一般功能（速率限制、边界情况）
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.rate_limit import reset_rate_limiters


class TestUserRegistration:
    """用户注册测试 - P0 核心功能"""

    def setup_method(self):
        """每个测试方法前重置速率限制器"""
        reset_rate_limiters()

    @pytest.mark.p0
    def test_register_success(self, client: TestClient, db_session: Session):
        """测试成功注册 - P0 核心功能"""
        # 准备测试数据
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Pass12345",  # 8字符密码满足要求
            "confirm_password": "Pass12345",
            "full_name": "Test User",
            "age": 30,
            "gender": "male",
            "height": 175,
            "initial_weight": 80000,  # 80kg in grams
            "target_weight": 70000,  # 70kg in grams
            "activity_level": "moderate",
        }

        # 发送注册请求
        response = client.post("/api/v1/auth/register", json=user_data)

        # 验证响应
        assert response.status_code == 201
        data = response.json()

        # 验证返回的用户数据
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # 密码不应返回
        assert "hashed_password" not in data

    @pytest.mark.p0
    def test_register_duplicate_email(self, client: TestClient, db_session: Session):
        """测试重复邮箱注册 - P0 核心功能验证"""
        # 先创建一个用户
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 尝试用相同邮箱注册
        duplicate_data = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "Pass45678",
            "confirm_password": "Pass45678",
        }

        response = client.post("/api/v1/auth/register", json=duplicate_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "validation_error"
        assert "message" in data["detail"]
        assert (
            "email" in data["detail"]["message"].lower()
            or "registered" in data["detail"]["message"].lower()
        )

    @pytest.mark.p1
    def test_register_duplicate_username(self, client: TestClient, db_session: Session):
        """测试重复用户名注册 - P1 重要验证"""
        # 先创建一个用户
        user_data = {
            "email": "user1@example.com",
            "username": "duplicate_user",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 尝试用相同用户名注册
        duplicate_data = {
            "email": "user2@example.com",
            "username": "duplicate_user",
            "password": "Pass45678",
            "confirm_password": "Pass45678",
        }

        response = client.post("/api/v1/auth/register", json=duplicate_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "validation_error"
        assert "message" in data["detail"]
        assert (
            "username" in data["detail"]["message"].lower()
            or "taken" in data["detail"]["message"].lower()
        )

    @pytest.mark.p0
    def test_register_password_all_numbers(self, client: TestClient):
        """测试纯数字弱密码应失败 - 边界条件测试"""
        user_data = {
            "email": "allnumbers@example.com",
            "username": "allnumbersuser",
            "password": "12345678",  # 纯数字，缺少字母
            "confirm_password": "12345678",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # 验证失败
        data = response.json()
        assert "detail" in data

    @pytest.mark.p0
    def test_register_password_all_letters(self, client: TestClient):
        """测试纯字母弱密码应失败 - 边界条件测试"""
        user_data = {
            "email": "allletters@example.com",
            "username": "alllettersuser",
            "password": "abcdefgh",  # 纯字母，缺少数字
            "confirm_password": "abcdefgh",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # 验证失败
        data = response.json()
        assert "detail" in data

    @pytest.mark.p0
    def test_register_username_optional(self, client: TestClient):
        """测试用户名为可选项 - 修复 AC 1 问题"""
        user_data = {
            "email": "nousername@example.com",
            # username 字段省略，应为可选
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201  # 注册成功
        data = response.json()
        assert data["email"] == user_data["email"]

    @pytest.mark.p0
    def test_register_email_invalid_format(self, client: TestClient):
        """测试无效邮箱格式应失败 - 边界条件测试"""
        user_data = {
            "email": "invalidemail@",  # 无效邮箱
            "username": "testuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # 验证失败
        data = response.json()
        assert "detail" in data

    @pytest.mark.p0
    def test_register_password_too_short(self, client: TestClient):
        """测试密码太短应失败 - 边界条件测试"""
        user_data = {
            "email": "shortpass@example.com",
            "username": "shortpassuser",
            "password": "Pass1",  # 少于 8 位
            "confirm_password": "Pass1",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # 验证失败
        data = response.json()
        assert "detail" in data

    def test_register_weak_password(self, client: TestClient):
        """测试弱密码注册"""
        user_data = {
            "email": "weakpass@example.com",
            "username": "weakuser",
            "password": "weak",  # 太短
            "confirm_password": "weak",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Pydantic验证错误
        data = response.json()
        assert "detail" in data

    def test_register_password_mismatch(self, client: TestClient):
        """测试密码不匹配"""
        user_data = {
            "email": "mismatch@example.com",
            "username": "mismatchuser",
            "password": "StrongPass123",
            "confirm_password": "DifferentPass123",  # 不匹配
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Pydantic验证错误
        data = response.json()
        assert "detail" in data

    def test_register_invalid_email(self, client: TestClient):
        """测试无效邮箱格式"""
        user_data = {
            "email": "invalid-email",
            "username": "invaliduser",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Pydantic验证错误
        data = response.json()
        assert "detail" in data

    def test_register_missing_required_fields(self, client: TestClient):
        """测试缺少必填字段"""
        # 缺少邮箱
        user_data = {
            "username": "missingemail",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Pydantic验证错误
        data = response.json()
        assert "detail" in data


class TestUserLogin:
    """用户登录测试"""

    def setup_method(self):
        """每个测试方法前重置速率限制器"""
        reset_rate_limiters()

    def test_login_success(self, client: TestClient, db_session: Session):
        """测试成功登录"""
        # 先注册一个用户
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 登录
        login_data = {"username": "login@example.com", "password": "Pass12345"}

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()

        # 验证返回的令牌
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    def test_login_wrong_password(self, client: TestClient, db_session: Session):
        """测试错误密码登录"""
        # 先注册一个用户
        user_data = {
            "email": "wrongpass@example.com",
            "username": "wrongpassuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 用错误密码登录
        login_data = {
            "username": "wrongpass@example.com",
            "password": "WrongPass1",
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "authentication_error"
        assert "message" in data["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """测试不存在的用户登录"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "SomePass1",
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "authentication_error"
        assert "message" in data["detail"]
        # 检查是否为"邮箱未注册"错误消息
        assert "邮箱未注册" in data["detail"]["message"]

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """测试非活跃用户登录"""
        # 先注册一个用户
        user_data = {
            "email": "inactive@example.com",
            "username": "inactiveuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 从数据库获取用户并设置为非活跃
        from app.models.user import User

        user = (
            db_session.query(User).filter(User.email == "inactive@example.com").first()
        )
        if user:
            user.is_active = False  # type: ignore
            db_session.commit()

        # 尝试登录
        login_data = {
            "username": "inactive@example.com",
            "password": "Pass12345",
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "authentication_error"
        assert "message" in data["detail"]
        # 检查是否为"账户已被禁用"错误消息
        assert "账户已被禁用" in data["detail"]["message"]

    def test_login_error_messages_differentiation(
        self, client: TestClient, db_session: Session
    ):
        """测试错误消息区分：邮箱未注册 vs 密码错误"""
        # 测试不存在的用户 - 应该返回"邮箱未注册"
        login_data_nonexistent = {
            "username": "nonexistent2@example.com",
            "password": "SomePass1",
        }

        response = client.post("/api/v1/auth/login", data=login_data_nonexistent)
        assert response.status_code == 401
        data = response.json()
        assert "邮箱未注册" in data["detail"]["message"]

        # 注册一个用户
        user_data = {
            "email": "errortest@example.com",
            "username": "errortestuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 测试错误密码 - 应该返回"密码错误"
        login_data_wrong_pass = {
            "username": "errortest@example.com",
            "password": "WrongPass1",
        }

        response = client.post("/api/v1/auth/login", data=login_data_wrong_pass)
        assert response.status_code == 401
        data = response.json()
        assert "密码错误" in data["detail"]["message"]


class TestUserProfile:
    """用户个人信息测试"""

    def setup_method(self):
        """每个测试方法前重置速率限制器"""
        reset_rate_limiters()

    def test_get_current_user(self, client: TestClient, db_session: Session):
        """测试获取当前用户信息"""
        # 注册并登录
        user_data = {
            "email": "profile@example.com",
            "username": "profileuser",
            "password": "Pass12345",
            "confirm_password": "Pass12345",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)

        # 登录获取令牌
        login_data = {"username": "profile@example.com", "password": "Pass12345"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # 获取当前用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # 验证用户信息
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "created_at" in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        """测试未授权访问用户信息"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestRateLimiting:
    """速率限制测试"""

    def setup_method(self):
        """每个测试方法前重置速率限制器"""
        reset_rate_limiters()

    def test_registration_rate_limit(self, client: TestClient):
        """测试注册速率限制"""
        # 快速发送多个注册请求
        for i in range(6):  # 超过5次限制
            user_data = {
                "email": f"ratelimit{i}@example.com",
                "username": f"ratelimituser{i}",
                "password": "Pass12345",
                "confirm_password": "Pass12345",
            }
            response = client.post("/api/v1/auth/register", json=user_data)

            if i >= 5:  # 第6次应该被限制
                assert response.status_code == 429
                data = response.json()
                assert "detail" in data
                assert data["detail"]["error"] == "Too many registration requests"
                assert "message" in data["detail"]
                assert "retry_after" in data["detail"]
                assert "remaining" in data["detail"]
                break

    def test_login_rate_limit(self, client: TestClient):
        """测试登录速率限制"""
        # 快速发送多个登录请求（使用不存在的用户）
        for i in range(11):  # 超过10次限制（登录限制是10次/分钟）
            login_data = {
                "username": f"loginratelimit{i}@example.com",
                "password": "WrongPass1",
            }
            response = client.post("/api/v1/auth/login", data=login_data)

            if i >= 10:  # 第11次应该被限制
                assert response.status_code == 429
                data = response.json()
                assert "detail" in data
                assert data["detail"]["error"] == "Too many login attempts"
                assert "message" in data["detail"]
                assert "retry_after" in data["detail"]
                assert "remaining" in data["detail"]
                break

    def test_rate_limit_reset(self, client: TestClient):
        """测试速率限制重置"""
        from app.core.rate_limit import reset_rate_limiters

        # 先触发速率限制（需要11次请求）
        for i in range(11):
            login_data = {
                "username": f"resetlimit{i}@example.com",
                "password": "WrongPass1",
            }
            response = client.post("/api/v1/auth/login", data=login_data)

            if i >= 10:
                assert response.status_code == 429

        # 重置速率限制器
        reset_rate_limiters()

        # 再次尝试应该成功（返回401而不是429）
        login_data = {
            "username": "resetlimit11@example.com",
            "password": "WrongPass1",
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401  # 用户不存在，但不是速率限制
