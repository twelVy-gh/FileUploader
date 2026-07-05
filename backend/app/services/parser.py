"""
Сервис для извлечения текста из документов.
Поддерживает PDF (через pdfplumber) и DOCX (через python-docx).
"""

import os
from typing import List, Tuple

import pdfplumber
from docx import Document as DocxDocument


class DocumentParser:
    """
    Парсер документов для извлечения текста.
    
    Methods:
        extract_text: Извлекает текст из файла
        extract_text_with_pages: Извлекает текст с номерами страниц
    """
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Извлекает весь текст из файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: Извлечённый текст
            
        Raises:
            ValueError: Если формат файла не поддерживается
            FileNotFoundError: Если файл не найден
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension == ".pdf":
            return DocumentParser._extract_from_pdf(file_path)
        elif extension == ".docx":
            return DocumentParser._extract_from_docx(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {extension}")
    
    @staticmethod
    def extract_text_with_pages(file_path: str) -> List[Tuple[int, str]]:
        """
        Извлекает текст с номерами страниц.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            List[Tuple[int, str]]: Список кортежей (номер_страницы, текст)
            
        Raises:
            ValueError: Если формат файла не поддерживается
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension == ".pdf":
            return DocumentParser._extract_from_pdf_with_pages(file_path)
        elif extension == ".docx":
            # DOCX не имеет явных страниц, возвращаем весь текст как страницу 1
            text = DocumentParser._extract_from_docx(file_path)
            return [(1, text)] if text.strip() else []
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {extension}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """
        Извлекает текст из PDF файла.
        
        Args:
            file_path: Путь к PDF файлу
            
        Returns:
            str: Извлечённый текст
        """
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n".join(text_parts)
    
    @staticmethod
    def _extract_from_pdf_with_pages(file_path: str) -> List[Tuple[int, str]]:
        """
        Извлекает текст из PDF файла с номерами страниц.
        
        Args:
            file_path: Путь к PDF файлу
            
        Returns:
            List[Tuple[int, str]]: Список кортежей (номер_страницы, текст)
        """
        pages = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append((page_num, page_text))
        
        return pages
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """
        Извлекает текст из DOCX файла.
        
        Args:
            file_path: Путь к DOCX файлу
            
        Returns:
            str: Извлечённый текст
        """
        doc = DocxDocument(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n".join(text_parts)


# Глобальный экземпляр парсера
parser = DocumentParser()