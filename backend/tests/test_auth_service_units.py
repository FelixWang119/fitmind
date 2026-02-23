"""
用户认证服务测试 - 使用正确的测试fixtures
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user_password,
    verify_token,
    verify_password,
    get_password_hash,
)
from app.models.user import User as UserModel
from app.schemas.user import TokenData


class TestAuthService:
    """认证服务测试 - 使用单元测试mock而不是真实数据库"""

    def test_authenticate_user_success(self):
        """测试用户认证成功"""
        # 创建模拟数据库会话
        mock_db = Mock()

        # 模拟用户数据
        mock_user = Mock(spec=UserModel)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("ValidPass1")
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.full_name = "Test User"

        # 模拟查询结果
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # 调用认证函数
        result = authenticate_user(mock_db, "test@example.com", "ValidPass1")

        # 断言结果
        assert result is not None
        assert result == mock_user

    def test_authenticate_user_invalid_credentials(self):
        """测试用户认证失败（邮箱不存在）"""
        # 创建模拟数据库会话
        mock_db = Mock()

        # 模拟查询返回 None（无此用户）
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # 调用认证函数并捕获异常
        with pytest.raises(ValueError) as exc_info:
            authenticate_user(mock_db, "nonexistent@example.com", "wrongpass")

        assert str(exc_info.value) == "邮箱未注册"

    def test_authenticate_user_wrong_password(self):
        """测试用户认证失败（密码错误）"""
        # 创建模拟数据库会话
        mock_db = Mock()

        # 模拟用户数据
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("CorrectPass123!")
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.full_name = "Test User"

        # 模拟查询返回用户
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # 调用认证函数并捕获异常
        with pytest.raises(ValueError) as exc_info:
            authenticate_user(mock_db, "test@example.com", "wrongpassword")

        assert str(exc_info.value) == "密码错误"

    def test_authenticate_user_inactive_user(self):
        """测试认证失败（用户未激活）"""
        # 创建模拟数据库会话
        mock_db = Mock()

        # 模拟未激活的用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("ValidPass1")
        mock_user.is_active = False
        mock_user.is_superuser = False
        mock_user.full_name = "Test User"

        # 模拟查询返回未激活的用户
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # 调用认证函数并捕获异常
        with pytest.raises(ValueError) as exc_info:
            authenticate_user(mock_db, "test@example.com", "ValidPass1")

        assert str(exc_info.value) == "账户已被禁用"

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)

        # 应该返回非空的字符串令牌
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_expires_custom(self):
        """测试创建带有自定义过期时间的令牌"""
        data = {"sub": "test@example.com", "user_id": 1}
        expires = timedelta(minutes=10)
        token = create_access_token(data, expires_delta=expires)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_invalid(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.format"
        result = verify_token(invalid_token)

        # 无效令牌应该返回 None
        assert result is None

    def test_verify_token_none_input(self):
        """测试验证None输入的令牌"""
        # verify_token函数需要字符串输入，传入None会抛异常
        # 这是一个边界情况，函数本身应该处理这种情况
        with pytest.raises(Exception):  # 预期会抛出异常
            verify_token(None)

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        plain_password = "CorrectPass123!"
        hashed = get_password_hash(plain_password)

        result = verify_password(plain_password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        plain_password = "CorrectPass123!"
        wrong_password = "WrongPass456!"
        hashed = get_password_hash(plain_password)

        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_get_password_hash(self):
        """测试密码哈希"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # 哈希应该是非空字符串
        assert isinstance(hashed, str)
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")

        # 应该可以被验证
        assert verify_password(password, hashed) is True

    def test_authenticate_user_empty_credentials(self):
        """测试使用空凭证进行认证"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError):
            authenticate_user(mock_db, "", "")

    def test_authenticate_user_whitespace_only_email(self):
        """测试使用空白字符邮箱进行认证"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError):
            authenticate_user(mock_db, "   ", "password")

    def test_update_user_password(self):
        """测试更新用户密码"""
        # 创建模拟用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.full_name = "Test User"

        mock_db = Mock()

        new_password = "NewSecurePass456!"

        # 调用更新密码函数 - 使用patch避免实际调用
        with patch("app.services.auth_service.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"
            # 调用函数
            update_user_password(mock_db, mock_user, new_password)

        # 验证数据库事务被调用
        assert mock_db.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
