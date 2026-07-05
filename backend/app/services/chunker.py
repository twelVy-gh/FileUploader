"""
Сервис для разбиения текста на чанки.
Реализует разбиение с перекрытием для лучшего контекста при поиске.
"""

from typing import List, Dict, Any
import uuid

from app.core.config import settings


class TextChunker:
    """
    Разбиение текста на чанки фиксированного размера с перекрытием.
    
    Attributes:
        chunk_size: Размер чанка в символах
        chunk_overlap: Размер перекрытия между чанками в символах
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Инициализация чанкера.
        
        Args:
            chunk_size: Размер чанка (по умолчанию из настроек)
            chunk_overlap: Размер перекрытия (по умолчанию из настроек)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def chunk_text(
        self,
        text: str,
        file_name: str,
        page_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Разбивает текст на чанки.
        
        Args:
            text: Текст для разбиения
            file_name: Имя файла (для метаданных)
            page_number: Номер страницы (для метаданных)
            
        Returns:
            List[Dict[str, Any]]: Список чанков с метаданными
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Если это последний чанк, берём до конца текста
            if end >= text_length:
                chunk_text = text[start:]
            else:
                chunk_text = text[start:end]
            
            # Пропускаем пустые чанки
            if chunk_text.strip():
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    "chunk_id": chunk_id,
                    "file_name": file_name,
                    "page_number": page_number,
                    "text": chunk_text.strip()
                })
            
            # Сдвигаем начало с учётом перекрытия
            start += self.chunk_size - self.chunk_overlap
            
            # Защита от бесконечного цикла
            if start >= text_length:
                break
        
        return chunks
    
    def chunk_text_with_pages(
        self,
        pages: List[tuple],
        file_name: str
    ) -> List[Dict[str, Any]]:
        """
        Разбивает текст с номерами страниц на чанки.
        
        Args:
            pages: Список кортежей (номер_страницы, текст)
            file_name: Имя файла
            
        Returns:
            List[Dict[str, Any]]: Список чанков с метаданными
        """
        all_chunks = []
        
        for page_number, text in pages:
            page_chunks = self.chunk_text(text, file_name, page_number)
            all_chunks.extend(page_chunks)
        
        return all_chunks


# Глобальный экземпляр чанкера
chunker = TextChunker()