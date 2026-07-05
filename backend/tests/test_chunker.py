"""
Тесты для сервиса разбиения текста на чанки (chunker.py).
"""

import pytest

from app.services.chunker import TextChunker


class TestTextChunker:
    """Тесты класса TextChunker."""

    def setup_method(self):
        """Инициализация чанкера перед каждым тестом."""
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=50)

    def test_chunk_text_with_pages_basic(self):
        """Тест базового разбиения текста на чанки."""
        pages = [
            {"page_number": 1, "text": "Это тестовый текст для проверки работы чанкера."}
        ]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        
        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert chunks[0]["file_name"] == "test.pdf"
        assert chunks[0]["page_number"] == 1
        assert "chunk_id" in chunks[0]
        assert "text" in chunks[0]

    def test_chunk_text_with_pages_empty(self):
        """Тест разбиения пустого текста."""
        pages = [{"page_number": 1, "text": ""}]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        assert isinstance(chunks, list)

    def test_chunk_text_with_pages_multiple_pages(self):
        """Тест разбиения текста с несколькими страницами."""
        pages = [
            {"page_number": 1, "text": "Текст первой страницы."},
            {"page_number": 2, "text": "Текст второй страницы."},
            {"page_number": 3, "text": "Текст третьей страницы."}
        ]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        
        assert len(chunks) >= 3
        # Проверяем что номера страниц сохраняются
        page_numbers = {c["page_number"] for c in chunks}
        assert 1 in page_numbers
        assert 2 in page_numbers
        assert 3 in page_numbers

    def test_chunk_text_with_pages_long_text(self):
        """Тест разбиения длинного текста на несколько чанков."""
        long_text = "Слово " * 500  # ~3000 символов
        pages = [{"page_number": 1, "text": long_text}]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        
        # При chunk_size=500 должно получиться несколько чанков
        assert len(chunks) >= 2

    def test_chunk_id_uniqueness(self):
        """Тест уникальности chunk_id."""
        pages = [
            {"page_number": 1, "text": "Текст " * 300},
            {"page_number": 2, "text": "Текст " * 300}
        ]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        
        chunk_ids = [c["chunk_id"] for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "chunk_id должны быть уникальными"

    def test_chunk_text_with_pages_file_name_preserved(self):
        """Тест сохранения имени файла в чанках."""
        pages = [{"page_number": 1, "text": "Тест"}]
        file_name = "документ.pdf"
        chunks = self.chunker.chunk_text_with_pages(pages, file_name)
        
        for chunk in chunks:
            assert chunk["file_name"] == file_name

    def test_chunker_default_params(self):
        """Тест параметров по умолчанию."""
        chunker = TextChunker()
        assert chunker.chunk_size > 0
        assert chunker.chunk_overlap >= 0

    def test_chunk_text_with_pages_whitespace_only(self):
        """Тест текста только с пробелами."""
        pages = [{"page_number": 1, "text": "   \n\n\t  "}]
        chunks = self.chunker.chunk_text_with_pages(pages, "test.pdf")
        # Может вернуть пустой список или список с пустым чанком
        assert isinstance(chunks, list)

    def test_chunk_text_with_pages_russian_text(self):
        """Тест работы с русским текстом."""
        text = "Документ содержит русский текст с различными символами: ё, й, ъ, ь."
        pages = [{"page_number": 1, "text": text}]
        chunks = self.chunker.chunk_text_with_pages(pages, "документ.docx")
        
        assert len(chunks) >= 1
        assert "русский" in chunks[0]["text"]