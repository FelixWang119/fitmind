#!/usr/bin/env python3
"""
验证基础设施配置脚本

此脚本验证三个核心基础设施系统的配置：
1. Qwen API 配置系统
2. 测试资源管理系统
3. 测试用户管理系统

运行方式：
    python validate_infrastructure.py
"""

import sys
import os
from pathlib import Path

# 添加backend到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def validate_qwen_config():
    """验证Qwen API配置系统"""
    print("=" * 60)
    print("验证 Qwen API 配置系统")
    print("=" * 60)

    try:
        from app.core.qwen_config import qwen_config

        print(f"✅ 成功导入 qwen_config 模块")

        # 验证配置
        validation = qwen_config.validate_configuration()

        print(f"\n配置验证结果:")
        print(f"  API密钥已配置: {validation['api_key_configured']}")
        print(f"  对话模型: {validation['chat_model']}")
        print(f"  视觉模型: {validation['vision_model']}")
        print(f"  快速模型: {validation['turbo_model']}")
        print(f"  Base URL: {validation['base_url']}")
        print(f"  API URL: {validation['api_url']}")
        print(f"  状态: {validation['status']}")

        # 测试模型选择功能
        print(f"\n模型选择功能测试:")
        for purpose in ["chat", "vision", "turbo"]:
            try:
                model = qwen_config.get_model_for_purpose(purpose)
                timeout = qwen_config.get_timeout_for_model(model)
                temperature = qwen_config.get_temperature_for_model(model)
                print(
                    f"  {purpose:10} -> 模型: {model:20} 超时: {timeout:5.1f}s 温度: {temperature:.1f}"
                )
            except Exception as e:
                print(f"  {purpose:10} -> 错误: {e}")

        # 测试headers
        try:
            headers = qwen_config.get_headers()
            print(f"\n✅ Headers生成成功: {list(headers.keys())}")
        except Exception as e:
            print(f"\n❌ Headers生成失败: {e}")

        return validation["status"] == "valid"

    except Exception as e:
        print(f"❌ 验证Qwen配置失败: {e}")
        return False


def validate_test_resources():
    """验证测试资源管理系统"""
    print("\n" + "=" * 60)
    print("验证 测试资源管理系统")
    print("=" * 60)

    try:
        from app.core.test_resources import TestResources

        print(f"✅ 成功导入 TestResources 模块")

        # 验证资源
        validation = TestResources.validate_test_resources()

        print(f"\n测试资源验证结果:")
        print(
            f"  测试根目录: {validation['test_root_path']} ({'✓' if validation['test_root_exists'] else '✗'})"
        )
        print(
            f"  餐图目录: {validation['meal_images_dir_path']} ({'✓' if validation['meal_images_dir_exists'] else '✗'})"
        )

        print(f"\n测试图像状态:")
        for image in validation["images"]:
            status = "✓" if image["exists"] else "✗"
            print(
                f"  {status} {image['name']:10} {image['extension']:5} {image['size_kb']:7.1f} KB  {image['description']}"
            )

        print(f"\n摘要:")
        print(f"  总图像数: {validation['summary']['total_images']}")
        print(f"  可用图像: {validation['summary']['images_exist']}")
        print(f"  缺失图像: {validation['summary']['images_missing']}")
        print(f"  总大小: {validation['summary']['total_size_kb']:.1f} KB")
        print(f"  状态: {validation['status']}")

        # 测试图像操作
        print(f"\n图像操作测试:")
        images = TestResources.list_available_images()
        if images:
            first_image = images[0]
            print(f"  第一个图像: {first_image['name']}")

            try:
                # 测试获取路径
                path = TestResources.get_image_path(first_image["name"])
                print(f"  ✓ 获取路径成功: {path}")

                # 测试base64编码
                base64_str = TestResources.encode_image_to_base64(first_image["name"])
                print(f"  ✓ Base64编码成功 (长度: {len(base64_str)})")
            except Exception as e:
                print(f"  ✗ 图像操作失败: {e}")

        return validation["status"] in [
            "all_resources_available",
            "partial_resources_available",
        ]

    except Exception as e:
        print(f"❌ 验证测试资源失败: {e}")
        return False


def validate_test_users():
    """验证测试用户管理系统"""
    print("\n" + "=" * 60)
    print("验证 测试用户管理系统")
    print("=" * 60)

    try:
        from app.core.test_users import test_user_manager
        from app.core.database import SessionLocal

        print(f"✅ 成功导入 test_user_manager 模块")

        # 创建数据库会话
        db = SessionLocal()

        try:
            # 验证用户
            validation = test_user_manager.validate_test_users(db)

            print(f"\n测试用户验证结果:")
            print(
                f"  测试用户文件: {validation['test_users_file_path']} ({'✓' if validation['test_users_file_exists'] else '✗'})"
            )
            print(f"  缓存用户数: {validation['cached_users']}")

            print(f"\n测试用户状态:")
            for user in validation["users"]:
                if "error" in user:
                    print(f"  ✗ {user['purpose']:10} -> 错误: {user['error']}")
                else:
                    cache_status = "✓" if user["in_cache"] else "✗"
                    db_status = "✓" if user["in_database"] else "✗"
                    token_status = "✓" if user.get("token_valid", False) else "✗"
                    print(
                        f"  {cache_status}{db_status}{token_status} {user['purpose']:10} {user['email']:30} {user['description']}"
                    )

            print(f"\n摘要:")
            print(f"  预期用户数: {validation['summary']['total_expected']}")
            print(f"  缓存中用户: {validation['summary']['in_cache']}")
            print(f"  数据库中用户: {validation['summary']['in_database']}")
            print(f"  有效令牌数: {validation['summary']['tokens_valid']}")
            print(f"  状态: {validation['status']}")

            # 测试用户操作
            print(f"\n用户操作测试:")
            try:
                # 测试获取用户
                user_data = test_user_manager.get_or_create_test_user(db, "default")
                print(
                    f"  ✓ 获取/创建用户成功: {user_data['email']} (ID: {user_data['id']})"
                )

                # 测试获取令牌
                token = test_user_manager.get_test_user_token(db, "default")
                if token:
                    print(f"  ✓ 获取令牌成功 (长度: {len(token)})")
                else:
                    print(f"  ✗ 获取令牌失败")

                # 测试获取带令牌的用户数据
                user_with_token = test_user_manager.get_test_user_with_token(
                    db, "default"
                )
                print(f"  ✓ 获取带令牌用户数据成功")

            except Exception as e:
                print(f"  ✗ 用户操作失败: {e}")

            return validation["status"] in [
                "all_users_available",
                "partial_users_available",
            ]

        finally:
            db.close()

    except Exception as e:
        print(f"❌ 验证测试用户失败: {e}")
        return False


def generate_report():
    """生成基础设施验证报告"""
    print("\n" + "=" * 60)
    print("基础设施验证报告")
    print("=" * 60)

    results = {
        "qwen_config": validate_qwen_config(),
        "test_resources": validate_test_resources(),
        "test_users": validate_test_users(),
    }

    print("\n" + "=" * 60)
    print("验证摘要")
    print("=" * 60)

    all_passed = True
    for system, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{system:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有基础设施系统验证通过!")
    else:
        print("❌ 部分基础设施系统验证失败，请检查上述错误")

    return all_passed


def main():
    """主函数"""
    print("开始验证基础设施配置...")
    print("=" * 60)

    try:
        success = generate_report()

        if success:
            print("\n✅ 基础设施验证完成，所有系统正常工作")
            return 0
        else:
            print("\n❌ 基础设施验证失败，请修复上述问题")
            return 1

    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
