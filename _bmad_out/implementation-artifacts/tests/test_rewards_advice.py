"""
奖励和个性化建议 API 端点测试

覆盖功能：
- 奖励系统
- 个性化建议
- 用户体验端点
"""

import pytest
from fastapi.testclient import TestClient


class TestRewardsEndpoints:
    """奖励端点测试"""

    def test_get_rewards_requires_auth(self, client: TestClient):
        """测试获取奖励需要认证"""
        response = client.get("/api/v1/rewards/")
        assert response.status_code == 401

    def test_get_rewards_with_auth(self, authenticated_client):
        """测试获取奖励列表"""
        client, headers, user = authenticated_client
        response = client.get("/api/v1/rewards/", headers=headers)
        assert response.status_code == 200

    def test_get_available_rewards(self, authenticated_client):
        """测试获取可用奖励"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/rewards/available", headers=headers)
        assert response.status_code == 200

    def test_claim_reward(self, authenticated_client):
        """测试领取奖励"""
        client, headers, user = authenticated_client

        # 尝试领取奖励
        response = client.post(
            "/api/v1/rewards/claim", json={"reward_id": 1}, headers=headers
        )
        # 可能成功或失败（取决于积分是否足够）
        assert response.status_code in [200, 400, 404]


class TestPersonalizedAdviceEndpoints:
    """个性化建议端点测试"""

    def test_get_advice_requires_auth(self, client: TestClient):
        """测试获取个性化建议需要认证"""
        response = client.get("/api/v1/advice/")
        assert response.status_code == 401

    def test_get_personalized_advice(self, authenticated_client):
        """测试获取个性化建议"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/advice/personalized", headers=headers)
        assert response.status_code == 200

    def test_get_daily_advice(self, authenticated_client):
        """测试获取每日建议"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/advice/daily", headers=headers)
        assert response.status_code == 200

    def test_get_health_advice_by_category(self, authenticated_client):
        """测试按类别获取健康建议"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/advice/health?category=nutrition", headers=headers
        )
        assert response.status_code == 200


class TestUserExperienceEndpoints:
    """用户体验端点测试"""

    def test_get_user_preferences_requires_auth(self, client: TestClient):
        """测试获取用户偏好需要认证"""
        response = client.get("/api/v1/user-experience/preferences")
        assert response.status_code == 401

    def test_get_user_preferences(self, authenticated_client):
        """测试获取用户偏好"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/user-experience/preferences", headers=headers)
        assert response.status_code == 200

    def test_update_user_preferences(self, authenticated_client):
        """测试更新用户偏好"""
        client, headers, user = authenticated_client

        preferences_data = {
            "theme": "dark",
            "language": "zh-CN",
            "notifications_enabled": True,
        }

        response = client.put(
            "/api/v1/user-experience/preferences",
            json=preferences_data,
            headers=headers,
        )
        assert response.status_code == 200


class TestHealthAssessmentEndpoints:
    """健康评估端点测试"""

    def test_get_health_assessment_requires_auth(self, client: TestClient):
        """测试获取健康评估需要认证"""
        response = client.get("/api/v1/health-assessment/")
        assert response.status_code == 401

    def test_get_health_assessment(self, authenticated_client):
        """测试获取健康评估"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/health-assessment/", headers=headers)
        assert response.status_code == 200

    def test_submit_health_assessment(self, authenticated_client):
        """测试提交健康评估问卷"""
        client, headers, user = authenticated_client

        assessment_data = {
            "age": 30,
            "gender": "male",
            "height": 175,
            "weight": 70,
            "activity_level": "moderate",
            "sleep_quality": "good",
            "stress_level": 5,
        }

        response = client.post(
            "/api/v1/health-assessment/", json=assessment_data, headers=headers
        )
        assert response.status_code == 200


class TestHealthReportsEndpoints:
    """健康报告端点测试"""

    def test_get_health_report_requires_auth(self, client: TestClient):
        """测试获取健康报告需要认证"""
        response = client.get("/api/v1/health-reports/")
        assert response.status_code == 401

    def test_get_health_report(self, authenticated_client):
        """测试获取健康报告"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/health-reports/", headers=headers)
        assert response.status_code == 200

    def test_get_health_report_pdf(self, authenticated_client):
        """测试获取健康报告 PDF"""
        client, headers, user = authenticated_client

        response = client.get("/api/v1/health-reports/pdf", headers=headers)
        # 可能返回 PDF 或 JSON
        assert response.status_code in [200, 404]


class TestScientificVisualizationEndpoints:
    """科学可视化端点测试"""

    def test_get_visualization_requires_auth(self, client: TestClient):
        """测试获取可视化数据需要认证"""
        response = client.get("/api/v1/scientific-visualization/")
        assert response.status_code == 401

    def test_get_pattern_recognition(self, authenticated_client):
        """测试获取模式识别数据"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/scientific-visualization/patterns", headers=headers
        )
        assert response.status_code == 200

    def test_get_correlation_data(self, authenticated_client):
        """测试获取相关性数据"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/scientific-visualization/correlations", headers=headers
        )
        assert response.status_code == 200

    def test_get_time_series_analysis(self, authenticated_client):
        """测试获取时间序列分析"""
        client, headers, user = authenticated_client

        response = client.get(
            "/api/v1/scientific-visualization/time-series", headers=headers
        )
        assert response.status_code == 200
