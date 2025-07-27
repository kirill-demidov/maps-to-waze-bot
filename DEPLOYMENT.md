# 🚀 Инструкции по развертыванию

## Локальный запуск

1. **Установите зависимости:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Установите токен бота:**
```bash
export TELEGRAM_BOT_TOKEN='ваш_токен_бота'
```

3. **Запустите бота:**
```bash
python maps_to_waze_bot.py
```

## Развертывание на Google Cloud Run

1. **Установите Google Cloud CLI**

2. **Войдите в аккаунт:**
```bash
gcloud auth login
```

3. **Установите переменные окружения:**
```bash
gcloud run services update maps-to-waze-bot \
  --set-env-vars TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

4. **Разверните приложение:**
```bash
gcloud run deploy maps-to-waze-bot --source .
```

## Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

## Тестирование

Бот поддерживает следующие форматы:
- ✅ Ссылки Google Maps с координатами
- ✅ Прямые координаты (40.7128, -74.0060)
- ✅ DMS координаты (31°44'49.8"N 35°01'46.6"E)
- ❌ Короткие ссылки на места без координат

## Порт

Бот работает на порту 8081 (как указано в памяти проекта). 