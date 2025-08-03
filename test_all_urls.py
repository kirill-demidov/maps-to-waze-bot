#!/usr/bin/env python3
"""
Скрипт для тестирования всех форматов Google Maps ссылок
"""

import requests
import json
import time
from typing import List, Dict, Tuple

# Конфигурация
BOT_TOKEN = "7980465326:AAGazpPHHvTB8ArTGRovbA49NgHqqFNErbw"
ADMIN_CHAT_ID = 110319269
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Тестовые ссылки разных форматов
TEST_URLS = [
    # 1. Короткие ссылки (maps.app.goo.gl)
    "https://maps.app.goo.gl/7Kbykswh6r89ybX78",
    "https://maps.app.goo.gl/hRMzL2YBR5MNWpe38",
    
    # 2. Прямые координаты
    "40.7128, -74.0060",
    "59.286887, 24.648914",
    "31.7683, 35.2137",
    "-33.8688, 151.2093",
    
    # 3. Координаты в формате DMS
    "31°44'49.8\"N 35°01'46.6\"E",
    "40°42'46\"N 74°00'22\"W",
    "59°17'12\"N 24°38'56\"E",
    
    # 4. Полные ссылки Google Maps с координатами
    "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z",
    "https://www.google.com/maps/place/Tallinn,+Estonia/@59.286887,24.648914,15z",
    "https://www.google.com/maps/place/Jerusalem,+Israel/@31.7683,35.2137,15z",
    
    # 5. Ссылки с параметром @
    "https://www.google.com/maps/@40.7128,-74.0060,15z",
    "https://www.google.com/maps/@59.286887,24.648914,15z",
    "https://www.google.com/maps/@31.7683,35.2137,15z",
    
    # 6. Ссылки с параметром ll
    "https://maps.google.com/maps?ll=40.7128,-74.0060&z=15",
    "https://maps.google.com/maps?ll=59.286887,24.648914&z=15",
    "https://maps.google.com/maps?ll=31.7683,35.2137&z=15",
    
    # 7. Ссылки с параметром q
    "https://maps.google.com/?q=40.7128,-74.0060",
    "https://maps.google.com/?q=59.286887,24.648914",
    "https://maps.google.com/?q=31.7683,35.2137",
    
    # 8. Ссылки с поиском места
    "https://www.google.com/maps/search/New+York+City",
    "https://www.google.com/maps/search/Tallinn,+Estonia",
    "https://www.google.com/maps/search/Jerusalem,+Israel",
    
    # 9. Ссылки с параметром !3d!4d
    "https://www.google.com/maps?q=New+York+City&ll=40.7128,-74.0060&z=15&!3d40.7128!4d-74.0060",
    "https://www.google.com/maps?q=Tallinn&ll=59.286887,24.648914&z=15&!3d59.286887!4d24.648914",
    
    # 10. Ссылки с consent.google.com
    "https://consent.google.com/m?continue=https://www.google.com/maps/search/59.286887,%2B24.648914",
    "https://consent.google.com/m?continue=https://www.google.com/maps/search/40.7128,-74.0060",
    
    # 11. Ссылки с place ID
    "https://www.google.com/maps/place/ChIJN1t_tDeuEmsRUsoyG83frY4",
    "https://www.google.com/maps/place/ChIJ7cv00DwsDogRAMD5aNs6AGQ",
    
    # 12. Ссылки с направлением
    "https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851",
    "https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574",
    
    # 13. Ссылки с улицей
    "https://www.google.com/maps/place/Times+Square,+New+York,+NY,+USA/@40.7580,-73.9855,17z",
    "https://www.google.com/maps/place/Old+Town+Square,+Tallinn,+Estonia/@59.436962,24.753574,17z",
    
    # 14. Ссылки с бизнесом
    "https://www.google.com/maps/place/Starbucks/@40.7128,-74.0060,15z",
    "https://www.google.com/maps/place/McDonald's/@59.286887,24.648914,15z",
    
    # 15. Ссылки с просмотром улиц
    "https://www.google.com/maps/@40.7128,-74.0060,3a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
    "https://www.google.com/maps/@59.286887,24.648914,3a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
    
    # 16. Ссылки с кастомными картами
    "https://www.google.com/maps/d/viewer?mid=1BQ8w33tQCdYJxiN0n_xHx1qXqXk&ll=40.7128,-74.0060&z=15",
    "https://www.google.com/maps/d/viewer?mid=1ABC123DEF456&ll=59.286887,24.648914&z=15",
    
    # 17. Ссылки с временными метками
    "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m2!3m1!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62",
    "https://www.google.com/maps/place/Tallinn,+Estonia/@59.286887,24.648914,15z/data=!4m2!3m1!1s0x4692946a80b5b8c7:0x400f1781360cb60",
    
    # 18. Ссылки с отзывами
    "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m8!3m7!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62!5m2!4m1!1i2!8m2!3d40.7128!4d-74.0060",
    
    # 19. Ссылки с фотографиями
    "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m8!3m7!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62!5m2!4m1!1i2!8m2!3d40.7128!4d-74.0060!6m1!1e1",
    
    # 20. Ссылки с велосипедными маршрутами
    "https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e1",
    "https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e1",
    
    # 21. Ссылки с общественным транспортом
    "https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e3",
    "https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e3",
    
    # 22. Ссылки с пешеходными маршрутами
    "https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e2",
    "https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e2",
    
    # 23. Ссылки с маршрутами на автомобиле
    "https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e0",
    "https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e0",
    
    # 24. Ссылки с аэрофотоснимками
    "https://www.google.com/maps/@40.7128,-74.0060,15a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
    "https://www.google.com/maps/@59.286887,24.648914,15a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
    
    # 25. Ссылки с гибридными картами
    "https://www.google.com/maps/@40.7128,-74.0060,15h,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
    "https://www.google.com/maps/@59.286887,24.648914,15h,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192",
]

