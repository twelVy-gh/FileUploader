"""
Тесты для API маршрутов полнотекстового поиска (api/search.py).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Создаёт тестовый клиент FastAPI."""
    return TestClient(app)


class TestSearchAPI:
    """Тесты API полнотекстового поиска."""

    @patch('app.api.search.es_service')
    def test_search_basic(self, mock_es, client):
        """Тест базового поиска."""
        mock_es.search.return_value = {
            "results": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "test.pdf",
                    "page": 1,
                    "text": "Результат поиска",
                    "score": 1.5
                }
            ],
            "total": 1,
            "from_item": 0,
            "size": 10
        }
        
        response = client.get("/api/v1/search?q=тест")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["results"]) == 1

    @patch('app.api.search.es_service')
    def test_search_with_pagination(self, mock_es, client):
        """Тест поиска с пагинацией."""
        mock_es.search.return_value = {
            "results": [],
            "total": 0,
            "from_item": 20,
            "size": 10
        }
        
        response = client.get("/api/v1/search?q=тест&from_item=20&size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["from_item"] == 20
        assert data["size"] == 10

    def test_search_empty_query(self, client):
        """Тест поиска с пустым запросом."""
        response = client.get("/api/v1/search?q=")
        # Пустой запрос должен вернуть ошибку (min_length=1)
        assert response.status_code == 422

    def test_search_missing_query(self, client):
        """Тест поиска без параметра q."""
        response = client.get("/api/v1/search")
        assert response.status_code == 422

    @patch('app.api.search.es_service')
    def test_search_multiple_results(self, mock_es, client):
        """Тест поиска с несколькими результатами."""
        mock_es.search.return_value = {
            "results": [
                {
                    "chunk_id": f"chunk_{i}",
                    "file_name": f"doc_{i}.pdf",
                    "page": i + 1,
                    "text": f"Текст результата {i}",
                    "score": 2.0 - i * 0.1
                }
                for i in range(5)
            ],
            "total": 5,
            "from_item": 0,
            "size": 10
        }
        
        response = client.get("/api/v1/search?q=документ")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["results"]) == 5

    @patch('app.api.search.es_service')
    def test_search_with_highlight(self, mock_es, client):
        """Тест что результаты содержат подсветку."""
        mock_es.search.return_value = {
            "results": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "test.pdf",
                    "page": 1,
                    "text": "Текст с <mark>подсветкой</mark>",
                    "score": 1.5
                }
            ],
            "total": 1,
            "from_item": 0,
            "size": 10
        }
        
        response = client.get("/api/v1/search?q=подсветка")
        assert response.status_code == 200
        data = response.json()
        assert "<mark>" in data["results"][0]["text"]

    @patch('app.api.search.es_service')
    def test_search_es_error(self, mock_es, client):
        """Тест обработки ошибки Elasticsearch."""
        mock_es.search.side_effect = Exception("Elasticsearch unavailable")
        
        response = client.get("/api/v1/search?q=тест")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @patch('app.api.search.es_service')
    def test_search_size_limit(self, mock_es, client):
        """Тест ограничения размера результатов."""
        mock_es.search.return_value = {
            "results": [],
            "total": 0,
            "from_item": 0,
            "size": 100
        }
        
        # size=100 — допустимо
        response = client.get("/api/v1/search?q=тест&size=100")
        assert response.status_code == 200
        
        # size=101 — превышает лимит
        response = client.get("/api/v1/search?q=тест&size=101")
        assert response.status_code == 422

    @patch('app.api.search.es_service')
    def test_search_negative_from(self, mock_es, client):
        """Тест отрицательного from_item."""
        response = client.get("/api/v1/search?q=тест&from_item=-1")
        assert response.status_code == 422

    @patch('app.api.search.es_service')
    def test_search_russian_query(self, mock_es, client):
        """Тест поиска с русским запросом."""
        mock_es.search.return_value = {
            "results": [
                {
                    "chunk_id": "chunk_ru",
                    "file_name": "документ.pdf",
                    "page": 1,
                    "text": "Результат по русскому запросу",
                    "score": 1.0
                }
            ],
            "total": 1,
            "from_item": 0,
            "size": 10
        }
        
        response = client.get("/api/v1/search?q=документ")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1