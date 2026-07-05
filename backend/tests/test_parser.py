"""
Тесты для сервиса парсинга документов (parser.py).
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.parser import DocumentParser


class TestDocumentParser:
    """Тесты класса DocumentParser."""

    def setup_method(self):
        """Инициализация парсера перед каждым тестом."""
        self.parser = DocumentParser()

    def test_extract_text_with_pages_pdf(self, sample_pdf_path):
        """Тест извлечения текста из PDF файла."""
        pages = self.parser.extract_text_with_pages(sample_pdf_path)
        # PDF может быть пустым, но метод должен вернуть список
        assert isinstance(pages, list)

    def test_extract_text_with_pages_docx(self, sample_docx_path):
        """Тест извлечения текста из DOCX файла."""
        pages = self.parser.extract_text_with_pages(sample_docx_path)
        assert isinstance(pages, list)
        assert len(pages) > 0
        # DOCX возвращается как одна "страница"
        assert pages[0]["page_number"] == 1
        assert "Тестовый текст" in pages[0]["text"]

    def test_extract_text_with_pages_invalid_format(self, tmp_path):
        """Тест обработки неподдерживаемого формата."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("Просто текст", encoding="utf-8")
        pages = self.parser.extract_text_with_pages(str(txt_path))
        assert pages == []

    def test_extract_text_with_pages_nonexistent_file(self):
        """Тест обработки несуществующего файла."""
        pages = self.parser.extract_text_with_pages("/nonexistent/file.pdf")
        assert pages == []

    def test_extract_text_with_pages_empty_pdf(self, sample_pdf_path):
        """Тест обработки PDF без текстового содержимого."""
        pages = self.parser.extract_text_with_pages(sample_pdf_path)
        # Минимальный PDF может не содержать текста
        assert isinstance(pages, list)

    def test_extract_text_with_pages_docx_multiple_paragraphs(self, tmp_path):
        """Тест DOCX с несколькими абзацами."""
        try:
            from docx import Document
            doc = Document()
            doc.add_paragraph("Первый абзац.")
            doc.add_paragraph("Второй абзац.")
            doc.add_paragraph("Третий абзац.")
            docx_path = tmp_path / "multi_para.docx"
            doc.save(str(docx_path))

            pages = self.parser.extract_text_with_pages(str(docx_path))
            assert len(pages) == 1
            assert "Первый абзац" in pages[0]["text"]
            assert "Второй абзац" in pages[0]["text"]
            assert "Третий абзац" in pages[0]["text"]
        except ImportError:
            pytest.skip("python-docx не установлен")

    def test_extract_text_with_pages_docx_empty(self, tmp_path):
        """Тест пустого DOCX файла."""
        try:
            from docx import Document
            doc = Document()
            docx_path = tmp_path / "empty.docx"
            doc.save(str(docx_path))

            pages = self.parser.extract_text_with_pages(str(docx_path))
            # Пустой документ должен вернуть пустой список или список с пустым текстом
            assert isinstance(pages, list)
        except ImportError:
            pytest.skip("python-docx не установлен")

    def test_is_pdf_extension(self):
        """Тест определения PDF по расширению."""
        assert self.parser._get_file_type("document.pdf") == "pdf"
        assert self.parser._get_file_type("DOCUMENT.PDF") == "pdf"

    def test_is_docx_extension(self):
        """Тест определения DOCX по расширению."""
        assert self.parser._get_file_type("document.docx") == "docx"
        assert self.parser._get_file_type("DOCUMENT.DOCX") == "docx"

    def test_unknown_extension(self):
        """Тест неизвестного расширения."""
        assert self.parser._get_file_type("document.txt") == "unknown"
        assert self.parser._get_file_type("document.jpg") == "unknown"
        assert self.parser._get_file_type("noextension") == "unknown"