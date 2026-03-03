"""
DailyTip 定时任务单元测试
Story 9.1: 科普内容生成服务
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.models.daily_tip import DailyTip, TipTopic


class TestDailyTipTask:
    """测试科普内容定时任务"""

    @pytest.mark.asyncio
    async def test_daily_tip_generation_skips_existing(self, db_session):
        """
        测试如果当天已有科普内容则跳过
        AC #5: 内容存储到数据库，支持历史查看
        """
        from app.schedulers.tasks.daily_tip_task import daily_tip_generation_task

        # Create existing tip for today
        today = datetime.now()
        existing_tip = DailyTip(
            date=today,
            topic=TipTopic.NUTRITION.value,
            title="Existing Title",
            summary="Existing Summary",
            content="Existing Content" * 30,
            is_active=True,
        )
        db_session.add(existing_tip)
        db_session.commit()

        # Run the task - it should handle existing tip
        await daily_tip_generation_task()

        # Verify existing tip is still there
        tips = (
            db_session.query(DailyTip)
            .filter(func.date(DailyTip.date) == today.date())
            .all()
        )

        assert len(tips) >= 1
        assert tips[0].title == "Existing Title"


class TestRegenerateDailyTip:
    """测试手动重新生成科普内容"""

    @pytest.mark.asyncio
    async def test_regenerate_creates_new_tip(self, db_session):
        """
        测试手动重新生成创建新内容
        AC #6: 支持手动触发重新生成
        """
        from app.schedulers.tasks.daily_tip_task import regenerate_daily_tip

        # Create existing tip for a past date to avoid conflicts
        past_date = datetime.now() - timedelta(days=1)
        existing_tip = DailyTip(
            date=past_date,
            topic=TipTopic.NUTRITION.value,
            title="Old Title",
            summary="Old Summary",
            content="Old Content" * 30,
            is_active=True,
        )
        db_session.add(existing_tip)
        db_session.commit()

        # Run regenerate for the past date
        new_tip = await regenerate_daily_tip(past_date.date())

        # Verify new tip was created
        assert new_tip is not None
        assert new_tip.title != "Old Title"

        # Verify old tip is marked inactive
        db_session.refresh(existing_tip)
        assert existing_tip.is_active is False

    @pytest.mark.asyncio
    async def test_regenerate_without_existing(self, db_session):
        """测试没有现有内容时重新生成"""
        from app.schedulers.tasks.daily_tip_task import regenerate_daily_tip

        # Use a future date to avoid conflicts
        future_date = date.today() + timedelta(days=7)

        # Run regenerate without existing
        new_tip = await regenerate_daily_tip(future_date)

        # Verify new tip was created
        assert new_tip is not None
        assert new_tip.title is not None
        assert new_tip.content is not None
