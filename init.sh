#!/usr/bin/env bash
# ============================================================
# init.sh — Скрипт быстрой инициализации проекта
# "Интеллектуальный поиск по документам"
# ============================================================
# Использование:
#   chmod +x init.sh
#   ./init.sh
# ============================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция вывода заголовка
print_header() {
  echo ""
  echo -e "${CYAN}============================================================${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}============================================================${NC}"
  echo ""
}

# Функция вывода информации
print_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

# Функция вывода успеха
print_success() {
  echo -e "${GREEN}[OK]${NC} $1"
}

# Функция вывода предупреждения
print_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Функция вывода ошибки
print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================
# Проверка зависимостей
# ============================================================
print_header "🔍 Проверка зависимостей"

# Проверка Docker
if command -v docker &> /dev/null; then
  DOCKER_VERSION=$(docker --version)
  print_success "Docker: $DOCKER_VERSION"
else
  print_error "Docker не установлен. Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
  exit 1
fi

# Проверка Docker Compose
if docker compose version &> /dev/null; then
  COMPOSE_VERSION=$(docker compose version --short)
  print_success "Docker Compose: $COMPOSE_VERSION"
elif command -v docker-compose &> /dev/null; then
  COMPOSE_VERSION=$(docker-compose --version)
  print_success "Docker Compose (legacy): $COMPOSE_VERSION"
else
  print_error "Docker Compose не установлен."
  exit 1
fi

# Проверка Python (опционально для локальной разработки)
if command -v python &> /dev/null; then
  PYTHON_VERSION=$(python --version)
  print_info "Python: $PYTHON_VERSION (для локальной разработки)"
elif command -v python3 &> /dev/null; then
  PYTHON_VERSION=$(python3 --version)
  print_info "Python: $PYTHON_VERSION (для локальной разработки)"
else
  print_warn "Python не установлен (нужен только для локальной разработки без Docker)"
fi

# Проверка Node.js (опционально для локальной разработки)
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version)
  print_info "Node.js: $NODE_VERSION (для локальной разработки)"
else
  print_warn "Node.js не установлен (нужен только для локальной разработки без Docker)"
fi

# ============================================================
# Проверка файлов окружения
# ============================================================
print_header "⚙️  Настройка окружения"

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    print_success "Файл .env создан из .env.example"
  else
    print_warn "Файл .env.example не найден, создаём минимальный .env"
    cat > .env << 'EOF'
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
EOF
    print_success "Минимальный .env создан"
  fi
else
  print_success "Файл .env уже существует"
fi

# ============================================================
# Создание необходимых директорий
# ============================================================
print_header "📁 Создание директорий"

mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p frontend/node_modules
print_success "Директории созданы"

# ============================================================
# Остановка старых контейнеров (если есть)
# ============================================================
print_header "🛑 Остановка старых контейнеров (если есть)"

if docker compose ps 2>/dev/null | grep -q "Up"; then
  print_info "Обнаружены запущенные контейнеры. Останавливаем..."
  docker compose down
  print_success "Контейнеры остановлены"
else
  print_info "Нет запущенных контейнеров"
fi

# ============================================================
# Сборка и запуск Docker-контейнеров
# ============================================================
print_header "🐳 Сборка Docker-образов"

print_info "Сборка может занять несколько минут при первом запуске..."
docker compose build

print_success "Docker-образы собраны"

# ============================================================
# Запуск сервисов
# ============================================================
print_header "🚀 Запуск сервисов"

docker compose up -d

print_success "Все сервисы запущены"

# ============================================================
# Ожидание готовности сервисов
# ============================================================
print_header "⏳ Ожидание готовности сервисов"

# Ожидание Elasticsearch
print_info "Ожидание готовности Elasticsearch..."
MAX_RETRIES=30
RETRY_COUNT=0
while ! curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "Elasticsearch не запустился в течение 60 секунд"
    print_info "Проверьте логи: docker compose logs elasticsearch"
    break
  fi
  sleep 2
  echo -n "."
done
echo ""

if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
  print_success "Elasticsearch готов"
fi

# Ожидание Backend API
print_info "Ожидание готовности Backend API..."
RETRY_COUNT=0
while ! curl -s http://localhost:8000/health > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "Backend API не запустился в течение 60 секунд"
    print_info "Проверьте логи: docker compose logs backend"
    break
  fi
  sleep 2
  echo -n "."
done
echo ""

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
  print_success "Backend API готов"
fi

# Ожидание Frontend
print_info "Ожидание готовности Frontend..."
RETRY_COUNT=0
while ! curl -s http://localhost:3000 > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "Frontend не запустился в течение 60 секунд"
    print_info "Проверьте логи: docker compose logs frontend"
    break
  fi
  sleep 2
  echo -n "."
done
echo ""

if curl -s http://localhost:3000 > /dev/null 2>&1; then
  print_success "Frontend готов"
fi

# ============================================================
# Финальный отчёт
# ============================================================
print_header "✅ Проект успешно инициализирован!"

echo -e "${GREEN}Сервисы запущены и доступны по адресам:${NC}"
echo ""
echo -e "  🌐 ${CYAN}Frontend:${NC}         http://localhost:3000"
echo -e "  🔧 ${CYAN}Backend API:${NC}      http://localhost:8000"
echo -e "  📚 ${CYAN}Swagger Docs:${NC}     http://localhost:8000/docs"
echo -e "  🔍 ${CYAN}Elasticsearch:${NC}    http://localhost:9200"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo ""
echo -e "  ${BLUE}docker compose logs -f${NC}          # Просмотр логов"
echo -e "  ${BLUE}docker compose down${NC}             # Остановить все сервисы"
echo -e "  ${BLUE}docker compose restart backend${NC}  # Перезапуск backend"
echo -e "  ${BLUE}docker compose ps${NC}               # Статус контейнеров"
echo ""
echo -e "${YELLOW}Для остановки проекта выполните:${NC}"
echo -e "  ${BLUE}docker compose down${NC}"
echo ""
echo -e "${YELLOW}Для полного удаления (включая данные):${NC}"
echo -e "  ${BLUE}docker compose down -v${NC}"
echo ""