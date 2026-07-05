"""
Сервис для управления документами.
Объединяет парсер, чанкер и Elasticsearch для полной обработки документов.
"""

import logging
import os
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.services.parser import parser
from app.services.chunker import chunker
from app.services.elasticsearch_service import es_service

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Сервис для управления жизненным циклом документа.

    Methods:
        process_document: Полная обработка загруженного файла
        get_all_documents: Получение списка всех документов
        get_document_by_id: Получение документа по ID
        update_status: Обновление статуса документа
    """

    @staticmethod
    def process_document(
        file_path: str,
        file_name: str,
        db: Session
    ) -> Document:
        """
        Полная обработка документа: парсинг, разбиение на чанки, индексация.

        Args:
            file_path: Путь к сохранённому файлу
            file_name: Оригинальное имя файла
            db: Сессия базы данных

        Returns:
            Document: Созданный объект документа

        Raises:
            Exception: Если произошла ошибка при обработке
        """
        # Создаём запись в PostgreSQL
        doc_id = uuid.uuid4()
        document = Document(
            id=doc_id,
            file_name=file_name,
            status=DocumentStatus.UPLOADING
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        try:
            # Обновляем статус на "индексация"
            document.status = DocumentStatus.INDEXING
            db.commit()

            # Извлекаем текст с номерами страниц
            pages = parser.extract_text_with_pages(file_path)

            if not pages:
                raise ValueError("Не удалось извлечь текст из файла")

            # Разбиваем на чанки
            chunks = chunker.chunk_text_with_pages(pages, file_name)

            if not chunks:
                raise ValueError("Файл не содержит текста для индексации")

            # Индексируем в Elasticsearch
            indexed_count = es_service.index_chunks(chunks)
            logger.info(
                f"Indexed {indexed_count} chunks for document '{file_name}'")

            # Обновляем статус на "готов"
            document.status = DocumentStatus.READY
            db.commit()
            db.refresh(document)

            return document

        except Exception as e:
            logger.error(f"Error processing document '{file_name}': {e}")
            document.status = DocumentStatus.ERROR
            db.commit()
            raise

    @staticmethod
    def get_all_documents(db: Session) -> List[Document]:
        """
        Получение списка всех загруженных документов.

        Args:
            db: Сессия базы данных

        Returns:
            List[Document]: Список документов, отсортированных по дате загрузки
        """
        return (
            db.query(Document)
            .order_by(Document.upload_date.desc())
            .all()
        )

    @staticmethod
    def get_document_by_id(
            doc_id: uuid.UUID,
            db: Session) -> Optional[Document]:
        """
        Получение документа по ID.

        Args:
            doc_id: UUID документа
            db: Сессия базы данных

        Returns:
            Optional[Document]: Документ или None
        """
        return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def update_status(
        doc_id: uuid.UUID,
        status: DocumentStatus,
        db: Session
    ) -> Optional[Document]:
        """
        Обновление статуса документа.

        Args:
            doc_id: UUID документа
            status: Новый статус
            db: Сессия базы данных

        Returns:
            Optional[Document]: Обновлённый документ или None
        """
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            document.status = status
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def validate_file(filename: str, file_size: int) -> tuple[bool, str]:
        """
        Валидация загружаемого файла.

        Args:
            filename: Имя файла
            file_size: Размер файла в байтах

        Returns:
            tuple[bool, str]: (валиден, сообщение об ошибке)
        """
        # Проверка расширения
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"Неподдерживаемый формат файла: {ext}. Разрешены только PDF и DOCX."

        # Проверка размера
        if file_size > settings.MAX_FILE_SIZE:
            max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"Размер файла превышает максимальный ({max_mb} МБ)."

        return True, ""


# Глобальный экземпляр сервиса
document_service = DocumentService()
