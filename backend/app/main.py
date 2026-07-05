"""
Главный файл FastAPI приложения.
Точка входа для REST API сервиса интеллектуального поиска по документам.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.services.elasticsearch_service import es_service
from app.api.documents import router as documents_router
from app.api.search import router as search_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения.
    Выполняется при старте и остановке приложения.
    """
    # === Startup ===
    logger.info("Starting application...")

    # Инициализация базы данных (создание таблиц)
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Создание индекса в Elasticsearch
    try:
        if es_service.ping():
            es_service.create_index()
            logger.info("Elasticsearch index initialized successfully")
        else:
            logger.warning("Elasticsearch is not available")
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch: {e}")

    logger.info(
        f"Application started on {settings.APP_HOST}:{settings.APP_PORT}")

    yield  # Приложение работает

    # === Shutdown ===
    logger.info("Shutting down application...")


# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="Document Search API",
    description=(
        "REST API сервис для интеллектуального поиска по документам. "
        "Поддерживает загрузку PDF и DOCX файлов, извлечение текста, "
        "индексацию в Elasticsearch и полнотекстовый поиск с подсветкой результатов."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Настройка CORS (для доступа с фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов (роутов)
app.include_router(documents_router)
app.include_router(search_router)


@app.get(
    "/",
    tags=["root"],
    summary="Корневой эндпоинт",
    description="Проверка работоспособности API."
)
async def root():
    """
    Корневой эндпоинт для проверки работоспособности API.

    Returns:
        dict: Сообщение о статусе API
    """
    return {
        "message": "Document Search API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Проверка состояния всех сервисов."
)
async def health_check():
    """
    Проверка состояния API и зависимостей.

    Returns:
        dict: Статус API, PostgreSQL и Elasticsearch
    """
    health = {
        "api": "healthy",
        "elasticsearch": "unknown",
        "database": "unknown"
    }

    # Проверка Elasticsearch
    try:
        if es_service.ping():
            health["elasticsearch"] = "healthy"
        else:
            health["elasticsearch"] = "unhealthy"
    except Exception:
        health["elasticsearch"] = "unhealthy"

    # Проверка PostgreSQL
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health["database"] = "healthy"
    except Exception:
        health["database"] = "unhealthy"

    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
