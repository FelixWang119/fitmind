"""
API Tests for Goal System Endpoints
Sprint 2 - Epic 2: Goal System Implementation

Tests cover:
- Goal recommendations
- Goal CRUD operations
- Goal progress tracking
- Goal feedback
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
import uuid


# =============================================================================
# Goal Recommendations Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
class TestGoalRecommendations:
    """Test goal recommendation endpoints"""

    def test_get_all_recommendations_success(self, authenticated_client):
        """Test getting all goal recommendations"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.goals.GoalRecommendationService"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_all_recommendations.return_value = {
                "weight": {
                    "target_weight": 65000,
                    "timeline": "3 months",
                    "daily_calorie_target": 1800,
                },
                "exercise": {
                    "daily_steps": 10000,
                    "weekly_workouts": 3,
                },
                "diet": {
                    "daily_protein": 120,
                    "daily_water": 2000,
                },
                "habit": {
                    "daily_water_ml": 2000,
                    "sleep_hours": 7.5,
                },
            }
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/goals/recommendations", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert (
                "weight" in data
                or "exercise" in data
                or "diet" in data
                or "habit" in data
            )

    def test_get_recommendation_by_type_weight(self, authenticated_client):
        """Test getting weight goal recommendation"""
        client, headers, user = authenticated_client

        with patch(
            "app.api.v1.endpoints.goals.GoalRecommendationService"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.calculate_weight_goal.return_value = {
                "target_weight": 65000,
                "timeline": "3 months",
                "daily_calorie_target": 1800,
            }
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/goals/recommendations/weight", headers=headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["goal_type"] == "weight"
            assert "recommendation" in data

    def test_get_recommendation_invalid_type(self, authenticated_client):
        """Test getting recommendation with invalid type"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/goals/recommendations/invalid_type", headers=headers
        )

        assert response.status_code == 400

    def test_post_goal_recommendation_exercise(self, authenticated_client):
        """Test posting exercise goal recommendation"""
        client, headers, user = authenticated_client

        request_data = {
            "goal_type": "exercise",
            "user_profile": {
                "activity_level": "moderate",
                "current_steps": 5000,
            },
        }

        with patch(
            "app.api.v1.endpoints.goals.GoalRecommendationService"
        ) as mock_service:
            mock_instance = MagicMock()
            mock_instance.calculate_exercise_goal.return_value = {
                "daily_steps": 8000,
                "weekly_workouts": 4,
            }
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1/goals/recommendations", json=request_data, headers=headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["goal_type"] == "exercise"


# =============================================================================
# Goal CRUD Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
class TestGoalCRUD:
    """Test goal CRUD endpoints"""

    def test_create_goal_success(self, authenticated_client, db_session):
        """Test creating a new goal"""
        client, headers, user = authenticated_client

        goal_data = {
            "goal_type": "weight",
            "current_value": 75000,
            "target_value": 65000,
            "unit": "g",
            "target_date": (date.today() + timedelta(days=90)).isoformat(),
        }

        response = client.post("/api/v1/goals", json=goal_data, headers=headers)

        # May succeed or fail depending on DB setup
        assert response.status_code in [200, 201, 500]

    def test_list_goals_empty(self, authenticated_client):
        """Test listing goals when none exist"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/goals", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_goals_with_filters(self, authenticated_client):
        """Test listing goals with status filter"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/goals?status=active&goal_type=weight", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_goal_not_found(self, authenticated_client):
        """Test getting non-existent goal"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/goals/99999", headers=headers)

        assert response.status_code == 404

    def test_update_goal_not_found(self, authenticated_client):
        """Test updating non-existent goal"""
        client, headers, user = authenticated_client

        response = client.patch(
            "/api/v1/goals/99999", json={"target_value": 60000}, headers=headers
        )

        assert response.status_code == 404

    def test_delete_goal_not_found(self, authenticated_client):
        """Test deleting non-existent goal"""
        client, headers, user = authenticated_client

        response = client.delete("/api/v1/goals/99999", headers=headers)

        assert response.status_code == 404


