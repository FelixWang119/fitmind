"""测试配置"""

import os
import sys

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["ALGORITHM"] = "HS256"

# 导入应用
from app.main import app

print("✅ 测试配置加载成功")
print(f"应用标题: {app.title}")
print(f"环境: {os.environ.get('ENVIRONMENT')}")
print(f"数据库URL: {os.environ.get('DATABASE_URL')}")
