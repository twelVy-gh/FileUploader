"""
Конфигурация приложения.
Загрузка переменных окружения из .env файла.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    Загружает переменные из .env файла или переменных окружения.
    """
    
    # PostgreSQL
    DATABASE_URL: str = "postgresql://app_user:app_password@postgres:5432/documents_db"
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "app_password"
    POSTGRES_DB: str = "documents_db"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    ES_PASSWORD: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Document processing
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 MB
    CHUNK_SIZE: int = 1000  # символов
    CHUNK_OVERLAP: int = 100  # символов
    
    # Allowed file types
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    
    class Config:
        """Конфигурация Pydantic."""
        env_file = ".env"
        case_sensitive = True


# Глобальный экземпляр настроек
settings = Settings()