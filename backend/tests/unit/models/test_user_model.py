"""
User 模型扩展字段单元测试
Story 1.1: 数据库模型扩展
测试覆盖率目标：> 80%
"""

import pytest
from sqlalchemy import select
from app.models.user import User
from tests.factories import create_test_user_data


class TestUserProfileExtension:
    """测试 User 模型扩展字段"""

    def test_new_fields_nullable(self, db_session):
        """
        测试新增字段可以为 null (向后兼容)
        AC 1.2: 向后兼容性保证
        """
        # Given: 创建一个只有必填字段的用户
        user_data = create_test_user_data()
        user = User(**user_data)

        # When: 添加到数据库
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Then: 新增字段都为 None
        assert user.current_weight is None
        assert user.waist_circumference is None
        assert user.hip_circumference is None
        assert user.body_fat_percentage is None
        assert user.muscle_mass is None
        assert user.bone_density is None
        assert user.metabolism_rate is None
        assert user.health_conditions is None
        assert user.medications is None
        assert user.allergies is None
        assert user.sleep_quality is None

    def test_new_fields_accept_values(self, db_session):
        """
        测试新增字段可以接受值
        AC 1.1: 新增 11 个字段到 users 表
        """
        # Given: 创建包含新字段的用户数据
        user_data = create_test_user_data(
            {
                "current_weight": 75000,  # 75kg
                "waist_circumference": 85,  # 85cm
                "hip_circumference": 95,  # 95cm
                "body_fat_percentage": 20.5,  # 20.5%
                "muscle_mass": 60000,  # 60kg
                "bone_density": 1.2,  # 1.2 g/cm²
                "metabolism_rate": 1800,  # 1800 kcal/day
                "sleep_quality": 7,  # 7/10
            }
        )
        user = User(**user_data)

        # When: 添加到数据库
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Then: 字段值正确保存
        assert user.current_weight == 75000
        assert user.waist_circumference == 85
        assert user.hip_circumference == 95
        assert user.body_fat_percentage == 20.5
        assert user.muscle_mass == 60000
        assert user.bone_density == 1.2
        assert user.metabolism_rate == 1800
        assert user.sleep_quality == 7

    def test_json_fields_structure(self, db_session):
        """
        测试 JSON 字段结构
        AC 1.1: JSON 字段正确保存
        """
        # Given: 包含 JSON 数据的用户
        user_data = create_test_user_data(
            {
                "health_conditions": {
                    "diabetes": False,
                    "hypertension": False,
                    "heart_disease": False,
                    "other": None,
                },
                "allergies": ["peanuts", "shellfish", "dairy"],
                "medications": {"daily_vitamin": True, "prescription_meds": []},
            }
        )
        user = User(**user_data)

        # When: 保存到数据库
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Then: JSON 数据正确保存和检索
        assert user.health_conditions is not None
        assert user.health_conditions["diabetes"] is False
        assert "peanuts" in user.allergies
        assert user.medications["daily_vitamin"] is True

        # 验证 JSON 类型
        assert isinstance(user.health_conditions, dict)
        assert isinstance(user.allergies, list)
        assert isinstance(user.medications, dict)

    def test_weight_fields_unit_consistency(self, db_session):
        """
        测试重量字段单位一致性
        AC 1.4: 重量单位一致性 (克)
        """
        # Given: 重量字段使用克为单位
        user_data = create_test_user_data(
            {
                "initial_weight": 70000,  # 70kg
                "target_weight": 65000,  # 65kg
                "current_weight": 68000,  # 68kg
                "muscle_mass": 55000,  # 55kg
            }
        )
        user = User(**user_data)

        # When: 保存到数据库
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Then: 所有重量字段都是克
        assert user.initial_weight == 70000
        assert user.target_weight == 65000
        assert user.current_weight == 68000
        assert user.muscle_mass == 55000

        # 验证单位转换：70kg = 70000g
        assert user.initial_weight > 1000  # 确保不是千克

    def test_field_validation_ranges(self, db_session):
        """
        测试字段验证范围
        AC 1.5: 数据验证规则
        """
        # Given: 边界值测试数据
        test_cases = [
            # (field, valid_value, description)
            ("body_fat_percentage", 3.0, "体脂率最小值"),
            ("body_fat_percentage", 70.0, "体脂率最大值"),
            ("sleep_quality", 1, "睡眠质量最小值"),
            ("sleep_quality", 10, "睡眠质量最大值"),
            ("waist_circumference", 50, "腰围最小值"),
            ("waist_circumference", 150, "腰围最大值"),
        ]

        for field, value, description in test_cases:
            user_data = create_test_user_data({field: value})
            user = User(**user_data)

            # When: 保存
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)

            # Then: 值正确保存
            assert getattr(user, field) == value, f"{description} 测试失败"

            # 清理
            db_session.delete(user)
            db_session.commit()

    def test_existing_user_data_preserved(self, db_session):
        """
        测试现有用户数据不受影响
        AC 1.2: 现有用户数据不受影响
        """
        # Given: 创建一个旧格式用户 (只有原有字段)
        user_data = create_test_user_data()
        user = User(**user_data)

        # When: 保存并查询
        db_session.add(user)
        db_session.commit()

        # Then: 查询用户
        stmt = select(User).where(User.email == user_data["email"])
        result = db_session.execute(stmt).scalar_one()

        # 原有字段正常
        assert result.email == user_data["email"]
        assert result.age is not None
        assert result.height is not None

        # 新字段为 null
        assert result.current_weight is None
        assert result.waist_circumference is None

    def test_partial_field_update(self, db_session):
        """
        测试部分字段更新
        AC 1.3: API 返回完整字段
        """
        # Given: 创建一个完整数据的用户
        user_data = create_test_user_data(
            {
                "current_weight": 75000,
                "waist_circumference": 85,
                "body_fat_percentage": 20.5,
            }
        )
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()

        # When: 只更新一个字段
        user.current_weight = 74000
        db_session.commit()
        db_session.refresh(user)

        # Then: 只有更新的字段变化
        assert user.current_weight == 74000
        assert user.waist_circumference == 85
        assert user.body_fat_percentage == 20.5

    def test_user_repr_includes_new_fields(self, db_session):
        """
        测试用户 repr 方法
        """
        # Given: 创建用户
        user_data = create_test_user_data()
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()

        # When: 调用 repr
        repr_str = repr(user)

        # Then: repr 包含基本信息
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert user.email in repr_str


class TestUserModelRelationships:
    """测试 User 模型关系在扩展后仍然正常工作"""

    def test_relationships_still_work(self, db_session):
        """测试扩展字段不影响现有关系"""
        # Given: 创建用户
        user_data = create_test_user_data(
            {
                "current_weight": 75000,
            }
        )
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()

        # When: 访问关系
        # Then: 关系正常访问 (不报错)
        assert user.health_records is not None
        assert user.conversations is not None
        assert user.habits is not None
        assert user.meals is not None
