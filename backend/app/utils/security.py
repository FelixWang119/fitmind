"""
数据加密工具
用于敏感健康数据的加密存储
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json


class DataEncryptor:
    """数据加密器"""

    def __init__(self, encryption_key: str = None):
        """
        初始化加密器

        Args:
            encryption_key: 加密密钥，如果为 None 则从环境变量读取
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")

        if not self.encryption_key:
            # 开发环境：生成临时密钥（不推荐生产使用）
            self.encryption_key = Fernet.generate_key().decode()
            print(
                "⚠️  WARNING: Using temporary encryption key. Set ENCRYPTION_KEY environment variable!"
            )

        self._cipher = Fernet(self.encryption_key.encode())

    def encrypt(self, data: dict) -> str:
        """
        加密字典数据

        Args:
            data: 要加密的字典

        Returns:
            加密后的字符串
        """
        if not data:
            return ""

        json_data = json.dumps(data, ensure_ascii=False)
        encrypted = self._cipher.encrypt(json_data.encode("utf-8"))
        return base64.urlsafe_b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> dict:
        """
        解密数据

        Args:
            encrypted_data: 加密的字符串

        Returns:
            解密后的字典
        """
        if not encrypted_data:
            return {}

        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
            decrypted = self._cipher.decrypt(decoded)
            return json.loads(decrypted.decode("utf-8"))
        except Exception as e:
            print(f"❌ Decryption failed: {str(e)}")
            return {}

    @staticmethod
    def generate_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode()


# 全局加密器实例
_encryptor = None


def get_encryptor() -> DataEncryptor:
    """获取全局加密器实例"""
    global _encryptor
    if _encryptor is None:
        _encryptor = DataEncryptor()
    return _encryptor


def encrypt_health_data(data: dict) -> str:
    """加密健康数据"""
    return get_encryptor().encrypt(data)


def decrypt_health_data(encrypted_data: str) -> dict:
    """解密健康数据"""
    return get_encryptor().decrypt(encrypted_data)
