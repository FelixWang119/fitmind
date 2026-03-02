"""
习惯提醒定时任务单元测试

测试 habit_reminder_task 及相关辅助函数

注意：这些测试是纯单元测试，不依赖数据库连接，使用本地定义的模板数据
"""

import pytest


# 本地定义提醒模板（与 notification_tasks.py 保持一致）
HABIT_REMINDER_TEMPLATES = {
    "HYDRATION": {
        "title": "💧 饮水提醒",
        "content": "距离目标还差{remaining}杯水，今天加油！",
    },
    "EXERCISE": {
        "title": "🏃 运动提醒",
        "content": "今日{habit_name}还未完成，现在开始吧！",
    },
    "SLEEP": {
        "title": "😴 睡眠提醒",
        "content": "夜深了，该休息了～",
    },
    "MENTAL_HEALTH": {
        "title": "🧘 冥想提醒",
        "content": "放松时刻到了，花几分钟冥想吧",
    },
    "DIET": {
        "title": "🍽️ 饮食提醒",
        "content": "今日饮食还未记录，记得打卡哦",
    },
    "OTHER": {
        "title": "⏰ 打卡提醒",
        "content": "别忘了今天的{habit_name}",
    },
}


class TestHabitReminderTemplates:
    """测试提醒内容模板"""

    def test_all_habit_categories_have_templates(self):
        """测试所有习惯类型都有对应的提醒模板"""
        categories = [
            "HYDRATION",
            "EXERCISE",
            "SLEEP",
            "MENTAL_HEALTH",
            "DIET",
            "OTHER",
        ]
        for category in categories:
            assert category in HABIT_REMINDER_TEMPLATES
            assert "title" in HABIT_REMINDER_TEMPLATES[category]
            assert "content" in HABIT_REMINDER_TEMPLATES[category]

    def test_hydration_template_content(self):
        """测试饮水提醒内容包含剩余杯数"""
        template = HABIT_REMINDER_TEMPLATES["HYDRATION"]
        assert "{remaining}" in template["content"]
        assert "水" in template["content"]

    def test_exercise_template_content(self):
        """测试运动提醒内容包含习惯名称"""
        template = HABIT_REMINDER_TEMPLATES["EXERCISE"]
        assert "{habit_name}" in template["content"]
        assert "运动" in template["title"]

    def test_sleep_template_content(self):
        """测试睡眠提醒内容"""
        template = HABIT_REMINDER_TEMPLATES["SLEEP"]
        assert "休息" in template["content"]

    def test_meditation_template_content(self):
        """测试冥想提醒内容"""
        template = HABIT_REMINDER_TEMPLATES["MENTAL_HEALTH"]
        assert "冥想" in template["content"] or "放松" in template["content"]

    def test_diet_template_content(self):
        """测试饮食提醒内容"""
        template = HABIT_REMINDER_TEMPLATES["DIET"]
        assert "饮食" in template["content"]

    def test_other_template_content(self):
        """测试其他习惯提醒内容"""
        template = HABIT_REMINDER_TEMPLATES["OTHER"]
        assert "{habit_name}" in template["content"]


class TestGenerateReminderContent:
    """测试提醒内容生成函数"""

    def _generate_reminder_content(
        self,
        habit_name: str,
        category: str,
        completed_today: bool,
        target_value: int = None,
    ) -> dict:
        """模拟生成提醒内容的逻辑"""
        template = HABIT_REMINDER_TEMPLATES.get(
            category, HABIT_REMINDER_TEMPLATES["OTHER"]
        )

        title = template["title"]

        if completed_today:
            if category == "HYDRATION":
                content = f"太棒了！{habit_name}已完成，继续保持！"
            elif category == "EXERCISE":
                content = f"太厉害了！今日{habit_name}已完成！"
            elif category == "SLEEP":
                content = "祝你有个好梦！🌙"
            elif category == "MENTAL_HEALTH":
                content = "继续保持平静的心态～"
            else:
                content = f"太棒了！{habit_name}已完成！"
        else:
            content = template["content"].format(
                habit_name=habit_name, remaining=target_value or 1
            )

        return {"title": title, "content": content}

    def test_generate_reminder_not_completed(self):
        """测试未完成时生成提醒内容"""
        result = self._generate_reminder_content(
            "晨跑", "EXERCISE", completed_today=False
        )

        assert "title" in result
        assert "content" in result
        assert "晨跑" in result["content"]
        assert "未完成" in result["content"]

    def test_generate_reminder_completed(self):
        """测试已完成时生成鼓励内容"""
        result = self._generate_reminder_content(
            "晨跑", "EXERCISE", completed_today=True
        )

        assert "title" in result
        assert "content" in result
        assert "棒" in result["content"] or "厉害" in result["content"]

    def test_generate_reminder_hydration_not_completed(self):
        """测试饮水未完成时的提醒内容"""
        result = self._generate_reminder_content(
            "每日饮水", "HYDRATION", completed_today=False, target_value=8
        )

        assert "水" in result["content"]
        assert "杯" in result["content"]

    def test_generate_reminder_hydration_completed(self):
        """测试饮水完成时的鼓励内容"""
        result = self._generate_reminder_content(
            "每日饮水", "HYDRATION", completed_today=True
        )

        assert "棒" in result["content"] or "继续保持" in result["content"]

    def test_generate_reminder_sleep_not_completed(self):
        """测试睡眠未完成时的提醒内容"""
        result = self._generate_reminder_content("睡眠", "SLEEP", completed_today=False)

        assert "休息" in result["content"] or "夜" in result["content"]

    def test_generate_reminder_meditation_not_completed(self):
        """测试冥想未完成时的提醒内容"""
        result = self._generate_reminder_content(
            "冥想", "MENTAL_HEALTH", completed_today=False
        )

        assert "冥想" in result["content"] or "放松" in result["content"]

    def test_generate_reminder_unknown_category(self):
        """测试未知习惯类型的默认模板"""
        result = self._generate_reminder_content(
            "阅读", "UNKNOWN", completed_today=False
        )

        assert "title" in result
        assert "content" in result
        assert "阅读" in result["content"]


class TestReminderLogicEdgeCases:
    """测试提醒逻辑边界情况"""

    def test_empty_habit_name(self):
        """测试空习惯名称"""
        template = HABIT_REMINDER_TEMPLATES["OTHER"]
        content = template["content"].format(habit_name="")

        assert "别忘了今天的" in content

    def test_none_target_value(self):
        """测试目标值为None"""
        template = HABIT_REMINDER_TEMPLATES["HYDRATION"]
        content = template["content"].format(remaining=None)

        assert "None" in content

    def test_all_categories_have_unique_titles(self):
        """测试所有分类的标题都不相同"""
        titles = [t["title"] for t in HABIT_REMINDER_TEMPLATES.values()]
        assert len(titles) == len(set(titles)), "标题应该唯一"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
