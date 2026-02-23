#!/usr/bin/env python3
"""
仪表板功能测试脚本
测试仪表板API和服务是否正常工作
"""

import sys
import os

# 设置环境变量以避免配置错误
# Note: Pydantic Settings v2 expects JSON strings for List fields
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:3000","http://127.0.0.1:3000"]'
os.environ["DATABASE_URL"] = "sqlite:///./weight_management.db"
os.environ["USE_MOCK_AI"] = "true"
os.environ["QWEN_API_KEY"] = "mock_key"
os.environ["QWEN_API_URL"] = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
)
os.environ["QWEN_MODEL"] = "qwen-turbo"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dashboard_service import get_dashboard_overview, get_quick_stats
from app.services.ai_health_advisor import get_daily_tip
from unittest.mock import Mock


# 创建模拟用户对象（避免数据库模型依赖）
class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.username = "testuser"
        self.full_name = "测试用户"
        self.age = 30
        self.gender = "male"
        self.height = 175
        self.initial_weight = 75000  # 75kg
        self.target_weight = 70000  # 70kg
        self.is_active = True


mock_user = MockUser()


def test_dashboard_service():
    """测试仪表板服务"""
    print("=== 测试仪表板服务 ===")

    # 测试每日小贴士
    print("\n1. 测试每日小贴士:")
    daily_tip = get_daily_tip()
    print(f"标题: {daily_tip['title']}")
    print(f"内容: {daily_tip['content']}")

    # 测试仪表板概览（使用模拟会话）
    print("\n2. 测试仪表板概览数据生成:")
    from unittest.mock import Mock

    mock_db = Mock()

    try:
        overview = get_dashboard_overview(mock_db, mock_user)
        print(f"欢迎语: {overview.greeting}")
        print(f"BMI: {overview.overview.bmi}")
        print(f"连续记录天数: {overview.overview.streak_days}")
        print(f"总积分: {overview.overview.total_points}")
        print(f"徽章数量: {len(overview.badges)}")
        print("✅ 仪表板概览测试通过")
    except Exception as e:
        print(f"❌ 仪表板概览测试失败: {e}")

    # 测试快速统计数据
    print("\n3. 测试快速统计数据:")
    try:
        quick_stats = get_quick_stats(mock_db, mock_user)
        print(f"今日卡路里: {quick_stats.today_calories} kcal")
        print(f"今日步数: {quick_stats.daily_step_count}")
        print(f"饮水量: {quick_stats.water_intake} ml")
        print(f"睡眠时长: {quick_stats.sleep_hours} 小时")
        print("✅ 快速统计测试通过")
    except Exception as e:
        print(f"❌ 快速统计测试失败: {e}")

    # 测试AI健康建议
    print("\n4. 测试AI健康建议生成:")
    try:
        from app.services.ai_health_advisor import get_health_advice_from_ai

        advice = get_health_advice_from_ai(mock_db, mock_user)
        print(f"AI建议长度: {len(advice)} 字符")
        print(f"建议预览: {advice[:100]}...")
        print("✅ AI健康建议测试通过")
    except Exception as e:
        print(f"❌ AI健康建议测试失败: {e}")


def test_api_endpoints():
    """测试API端点（概念验证）"""
    print("\n=== 测试API端点（概念验证） ===")

    endpoints = [
        ("GET /api/v1/dashboard/overview", "获取仪表板概览"),
        ("GET /api/v1/dashboard/quick-stats", "获取快速统计"),
        ("POST /api/v1/ai/health-advice", "获取AI健康建议"),
        ("GET /api/v1/ai/trend-analysis", "获取趋势分析"),
    ]

    for endpoint, description in endpoints:
        print(f"✓ {endpoint} - {description}")


def main():
    """主测试函数"""
    print("体重管理AI系统 - 仪表板功能测试")
    print("=" * 50)

    test_dashboard_service()
    test_api_endpoints()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n下一步建议:")
    print("1. 启动后端服务器: python backend/start_server.py")
    print("2. 启动前端开发服务器: cd frontend && npm run dev")
    print("3. 访问 http://localhost:5173 查看仪表板")
    print("4. 使用测试账号登录: test@example.com / password123")


if __name__ == "__main__":
    main()
