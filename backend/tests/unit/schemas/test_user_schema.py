"""
User Schema 单元测试
Story 1.2: Schema 更新
测试覆盖率目标：> 80%
"""

import pytest
from pydantic import ValidationError, EmailStr
from app.schemas.user import UserBase, UserUpdate


class TestUserBaseSchema:
    """测试 UserBase Schema"""

    def test_valid_user_base_minimal(self):
        """测试最小的有效 UserBase 数据"""
        # Given: 只有必填字段
        data = {"email": "test@example.com"}

        # When: 创建 Schema
        user = UserBase(**data)

        # Then: 验证通过，所有可选字段为 None
        assert user.email == "test@example.com"
        assert user.age is None
        assert user.current_weight is None
        assert user.waist_circumference is None

    def test_valid_user_base_with_new_fields(self):
        """测试包含新字段的有效数据"""
        # Given: 包含新字段的数据
        data = {
            "email": "test@example.com",
            "current_weight": 70000,  # 70kg
            "waist_circumference": 85,
            "hip_circumference": 95,
            "body_fat_percentage": 20.5,
            "muscle_mass": 60000,
            "bone_density": 1.2,
            "metabolism_rate": 1800,
            "sleep_quality": 7,
        }

        # When: 创建 Schema
        user = UserBase(**data)

        # Then: 所有字段正确保存
        assert user.current_weight == 70000
        assert user.waist_circumference == 85
        assert user.body_fat_percentage == 20.5
        assert user.muscle_mass == 60000
        assert user.bone_density == 1.2
        assert user.metabolism_rate == 1800
        assert user.sleep_quality == 7

    def test_new_fields_optional(self):
        """测试新增字段为可选 (向后兼容)"""
        # Given: 只有必填字段
        data = {"email": "test@example.com"}

        # When: 创建 Schema
        user = UserBase(**data)

        # Then: 新增字段为 None
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

    def test_weight_field_validation_min(self):
        """测试重量字段最小值验证"""
        # Given: 超出范围的最小值
        invalid_data = {
            "email": "test@example.com",
            "current_weight": 10000,  # 10kg，太小
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**invalid_data)

        assert "current_weight" in str(exc_info.value)

    def test_weight_field_validation_max(self):
        """测试重量字段最大值验证"""
        # Given: 超出范围的最大值
        invalid_data = {
            "email": "test@example.com",
            "current_weight": 400000,  # 400kg，太大
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**invalid_data)

        assert "current_weight" in str(exc_info.value)

    def test_body_fat_percentage_validation(self):
        """测试体脂率验证"""
        # Given: 有效数据
        valid_data = {
            "email": "test@example.com",
            "body_fat_percentage": 20.5,
        }
        user = UserBase(**valid_data)
        assert user.body_fat_percentage == 20.5

        # Given: 最小值
        valid_min = {"email": "test@example.com", "body_fat_percentage": 3.0}
        user_min = UserBase(**valid_min)
        assert user_min.body_fat_percentage == 3.0

        # Given: 最大值
        valid_max = {"email": "test@example.com", "body_fat_percentage": 70.0}
        user_max = UserBase(**valid_max)
        assert user_max.body_fat_percentage == 70.0

        # Given: 超出范围的值
        invalid_data = {
            "email": "test@example.com",
            "body_fat_percentage": 80.0,  # 超出 70%
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_data)

    def test_sleep_quality_validation(self):
        """测试睡眠质量验证"""
        # Given: 有效数据 - 最小值
        valid_min = {"email": "test@example.com", "sleep_quality": 1}
        user_min = UserBase(**valid_min)
        assert user_min.sleep_quality == 1

        # Given: 有效数据 - 最大值
        valid_max = {"email": "test@example.com", "sleep_quality": 10}
        user_max = UserBase(**valid_max)
        assert user_max.sleep_quality == 10

        # Given: 超出范围的值 - 太小
        invalid_too_low = {
            "email": "test@example.com",
            "sleep_quality": 0,  # 小于 1
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_too_low)

        # Given: 超出范围的值 - 太大
        invalid_too_high = {
            "email": "test@example.com",
            "sleep_quality": 11,  # 超出 10
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_too_high)

    def test_waist_circumference_validation(self):
        """测试腰围验证"""
        # Given: 有效数据
        valid_data = {
            "email": "test@example.com",
            "waist_circumference": 85,
        }
        user = UserBase(**valid_data)
        assert user.waist_circumference == 85

        # Given: 超出范围的值
        invalid_data = {
            "email": "test@example.com",
            "waist_circumference": 200,  # 超出 150cm
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_data)

    def test_bone_density_validation(self):
        """测试骨密度验证"""
        # Given: 有效数据
        valid_data = {
            "email": "test@example.com",
            "bone_density": 1.2,
        }
        user = UserBase(**valid_data)
        assert user.bone_density == 1.2

        # Given: 超出范围的值
        invalid_data = {
            "email": "test@example.com",
            "bone_density": 3.0,  # 超出 2.5
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_data)

    def test_metabolism_rate_validation(self):
        """测试基础代谢率验证"""
        # Given: 有效数据
        valid_data = {
            "email": "test@example.com",
            "metabolism_rate": 1800,
        }
        user = UserBase(**valid_data)
        assert user.metabolism_rate == 1800

        # Given: 超出范围的值
        invalid_data = {
            "email": "test@example.com",
            "metabolism_rate": 5000,  # 超出 4000
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError):
            UserBase(**invalid_data)

    def test_json_fields_structure(self):
        """测试 JSON 字段结构"""
        # Given: JSON 数据
        data = {
            "email": "test@example.com",
            "health_conditions": {
                "diabetes": False,
                "hypertension": False,
                "heart_disease": False,
            },
            "allergies": ["peanuts", "shellfish", "dairy"],
            "medications": {"daily_vitamin": True, "prescription_meds": []},
        }

        # When: 创建 Schema
        user = UserBase(**data)

        # Then: JSON 数据正确解析
        assert user.health_conditions is not None
        assert user.health_conditions["diabetes"] is False
        assert "peanuts" in user.allergies
        assert user.medications["daily_vitamin"] is True

        # 验证类型
        assert isinstance(user.health_conditions, dict)
        assert isinstance(user.allergies, list)
        assert isinstance(user.medications, dict)

    def test_all_17_fields(self):
        """测试所有 17 个字段"""
        # Given: 完整数据
        data = {
            "email": "test@example.com",
            # 原有 7 字段
            "age": 30,
            "gender": "male",
            "height": 175,
            "initial_weight": 70000,
            "target_weight": 65000,
            "activity_level": "moderate",
            "dietary_preferences": ["vegetarian"],
            # 新增 11 字段
            "current_weight": 68000,
            "waist_circumference": 85,
            "hip_circumference": 95,
            "body_fat_percentage": 20.5,
            "muscle_mass": 60000,
            "bone_density": 1.2,
            "metabolism_rate": 1800,
            "health_conditions": {"diabetes": False},
            "medications": {"vitamin": True},
            "allergies": ["peanuts"],
            "sleep_quality": 7,
        }

        # When: 创建 Schema
        user = UserBase(**data)

        # Then: 所有字段都存在
        assert user.email == "test@example.com"
        assert user.age == 30
        assert user.gender == "male"
        assert user.height == 175
        assert user.initial_weight == 70000
        assert user.target_weight == 65000
        assert user.current_weight == 68000
        assert user.waist_circumference == 85
        assert user.body_fat_percentage == 20.5
        assert user.muscle_mass == 60000
        assert user.bone_density == 1.2
        assert user.metabolism_rate == 1800
        assert user.sleep_quality == 7


