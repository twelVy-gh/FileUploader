"""
Модель документа для хранения метаданных в PostgreSQL.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class DocumentStatus(str, PyEnum):
    """
    Перечисление статусов обработки документа.
    """
    UPLOADING = "uploading"      # Файл загружается
    INDEXING = "indexing"        # Файл индексируется
    READY = "ready"              # Готов к поиску
    ERROR = "error"              # Ошибка при обработке


class Document(Base):
    """
    Модель документа для хранения в PostgreSQL.

    Attributes:
        id: Уникальный идентификатор (UUID)
        file_name: Имя загруженного файла
        upload_date: Дата и время загрузки
        status: Статус обработки документа
    """

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор документа"
    )

    file_name = Column(
        String(255),
        nullable=False,
        comment="Имя загруженного файла"
    )

    upload_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Дата и время загрузки"
    )

    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.UPLOADING,
        nullable=False,
        comment="Статус обработки документа"
    )

    def __repr__(self) -> str:
        """Строковое представление модели."""
        return f"<Document(id={self.id}, file_name={self.file_name}, status={self.status})>"

    def to_dict(self) -> dict:
        """
        Преобразование модели в словарь.

        Returns:
            dict: Словарь с данными документа
        """
        return {
            "id": str(self.id),
            "file_name": self.file_name,
            "upload_date": self.upload_date.isoformat(),
            "status": self.status.value
        }
