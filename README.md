# Maps to Waze Telegram Bot

🤖 Telegram бот для конвертации ссылок Google Maps в Waze навигацию.

## ✨ Возможности

- ✅ Конвертация любых ссылок Google Maps в Waze
- ✅ Поддержка коротких ссылок (maps.app.goo.gl)
- ✅ Обработка координат в десятичном формате (40.7128, -74.0060)
- ✅ Обработка координат в формате DMS (31°44'49.8"N 35°01'46.6"E)
- ✅ Google Maps API для извлечения координат из ссылок на места
- ✅ Автоматическое расширение коротких ссылок
- ✅ Подробное логирование
- ✅ Готов к развертыванию в облаке

## 📋 Поддерживаемые форматы

### Ссылки Google Maps
- `https://maps.google.com/...`
- `https://www.google.com/maps/...`
- `https://goo.gl/maps/...`
- `https://maps.app.goo.gl/...`
- Любые ссылки на места и достопримечательности

### Координаты
- **Десятичные**: `40.7128, -74.0060`
- **DMS**: `31°44'49.8"N 35°01'46.6"E`

## 🔑 Получение API ключей

### Telegram Bot Token

1. **Найдите @BotFather в Telegram**
2. **Отправьте команду:** `/newbot`
3. **Следуйте инструкциям:**
   - Введите имя бота
   - Введите username бота (должен заканчиваться на `bot`)
4. **Скопируйте полученный токен**

### Google Maps API Key

1. **Перейдите в [Google Cloud Console](https://console.cloud.google.com/)**
2. **Выберите или создайте проект**
3. **Включите Places API:**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Places API"
   - Нажмите "Enable"
4. **Создайте API ключ:**
   - Перейдите в "APIs & Services" → "Credentials"
   - Нажмите "Create Credentials" → "API Key"
   - Скопируйте созданный ключ
5. **Ограничьте ключ (рекомендуется):**
   - Нажмите на созданный ключ
   - В разделе "Application restrictions" выберите "HTTP referrers"
   - Добавьте домены: `*.run.app`
   - В разделе "API restrictions" выберите "Restrict key"
   - Выберите "Places API"

## 🚀 Локальная разработка

### Требования
- Python 3.9+
- Telegram bot token
- Google Maps API key (опционально)

### Установка
1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd maps-to-waze-bot
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Установите переменные окружения:**
```bash
export TELEGRAM_BOT_TOKEN="ваш_токен_бота"
export GOOGLE_MAPS_API_KEY="ваш_ключ_google_maps_api"
```

4. **Запустите бота:**
```bash
python maps_to_waze_bot.py
```

## ☁️ Развертывание в облаке (Google Cloud Run)

### Быстрое развертывание
```bash
# Развернуть с токенами
gcloud run deploy maps-to-waze-bot \
  --source . \
  --port 8081 \
  --allow-unauthenticated \
  --region europe-central2 \
  --set-env-vars TELEGRAM_BOT_TOKEN="ваш_токен_бота",GOOGLE_MAPS_API_KEY="ваш_ключ_google_maps_api"
```

### Безопасное развертывание с Secret Manager
```bash
# Создать секреты
echo -n "ваш_токен_бота" | gcloud secrets create telegram-bot-token --data-file=-
echo -n "ваш_ключ_google_maps_api" | gcloud secrets create google-maps-api-key --data-file=-

# Развернуть с секретами
gcloud run deploy maps-to-waze-bot \
  --source . \
  --port 8081 \
  --allow-unauthenticated \
  --region europe-central2 \
  --set-secrets TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,GOOGLE_MAPS_API_KEY=google-maps-api-key:latest
```

## 🤖 Команды бота

- `/start` - Показать приветственное сообщение и инструкции
- `/help` - Показать справку

## 🏗️ Архитектура

- **maps_to_waze_bot.py** - Основная логика бота с обработкой координат
- **Dockerfile** - Конфигурация контейнера
- **requirements.txt** - Python зависимости

## 📊 Логирование

Бот предоставляет подробное логирование:
- Взаимодействия с пользователями
- Процессы расширения URL
- Извлечение координат
- Результаты конвертации
- Обработка ошибок

## 🔒 Безопасность

- Токены хранятся в переменных окружения
- Рекомендуется использовать Google Secret Manager для продакшн
- API ключи ограничены по доменам и API

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для функции
3. Внесите изменения
4. Тщательно протестируйте
5. Отправьте pull request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.