"""
API Tests for Gamification Endpoints
Sprint 2 - Epic 4: Gamification System Expansion

Tests cover:
- Gamification overview
- User points and points history
- Badges and achievements
- Challenges
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


# =============================================================================
# Gamification Overview Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
@pytest.mark.integration
class TestGamificationOverview:
    """Test gamification overview endpoint"""

    def test_get_gamification_overview_success(self, authenticated_client):
        """Test getting gamification overview"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_gamification_overview.return_value = {
                "total_points": 1500,
                "current_level": 5,
                "points_to_next_level": 500,
                "total_badges": 8,
                "unlocked_badges": 5,
                "total_challenges": 10,
                "completed_challenges": 3,
                "current_streak": 7,
                "longest_streak": 14,
            }
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/gamification/overview", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert "total_points" in data
            assert "current_level" in data

    def test_get_gamification_overview_error(self, authenticated_client):
        """Test gamification overview error handling"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_gamification_overview.side_effect = Exception(
                "Service error"
            )
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/gamification/overview", headers=headers)

            assert response.status_code == 500


# =============================================================================
# Points Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
class TestUserPoints:
    """Test user points endpoints"""

    def test_get_user_points_success(self, authenticated_client):
        """Test getting user points"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_user_points.return_value = {
                "user_id": user.id,
                "total_points": 1500,
                "lifetime_points": 2500,
                "level": 5,
            }
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/gamification/points", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["total_points"] == 1500
            assert data["level"] == 5

    def test_get_points_history_success(self, authenticated_client):
        """Test getting points history"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_points_history.return_value = [
                {
                    "id": 1,
                    "user_id": user.id,
                    "points": 100,
                    "transaction_type": "achievement_unlocked",
                    "description": "First meal logged",
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "id": 2,
                    "user_id": user.id,
                    "points": 50,
                    "transaction_type": "daily_checkin",
                    "description": "Daily check-in bonus",
                    "created_at": datetime.now().isoformat(),
                },
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/points-history?limit=10", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 2

    def test_get_points_history_default_limit(self, authenticated_client):
        """Test points history with default limit"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_points_history.return_value = []
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/points-history", headers=headers
            )

            assert response.status_code == 200

            # Verify default limit of 50 was used
            mock_instance.get_points_history.assert_called_once_with(user, 50)

    def test_get_points_history_custom_limit(self, authenticated_client):
        """Test points history with custom limit"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_points_history.return_value = []
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/points-history?limit=20", headers=headers
            )

            assert response.status_code == 200

            # Verify custom limit was used
            mock_instance.get_points_history.assert_called_once_with(user, 20)

    def test_get_points_history_invalid_limit(self, authenticated_client):
        """Test points history with invalid limit"""
        client, headers, user = authenticated_client

        # Limit too high
        response = client.get(
            "/api/v1/gamification/points-history?limit=200", headers=headers
        )

        # Should fail validation (max 100)
        assert response.status_code == 422


# =============================================================================
# Badge Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
class TestBadges:
    """Test badge endpoints"""

    def test_get_user_badges_success(self, authenticated_client):
        """Test getting user badges"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_user_badges.return_value = [
                {
                    "id": 1,
                    "badge_type": "meal_logging",
                    "name": "First Meal",
                    "description": "Log your first meal",
                    "unlocked_at": datetime.now().isoformat(),
                    "points_value": 100,
                },
            ]
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/gamification/badges", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)

    def test_get_available_badges_success(self, authenticated_client):
        """Test getting available badges"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_available_badges.return_value = [
                {
                    "id": 1,
                    "badge_type": "streak",
                    "name": "7 Day Streak",
                    "description": "Maintain a 7-day streak",
                    "requirement": {"type": "streak", "value": 7},
                    "points_value": 200,
                },
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/badges/available", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)


# =============================================================================
# Challenge Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
class TestChallenges:
    """Test challenge endpoints"""

    def test_get_active_challenges_success(self, authenticated_client):
        """Test getting active challenges"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_active_challenges.return_value = [
                {
                    "id": 1,
                    "challenge_type": "weekly",
                    "name": "Weekly Goal Crusher",
                    "description": "Complete 5 workouts this week",
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now().isoformat()),
                    "target_value": 5,
                    "current_progress": 3,
                    "points_reward": 500,
                },
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/challenges/active", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)

    def test_get_challenge_progress_success(self, authenticated_client):
        """Test getting challenge progress"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_challenge_progress.return_value = {
                "challenge_id": 1,
                "current_progress": 3,
                "target_value": 5,
                "completion_percentage": 60.0,
                "is_completed": False,
            }
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/challenges/1/progress", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert data["completion_percentage"] == 60.0


# =============================================================================
# Streak Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
class TestStreaks:
    """Test streak endpoints"""

    def test_get_streak_info_success(self, authenticated_client):
        """Test getting streak information"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_streak_info.return_value = {
                "current_streak": 7,
                "longest_streak": 14,
                "streak_type": "checkin",
                "last_checkin_date": datetime.now().isoformat(),
            }
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/gamification/streaks", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["current_streak"] == 7

    def test_get_streak_history_success(self, authenticated_client):
        """Test getting streak history"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_streak_history.return_value = [
                {
                    "id": 1,
                    "streak_type": "checkin",
                    "start_date": datetime.now().isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "length": 7,
                },
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/streaks/history?limit=10", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)


# =============================================================================
# Level Progress Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.gamification
class TestLevelProgress:
    """Test level progress endpoints"""

    def test_get_level_progress_success(self, authenticated_client):
        """Test getting level progress"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_level_progress.return_value = {
                "current_level": 5,
                "current_points": 1500,
                "points_for_current_level": 1000,
                "points_for_next_level": 2000,
                "points_to_next_level": 500,
                "progress_percentage": 50.0,
            }
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/level/progress", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert data["current_level"] == 5
            assert data["progress_percentage"] == 50.0

    def test_get_level_benefits_success(self, authenticated_client):
        """Test getting level benefits"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.gamification.get_gamification_service"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_level_benefits.return_value = {
                "level": 5,
                "benefits": [
                    "Exclusive badges",
                    "2x bonus points",
                    "Priority support",
                ],
            }
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/gamification/level/5/benefits", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert "benefits" in data
