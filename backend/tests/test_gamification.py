"""游戏化功能单元测试"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.gamification import (
    UserPoints,
    PointsTransaction,
    UserBadge,
    Achievement,
    Challenge,
    StreakRecord,
    LeaderboardEntry,
    UserLevel,
    BadgeCategory,
    BadgeLevel,
)


@pytest.fixture(scope="function")
def auth_token(client: TestClient, test_user: User):
    """获取认证令牌"""
    from app.core.rate_limit import reset_rate_limiters

    reset_rate_limiters()

    login_data = {"username": test_user.email, "password": "TestPassword123!"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


class TestGamificationEndpoints:
    """测试游戏化 API 端点"""

    def test_get_gamification_overview(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取游戏化概览"""
        user_points = UserPoints(
            user_id=test_user.id,
            total_points=1000,
            current_points=500,
            habit_points=200,
            nutrition_points=200,
            emotional_points=100,
            login_points=300,
            achievement_points=200,
        )
        db_session.add(user_points)

        user_level = UserLevel(
            user_id=test_user.id,
            current_level=3,
            current_title="探索者",
            experience_points=750,
            points_to_next_level=1000,
        )
        db_session.add(user_level)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/overview",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "user_points" in data
        assert "user_level" in data
        assert data["user_points"]["total_points"] == 1000
        assert data["user_points"]["current_points"] == 500
        assert data["user_level"]["current_level"] == 3

    def test_get_points(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户积分"""
        user_points = UserPoints(
            user_id=test_user.id,
            total_points=1500,
            current_points=800,
            habit_points=400,
            nutrition_points=400,
            emotional_points=200,
            login_points=300,
            achievement_points=200,
        )
        db_session.add(user_points)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/points",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_points"] == 1500
        assert data["current_points"] == 800

    def test_get_points_history(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取积分历史"""
        transactions = [
            PointsTransaction(
                user_id=test_user.id,
                points_amount=100,
                transaction_type="habit_completion",
                description="完成每日运动习惯",
                reference_id="1",
                reference_type="habit",
            ),
            PointsTransaction(
                user_id=test_user.id,
                points_amount=50,
                transaction_type="weight_log",
                description="记录体重下降",
            ),
            PointsTransaction(
                user_id=test_user.id,
                points_amount=-200,
                transaction_type="reward_redemption",
                description="兑换虚拟奖品",
                reference_id="1",
                reference_type="reward",
            ),
        ]
        db_session.add_all(transactions)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/points-history",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert all("points_amount" in item for item in data)

    def test_get_level(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户等级"""
        user_points = UserPoints(
            user_id=test_user.id,
            total_points=2500,
            current_points=1200,
            habit_points=500,
            nutrition_points=500,
            emotional_points=300,
            login_points=700,
            achievement_points=500,
        )
        db_session.add(user_points)

        user_level = UserLevel(
            user_id=test_user.id,
            current_level=7,
            current_title="熟练者",
            experience_points=2500,
            points_to_next_level=3500,
        )
        db_session.add(user_level)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/level",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_level"] == 7

    def test_get_badges(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户徽章"""
        badges = [
            UserBadge(
                user_id=test_user.id,
                badge_id="habit_30days",
                badge_name="习惯建立者",
                badge_description="连续坚持习惯 30 天",
                badge_category=BadgeCategory.HABIT_MASTERY,
                badge_level=BadgeLevel.SILVER,
                badge_icon="🎯",
                earned_at=datetime.utcnow() - timedelta(days=10),
            ),
            UserBadge(
                user_id=test_user.id,
                badge_id="weight_loss_5kg",
                badge_name="减重勇士",
                badge_description="成功减重 5 公斤",
                badge_category=BadgeCategory.WEIGHT_LOSS,
                badge_level=BadgeLevel.SILVER,
                badge_icon="🥈",
                earned_at=datetime.utcnow() - timedelta(days=5),
            ),
        ]
        db_session.add_all(badges)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/badges",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_achievements(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户成就"""
        achievements = [
            Achievement(
                user_id=test_user.id,
                achievement_id="health_30days",
                achievement_name="健康生活 30 天",
                achievement_description="连续 30 天记录健康数据",
                achievement_category="consistency",
                target_value=30,
                current_value=30,
                progress_percentage=100.0,
                is_completed=True,
                points_reward=100,
            ),
            Achievement(
                user_id=test_user.id,
                achievement_id="nutrition_master",
                achievement_name="营养均衡大师",
                achievement_description="连续 7 天达到营养目标",
                achievement_category="nutrition",
                target_value=7,
                current_value=6,
                progress_percentage=85.7,
                is_completed=False,
                points_reward=50,
            ),
        ]
        db_session.add_all(achievements)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/achievements",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_challenges(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户挑战"""
        challenges = [
            Challenge(
                user_id=test_user.id,
                challenge_id="7day_exercise",
                challenge_name="七日运动挑战",
                challenge_description="连续 7 天每天运动 30 分钟",
                challenge_type="exercise",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                duration_days=7,
                target_metric="exercise_minutes",
                target_value=210,
                current_value=90,
                status="active",
                points_reward=500,
            ),
        ]
        db_session.add_all(challenges)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/challenges",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_get_streaks(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取用户连击记录"""
        streaks = [
            StreakRecord(
                user_id=test_user.id,
                streak_type="weight_logging",
                streak_name="体重记录连击",
                current_streak=15,
                longest_streak=30,
                streak_start_date=datetime.utcnow() - timedelta(days=15),
                last_activity_date=datetime.utcnow(),
                milestones_reached=[7],
            ),
        ]
        db_session.add_all(streaks)
        db_session.commit()

        response = client.get(
            "/api/v1/gamification/streaks",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_get_leaderboard(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取排行榜"""
        response = client.get(
            "/api/v1/gamification/leaderboard",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "leaderboard_type" in data
        assert "period" in data

    def test_get_daily_reward(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试获取每日奖励"""
        response = client.get(
            "/api/v1/gamification/daily-reward",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "day" in data
        assert "points" in data

    def test_claim_daily_reward(
        self, client: TestClient, test_user: User, db_session: Session, auth_token: str
    ):
        """测试领取每日奖励"""
        response = client.post(
            "/api/v1/gamification/claim-daily-reward",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "points" in data
        assert "new_total" in data

    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_get_health_score(
        self, client: TestClient, test_user: User, auth_token: str
    ):
        """测试获取健康评分 - 暂未实现"""
        pass

    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_get_scientific_metrics(
        self, client: TestClient, test_user: User, auth_token: str
    ):
        """测试获取科学指标 - 暂未实现"""
        pass

    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_get_correlations(
        self, client: TestClient, test_user: User, auth_token: str
    ):
        """测试获取相关性分析 - 暂未实现"""
        pass


class TestGamificationService:
    """测试游戏化服务逻辑"""

    def test_gamification_service_initialization(
        self, db_session: Session, test_user: User
    ):
        """测试游戏化服务初始化"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        assert service.db == db_session
        assert service.LEVEL_CONFIG is not None
        assert service.BADGES is not None

    def test_initialize_user_gamification(self, db_session: Session, test_user: User):
        """测试初始化用户游戏化数据"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        service.initialize_user_gamification(test_user)

        user_points = (
            db_session.query(UserPoints)
            .filter(UserPoints.user_id == test_user.id)
            .first()
        )
        assert user_points is not None
        assert user_points.total_points == 0

        user_level = (
            db_session.query(UserLevel)
            .filter(UserLevel.user_id == test_user.id)
            .first()
        )
        assert user_level is not None
        assert user_level.current_level == 1

    def test_award_points_method(self, db_session: Session, test_user: User):
        """测试授予积分方法"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        service.initialize_user_gamification(test_user)

        # Award 50 points - not enough to level up (needs 100)
        result = service.award_points(
            user=test_user,
            points=50,
            transaction_type="habit_completion",
            description="完成习惯",
        )

        assert result.points == 50
        assert result.new_total == 50
        assert result.level_up is False

        user_points = (
            db_session.query(UserPoints)
            .filter(UserPoints.user_id == test_user.id)
            .first()
        )
        assert user_points.total_points == 50

    def test_get_user_points_method(self, db_session: Session, test_user: User):
        """测试获取用户积分方法"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        service.initialize_user_gamification(test_user)
        service.award_points(test_user, 500, "login", "登录奖励")

        points = service.get_user_points(test_user)
        assert points.total_points == 500

    def test_get_level_progress_method(self, db_session: Session, test_user: User):
        """测试获取等级进度方法"""
        from app.services.gamification_service import GamificationService

        service = GamificationService(db_session)
        service.initialize_user_gamification(test_user)

        progress = service.get_level_progress(test_user)
        assert progress.current_level == 1
        assert progress.current_title == "新手"
        assert 0 <= progress.progress_percentage <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
