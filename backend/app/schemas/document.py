"""
Pydantic схемы для работы с документами.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """
    Схема ответа с информацией о документе.
    
    Attributes:
        id: Уникальный идентификатор документа
        file_name: Имя файла
        upload_date: Дата загрузки
        status: Статус обработки
    """
    
    id: UUID = Field(..., description="Уникальный идентификатор документа")
    file_name: str = Field(..., description="Имя загруженного файла")
    upload_date: datetime = Field(..., description="Дата и время загрузки")
    status: str = Field(..., description="Статус обработки документа")
    
    class Config:
        """Конфигурация Pydantic."""
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """
    Схема ответа после успешной загрузки документа.
    
    Attributes:
        message: Сообщение о результате
        document_id: ID загруженного документа
        file_name: Имя файла
        status: Статус обработки
    """
    
    message: str = Field(..., description="Сообщение о результате загрузки")
    document_id: UUID = Field(..., description="ID загруженного документа")
    file_name: str = Field(..., description="Имя файла")
    status: str = Field(..., description="Текущий статус обработки")


class DocumentListResponse(BaseModel):
    """
    Схема ответа со списком документов.
    
    Attributes:
        documents: Список документов
        total: Общее количество документов
    """
    
    documents: list[DocumentResponse] = Field(..., description="Список документов")
    total: int = Field(..., description="Общее количество документов")


class ErrorResponse(BaseModel):
    """
    Схема ответа с ошибкой.
    
    Attributes:
        error: Тип ошибки
        detail: Детальное описание ошибки
    """
    
    error: str = Field(..., description="Тип ошибки")
    detail: str = Field(..., description="Детальное описание ошибки")