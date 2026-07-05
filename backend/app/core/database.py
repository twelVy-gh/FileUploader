"""
Подключение к базе данных PostgreSQL.
Использует SQLAlchemy для работы с БД.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Создание движка SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Генератор сессии базы данных.
    Используется как зависимость в FastAPI эндпоинтах.

    Yields:
        Session: Сессия SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных.
    Создает все таблицы, если они не существуют.
    """
    from app.models.document import Document  # noqa: F401
    Base.metadata.create_all(bind=engine)
