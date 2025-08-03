#!/bin/bash

# Безопасный деплой Telegram бота на DigitalOcean
# Не влияет на другие системы

set -e

echo "🚀 Начинаем безопасный деплой бота..."

# Проверяем подключение к серверу
echo "📡 Проверяем подключение к серверу..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "echo '✅ Подключение к серверу успешно'"

# Создаем директорию для бота
echo "📁 Создаем изолированную директорию..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "mkdir -p /opt/telegram-bots/maps-to-waze-bot/data"

# Копируем файлы
echo "📦 Копируем файлы бота..."
scp -i ~/.ssh/do_key -r . root@159.223.0.234:/opt/telegram-bots/maps-to-waze-bot/

# Настраиваем права доступа
echo "🔐 Настраиваем права доступа..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "cd /opt/telegram-bots/maps-to-waze-bot && chown -R telegram-bot:telegram-bot . && chmod +x deploy.sh"

# Останавливаем старый контейнер если есть
echo "🛑 Останавливаем старый контейнер..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "cd /opt/telegram-bots/maps-to-waze-bot && docker-compose down || true"

# Собираем и запускаем новый контейнер
echo "🐳 Собираем и запускаем Docker контейнер..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "cd /opt/telegram-bots/maps-to-waze-bot && docker-compose up -d --build"

# Проверяем статус
echo "✅ Проверяем статус бота..."
ssh -i ~/.ssh/do_key root@159.223.0.234 "cd /opt/telegram-bots/maps-to-waze-bot && docker-compose ps"

echo "🎉 Деплой завершен! Бот запущен в изолированном контейнере."
echo "📊 Логи: docker-compose logs -f maps-to-waze-bot"
echo "🛑 Остановка: docker-compose down" 