class TestUserUpdateSchema:
    """测试 UserUpdate Schema"""

    def test_partial_update_single_field(self):
        """测试单个字段更新"""
        # Given: 只更新一个字段
        data = {"current_weight": 67000}

        # When: 创建 Schema
        update = UserUpdate(**data)

        # Then: 只更新的字段有值
        assert update.current_weight == 67000
        assert update.age is None
        assert update.height is None
        assert update.waist_circumference is None

    def test_partial_update_multiple_fields(self):
        """测试多个字段更新"""
        # Given: 更新多个字段
        data = {
            "current_weight": 67000,
            "body_fat_percentage": 19.5,
            "sleep_quality": 8,
        }

        # When: 创建 Schema
        update = UserUpdate(**data)

        # Then: 所有更新的字段都有值
        assert update.current_weight == 67000
        assert update.body_fat_percentage == 19.5
        assert update.sleep_quality == 8

        # 其他字段为 None
        assert update.age is None
        assert update.waist_circumference is None

    def test_all_update_fields_optional(self):
        """测试所有更新字段都是可选的"""
        # Given: 空数据
        data = {}

        # When: 创建 Schema
        update = UserUpdate(**data)

        # Then: 所有字段都是 None
        assert update.email is None
        assert update.current_weight is None
        assert update.waist_circumference is None
        assert update.body_fat_percentage is None
        assert update.sleep_quality is None

    def test_update_validation_rules(self):
        """测试更新时的验证规则"""
        # Given: 无效的更新数据
        invalid_data = {
            "current_weight": 10000,  # 太小
            "sleep_quality": 15,  # 超出范围
        }

        # When/Then: 应该抛出验证错误
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**invalid_data)

        assert "current_weight" in str(exc_info.value) or "sleep_quality" in str(
            exc_info.value
        )

    def test_update_json_fields(self):
        """测试更新 JSON 字段"""
        # Given: JSON 字段更新
        data = {
            "health_conditions": {"diabetes": True, "hypertension": False},
            "allergies": ["nuts", "dairy"],
        }

        # When: 创建 Schema
        update = UserUpdate(**data)

        # Then: JSON 字段正确解析
        assert update.health_conditions["diabetes"] is True
        assert "nuts" in update.allergies

    def test_update_all_11_new_fields(self):
        """测试更新所有 11 个新字段"""
        # Given: 所有新字段的更新
        data = {
            "current_weight": 68000,
            "waist_circumference": 86,
            "hip_circumference": 96,
            "body_fat_percentage": 19.0,
            "muscle_mass": 61000,
            "bone_density": 1.25,
            "metabolism_rate": 1850,
            "health_conditions": {"diabetes": False},
            "medications": {"vitamin_d": True},
            "allergies": ["shellfish"],
            "sleep_quality": 8,
        }

        # When: 创建 Schema
        update = UserUpdate(**data)

        # Then: 所有字段都正确
        assert update.current_weight == 68000
        assert update.waist_circumference == 86
        assert update.body_fat_percentage == 19.0
        assert update.muscle_mass == 61000
        assert update.bone_density == 1.25
        assert update.metabolism_rate == 1850
        assert update.sleep_quality == 8


class TestUserBaseFieldDescriptions:
    """测试字段描述"""

    def test_field_descriptions_exist(self):
        """测试字段描述存在"""
        # Given: UserBase Schema
        schema = UserBase.model_json_schema()

        # Then: 检查字段描述
        props = schema.get("properties", {})

        # 验证部分字段有描述
        assert "current_weight" in props
        assert "description" in props["current_weight"]
        assert "克" in props["current_weight"]["description"]

        assert "body_fat_percentage" in props
        assert "description" in props["body_fat_percentage"]
        assert "%" in props["body_fat_percentage"]["description"]

        assert "sleep_quality" in props
        assert "description" in props["sleep_quality"]
