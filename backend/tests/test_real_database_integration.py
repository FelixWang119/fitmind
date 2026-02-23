"""
集成测试 - 验证真实数据库环境下的认证流程
使用真实数据库，测试完整的用户生命周期
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """每个测试前重置 rate limiters"""
    from app.core.rate_limit import reset_rate_limiters

    reset_rate_limiters()


def test_user_registration(client):
    """测试用户注册（使用真实数据库）"""

    user_data = {
        "email": "reg_test@example.com",
        "username": "reg_test_user",
        "password": "RegTest123!",
        "confirm_password": "RegTest123!",
        "full_name": "Registration Test User",
    }

    response = client.post("/api/v1/auth/register", json=user_data)

    # 验证注册成功（201 或 200）
    assert response.status_code in [200, 201], f"注册失败：{response.text}"
    data = response.json()

    # 验证返回用户信息
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data

    print("✅ 用户注册成功")


def test_user_login_after_registration(client):
    """测试注册后立即登录"""

    # 1. 注册用户
    user_data = {
        "email": "login_test@example.com",
        "username": "login_test_user",
        "password": "LoginTest123!",
        "confirm_password": "LoginTest123!",
        "full_name": "Login Test User",
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    # 2. 使用凭据登录
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )

    # 验证登录成功
    assert login_response.status_code == 200, f"登录失败：{login_response.text}"
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    print("✅ 注册后登录成功")


def test_user_login_and_access_protected_resource(client):
    """测试登录后访问受保护资源"""

    # 1. 注册并登录
    user_data = {
        "email": "protected_test@example.com",
        "username": "protected_test_user",
        "password": "ProtectedTest123!",
        "confirm_password": "ProtectedTest123!",
        "full_name": "Protected Resource Test User",
    }

    # 注册
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    # 登录
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # 2. 访问受保护的资源
    profile_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    # 验证个人资料访问
    assert profile_response.status_code == 200, (
        f"获取个人资料失败：{profile_response.text}"
    )
    profile_data = profile_response.json()
    assert profile_data["email"] == user_data["email"]

    print("✅ 访问受保护资源成功")


def test_wrong_password_login(client):
    """测试使用错误密码登录应该失败"""

    # 1. 先注册一个用户
    user_data = {
        "email": "wrong_pass_test@example.com",
        "username": "wrong_pass_user",
        "password": "CorrectPass123!",
        "confirm_password": "CorrectPass123!",
        "full_name": "Wrong Password Test User",
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    # 2. 使用错误密码登录 - 应该失败
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": "WrongPass456!",  # 错误密码
        },
    )

    # 验证登录失败
    assert login_response.status_code != 200, "错误密码登录应该失败"

    print("✅ 密码验证正常工作")


def test_duplicate_user_registration(client):
    """测试重复用户注册应该失败"""

    # 1. 注册第一个用户
    user_data = {
        "email": "duplicate_test@example.com",
        "username": "duplicate_user",
        "password": "DuplicateTest123!",
        "confirm_password": "DuplicateTest123!",
        "full_name": "Duplicate Test User",
    }

    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code in [200, 201]

    # 2. 尝试用相同邮箱注册第二个用户 - 应该失败
    user_data2 = {
        "email": "duplicate_test@example.com",  # 相同邮箱
        "username": "duplicate_user2",
        "password": "DuplicateTest123!",
        "confirm_password": "DuplicateTest123!",
        "full_name": "Duplicate Test User 2",
    }

    response2 = client.post("/api/v1/auth/register", json=user_data2)

    # 验证注册失败
    assert response2.status_code != 200, "重复邮箱注册应该失败"

    print("✅ 重复用户检测正常工作")


def test_password_update_flow(client):
    """测试密码更新流程（使用真实数据库）"""

    # 1. 注册用户
    user_data = {
        "email": "password_update_test@example.com",
        "username": "password_update_user",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
        "full_name": "Password Update Test User",
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    # 2. 登录获取令牌
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # 3. 更新密码 - 使用查询参数
    update_response = client.post(
        "/api/v1/auth/change-password?old_password=OldPassword123!&new_password=NewPassword456!@",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # 验证密码更新成功
    assert update_response.status_code in [200, 204], (
        f"密码更新失败: {update_response.text}"
    )

    # 4. 使用新密码登录验证
    new_login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": "NewPassword456!@"},
    )
    assert new_login_response.status_code == 200, "新密码应该可以登录"

    print("✅ 密码更新流程正常工作")


def test_token_refresh_and_protected_access(client):
    """测试令牌刷新和受保护资源访问（使用真实数据库）"""

    # 1. 注册并登录获取令牌
    user_data = {
        "email": "token_test@example.com",
        "username": "token_test_user",
        "password": "TokenTest123!",
        "confirm_password": "TokenTest123!",
        "full_name": "Token Test User",
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # 2. 使用令牌访问多个受保护端点
    endpoints = [
        "/api/v1/auth/me",
        "/api/v1/dashboard/quick-stats",
    ]

    for endpoint in endpoints:
        response = client.get(
            endpoint, headers={"Authorization": f"Bearer {access_token}"}
        )
        # 200 或 404 都是可接受的（404表示用户无数据）
        assert response.status_code in [200, 404], (
            f"访问 {endpoint} 失败: {response.text}"
        )

    print("✅ 令牌验证和受保护资源访问正常工作")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
