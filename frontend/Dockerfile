# Frontend Dockerfile - многоступенчатая сборка
# Этап 1: Сборка React приложения
FROM node:18-alpine AS builder

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Этап 2: Nginx для раздачи статики
FROM nginx:alpine

# Копирование nginx конфигурации
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копирование собранных файлов из предыдущего этапа
COPY --from=builder /app/dist /usr/share/nginx/html

# Открытие порта
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]