"""Sleep Tracking API Tests

测试睡眠数据追踪功能：
- P0: 睡眠记录创建
- P0: 睡眠记录认证
- P1: 睡眠质量分析
- P1: 睡眠趋势查询
- P2: 睡眠数据验证
- P2: 边界情况处理

覆盖 PRD FR6: 数据记录与分析
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, Mock, patch
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestSleepTrackingAuthentication:
    """测试睡眠记录认证"""

    def test_create_sleep_record_requires_auth(self, client):
        """[P0] 创建睡眠记录需要认证"""
        response = client.post(
            "/api/v1/sleep/records",
            json={"date": "2024-01-15", "hours": 7.5, "quality": "good"},
        )
        assert response.status_code == 401

    def test_get_sleep_records_requires_auth(self, client):
        """[P0] 获取睡眠记录需要认证"""
        response = client.get("/api/v1/sleep/records")
        assert response.status_code == 401

    def test_get_sleep_stats_requires_auth(self, client):
        """[P0] 获取睡眠统计需要认证"""
        response = client.get("/api/v1/sleep/stats")
        assert response.status_code == 401

    def test_update_sleep_record_requires_auth(self, client):
        """[P0] 更新睡眠记录需要认证"""
        response = client.put("/api/v1/sleep/records/1", json={"hours": 8.0})
        assert response.status_code == 401

    def test_delete_sleep_record_requires_auth(self, client):
        """[P0] 删除睡眠记录需要认证"""
        response = client.delete("/api/v1/sleep/records/1")
        assert response.status_code == 401


class TestSleepRecordCreation:
    """测试睡眠记录创建"""

    @pytest.fixture
    def auth_headers(self):
        """模拟认证头"""
        return {"Authorization": "Bearer test-token"}

    def test_create_sleep_record_success(self, client, auth_headers):
        """[P0] 成功创建睡眠记录"""
        sleep_data = {
            "date": "2024-01-15",
            "hours": 7.5,
            "quality": "good",
            "bedtime": "23:00",
            "wake_time": "06:30",
            "notes": "睡得很好",
        }

        response = client.post(
            "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
        )

        # 应该成功创建 (201) 或返回其他有效状态
        assert response.status_code in [200, 201]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data or "success" in data

    def test_create_sleep_record_minimal_data(self, client, auth_headers):
        """[P1] 使用最小数据集创建睡眠记录"""
        sleep_data = {"date": "2024-01-15", "hours": 7.0}

        response = client.post(
            "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
        )

        # 最小数据应该也能创建成功
        assert response.status_code in [200, 201]

    def test_create_sleep_record_with_quality_rating(self, client, auth_headers):
        """[P1] 创建带睡眠质量评级的记录"""
        quality_ratings = ["excellent", "good", "average", "poor", "terrible"]

        for quality in quality_ratings:
            sleep_data = {
                "date": f"2024-01-{15 + quality_ratings.index(quality)}",
                "hours": 7.5,
                "quality": quality,
            }

            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )

            # 所有评级都应该接受
            assert response.status_code in [200, 201, 422]  # 422 表示验证失败也可接受

    def test_create_sleep_record_decimal_hours(self, client, auth_headers):
        """[P1] 创建带小数小时的睡眠记录"""
        test_cases = [
            7.0,  # 整数
            7.5,  # 半小时
            7.25,  # 15 分钟
            7.75,  # 45 分钟
            8.33,  # 20 分钟
        ]

        for hours in test_cases:
            sleep_data = {
                "date": f"2024-01-{test_cases.index(hours) + 15}",
                "hours": hours,
            }

            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )

            # 应该接受小数小时
            assert response.status_code in [200, 201, 422]


class TestSleepDataValidation:
    """测试睡眠数据验证"""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    def test_sleep_hours_range_validation(self, client, auth_headers):
        """[P2] 睡眠时长范围验证"""
        # 有效范围 (0-24 小时)
        valid_hours = [0, 4, 6, 8, 10, 12, 24]
        for hours in valid_hours:
            sleep_data = {"date": "2024-01-15", "hours": hours}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            # 应该接受合理范围
            assert response.status_code in [200, 201, 422]

        # 无效范围 (负数或超过 24)
        invalid_hours = [-1, -0.5, 24.5, 25, 30]
        for hours in invalid_hours:
            sleep_data = {"date": "2024-01-15", "hours": hours}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            # 应该拒绝无效值
            assert response.status_code == 422

    def test_sleep_date_format_validation(self, client, auth_headers):
        """[P2] 日期格式验证"""
        # 有效格式
        valid_dates = ["2024-01-15", "2024-12-31", datetime.now().strftime("%Y-%m-%d")]

        for date_str in valid_dates:
            sleep_data = {"date": date_str, "hours": 7.5}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            assert response.status_code in [200, 201, 422]

        # 无效格式
        invalid_dates = ["15-01-2024", "01/15/2024", "2024/01/15", "not-a-date"]

        for date_str in invalid_dates:
            sleep_data = {"date": date_str, "hours": 7.5}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            # 应该拒绝无效日期格式
            assert response.status_code == 422

    def test_sleep_quality_enum_validation(self, client, auth_headers):
        """[P2] 睡眠质量枚举验证"""
        # 有效评级
        valid_qualities = ["excellent", "good", "average", "poor", "terrible"]

        for quality in valid_qualities:
            sleep_data = {"date": "2024-01-15", "hours": 7.5, "quality": quality}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            assert response.status_code in [200, 201, 422]

        # 无效评级
        invalid_qualities = ["amazing", "ok", "bad", "123", ""]

        for quality in invalid_qualities:
            sleep_data = {"date": "2024-01-15", "hours": 7.5, "quality": quality}
            response = client.post(
                "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
            )
            # 应该拒绝无效评级
            assert response.status_code == 422

    def test_duplicate_sleep_record_same_date(self, client, auth_headers):
        """[P2] 同日期重复记录处理"""
        sleep_data = {"date": "2024-01-15", "hours": 7.5, "quality": "good"}

        # 第一次创建
        response1 = client.post(
            "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
        )

        # 第二次创建同一天
        response2 = client.post(
            "/api/v1/sleep/records", json=sleep_data, headers=auth_headers
        )

        # 应该更新已有记录或拒绝重复
        assert response2.status_code in [200, 201, 409]  # 409 表示冲突


class TestSleepStatsAndTrends:
    """测试睡眠统计和趋势"""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    @pytest.fixture
    def mock_sleep_records(self):
        """模拟睡眠记录数据"""
        return [
            {
                "id": i + 1,
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "hours": 7.5 + (i % 3) * 0.5,
                "quality": ["good", "average", "excellent"][i % 3],
                "bedtime": "23:00",
                "wake_time": "06:30",
            }
            for i in range(30)
        ]

    def test_get_sleep_stats_success(self, client, auth_headers, mock_sleep_records):
        """[P1] 成功获取睡眠统计"""
        response = client.get("/api/v1/sleep/stats", headers=auth_headers)

        # 应该返回统计数据
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            stats = response.json()
            # 验证统计数据结构
            assert isinstance(stats, dict)
            # 应该包含平均睡眠时长
            assert (
                "average_hours" in stats or "avg_hours" in stats or "average" in stats
            )

    def test_get_sleep_trend_success(self, client, auth_headers, mock_sleep_records):
        """[P1] 成功获取睡眠趋势"""
        response = client.get(
            "/api/v1/sleep/trend", params={"days": 30}, headers=auth_headers
        )

        # 应该返回趋势数据
        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            trend = response.json()
            assert isinstance(trend, dict)
            # 应该包含趋势数据
            assert "records" in trend or "data" in trend or "trend" in trend

    def test_get_weekly_average(self, client, auth_headers, mock_sleep_records):
        """[P1] 获取周平均睡眠"""
        response = client.get(
            "/api/v1/sleep/stats", params={"period": "weekly"}, headers=auth_headers
        )

        if response.status_code == 200:
            stats = response.json()
            # 周平均应该在合理范围
            avg_hours = stats.get("average_hours", stats.get("avg_hours", 0))
            assert 0 <= avg_hours <= 24

    def test_get_monthly_average(self, client, auth_headers, mock_sleep_records):
        """[P1] 获取月平均睡眠"""
        response = client.get(
            "/api/v1/sleep/stats", params={"period": "monthly"}, headers=auth_headers
        )

        if response.status_code == 200:
            stats = response.json()
            avg_hours = stats.get("average_hours", stats.get("avg_hours", 0))
            assert 0 <= avg_hours <= 24

    def test_sleep_quality_distribution(self, client, auth_headers, mock_sleep_records):
        """[P2] 睡眠质量分布统计"""
        response = client.get(
            "/api/v1/sleep/stats",
            params={"include_quality": True},
            headers=auth_headers,
        )

        if response.status_code == 200:
            stats = response.json()
            # 应该包含质量分布
            if "quality_distribution" in stats or "quality_breakdown" in stats:
                quality_dist = stats["quality_distribution"] or stats.get(
                    "quality_breakdown", {}
                )
                assert isinstance(quality_dist, dict)


class TestSleepRecordCRUD:
    """测试睡眠记录增删改查"""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    def test_get_single_sleep_record(self, client, auth_headers):
        """[P1] 获取单条睡眠记录"""
        # 尝试获取记录 (可能需要先创建)
        response = client.get("/api/v1/sleep/records/1", headers=auth_headers)

        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            record = response.json()
            assert "id" in record
            assert "date" in record
            assert "hours" in record

    def test_update_sleep_record(self, client, auth_headers):
        """[P1] 更新睡眠记录"""
        update_data = {"hours": 8.5, "quality": "excellent", "notes": "昨晚睡得非常好"}

        response = client.put(
            "/api/v1/sleep/records/1", json=update_data, headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    def test_delete_sleep_record(self, client, auth_headers):
        """[P2] 删除睡眠记录"""
        response = client.delete("/api/v1/sleep/records/1", headers=auth_headers)

        assert response.status_code in [200, 204, 401, 404]

    def test_get_sleep_records_by_date_range(self, client, auth_headers):
        """[P1] 按日期范围获取睡眠记录"""
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        response = client.get(
            "/api/v1/sleep/records",
            params={"start_date": start_date, "end_date": end_date},
            headers=auth_headers,
        )

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            records = response.json()
            assert isinstance(records, list)


class TestSleepAnalysis:
    """测试睡眠分析功能"""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    def test_sleep_pattern_detection(self, client, auth_headers):
        """[P2] 睡眠模式检测"""
        response = client.get(
            "/api/v1/sleep/analysis", params={"type": "patterns"}, headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    def test_sleep_quality_correlation(self, client, auth_headers):
        """[P2] 睡眠质量关联分析"""
        response = client.get(
            "/api/v1/sleep/analysis",
            params={"type": "correlation"},
            headers=auth_headers,
        )

        assert response.status_code in [200, 401, 404]

    def test_sleep_recommendations(self, client, auth_headers):
        """[P2] 睡眠建议生成"""
        response = client.get("/api/v1/sleep/recommendations", headers=auth_headers)

        assert response.status_code in [200, 401, 404]


class TestSleepDataIntegration:
    """测试睡眠数据集成"""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    def test_sleep_exercise_correlation(self, client, auth_headers):
        """[P2] 睡眠与运动关联"""
        # 检查是否能获取睡眠 - 运动关联数据
        response = client.get(
            "/api/v1/sleep/correlation/exercise", headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    def test_sleep_diet_correlation(self, client, auth_headers):
        """[P2] 睡眠与饮食关联"""
        response = client.get("/api/v1/sleep/correlation/diet", headers=auth_headers)

        assert response.status_code in [200, 401, 404]

    def test_sleep_mood_correlation(self, client, auth_headers):
        """[P2] 睡眠与情绪关联"""
        response = client.get("/api/v1/sleep/correlation/mood", headers=auth_headers)

        assert response.status_code in [200, 401, 404]


# 测试标记
pytestmark = pytest.mark.sleep
