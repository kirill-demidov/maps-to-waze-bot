# -*- coding: utf-8 -*-
"""
Translations for Maps to Waze Bot
Supports: Russian, English, Ukrainian, Hebrew
"""

from typing import Dict, Any

# Language codes
LANGUAGES = {
    'ru': 'Русский',
    'en': 'English', 
    'uk': 'Українська',
    'he': 'עברית'
}

# Translations dictionary
TRANSLATIONS = {
    'ru': {
        'welcome': (
            "Привет! 👋\n\n"
            "Я бот для конвертации ссылок Google Maps в Waze.\n\n"
            "📡 {api_status}\n\n"
            "Отправьте мне:\n"
            "• Ссылку Google Maps (любую)\n"
            "• Координаты в десятичном формате (lat, lng)\n"
            "• Координаты в формате DMS\n\n"
            "Примеры:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'help': (
            "Как использовать бота:\n\n"
            "1. Отправьте ссылку Google Maps или координаты\n"
            "2. Получите ссылку для Waze\n\n"
            "Поддерживаемые форматы:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• https://www.google.com/maps/...\n"
            "• https://goo.gl/maps/...\n"
            "• Десятичные: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "Команды:\n"
            "/start - Начать использование бота\n"
            "/help - Показать это сообщение\n"
            "/menu - Открыть меню\n"
            "/language - Сменить язык"
        ),
        'menu': (
            "🔧 Меню бота\n\n"
            "Выберите действие:"
        ),
        'language_menu': (
            "🌐 Выберите язык:\n\n"
            "Выберите предпочитаемый язык для бота:"
        ),
        'language_changed': "✅ Язык изменен на: {language}",
        'api_available': "✅ Google Maps API доступен",
        'api_unavailable': "❌ Google Maps API недоступен",
        'coordinates_extracted': (
            "✅ Ссылка успешно обработана!\n\n"
            "📍 Координаты: {lat}, {lng}\n\n"
            "🚗 Открыть в Waze:\n{waze_url}"
        ),
        'error_google_maps': (
            "❌ Не удалось извлечь координаты из ссылки Google Maps.\n\n"
            "Это может быть ссылка на место без точных координат.\n\n"
            "Попробуйте:\n"
            "• Открыть ссылку в браузере\n"
            "• Нажать на кнопку 'Поделиться'\n"
            "• Выбрать 'Копировать ссылку'\n"
            "• Отправить новую ссылку\n\n"
            "Или отправьте координаты напрямую:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_short_url': (
            "🔗 Обнаружена короткая ссылка Google Maps\n\n"
            "Для получения координат:\n"
            "1. Откройте ссылку в браузере\n"
            "2. Нажмите 'Поделиться' (Share)\n"
            "3. Выберите 'Копировать ссылку' (Copy link)\n"
            "4. Отправьте новую ссылку\n\n"
            "Или отправьте координаты напрямую:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_general': (
            "❌ Не удалось извлечь координаты из вашего сообщения.\n\n"
            "Пожалуйста, отправьте:\n"
            "• Ссылку Google Maps (включая короткие ссылки)\n"
            "• Координаты в десятичном формате (lat, lng)\n"
            "• Координаты в формате DMS\n\n"
            "Примеры:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'processing': "⏳ Обрабатываю ссылку...",
        'error_processing': (
            "❌ Произошла ошибка при обработке вашего сообщения.\n"
            "Пожалуйста, попробуйте еще раз или отправьте /help для справки."
        ),
        'buttons': {
            'menu': '🔧 Меню',
            'help': '❓ Помощь',
            'language': '🌐 Язык',
            'analytics': '📊 Аналитика',
            'back': '⬅️ Назад',
            'ru': '🇷🇺 Русский',
            'en': '🇺🇸 English',
            'uk': '🇺🇦 Українська',
            'he': '🇮🇱 עברית'
        }
    },
    
    'en': {
        'welcome': (
            "Hello! 👋\n\n"
            "I'm a bot for converting Google Maps links to Waze.\n\n"
            "📡 {api_status}\n\n"
            "Send me:\n"
            "• Google Maps link (any)\n"
            "• Coordinates in decimal format (lat, lng)\n"
            "• Coordinates in DMS format\n\n"
            "Examples:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'help': (
            "How to use the bot:\n\n"
            "1. Send a Google Maps link or coordinates\n"
            "2. Get a Waze link\n\n"
            "Supported formats:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• https://www.google.com/maps/...\n"
            "• https://goo.gl/maps/...\n"
            "• Decimal: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "Commands:\n"
            "/start - Start using the bot\n"
            "/help - Show this message\n"
            "/menu - Open menu\n"
            "/language - Change language"
        ),
        'menu': (
            "🔧 Bot Menu\n\n"
            "Choose an action:"
        ),
        'language_menu': (
            "🌐 Choose language:\n\n"
            "Select your preferred language for the bot:"
        ),
        'language_changed': "✅ Language changed to: {language}",
        'api_available': "✅ Google Maps API available",
        'api_unavailable': "❌ Google Maps API unavailable",
        'coordinates_extracted': (
            "✅ Link successfully processed!\n\n"
            "📍 Coordinates: {lat}, {lng}\n\n"
            "🚗 Open in Waze:\n{waze_url}"
        ),
        'error_google_maps': (
            "❌ Failed to extract coordinates from Google Maps link.\n\n"
            "This might be a place link without exact coordinates.\n\n"
            "Try:\n"
            "• Open the link in browser\n"
            "• Click 'Share' button\n"
            "• Select 'Copy link'\n"
            "• Send the new link\n\n"
            "Or send coordinates directly:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_short_url': (
            "🔗 Google Maps short link detected\n\n"
            "To get coordinates:\n"
            "1. Open the link in browser\n"
            "2. Click 'Share' button\n"
            "3. Select 'Copy link'\n"
            "4. Send the new link\n\n"
            "Or send coordinates directly:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_general': (
            "❌ Failed to extract coordinates from your message.\n\n"
            "Please send:\n"
            "• Google Maps link (including short links)\n"
            "• Coordinates in decimal format (lat, lng)\n"
            "• Coordinates in DMS format\n\n"
            "Examples:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'processing': "⏳ Processing link...",
        'error_processing': (
            "❌ An error occurred while processing your message.\n"
            "Please try again or send /help for assistance."
        ),
        'buttons': {
            'menu': '🔧 Menu',
            'help': '❓ Help',
            'language': '🌐 Language',
            'analytics': '📊 Analytics',
            'back': '⬅️ Back',
            'ru': '🇷🇺 Русский',
            'en': '🇺🇸 English',
            'uk': '🇺🇦 Українська',
            'he': '🇮🇱 עברית'
        }
    },
    
    'uk': {
        'welcome': (
            "Привіт! 👋\n\n"
            "Я бот для конвертації посилань Google Maps у Waze.\n\n"
            "📡 {api_status}\n\n"
            "Надішліть мені:\n"
            "• Посилання Google Maps (будь-яке)\n"
            "• Координати в десятковому форматі (lat, lng)\n"
            "• Координати в форматі DMS\n\n"
            "Приклади:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'help': (
            "Як використовувати бота:\n\n"
            "1. Надішліть посилання Google Maps або координати\n"
            "2. Отримайте посилання для Waze\n\n"
            "Підтримувані формати:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• https://www.google.com/maps/...\n"
            "• https://goo.gl/maps/...\n"
            "• Десяткові: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "Команди:\n"
            "/start - Почати використання бота\n"
            "/help - Показати це повідомлення\n"
            "/menu - Відкрити меню\n"
            "/language - Змінити мову"
        ),
        'menu': (
            "🔧 Меню бота\n\n"
            "Виберіть дію:"
        ),
        'language_menu': (
            "🌐 Виберіть мову:\n\n"
            "Виберіть бажану мову для бота:"
        ),
        'language_changed': "✅ Мову змінено на: {language}",
        'api_available': "✅ Google Maps API доступний",
        'api_unavailable': "❌ Google Maps API недоступний",
        'coordinates_extracted': (
            "✅ Посилання успішно оброблено!\n\n"
            "📍 Координати: {lat}, {lng}\n\n"
            "🚗 Відкрити в Waze:\n{waze_url}"
        ),
        'error_google_maps': (
            "❌ Не вдалося витягти координати з посилання Google Maps.\n\n"
            "Це може бути посилання на місце без точних координат.\n\n"
            "Спробуйте:\n"
            "• Відкрити посилання в браузері\n"
            "• Натиснути кнопку 'Поділитися'\n"
            "• Вибрати 'Копіювати посилання'\n"
            "• Надіслати нове посилання\n\n"
            "Або надішліть координати безпосередньо:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_general': (
            "❌ Не вдалося витягти координати з вашого повідомлення.\n\n"
            "Будь ласка, надішліть:\n"
            "• Посилання Google Maps (включаючи короткі посилання)\n"
            "• Координати в десятковому форматі (lat, lng)\n"
            "• Координати в форматі DMS\n\n"
            "Приклади:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'processing': "⏳ Обробляю посилання...",
        'error_processing': (
            "❌ Сталася помилка при обробці вашого повідомлення.\n"
            "Будь ласка, спробуйте ще раз або надішліть /help для довідки."
        ),
        'buttons': {
            'menu': '🔧 Меню',
            'help': '❓ Допомога',
            'language': '🌐 Мова',
            'analytics': '📊 Аналітика',
            'back': '⬅️ Назад',
            'ru': '🇷🇺 Русский',
            'en': '🇺🇸 English',
            'uk': '🇺🇦 Українська',
            'he': '🇮🇱 עברית'
        }
    },
    
    'he': {
        'welcome': (
            "שלום! 👋\n\n"
            "אני בוט להמרת קישורי Google Maps ל-Waze.\n\n"
            "📡 {api_status}\n\n"
            "שלח לי:\n"
            "• קישור Google Maps (כלשהו)\n"
            "• קואורדינטות בפורמט עשרוני (lat, lng)\n"
            "• קואורדינטות בפורמט DMS\n\n"
            "דוגמאות:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'help': (
            "איך להשתמש בבוט:\n\n"
            "1. שלח קישור Google Maps או קואורדינטות\n"
            "2. קבל קישור ל-Waze\n\n"
            "פורמטים נתמכים:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• https://www.google.com/maps/...\n"
            "• https://goo.gl/maps/...\n"
            "• עשרוני: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "פקודות:\n"
            "/start - התחל להשתמש בבוט\n"
            "/help - הצג הודעה זו\n"
            "/menu - פתח תפריט\n"
            "/language - שנה שפה"
        ),
        'menu': (
            "🔧 תפריט הבוט\n\n"
            "בחר פעולה:"
        ),
        'language_menu': (
            "🌐 בחר שפה:\n\n"
            "בחר את השפה המועדפת שלך לבוט:"
        ),
        'language_changed': "✅ השפה שונתה ל: {language}",
        'api_available': "✅ Google Maps API זמין",
        'api_unavailable': "❌ Google Maps API לא זמין",
        'coordinates_extracted': (
            "✅ הקישור עובד בהצלחה!\n\n"
            "📍 קואורדינטות: {lat}, {lng}\n\n"
            "🚗 פתח ב-Waze:\n{waze_url}"
        ),
        'error_google_maps': (
            "❌ לא הצלחתי לחלץ קואורדינטות מקישור Google Maps.\n\n"
            "זה יכול להיות קישור למקום ללא קואורדינטות מדויקות.\n\n"
            "נסה:\n"
            "• פתח את הקישור בדפדפן\n"
            "• לחץ על כפתור 'שתף'\n"
            "• בחר 'העתק קישור'\n"
            "• שלח את הקישור החדש\n\n"
            "או שלח קואורדינטות ישירות:\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'error_general': (
            "❌ לא הצלחתי לחלץ קואורדינטות מההודעה שלך.\n\n"
            "אנא שלח:\n"
            "• קישור Google Maps (כולל קישורים קצרים)\n"
            "• קואורדינטות בפורמט עשרוני (lat, lng)\n"
            "• קואורדינטות בפורמט DMS\n\n"
            "דוגמאות:\n"
            "• https://maps.app.goo.gl/...\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'processing': "⏳ מעבד קישור...",
        'error_processing': (
            "❌ אירעה שגיאה בעיבוד ההודעה שלך.\n"
            "אנא נסה שוב או שלח /help לעזרה."
        ),
        'buttons': {
            'menu': '🔧 תפריט',
            'help': '❓ עזרה',
            'language': '🌐 שפה',
            'analytics': '📊 אנליטיקה',
            'back': '⬅️ חזור',
            'ru': '🇷🇺 Русский',
            'en': '🇺🇸 English',
            'uk': '🇺🇦 Українська',
            'he': '🇮🇱 עברית'
        }
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """Get translated text for given key and language"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    if key not in TRANSLATIONS[lang]:
        # Fallback to English
        if key in TRANSLATIONS['en']:
            return TRANSLATIONS['en'][key].format(**kwargs)
        return f"Missing translation: {key}"
    
    return TRANSLATIONS[lang][key].format(**kwargs)

def get_button_text(key: str, lang: str = 'en') -> str:
    """Get button text for given key and language"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    buttons = TRANSLATIONS[lang].get('buttons', {})
    if key not in buttons:
        # Fallback to English
        english_buttons = TRANSLATIONS['en'].get('buttons', {})
        return english_buttons.get(key, key)
    
    return buttons[key]

def get_language_name(lang_code: str) -> str:
    """Get language name for language code"""
    return LANGUAGES.get(lang_code, lang_code)

def is_valid_language(lang_code: str) -> bool:
    """Check if language code is valid"""
    return lang_code in LANGUAGES 