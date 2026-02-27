import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash
from datetime import datetime
import uuid

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == "admin@fitmind.com").first()
    if existing:
        print("⚠️  管理员账号已存在")
    else:
        admin = User(
            id=uuid.uuid4(),
            email="admin@fitmind.com",
            username="admin",
            hashed_password=get_password_hash("admin123456"),
            is_active=True,
            created_at=datetime.now(),
        )
        db.add(admin)
        db.commit()
        print("\n✅ 管理员账号创建成功！")
        print("=" * 50)
        print("📧 邮箱：admin@fitmind.com")
        print("🔑 密码：admin123456")
        print("=" * 50)
except Exception as e:
    print(f"❌ 创建失败：{e}")
    db.rollback()
finally:
    db.close()
