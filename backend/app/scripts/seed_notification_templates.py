"""通知系统种子数据

运行方式：
    python -m app.scripts.seed_notification_templates
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.notification import NotificationTemplate


DEFAULT_TEMPLATES = [
    # 习惯相关
    {
        "code": "habit_completed",
        "name": "习惯完成通知",
        "event_type": "habit.completed",
        "title_template": "💪 {{habit_name}} 完成！",
        "content_template": "你已经连续 {{streak_days}} 天完成{{habit_name}}，保持这个好习惯！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "streak_days", "type": "number", "description": "连续天数"},
        ],
    },
    {
        "code": "habit_streak_7",
        "name": "连续 7 天打卡",
        "event_type": "habit.streak_7days",
        "title_template": "🔥 连续打卡 7 天！",
        "content_template": "你已经连续 7 天完成{{habit_name}}，一周的坚持值得庆祝！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
        ],
    },
    {
        "code": "habit_streak_30",
        "name": "连续 30 天打卡",
        "event_type": "habit.streak_30days",
        "title_template": "🏆 连续打卡 30 天！",
        "content_template": "太棒了！你已连续 30 天完成{{habit_name}}，这是真正的习惯养成！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
        ],
    },
    # 里程碑相关 - 连续打卡天数
    {
        "code": "milestone_streak_3",
        "name": "连续3天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🌟 连续3天打卡！",
        "content_template": "恭喜你完成「{{habit_name}}」连续3天打卡，获得「初出茅庐」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_streak_7",
        "name": "连续7天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🔥 连续7天打卡！",
        "content_template": "恭喜你完成「{{habit_name}}」连续7天打卡，获得「小有所成」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_streak_14",
        "name": "连续14天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "💪 连续14天打卡！",
        "content_template": "恭喜你完成「{{habit_name}}」连续14天打卡，获得「持之以恒」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_streak_30",
        "name": "连续30天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🏆 连续30天打卡！",
        "content_template": "太棒了！你已完成「{{habit_name}}」连续30天打卡，获得「习惯养成者」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_streak_60",
        "name": "连续60天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🌟 连续60天打卡！",
        "content_template": "太厉害了！你已完成「{{habit_name}}」连续60天打卡，获得「坚持不懈」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_streak_90",
        "name": "连续90天打卡里程碑",
        "event_type": "milestone.achieved",
        "title_template": "💎 连续90天打卡！",
        "content_template": "你已封神！完成「{{habit_name}}」连续90天打卡，获得「习惯大师」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    # 里程碑相关 - 累计记录
    {
        "code": "milestone_total_10",
        "name": "累计10次记录里程碑",
        "event_type": "milestone.achieved",
        "title_template": "📝 累计10次记录！",
        "content_template": "恭喜你在「{{habit_name}}」累计完成10次记录，获得「记录达人」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_total_50",
        "name": "累计50次记录里程碑",
        "event_type": "milestone.achieved",
        "title_template": "📚 累计50次记录！",
        "content_template": "恭喜你在「{{habit_name}}」累计完成50次记录，获得「记录高手」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    {
        "code": "milestone_total_100",
        "name": "累计100次记录里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🎖️ 累计100次记录！",
        "content_template": "太棒了！你已在「{{habit_name}}」累计完成100次记录，获得「记录大师」徽章！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "badge", "type": "string", "description": "徽章名称"},
        ],
    },
    # 里程碑相关 - 目标达成
    {
        "code": "milestone_goal_achieved",
        "name": "目标达成里程碑",
        "event_type": "milestone.achieved",
        "title_template": "🎯 目标达成！",
        "content_template": "恭喜你达成「{{habit_name}}」{{period}}目标！",
        "variables": [
            {"name": "habit_name", "type": "string", "description": "习惯名称"},
            {"name": "period", "type": "string", "description": "目标周期"},
            {"name": "target_value", "type": "number", "description": "目标值"},
            {"name": "current_progress", "type": "number", "description": "当前进度"},
        ],
    },
    # 体重目标（保留原有）
    {
        "code": "milestone_weight_goal",
        "name": "体重目标达成",
        "event_type": "milestone.weight_goal",
        "title_template": "🎉 恭喜你达成体重目标！",
        "content_template": "你已经成功减重{{weight}}kg，继续加油！",
        "variables": [
            {"name": "weight", "type": "number", "description": "减重公斤数"},
        ],
    },
    # 游戏化相关
    {
        "code": "badge_unlocked",
        "name": "徽章解锁",
        "event_type": "badge.unlocked",
        "title_template": "🎖️ 新徽章解锁！",
        "content_template": '恭喜你获得"{{badge_name}}"徽章！',
        "variables": [
            {"name": "badge_name", "type": "string", "description": "徽章名称"},
        ],
    },
    # 关怀相关
    {
        "code": "morning_care",
        "name": "早安关怀",
        "event_type": "care.morning",
        "title_template": "☀️ 早安！",
        "content_template": "新的一天开始了，今天也要加油哦～",
        "variables": [],
    },
    {
        "code": "care_inactive",
        "name": "未登录关怀",
        "event_type": "care.inactive",
        "title_template": "💙 想你啦！",
        "content_template": "{{days}}天没见到你了，一切还好吗？",
        "variables": [
            {"name": "days", "type": "number", "description": "未登录天数"},
        ],
    },
]


def seed_notification_templates():
    """初始化通知模板种子数据"""
    db = SessionLocal()

    try:
        for template_data in DEFAULT_TEMPLATES:
            # 检查是否已存在
            existing = (
                db.query(NotificationTemplate)
                .filter(NotificationTemplate.code == template_data["code"])
                .first()
            )

            if existing:
                print(f"⏭️  模板已存在：{template_data['code']}")
                continue

            # 创建模板
            template = NotificationTemplate(
                code=template_data["code"],
                name=template_data["name"],
                event_type=template_data.get("event_type"),
                title_template=template_data["title_template"],
                content_template=template_data["content_template"],
                variables=template_data.get("variables", []),
                is_active=True,
            )

            db.add(template)
            print(f"✅ 创建模板：{template_data['code']}")

        db.commit()
        print(f"\n🎉 成功创建 {len(DEFAULT_TEMPLATES)} 个通知模板")

    except Exception as e:
        db.rollback()
        print(f"❌ 错误：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 开始初始化通知模板种子数据...")
    seed_notification_templates()
    print("✅ 完成！")
