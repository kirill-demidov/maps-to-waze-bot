#!/bin/bash

echo "🛑 Останавливаем локальный Docker контейнер..."

# Останавливаем контейнеры
docker-compose -f docker-compose.local.yml down

# Удаляем контейнеры и образы
docker-compose -f docker-compose.local.yml down --rmi all --volumes --remove-orphans

echo "✅ Контейнер остановлен и очищен"
