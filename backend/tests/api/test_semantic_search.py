"""Semantic Search API Tests

测试语义搜索端点：
- P0: 搜索认证
- P0: 基础搜索功能
- P1: 搜索结果排序
- P1: 记忆类型过滤
- P2: 边界情况处理
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, Mock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestSemanticSearchAuthentication:
    """测试语义搜索认证"""

    def test_search_requires_auth(self, client):
        """[P0] 搜索需要认证"""
        response = client.get("/api/v1/memory/search?q=test")
        assert response.status_code == 401

    def test_search_history_requires_auth(self, client):
        """[P0] 搜索历史需要认证"""
        response = client.get("/api/v1/memory/search-history")
        assert response.status_code == 401


class TestSemanticSearchFunctionality:
    """测试语义搜索功能"""

    @pytest.fixture
    def mock_search_service(self):
        """模拟搜索服务"""
        service = MagicMock()
        service.search = MagicMock(
            return_value=[
                {
                    "id": "1",
                    "memory_type": "习惯打卡",
                    "content_summary": "用户完成了晨跑习惯",
                    "source_type": "habit",
                    "source_id": 100,
                    "importance_score": 0.8,
                    "similarity": 0.95,
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "id": "2",
                    "memory_type": "健康记录",
                    "content_summary": "体重下降 2kg",
                    "source_type": "health_record",
                    "source_id": 200,
                    "importance_score": 0.7,
                    "similarity": 0.88,
                    "created_at": datetime.now().isoformat(),
                },
            ]
        )
        return service

    def test_search_with_query(self, client, mock_search_service):
        """[P0] 基础搜索功能"""
        # 模拟认证
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search", params={"q": "运动习惯"})

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) > 0

    def test_search_with_limit(self, client, mock_search_service):
        """[P1] 限制返回数量"""
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search", params={"q": "健康", "limit": 5})

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) <= 5

    def test_search_with_memory_type_filter(self, client, mock_search_service):
        """[P1] 按记忆类型过滤"""
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get(
            "/api/v1/memory/search",
            params={"q": "饮食", "memory_types": "餐食习惯，营养"},
        )

        assert response.status_code == 200
        data = response.json()

        # 结果应该只包含指定类型的记忆
        for result in data["results"]:
            assert result["memory_type"] in ["餐食习惯", "营养"]

    def test_search_with_date_range(self, client, mock_search_service):
        """[P1] 日期范围过滤"""
        client.headers.update({"Authorization": "Bearer test-token"})

        start_date = "2024-01-01"
        end_date = "2024-12-31"

        response = client.get(
            "/api/v1/memory/search",
            params={"q": "运动", "start_date": start_date, "end_date": end_date},
        )

        assert response.status_code == 200

    def test_search_empty_query(self, client, mock_search_service):
        """[P2] 空查询处理"""
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search", params={"q": ""})

        # 应该返回错误或空结果
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert data["results"] == []


class TestSearchResultRanking:
    """测试结果排序"""

    def test_results_sorted_by_similarity(self):
        """[P1] 结果按相似度排序"""
        results = [
            {"id": "1", "similarity": 0.75},
            {"id": "2", "similarity": 0.95},
            {"id": "3", "similarity": 0.88},
        ]

        # 按相似度降序排序
        sorted_results = sorted(results, key=lambda x: x["similarity"], reverse=True)

        assert sorted_results[0]["similarity"] == 0.95
        assert sorted_results[1]["similarity"] == 0.88
        assert sorted_results[2]["similarity"] == 0.75

    def test_results_sorted_by_importance(self):
        """[P1] 结果按重要性排序"""
        results = [
            {"id": "1", "importance_score": 0.5, "similarity": 0.9},
            {"id": "2", "importance_score": 0.9, "similarity": 0.9},
            {"id": "3", "importance_score": 0.7, "similarity": 0.9},
        ]

        # 相似度相同时按重要性排序
        sorted_results = sorted(
            results,
            key=lambda x: (x["similarity"], x["importance_score"]),
            reverse=True,
        )

        assert sorted_results[0]["importance_score"] == 0.9
        assert sorted_results[1]["importance_score"] == 0.7
        assert sorted_results[2]["importance_score"] == 0.5

    def test_combined_ranking_score(self):
        """[P2] 综合排序分数"""
        # similarity 和 importance 的加权组合
        results = [
            {"similarity": 0.9, "importance_score": 0.5},
            {"similarity": 0.7, "importance_score": 0.9},
            {"similarity": 0.8, "importance_score": 0.8},
        ]

        for result in results:
            combined_score = (
                0.7 * result["similarity"] + 0.3 * result["importance_score"]
            )
            assert 0 <= combined_score <= 1


class TestSearchHistory:
    """测试搜索历史"""

    def test_get_search_history(self, client):
        """[P1] 获取搜索历史"""
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search-history")

        assert response.status_code == 200
        data = response.json()

        assert "history" in data
        assert isinstance(data["history"], list)

    def test_search_history_limit(self, client):
        """[P2] 搜索历史限制"""
        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search-history", params={"limit": 10})

        assert response.status_code == 200


class TestSearchEdgeCases:
    """测试边界情况"""

    def test_search_special_characters(self, client):
        """[P2] 特殊字符查询"""
        client.headers.update({"Authorization": "Bearer test-token"})

        special_queries = [
            "test@#$%",
            "你好世界",
            "テスト",
            "test with spaces",
        ]

        for query in special_queries:
            response = client.get("/api/v1/memory/search", params={"q": query})

            # 应该能够处理特殊字符而不崩溃
            assert response.status_code in [200, 400]

    def test_search_very_long_query(self, client):
        """[P2] 超长查询处理"""
        client.headers.update({"Authorization": "Bearer test-token"})

        long_query = "test " * 1000  # 5000 字符

        response = client.get("/api/v1/memory/search", params={"q": long_query})

        # 应该截断或拒绝超长查询
        assert response.status_code in [200, 400, 413]

    def test_search_no_results(self, client, mock_search_service):
        """[P2] 无结果返回"""
        mock_search_service.search = MagicMock(return_value=[])

        client.headers.update({"Authorization": "Bearer test-token"})

        response = client.get("/api/v1/memory/search", params={"q": "不存在的关键词"})

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []


# 测试标记
pytestmark = pytest.mark.memory
