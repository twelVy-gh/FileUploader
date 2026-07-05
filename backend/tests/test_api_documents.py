"""
Тесты для API маршрутов работы с документами (api/documents.py).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.database import get_db


@pytest.fixture
def client():
    """Создаёт тестовый клиент FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Создаёт мок сессии БД."""
    db = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.close = MagicMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def override_db(mock_db):
    """Переопределяет зависимость get_db в FastAPI."""
    def _override_get_db():
        yield mock_db
    app.dependency_overrides[get_db] = _override_get_db
    yield mock_db
    app.dependency_overrides.clear()


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
    def test_get_documents_empty(self, mock_doc_service, client, override_db):
        """Тест получения пустого списка документов."""
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
    def test_upload_pdf_file(self, mock_doc_service, client, override_db):
        """Тест загрузки PDF файла."""
        # Мок валидации — файл валиден
        mock_doc_service.validate_file.return_value = (True, "")

        # Создаём тестовый PDF
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"%PDF-1.4 test content")
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/api/v1/documents/upload",
                    files=[("files", ("test.pdf", f, "application/pdf"))]
                )

            # Должен вернуть 200 с информацией о загрузке
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 1
            assert "document_id" in data[0]
            assert data[0]["file_name"] == "test.pdf"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('app.api.documents.document_service')
    def test_upload_file_too_large(self, mock_doc_service, client, override_db):
        """Тест загрузки слишком большого файла."""
        # Мок валидации — файл слишком большой
        mock_doc_service.validate_file.return_value = (
            False, "Размер файла превышает максимальный (20 МБ)."
        )

        # Создаём файл размером > 20MB
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"x" * (21 * 1024 * 1024))
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/api/v1/documents/upload",
                    files=[("files", ("large.pdf", f, "application/pdf"))]
                )

            assert response.status_code == 400
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('app.api.documents.document_service')
    def test_get_documents_with_results(self, mock_doc_service, client, override_db):
        """Тест получения списка документов с данными."""
        mock_doc = MagicMock()
        mock_doc.id = uuid4()
        mock_doc.file_name = "test.pdf"
        mock_doc.upload_date = "2026-01-05T12:00:00"
        mock_doc.status = "ready"

        mock_doc_service.get_all_documents.return_value = [mock_doc]

        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["documents"]) == 1