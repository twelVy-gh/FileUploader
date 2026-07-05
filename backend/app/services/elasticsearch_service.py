"""
Сервис для работы с Elasticsearch.
Управление индексом, индексация документов и полнотекстовый поиск.
"""

import logging
from typing import List, Dict, Any

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.core.config import settings

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """
    Сервис для взаимодействия с Elasticsearch.

    Methods:
        create_index: Создание индекса с маппингом
        index_chunks: Индексация списка чанков
        search: Полнотекстовый поиск
        ping: Проверка соединения
    """

    INDEX_NAME = "documents"

    def __init__(self):
        """Инициализация клиента Elasticsearch."""
        self.client = Elasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )

    def ping(self) -> bool:
        """
        Проверка соединения с Elasticsearch.

        Returns:
            bool: True если соединение установлено
        """
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Elasticsearch ping failed: {e}")
            return False

    def create_index(self) -> bool:
        """
        Создание индекса documents с русскоязычным анализатором.

        Returns:
            bool: True если индекс создан или уже существует
        """
        if self.client.indices.exists(index=self.INDEX_NAME):
            logger.info(f"Index '{self.INDEX_NAME}' already exists")
            return True

        settings_body = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ru_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_morphology", "ru_stop", "ru_stemmer"]
                        }
                    },
                    "filter": {
                        "ru_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "ru_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        },
                        "russian_morphology": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "file_name": {
                        "type": "keyword"
                    },
                    "page_number": {
                        "type": "integer"
                    },
                    "chunk_id": {
                        "type": "keyword"
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "ru_analyzer",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        }

        try:
            self.client.indices.create(
                index=self.INDEX_NAME, body=settings_body)
            logger.info(f"Index '{self.INDEX_NAME}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Индексация списка чанков в Elasticsearch.

        Args:
            chunks: Список чанков с полями chunk_id, file_name, page_number, text

        Returns:
            int: Количество успешно проиндексированных чанков
        """
        if not chunks:
            return 0

        actions = []
        for chunk in chunks:
            action = {
                "_index": self.INDEX_NAME,
                "_id": chunk["chunk_id"],
                "_source": {
                    "chunk_id": chunk["chunk_id"],
                    "file_name": chunk["file_name"],
                    "page_number": chunk.get("page_number", 1),
                    "text": chunk["text"]
                }
            }
            actions.append(action)

        try:
            success, _ = bulk(self.client, actions, raise_on_error=True)
            logger.info(f"Indexed {success} chunks")
            return success
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            raise

    def search(
        self,
        query: str,
        from_item: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Полнотекстовый поиск по индексу documents.

        Args:
            query: Поисковый запрос
            from_item: Начальный индекс для пагинации
            size: Количество результатов на странице

        Returns:
            Dict[str, Any]: Результаты поиска с метаданными
        """
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "highlight": {
                "fields": {
                    "text": {}
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            },
            "from": from_item,
            "size": size
        }

        try:
            response = self.client.search(index=self.INDEX_NAME, body=body)
            hits = response["hits"]
            total = hits["total"]["value"]

            results = []
            for hit in hits["hits"]:
                source = hit["_source"]
                highlighted = hit.get(
                    "highlight", {}).get(
                    "text", [
                        source["text"]])
                results.append({
                    "chunk_id": source["chunk_id"],
                    "file_name": source["file_name"],
                    "page": source.get("page_number", 1),
                    "text": highlighted[0] if highlighted else source["text"],
                    "score": hit["_score"]
                })

            return {
                "results": results,
                "total": total,
                "from_item": from_item,
                "size": size
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise


# Глобальный экземпляр сервиса
es_service = ElasticsearchService()