def send_message_to_bot(text: str) -> Dict:
    """Отправляет сообщение боту и возвращает ответ"""
    url = f"{BOT_API_URL}/sendMessage"
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_bot_updates() -> List[Dict]:
    """Получает последние обновления от бота"""
    url = f"{BOT_API_URL}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        return response.json().get("result", [])
    except Exception as e:
        return []

def test_url(url: str, index: int) -> Dict:
    """Тестирует одну ссылку"""
    print(f"\n🧪 Тест {index + 1}/{len(TEST_URLS)}: {url[:50]}...")
    
    # Отправляем сообщение боту
    send_result = send_message_to_bot(url)
    if "error" in send_result:
        return {
            "url": url,
            "status": "error",
            "error": send_result["error"]
        }
    
    # Ждем ответа бота
    time.sleep(5)
    
    # Получаем обновления
    updates = get_bot_updates()
    
    # Ищем ответ бота
    bot_response = None
    for update in updates:
        if "message" in update and update["message"]["from"]["is_bot"]:
            message_text = update["message"]["text"]
            if "waze.com" in message_text or "❌" in message_text:
                bot_response = message_text
                break
    
    if bot_response:
        if "waze.com" in bot_response:
            return {
                "url": url,
                "status": "success",
                "response": bot_response
            }
        else:
            return {
                "url": url,
                "status": "failed",
                "response": bot_response
            }
    else:
        return {
            "url": url,
            "status": "no_response",
            "response": "Бот не ответил"
        }

def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем тестирование всех форматов Google Maps ссылок...")
    print(f"📊 Всего ссылок для тестирования: {len(TEST_URLS)}")
    
    results = []
    
    for i, url in enumerate(TEST_URLS):
        result = test_url(url, i)
        results.append(result)
        
        # Выводим результат
        if result["status"] == "success":
            print(f"✅ Успешно: {result['response'][:50]}...")
        elif result["status"] == "failed":
            print(f"❌ Ошибка: {result['response'][:50]}...")
        else:
            print(f"⚠️ {result['status']}: {result['response']}")
        
        # Пауза между тестами
        time.sleep(2)
    
    # Статистика
    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "failed"])
    no_response = len([r for r in results if r["status"] == "no_response"])
    errors = len([r for r in results if r["status"] == "error"])
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Успешно: {successful}")
    print(f"❌ Ошибки: {failed}")
    print(f"⚠️ Нет ответа: {no_response}")
    print(f"🚫 Ошибки API: {errors}")
    print(f"📈 Успешность: {successful/len(TEST_URLS)*100:.1f}%")
    
    # Сохраняем результаты
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в test_results.json")
    
    # Показываем неудачные тесты
    if failed > 0 or no_response > 0:
        print(f"\n🔍 НЕУДАЧНЫЕ ТЕСТЫ:")
        for result in results:
            if result["status"] in ["failed", "no_response"]:
                print(f"❌ {result['url']}")
                print(f"   Ответ: {result['response']}")
                print()

if __name__ == "__main__":
    main() 