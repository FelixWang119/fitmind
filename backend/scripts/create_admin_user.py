"""创建管理员测试账号"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash
from app.services.config_initializer import initialize_all_configs
from datetime import datetime

def create_admin_user():
    """创建管理员账号"""
    db = SessionLocal()
    
    try:
        existing = db.query(User).filter(User.email == "admin@fitmind.com").first()
        if existing:
            print("⚠️  管理员账号已存在")
            return False
        
        admin = User(
            email="admin@fitmind.com",
            username="admin",
            hashed_password=get_password_hash("admin123456"),
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow(),
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ 管理员账号创建成功！")
        print(f"   邮箱：admin@fitmind.com")
        print(f"   密码：admin123456")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败：{e}")
        return False
    finally:
        db.close()

def initialize_configs():
    """初始化系统配置"""
    db = SessionLocal()
    try:
        count = initialize_all_configs(db)
        print(f"✅ 初始化 {count} 个系统配置")
        return True
    except Exception as e:
        print(f"❌ 配置初始化失败：{e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 创建管理员账号和初始化配置...")
    print("=" * 50)
    create_admin_user()
    initialize_configs()
    print("=" * 50)
    print("✅ 完成！")
