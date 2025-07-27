# 🔑 Настройка Google Maps API

## Получение API ключа

1. **Перейдите в Google Cloud Console:**
   https://console.cloud.google.com/

2. **Выберите проект:** playground-332710

3. **Включите Google Maps API:**
   - Перейдите в "APIs & Services" > "Library"
   - Найдите "Places API"
   - Нажмите "Enable"

4. **Создайте API ключ:**
   - Перейдите в "APIs & Services" > "Credentials"
   - Нажмите "Create Credentials" > "API Key"
   - Скопируйте созданный ключ

5. **Ограничьте ключ (рекомендуется):**
   - Нажмите на созданный ключ
   - В разделе "Application restrictions" выберите "HTTP referrers"
   - Добавьте домены: `*.run.app`
   - В разделе "API restrictions" выберите "Restrict key"
   - Выберите "Places API"

## Установка ключа в Cloud Run

```bash
gcloud run services update maps-to-waze-bot \
  --set-env-vars GOOGLE_MAPS_API_KEY=ваш_ключ_здесь \
  --region europe-central2
```

## Проверка работы

После установки ключа бот сможет обрабатывать любые ссылки Google Maps, включая:
- Ссылки на места без координат
- Короткие ссылки maps.app.goo.gl
- Ссылки на бизнесы и достопримечательности

## Стоимость

Google Maps API имеет бесплатный лимит:
- 1000 запросов в день для Places API
- Дополнительные запросы: $0.017 за 1000 запросов

Для большинства ботов этого достаточно. 