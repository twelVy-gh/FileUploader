"""
Тесты для API маршрутов работы с документами (api/documents.py).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Создаёт тестовый клиент FastAPI."""
    return TestClient(app)


class TestDocumentsAPI:
    """Тесты API работы с документами."""

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Document Search API" in data["message"]

    def test_health_endpoint(self, client):
        """Тест эндпоинта health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert data["api"] == "healthy"

    @patch('app.api.documents.document_service')
    @patch('app.core.database.get_db')
    def test_get_documents_empty(self, mock_get_db, mock_doc_service, client):
        """Тест получения пустого списка документов."""
        # Мок сессии БД
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # Мок возврата пустого списка
        mock_doc_service.get_all_documents.return_value = []
        
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert data["total"] == 0

    def test_upload_no_files(self, client):
        """Тест загрузки без файлов."""
        response = client.post("/api/v1/documents/upload")
        # FastAPI вернёт 422 при отсутствии обязательного параметра
        assert response.status_code in [400, 422]

    def test_upload_invalid_format(self, client, tmp_path):
        """Тест загрузки файла неподдерживаемого формата."""
        # Создаём тестовый .txt файл
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Тестовый текст", encoding="utf-8")
        
        with open(txt_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files=[("files", ("test.txt", f, "text/plain"))]
            )
        
        # Должен вернуть ошибку валидации
        assert response.status_code == 400

    @patch('app.api.documents.document_service')
    @patch('app.core.database.get_db')
    def test_upload_pdf_file(self, mock_get_db, mock_doc_service, client, tmp_path):
        """Тест загрузки PDF файла."""
        # Мок сессии БД
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # Мок валидации
        mock_doc_service.validate_file.return_value = (True, "")
        
        # Создаём тестовый PDF
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test content")
        
        with open(pdf_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files=[("files", ("test.pdf", f, "application/pdf"))]
            )
        
        # Должен вернуть 200 с информацией о загрузке
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @patch('app.api.documents.document_service')
    @patch('app.core.database.get_db')
    def test_upload_file_too_large(self, mock_get_db, mock_doc_service, client, tmp_path):
        """Тест загрузки слишком большого файла."""
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # Мок валидации — файл слишком большой
        mock_doc_service.validate_file.return_value = (
            False, "Размер файла превышает максимальный (20 МБ)."
        )
        
        # Создаём файл размером > 20MB
        large_file = tmp_path / "large.pdf"
        large_file.write_bytes(b"x" * (21 * 1024 * 1024))
        
        with open(large_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files=[("files", ("large.pdf", f, "application/pdf"))]
            )
        
        assert response.status_code == 400