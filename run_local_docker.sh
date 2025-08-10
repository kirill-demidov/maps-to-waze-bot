#!/bin/bash

echo "🐳 Запускаем бота в Docker контейнере..."

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose -f docker-compose.local.yml down

# Удаляем старые образы
echo "🧹 Очищаем старые образы..."
docker-compose -f docker-compose.local.yml build --no-cache

# Запускаем контейнер
echo "🚀 Запускаем бота..."
docker-compose -f docker-compose.local.yml up --build

echo "✅ Бот запущен в контейнере на порту 8082"
