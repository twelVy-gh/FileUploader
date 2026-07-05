"""
API маршруты для полнотекстового поиска.
"""

import logging

from fastapi import APIRouter, Query, HTTPException

from app.schemas.search import SearchResponse, SearchResultItem
from app.services.elasticsearch_service import es_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Полнотекстовый поиск",
    description="Поиск по проиндексированным документам с подсветкой совпадений."
)
async def search_documents(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    from_item: int = Query(0, ge=0, description="Начальный индекс для пагинации"),
    size: int = Query(10, ge=1, le=100, description="Количество результатов на странице")
):
    """
    Полнотекстовый поиск по документам.

    Выполняет поиск в Elasticsearch по полю text с использованием
    русскоязычного анализатора. Поддерживает пагинацию.

    Args:
        q: Поисковый запрос (обязательный параметр)
        from_item: Начальный индекс для пагинации (по умолчанию 0)
        size: Количество результатов на странице (по умолчанию 10, макс 100)

    Returns:
        SearchResponse: Результаты поиска с метаданными

    Raises:
        HTTPException: Если поиск не удался или запрос пустой
    """
    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос не может быть пустым"
        )

    try:
        result = es_service.search(
            query=q.strip(),
            from_item=from_item,
            size=size
        )

        return SearchResponse(
            results=[
                SearchResultItem(
                    chunk_id=item["chunk_id"],
                    file_name=item["file_name"],
                    page=item["page"],
                    text=item["text"],
                    score=item["score"]
                )
                for item in result["results"]
            ],
            total=result["total"],
            from_item=result["from_item"],
            size=result["size"]
        )

    except Exception as e:
        logger.error(f"Search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при выполнении поиска: {str(e)}"
        )
