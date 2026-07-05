# Интеллектуальный поиск по документам

Веб-приложение для загрузки, индексации и полнотекстового поиска по документам (PDF, DOCX) с использованием Elasticsearch и русскоязычного анализатора.

## 🚀 Возможности

- **Загрузка документов**: Drag-and-Drop загрузка PDF и DOCX файлов (макс. 20 МБ)
- **Автоматическая обработка**: Извлечение текста, разбиение на чанки, индексация
- **Полнотекстовый поиск**: Поиск с подсветкой совпадений и пагинацией
- **Русскоязычный анализатор**: Морфологический анализ, стоп-слова, стемминг
- **Асинхронная обработка**: Фоновая индексация документов
- **REST API**: Полная документация через Swagger/OpenAPI
- **Docker**: Готовая конфигурация для контейнеризации
- **CI/CD**: GitHub Actions для автоматического тестирования

## 📋 Технологический стек

### Backend
- **FastAPI** — современный веб-фреймворк для Python
- **PostgreSQL** — реляционная база данных для метаданных
- **Elasticsearch 8** — полнотекстовый поиск
- **SQLAlchemy** — ORM для работы с БД
- **PyMuPDF** — извлечение текста из PDF
- **python-docx** — извлечение текста из DOCX

### Frontend
- **React 18** — UI библиотека
- **TypeScript** — типизация
- **Vite** — сборщик и dev-сервер
- **React Router** — маршрутизация
- **Axios** — HTTP клиент

### Инфраструктура
- **Docker & Docker Compose** — контейнеризация
- **Nginx** — reverse proxy для фронтенда
- **GitHub Actions** — CI/CD

## 📁 Структура проекта

```
.
├── backend/                    # Backend приложение
│   ├── app/
│   │   ├── api/               # API маршруты
│   │   │   ├── documents.py   # Загрузка и список документов
│   │   │   └── search.py      # Полнотекстовый поиск
│   │   ├── core/              # Конфигурация и БД
│   │   │   ├── config.py      # Настройки приложения
│   │   │   └── database.py    # Подключение к PostgreSQL
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── services/          # Бизнес-логика
│   │   │   ├── parser.py      # Парсинг PDF/DOCX
│   │   │   ├── chunker.py     # Разбиение на чанки
│   │   │   ├── elasticsearch_service.py  # Работа с ES
│   │   │   └── document_service.py       # Оркестрация
│   │   └── main.py            # Точка входа FastAPI
│   ├── tests/                 # Тесты (pytest)
│   ├── requirements.txt       # Python зависимости
│   └── Dockerfile
├── frontend/                   # Frontend приложение
│   ├── src/
│   │   ├── api/               # API клиент
│   │   ├── components/        # React компоненты
│   │   ├── pages/             # Страницы
│   │   ├── styles/            # CSS стили
│   │   └── types/             # TypeScript типы
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml          # Docker Compose конфигурация
├── .env                        # Переменные окружения
├── .env.example               # Пример переменных окружения
└── README.md
```

## 🛠️ Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Node.js 20+ (для локальной разработки)

### Быстрый старт с Docker

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd "practice app"
```

2. **Настройте переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

3. **Запустите все сервисы**
```bash
docker-compose up -d
```

4. **Откройте приложение**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Elasticsearch: http://localhost:9200

### Локальная разработка

#### Backend

```bash
cd backend

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Запустите PostgreSQL и Elasticsearch через Docker
docker-compose up -d postgres elasticsearch

# Запустите backend сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Установите зависимости
npm install

# Запустите dev-сервер
npm run dev
```

## 📡 API Endpoints

### Загрузка документов
```
POST /api/v1/documents/upload
Content-Type: multipart/form-data

Параметры:
- files: Список файлов (PDF, DOCX)

Ответ:
[
  {
    "message": "Файл 'document.pdf' принят на обработку",
    "document_id": "uuid",
    "file_name": "document.pdf",
    "status": "uploading"
  }
]
```

### Список документов
```
GET /api/v1/documents

Ответ:
{
  "documents": [
    {
      "id": "uuid",
      "file_name": "document.pdf",
      "upload_date": "2026-01-05T12:00:00",
      "status": "ready"
    }
  ],
  "total": 1
}
```

### Полнотекстовый поиск
```
GET /api/v1/search?q=поисковый+запрос&from_item=0&size=10

Параметры:
- q: Поисковый запрос (обязательный)
- from_item: Начальный индекс для пагинации (по умолчанию 0)
- size: Количество результатов (по умолчанию 10, макс 100)

Ответ:
{
  "results": [
    {
      "chunk_id": "chunk_uuid",
      "file_name": "document.pdf",
      "page": 1,
      "text": "Текст с <mark>подсветкой</mark>",
      "score": 1.5
    }
  ],
  "total": 1,
  "from_item": 0,
  "size": 10
}
```

### Health Check
```
GET /health

Ответ:
{
  "api": "healthy",
  "elasticsearch": "healthy",
  "database": "healthy"
}
```

## 🧪 Тестирование

### Запуск тестов backend

```bash
cd backend

# Установите тестовые зависимости
pip install pytest pytest-cov pytest-asyncio httpx

# Запустите все тесты
pytest tests/ -v

# Запустите с покрытием кода
pytest tests/ --cov=app --cov-report=html
```

### Запуск тестов frontend

```bash
cd frontend
npm test
```

## 🏗️ Сборка для продакшена

### Docker образы

```bash
# Сборка backend
docker build -t document-search-backend ./backend

# Сборка frontend
docker build -t document-search-frontend ./frontend
```

### Production запуск

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f elasticsearch
```

### Проверка состояния

```bash
# Health check API
curl http://localhost:8000/health

# Статус Elasticsearch
curl http://localhost:9200/_cluster/health

# Статус PostgreSQL
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

## 🔧 Конфигурация

Основные параметры в `.env`:

```env
# Backend
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=document_search
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/document_search

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Frontend
VITE_API_URL=http://localhost:8000
```

## 📝 Особенности реализации

### Русскоязычный анализатор

Elasticsearch настроен с кастомным анализатором для русского языка:
- **lowercase** — приведение к нижнему регистру
- **russian_morphology** — морфологический анализ
- **ru_stop** — удаление стоп-слов
- **ru_stemmer** — стемминг (усечение окончаний)

### Разбиение на чанки

Документы разбиваются на чанки по ~1000 символов с перекрытием 100 символов для сохранения контекста.

### Асинхронная обработка

Загрузка файлов происходит синхронно, но индексация выполняется в фоновых задачах FastAPI, что позволяет не блокировать API.

## 🐛 Отладка

### Проблемы с Elasticsearch

```bash
# Проверка доступности
curl http://localhost:9200

# Перезапуск
docker-compose restart elasticsearch

# Очистка индекса
curl -X DELETE "http://localhost:9200/documents"
```

### Проблемы с PostgreSQL

```bash
# Проверка подключения
docker-compose exec postgres psql -U postgres -c "\l"

# Перезапуск
docker-compose restart postgres
```

### Проблемы с frontend

```bash
# Очистка кэша
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

## 📄 Лицензия

MIT

## 👥 Авторы

Создано в рамках учебной практики.

## 🤝 Вклад

Pull requests приветствуются! Для крупных изменений сначала откройте issue для обсуждения.

---

**Версия**: 1.0.0  
**Дата**: 2026-01-05