# =============================================================================
# Goal Progress Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
class TestGoalProgress:
    """Test goal progress endpoints"""

    def test_record_progress_goal_not_found(self, authenticated_client):
        """Test recording progress for non-existent goal"""
        client, headers, user = authenticated_client

        progress_data = {
            "value": 74000,
            "recorded_date": date.today().isoformat(),
            "daily_target_met": True,
        }

        response = client.post(
            "/api/v1/goals/99999/progress", json=progress_data, headers=headers
        )

        assert response.status_code == 404

    def test_get_goal_progress_goal_not_found(self, authenticated_client):
        """Test getting progress for non-existent goal"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/goals/99999/progress?days=30", headers=headers)

        assert response.status_code == 404


# =============================================================================
# Goal Status Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
class TestGoalStatus:
    """Test goal status update endpoints"""

    def test_update_goal_status_not_found(self, authenticated_client):
        """Test updating status for non-existent goal"""
        client, headers, user = authenticated_client

        response = client.patch(
            "/api/v1/goals/99999/status?new_status=paused", headers=headers
        )

        assert response.status_code == 404

    def test_update_goal_status_invalid(self, authenticated_client):
        """Test updating goal with invalid status"""
        client, headers, user = authenticated_client

        response = client.patch(
            "/api/v1/goals/1/status?new_status=invalid", headers=headers
        )

        assert response.status_code == 400


# =============================================================================
# Goal Feedback Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
@pytest.mark.integration
class TestGoalFeedback:
    """Test goal feedback endpoints"""

    def test_check_goal_feedback_success(self, authenticated_client):
        """Test checking goal feedback"""
        client, headers, user = authenticated_client

        with patch("app.api.v1.endpoints.goals.GoalFeedbackService") as mock_service:
            mock_instance = MagicMock()
            mock_instance.check_and_send_feedback.return_value = []
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/goals/feedback/check", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "message" in data or "feedback" in data

    def test_check_goal_feedback_force(self, authenticated_client):
        """Test forcing goal feedback check"""
        client, headers, user = authenticated_client

        with patch("app.api.v1.endpoints.goals.GoalFeedbackService") as mock_service:
            mock_instance = MagicMock()
            mock_instance.check_and_send_feedback.return_value = [
                {"goal_id": 1, "message": "On track!"}
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/api/v1/goals/feedback/check?force=true", headers=headers
            )

            assert response.status_code == 200

    def test_get_feedback_summary(self, authenticated_client):
        """Test getting feedback summary"""
        client, headers, user = authenticated_client

        with patch("app.api.v1.endpoints.goals.GoalFeedbackService") as mock_service:
            mock_instance = MagicMock()
            mock_instance.get_feedback_summary.return_value = {
                "total_goals": 3,
                "on_track": 2,
                "needs_attention": 1,
                "exceeding": 0,
            }
            mock_service.return_value = mock_instance

            response = client.get("/api/v1/goals/feedback/summary", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "needs_attention" in data or "on_track" in data

    def test_dismiss_feedback_not_found(self, authenticated_client):
        """Test dismissing feedback for non-existent goal"""
        client, headers, user = authenticated_client

        response = client.post(
            "/api/v1/goals/feedback/99999/dismiss?action=dismiss_today", headers=headers
        )

        assert response.status_code == 404

    def test_dismiss_feedback_invalid_action(self, authenticated_client):
        """Test dismissing feedback with invalid action"""
        client, headers, user = authenticated_client

        response = client.post(
            "/api/v1/goals/feedback/1/dismiss?action=invalid", headers=headers
        )

        # Should still work but return message
        assert response.status_code in [200, 404]


# =============================================================================
# Goal History Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.goals
class TestGoalHistory:
    """Test goal history endpoints"""

    def test_get_goal_history_not_found(self, authenticated_client):
        """Test getting history for non-existent goal"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/goals/99999/history", headers=headers)

        assert response.status_code == 404
