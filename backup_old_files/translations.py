"""Multi-language support for the Maps to Waze bot"""

# Language translations
TRANSLATIONS = {
    'en': {
        'welcome': (
            "Hello! 👋\n\n"
            "I'm a bot for converting Google Maps links to Waze.\n\n"
            "Send me:\n"
            "• Google Maps link\n"
            "• Decimal coordinates (40.7128, -74.0060)\n"
            "• DMS coordinates (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "Language: /lang"
        ),
        'help': (
            "How to use:\n\n"
            "📝 Send me any of these formats:\n"
            "• https://maps.google.com/...\n"
            "• https://maps.app.goo.gl/...\n"
            "• Decimal: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "I'll convert them to Waze navigation links!\n\n"
            "🌐 Languages: /lang"
        ),
        'invalid_input': (
            "Please send:\n"
            "• Google Maps link\n"
            "• Coordinates (40.7128, -74.0060)\n"
            "• DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "Examples:\n"
            "• https://maps.app.goo.gl/abc123\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'converted': "✅ Converted!",
        'coordinates': "📍 Coordinates",
        'open_waze': "🚗 Open in Waze:",
        'language_select': (
            "🌐 Select your language:\n\n"
            "🇺🇸 English\n"
            "🇷🇺 Русский\n"
            "🇮🇱 עברית"
        ),
        'language_changed': "✅ Language changed to English",
        'expanding_url': "🔗 Expanding URL",
        'found_coordinates': "📍 Found coordinates",
        'converted_for_user': "✅ Converted for"
    },
    'ru': {
        'welcome': (
            "Привет! 👋\n\n"
            "Я бот для конвертации ссылок Google Maps в Waze.\n\n"
            "Отправьте мне:\n"
            "• Ссылку Google Maps\n"
            "• Десятичные координаты (40.7128, -74.0060)\n"
            "• Координаты DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "Язык: /lang"
        ),
        'help': (
            "Как использовать:\n\n"
            "📝 Отправьте любой из этих форматов:\n"
            "• https://maps.google.com/...\n"
            "• https://maps.app.goo.gl/...\n"
            "• Десятичные: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "Я конвертирую их в ссылки навигации Waze!\n\n"
            "🌐 Языки: /lang"
        ),
        'invalid_input': (
            "Пожалуйста, отправьте:\n"
            "• Ссылку Google Maps\n"
            "• Координаты (40.7128, -74.0060)\n"
            "• DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "Примеры:\n"
            "• https://maps.app.goo.gl/abc123\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'converted': "✅ Конвертировано!",
        'coordinates': "📍 Координаты",
        'open_waze': "🚗 Открыть в Waze:",
        'language_select': (
            "🌐 Выберите язык:\n\n"
            "🇺🇸 English\n"
            "🇷🇺 Русский\n"
            "🇮🇱 עברית"
        ),
        'language_changed': "✅ Язык изменен на Русский",
        'expanding_url': "🔗 Разворачиваю ссылку",
        'found_coordinates': "📍 Найдены координаты",
        'converted_for_user': "✅ Конвертировано для"
    },
    'he': {
        'welcome': (
            "שלום! 👋\n\n"
            "אני בוט להמרת קישורי Google Maps ל-Waze.\n\n"
            "שלח לי:\n"
            "• קישור Google Maps\n"
            "• קואורדינטות עשרוניות (40.7128, -74.0060)\n"
            "• קואורדינטות DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "שפה: /lang"
        ),
        'help': (
            "איך להשתמש:\n\n"
            "📝 שלח לי כל אחד מהפורמטים הבאים:\n"
            "• https://maps.google.com/...\n"
            "• https://maps.app.goo.gl/...\n"
            "• עשרוני: 40.7128, -74.0060\n"
            "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "אני אמיר אותם לקישורי ניווט Waze!\n\n"
            "🌐 שפות: /lang"
        ),
        'invalid_input': (
            "אנא שלח:\n"
            "• קישור Google Maps\n"
            "• קואורדינטות (40.7128, -74.0060)\n"
            "• DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "דוגמאות:\n"
            "• https://maps.app.goo.gl/abc123\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        ),
        'converted': "✅ הומר!",
        'coordinates': "📍 קואורדינטות",
        'open_waze': "🚗 פתח ב-Waze:",
        'language_select': (
            "🌐 בחר שפה:\n\n"
            "🇺🇸 English\n"
            "🇷🇺 Русский\n"
            "🇮🇱 עברית"
        ),
        'language_changed': "✅ השפה שונתה לעברית",
        'expanding_url': "🔗 מרחיב קישור",
        'found_coordinates': "📍 נמצאו קואורדינטות",
        'converted_for_user': "✅ הומר עבור"
    }
}

# User language storage (in production, use database)
user_languages = {}

def get_user_language(user_id):
    """Get user's preferred language, default to English"""
    return user_languages.get(user_id, 'en')

def set_user_language(user_id, language):
    """Set user's preferred language"""
    if language in TRANSLATIONS:
        user_languages[user_id] = language
        return True
    return False

def get_text(user_id, key):
    """Get translated text for user"""
    lang = get_user_language(user_id)
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))

def detect_language_from_text(text):
    """Simple language detection based on common words"""
    if any(word in text.lower() for word in ['привет', 'русский', 'координаты']):
        return 'ru'
    elif any(char in text for char in 'אבגדהוזחטיכלמנסעפצקרשת'):
        return 'he'
    return 'en'