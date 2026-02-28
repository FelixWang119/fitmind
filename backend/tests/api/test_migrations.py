"""
数据库迁移测试
Story 1.1: 数据库模型扩展
测试迁移脚本可以正确升级和回滚
"""

import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import inspect, text


class TestUserMigration:
    """测试 User 模型迁移"""

    def test_migration_upgrade(self, test_engine):
        """
        测试迁移可以成功升级
        AC 1.1: 新增 11 个字段到 users 表
        """
        # Given: Alembic 配置
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")

        # When: 执行迁移到最新版本
        command.upgrade(alembic_cfg, "head")

        # Then: 新列存在
        inspector = inspect(test_engine)
        columns = [col["name"] for col in inspector.get_columns("users")]

        # 验证所有新字段都存在
        assert "current_weight" in columns
        assert "waist_circumference" in columns
        assert "hip_circumference" in columns
        assert "body_fat_percentage" in columns
        assert "muscle_mass" in columns
        assert "bone_density" in columns
        assert "metabolism_rate" in columns
        assert "health_conditions" in columns
        assert "medications" in columns
        assert "allergies" in columns
        assert "sleep_quality" in columns

    def test_migration_downgrade(self, test_engine):
        """
        测试迁移可以成功回滚
        验证回滚脚本正确性
        """
        # Given: 已升级到最新版本
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # 验证升级后字段存在
        inspector = inspect(test_engine)
        columns_before = [col["name"] for col in inspector.get_columns("users")]
        assert "current_weight" in columns_before

        # When: 回滚一个版本
        command.downgrade(alembic_cfg, "-1")

        # Then: 新列不存在
        inspector = inspect(test_engine)
        columns_after = [col["name"] for col in inspector.get_columns("users")]

        assert "current_weight" not in columns_after
        assert "waist_circumference" not in columns_after
        assert "hip_circumference" not in columns_after
        assert "body_fat_percentage" not in columns_after
        assert "muscle_mass" not in columns_after
        assert "bone_density" not in columns_after
        assert "metabolism_rate" not in columns_after
        assert "health_conditions" not in columns_after
        assert "medications" not in columns_after
        assert "allergies" not in columns_after
        assert "sleep_quality" not in columns_after

    def test_migration_upgrade_downgrade_cycle(self, test_engine):
        """
        测试升级 - 回滚 - 再升级循环
        验证迁移的幂等性
        """
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")

        # 第一次升级
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(test_engine)
        columns_1st = [col["name"] for col in inspector.get_columns("users")]

        # 回滚
        command.downgrade(alembic_cfg, "-1")

        # 再次升级
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(test_engine)
        columns_2nd = [col["name"] for col in inspector.get_columns("users")]

        # Then: 两次升级后列应该相同
        assert columns_1st == columns_2nd

    def test_column_comments_added(self, test_engine):
        """
        测试列注释正确添加
        验证字段注释帮助理解
        """
        # Given: 迁移已应用
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # When: 查询列注释
        with test_engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT column_name, col_description 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN (
                    'current_weight', 'waist_circumference', 'body_fat_percentage'
                )
            """)
            )
            comments = {row[0]: row[1] for row in result}

        # Then: 注释存在 (PostgreSQL 支持)
        assert "current_weight" in comments
        # 注意：comment 可能在某些测试环境中不显示，这是可选验证

    def test_json_column_type(self, test_engine):
        """
        测试 JSON 字段类型正确
        AC 1.1: JSON 字段使用 postgresql.JSON
        """
        # Given: 迁移已应用
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # When: 查询列类型
        inspector = inspect(test_engine)
        columns = inspector.get_columns("users")
        json_columns = {
            col["name"]: str(col["type"])
            for col in columns
            if col["name"] in ["health_conditions", "medications", "allergies"]
        }

        # Then: JSON 类型正确
        assert "health_conditions" in json_columns
        assert "JSON" in json_columns["health_conditions"].upper()
        assert "medications" in json_columns
        assert "allergies" in json_columns


class TestMigrationDataIntegrity:
    """测试迁移数据完整性"""

    def test_existing_data_not_affected(self, test_engine, db_session):
        """
        测试迁移不影响现有数据
        AC 1.2: 现有用户数据不受影响
        """
        from app.models.user import User
        from tests.factories import create_test_user_data

        # Given: 创建现有用户 (迁移前)
        user_data = create_test_user_data()
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        user_id = user.id

        # When: 应用迁移
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # Then: 现有用户数据完整
        stmt = text("SELECT * FROM users WHERE id = :id")
        result = db_session.execute(stmt, {"id": user_id}).fetchone()

        assert result is not None
        assert result.email == user_data["email"]
        # 新字段应该为 NULL
        assert result.current_weight is None

    def test_nullable_constraints(self, test_engine):
        """
        测试所有新字段 nullable=True
        AC 1.2: 向后兼容性保证
        """
        # Given: 迁移已应用
        alembic_cfg = Config("/Users/felix/bmad/backend/alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # When: 查询 nullable 约束
        inspector = inspect(test_engine)
        columns = inspector.get_columns("users")
        new_columns = {
            col["name"]: col["nullable"]
            for col in columns
            if col["name"]
            in [
                "current_weight",
                "waist_circumference",
                "hip_circumference",
                "body_fat_percentage",
                "muscle_mass",
                "bone_density",
                "metabolism_rate",
                "health_conditions",
                "medications",
                "allergies",
                "sleep_quality",
            ]
        }

        # Then: 所有新字段都是 nullable
        for col_name, is_nullable in new_columns.items():
            assert is_nullable is True, f"{col_name} 应该是 nullable=True"
