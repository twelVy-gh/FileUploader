"""
Pydantic схемы для результатов поиска.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """
    Схема одного результата поиска.

    Attributes:
        chunk_id: Уникальный идентификатор чанка
        file_name: Имя файла, в котором найден фрагмент
        page: Номер страницы
        text: Фрагмент текста с совпадением
        score: Релевантность (score от Elasticsearch)
    """

    chunk_id: str = Field(..., description="Уникальный идентификатор чанка")
    file_name: str = Field(..., description="Имя файла")
    page: Optional[int] = Field(None, description="Номер страницы")
    text: str = Field(..., description="Фрагмент текста")
    score: float = Field(..., description="Релевантность (score)")


class SearchResponse(BaseModel):
    """
    Схема ответа на поисковый запрос.

    Attributes:
        results: Список результатов поиска
        total: Общее количество найденных результатов
        from_item: Начальный индекс (для пагинации)
        size: Размер страницы
    """

    results: list[SearchResultItem] = Field(...,
                                            description="Список результатов")
    total: int = Field(..., description="Общее количество результатов")
    from_item: int = Field(0, description="Начальный индекс")
    size: int = Field(10, description="Размер страницы")

    class Config:
        """Конфигурация Pydantic."""
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "chunk_id": "abc123",
                        "file_name": "document.pdf",
                        "page": 1,
                        "text": "Пример текста с совпадением",
                        "score": 5.67
                    }
                ],
                "total": 1,
                "from_item": 0,
                "size": 10
            }
        }
