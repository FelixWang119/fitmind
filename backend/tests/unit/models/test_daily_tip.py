"""
DailyTip 模型单元测试
Story 9.1: 科普内容生成服务
"""

import pytest
from datetime import datetime, date
from app.models.daily_tip import DailyTip, TipTopic


class TestDailyTipModel:
    """测试 DailyTip 数据模型"""

    def test_create_daily_tip(self, db_session):
        """
        测试创建每日科普内容
        AC #5: 内容存储到数据库
        """
        # Given: 科普内容数据
        tip_data = {
            "date": datetime.now(),
            "topic": TipTopic.NUTRITION.value,
            "title": "如何健康饮水",
            "summary": "每日饮水指南，帮助您养成健康饮水习惯",
            "content": "健康的饮水习惯对人体至关重要。建议成年人每天饮用约2000毫升的水，分为多次饮用。早晨起床后喝一杯温水有助于唤醒身体机能，餐前半小时适量饮水可以增加饱腹感。",
            "is_active": True,
        }

        # When: 创建科普内容
        tip = DailyTip(**tip_data)
        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 数据正确保存
        assert tip.id is not None
        assert tip.date.date() == date.today()
        assert tip.topic == TipTopic.NUTRITION.value
        assert tip.title == "如何健康饮水"
        assert tip.summary == "每日饮水指南，帮助您养成健康饮水习惯"
        assert len(tip.content) > 0
        assert tip.is_active is True

    def test_topic_enum_values(self, db_session):
        """
        测试主题枚举值
        AC #2: 每周一个主题（营养/运动/睡眠/心理）
        """
        topics = [
            TipTopic.NUTRITION,
            TipTopic.EXERCISE,
            TipTopic.SLEEP,
            TipTopic.PSYCHOLOGY,
        ]

        for topic in topics:
            tip = DailyTip(
                date=datetime.now(),
                topic=topic.value,
                title="Test Title",
                summary="Test Summary",
                content="Test Content",
            )
            db_session.add(tip)
            db_session.commit()

            # Then: 主题值正确
            assert tip.topic == topic.value

            # Cleanup
            db_session.delete(tip)
            db_session.commit()

    def test_default_disclaimer(self, db_session):
        """
        测试默认免责声明
        AC #4: 添加医学免责声明
        """
        # Given: 没有提供免责声明
        tip_data = {
            "date": datetime.now(),
            "topic": TipTopic.NUTRITION.value,
            "title": "Test Title",
            "summary": "Test Summary",
            "content": "Test Content",
        }

        # When: 创建科普内容
        tip = DailyTip(**tip_data)
        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 默认免责声明已设置
        assert tip.disclaimer is not None
        assert "医疗" in tip.disclaimer or "专业" in tip.disclaimer

    def test_custom_disclaimer(self, db_session):
        """
        测试自定义免责声明
        """
        # Given: 自定义免责声明
        custom_disclaimer = "这是自定义免责声明"
        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.EXERCISE.value,
            title="Test",
            summary="Test",
            content="Test",
            disclaimer=custom_disclaimer,
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 使用自定义免责声明
        assert tip.disclaimer == custom_disclaimer

    def test_summary_length_constraint(self, db_session):
        """
        测试摘要长度约束
        AC #3: 摘要 50 字内
        """
        # Given: 50字内的摘要
        summary = "健康的饮水习惯对人体至关重要，建议每天饮用约2000毫升"
        assert len(summary) <= 50

        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test Title",
            summary=summary,
            content="Test Content",
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 摘要正确保存
        assert tip.summary == summary
        assert len(tip.summary) <= 50

    def test_content_length_constraint(self, db_session):
        """
        测试正文长度约束
        AC #3: 正文 300-500 字
        """
        # Given: 300-500字的正文
        content = """健康的饮水习惯对人体至关重要。建议成年人每天饮用约2000毫升的水，分为多次饮用。早晨起床后喝一杯温水有助于唤醒身体机能，餐前半小时适量饮水可以增加饱腹感。运动前后补充适量水分有助于维持身体水合状态。

过量饮水可能导致电解质失衡，应根据个人体重和活动量调整饮水量。养成健康的饮水习惯可以改善皮肤状态、提高免疫力、促进新陈代谢。每个人的饮水量可能因年龄、体重、运动量和气候条件而有所不同，建议根据自身情况调整饮水计划。

除了白开水，也可以适量饮用淡茶、蜂蜜水等，但应避免含糖饮料和酒精。特殊人群如孕妇、哺乳期妇女、肾病患者等应在医生指导下调整饮水量。保持良好的饮水习惯是健康生活的重要组成部分。合理饮水，从今天开始！"""

        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test Title",
            summary="Test Summary",
            content=content,
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 正文正确保存
        assert tip.content == content
        assert 300 <= len(tip.content) <= 500

    def test_is_active_default(self, db_session):
        """
        测试 is_active 默认值
        """
        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test",
            summary="Test",
            content="Test",
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: 默认 is_active 为 True
        assert tip.is_active is True

    def test_is_active_can_be_false(self, db_session):
        """
        测试 is_active 可以设为 False
        """
        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test",
            summary="Test",
            content="Test",
            is_active=False,
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        assert tip.is_active is False

    def test_unique_date_constraint(self, db_session):
        """
        测试日期唯一性约束
        每天只能有一条科普内容
        """
        # Given: 创建当天科普内容
        today = datetime.now()
        tip1 = DailyTip(
            date=today,
            topic=TipTopic.NUTRITION.value,
            title="First Tip",
            summary="First",
            content="First Content",
        )
        db_session.add(tip1)
        db_session.commit()

        # When: 尝试创建同一天的另一条内容
        tip2 = DailyTip(
            date=today,
            topic=TipTopic.EXERCISE.value,
            title="Second Tip",
            summary="Second",
            content="Second Content",
        )
        db_session.add(tip2)

        # Then: 应该抛出唯一性约束错误
        with pytest.raises(Exception):
            db_session.commit()

    def test_timestamps_auto_populated(self, db_session):
        """
        测试时间戳自动填充
        """
        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test",
            summary="Test",
            content="Test",
        )

        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)

        # Then: created_at 自动填充
        assert tip.created_at is not None

    def test_repr_method(self, db_session):
        """
        测试 __repr__ 方法
        """
        tip = DailyTip(
            date=datetime.now(),
            topic=TipTopic.NUTRITION.value,
            title="Test Title",
            summary="Test Summary",
            content="Test Content",
        )

        db_session.add(tip)
        db_session.commit()

        repr_str = repr(tip)

        assert "DailyTip" in repr_str
        assert str(tip.id) in repr_str
        assert tip.topic in repr_str
