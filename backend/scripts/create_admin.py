import sys, os, uuid
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import bcrypt

def create_admin():
    try:
        engine = create_engine(settings.DATABASE_URL)
        password_hash = bcrypt.hashpw("admin123456".encode(), bcrypt.gensalt()).decode()
        now = datetime.now().isoformat()
        admin_id = str(uuid.uuid4())
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users WHERE email = 'admin@fitmind.com'")).first()
            if result:
                print("⚠️  管理员账号已存在")
                return
            
            conn.execute(text(f"""
                INSERT INTO users (id, email, username, hashed_password, is_active, created_at)
                VALUES ('{admin_id}', 'admin@fitmind.com', 'admin', '{password_hash}', 1, '{now}')
            """))
            conn.commit()
            
            print("\n✅ 管理员账号创建成功！")
            print("=" * 50)
            print("📧 邮箱：admin@fitmind.com")
            print("🔑 密码：admin123456")
            print("=" * 50)
    except Exception as e:
        print(f"❌ 创建失败：{e}")

if __name__ == "__main__":
    create_admin()
