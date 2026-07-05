"""
API маршруты для работы с документами.
Загрузка файлов и получение списка документов.
"""

import logging
import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db, init_db
from app.core.config import settings
from app.models.document import Document
from app.schemas.document import (
    DocumentResponse,
    DocumentUploadResponse,
    DocumentListResponse,
    ErrorResponse
)
from app.services.document_service import document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# Директория для временного хранения загруженных файлов
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _process_document_background(file_path: str, file_name: str, db_session_factory):
    """
    Фоновая обработка документа.
    
    Args:
        file_path: Путь к файлу
        file_name: Имя файла
        db_session_factory: Фабрика сессий БД
    """
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        document_service.process_document(file_path, file_name, db)
    except Exception as e:
        logger.error(f"Background processing failed for '{file_name}': {e}")
    finally:
        db.close()


@router.post(
    "/upload",
    response_model=List[DocumentUploadResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации файла"},
        200: {"description": "Файлы успешно загружены"}
    },
    summary="Загрузка документов",
    description="Загрузка PDF или DOCX файлов. Максимальный размер — 20 МБ."
)
async def upload_documents(
    files: List[UploadFile] = File(..., description="Список файлов для загрузки"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Загрузка одного или нескольких документов.
    
    Принимает файлы в формате multipart/form-data.
    Поддерживаются только PDF и DOCX файлы.
    Для каждого файла генерируется UUID и запускается процесс индексации.
    
    Args:
        files: Список загруженных файлов
        background_tasks: Фоновые задачи FastAPI
        db: Сессия базы данных
        
    Returns:
        List[DocumentUploadResponse]: Список ответов для каждого файла
        
    Raises:
        HTTPException: Если файл не прошёл валидацию
    """
    results = []
    
    for file in files:
        # Валидация имени файла
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Имя файла не может быть пустым"
            )
        
        # Читаем содержимое для проверки размера
        content = await file.read()
        file_size = len(content)
        
        # Валидация файла
        is_valid, error_msg = document_service.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Генерируем UUID для файла
        file_uuid = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower()
        saved_filename = f"{file_uuid}{ext}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        # Сохраняем файл на диск
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Создаём запись в БД со статусом UPLOADING
        document = Document(
            id=uuid.UUID(file_uuid),
            file_name=file.filename,
            status="uploading"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Запускаем фоновую обработку
        background_tasks.add_task(
            _process_document_background,
            file_path,
            file.filename,
            None
        )
        
        results.append(DocumentUploadResponse(
            message=f"Файл '{file.filename}' принят на обработку",
            document_id=document.id,
            file_name=file.filename,
            status=document.status.value if hasattr(document.status, 'value') else document.status
        ))
        
        logger.info(f"File '{file.filename}' uploaded, size: {file_size} bytes")
    
    return results


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="Список документов",
    description="Получение списка всех загруженных документов с метаданными."
)
async def get_documents(
    db: Session = Depends(get_db)
):
    """
    Получение списка всех загруженных документов.
    
    Возвращает метаданные: имя файла, дата загрузки, статус обработки.
    Документы отсортированы по дате загрузки (новые первые).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        DocumentListResponse: Список документов и общее количество
    """
    documents = document_service.get_all_documents(db)
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                file_name=doc.file_name,
                upload_date=doc.upload_date,
                status=doc.status.value if hasattr(doc.status, 'value') else doc.status
            )
            for doc in documents
        ],
        total=len(documents)
    )