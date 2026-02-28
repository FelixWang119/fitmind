"""
API Tests for Calorie Balance Endpoints
Sprint 2 - Epic 3: Calorie Balance Enhancement

Tests cover:
- Calorie balance calculation
- Calorie balance history
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock


# =============================================================================
# Calorie Balance Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.calorie
@pytest.mark.integration
class TestCalorieBalance:
    """Test calorie balance endpoints"""

    def test_get_calorie_balance_success(self, authenticated_client):
        """Test getting calorie balance for today"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1800.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get("/api/v1/calorie-balance", headers=headers)

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "intake" in data
            assert "bmr" in data
            assert "burn" in data
            assert "surplus" in data
            assert "net" in data
            assert "progress" in data
            assert "target" in data

    def test_get_calorie_balance_with_date(self, authenticated_client):
        """Test getting calorie balance for specific date"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 2000.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            target_date = (date.today() - timedelta(days=1)).isoformat()
            response = client.get(
                f"/api/v1/calorie-balance?date={target_date}", headers=headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["date"] == target_date

    def test_get_calorie_balance_invalid_date(self, authenticated_client):
        """Test getting calorie balance with invalid date format"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/calorie-balance?date=invalid-date", headers=headers
        )

        # Should fallback to today
        assert response.status_code == 200

    def test_get_calorie_balance_calculation(self, authenticated_client):
        """Test calorie balance calculation logic"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            # Given: intake = 2000, bmr = 1500, burn = 300
            mock_intake.return_value = 2000.0
            mock_burn.return_value = 300.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get("/api/v1/calorie-balance", headers=headers)

            assert response.status_code == 200
            data = response.json()

            # surplus = intake - bmr - burn = 2000 - 1500 - 300 = 200
            assert data["surplus"] == 200.0

            # net = bmr + burn - intake = 1500 + 300 - 2000 = -200
            assert data["net"] == -200.0

            # progress = (intake / bmr) * 100 = (2000 / 1500) * 100 = 133.3%
            assert data["progress"] == pytest.approx(133.3, rel=0.1)

    def test_get_calorie_balance_zero_bmr(self, authenticated_client):
        """Test calorie balance with zero BMR"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1000.0
            mock_burn.return_value = 0.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 0.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get("/api/v1/calorie-balance", headers=headers)

            assert response.status_code == 200
            data = response.json()

            # Progress should be 0 when BMR is 0
            assert data["progress"] == 0.0

    def test_get_calorie_balance_progress_cap(self, authenticated_client):
        """Test that progress is capped at 200%"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            # High intake that would result in > 200% progress
            mock_intake.return_value = 5000.0
            mock_burn.return_value = 0.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get("/api/v1/calorie-balance", headers=headers)

            assert response.status_code == 200
            data = response.json()

            # Progress should be capped at 200%
            assert data["progress"] == 200.0


# =============================================================================
# Calorie Balance History Tests
# =============================================================================


@pytest.mark.api
@pytest.mark.calorie
class TestCalorieBalanceHistory:
    """Test calorie balance history endpoints"""

    def test_get_calorie_balance_history_default(self, authenticated_client):
        """Test getting calorie balance history with default 7 days"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1800.0
            mock_burn.return_value = 200.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get("/api/v1/calorie-balance/history", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert "history" in data
            assert "days" in data
            assert data["days"] == 7
            assert len(data["history"]) == 7

    def test_get_calorie_balance_history_custom_days(self, authenticated_client):
        """Test getting calorie balance history with custom days"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1800.0
            mock_burn.return_value = 200.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get(
                "/api/v1/calorie-balance/history?days=14", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert data["days"] == 14
            assert len(data["history"]) == 14

    def test_get_calorie_balance_history_max_days(self, authenticated_client):
        """Test getting calorie balance history with max 30 days"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1800.0
            mock_burn.return_value = 200.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get(
                "/api/v1/calorie-balance/history?days=30", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            assert data["days"] == 30
            assert len(data["history"]) == 30

    def test_get_calorie_balance_history_invalid_days(self, authenticated_client):
        """Test getting calorie balance history with invalid days"""
        client, headers, user = authenticated_client

        # Days too low
        response = client.get("/api/v1/calorie-balance/history?days=0", headers=headers)

        # Should fail validation
        assert response.status_code == 422

    def test_get_calorie_balance_history_exceeds_max(self, authenticated_client):
        """Test getting calorie balance history exceeding max"""
        client, headers, user = authenticated_client

        # Days exceeds max of 30
        response = client.get(
            "/api/v1/calorie-balance/history?days=31", headers=headers
        )

        # Should fail validation
        assert response.status_code == 422

    def test_get_calorie_balance_history_order(self, authenticated_client):
        """Test that history is in chronological order"""
        client, headers, user = authenticated_client

        with (
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_calorie_intake"
            ) as mock_intake,
            patch(
                "app.api.v1.endpoints.calorie_balance.get_daily_exercise_burn"
            ) as mock_burn,
            patch(
                "app.api.v1.endpoints.calorie_balance.NutritionService"
            ) as mock_nutrition,
        ):
            mock_intake.return_value = 1800.0
            mock_burn.return_value = 200.0

            mock_service_instance = MagicMock()
            mock_service_instance.calculate_bmr.return_value = 1500.0
            mock_nutrition.return_value = mock_service_instance

            response = client.get(
                "/api/v1/calorie-balance/history?days=5", headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            history = data["history"]

            # Verify chronological order
            for i in range(len(history) - 1):
                assert history[i]["date"] < history[i + 1]["date"]


# =============================================================================
# Helper Function Tests
# =============================================================================


@pytest.mark.unit
def test_get_daily_calorie_intake():
    """Test the get_daily_calorie_intake helper function"""
    from app.api.v1.endpoints.calorie_balance import get_daily_calorie_intake
    from unittest.mock import MagicMock

    mock_db = MagicMock()
    user_id = 1
    target_date = date.today()

    # Mock empty meals
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_daily_calorie_intake(mock_db, user_id, target_date)

    assert result == 0.0


@pytest.mark.unit
def test_get_daily_exercise_burn():
    """Test the get_daily_exercise_burn helper function"""
    from app.api.v1.endpoints.calorie_balance import get_daily_exercise_burn
    from unittest.mock import MagicMock

    mock_db = MagicMock()
    user_id = 1
    target_date = date.today()

    # Mock empty exercises
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_daily_exercise_burn(mock_db, user_id, target_date)

    assert result == 0.0
