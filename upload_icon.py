#!/usr/bin/env python3
"""
Скрипт для загрузки иконки бота через Telegram Bot API
"""

import requests
import os

def upload_bot_icon():
    """Загружает иконку для бота"""
    
    bot_token = "***REMOVED***"
    icon_file = "bot_icon.png"
    
    if not os.path.exists(icon_file):
        print(f"❌ Файл {icon_file} не найден!")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/setProfilePhoto"
    
    with open(icon_file, 'rb') as photo:
        files = {'photo': photo}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("✅ Иконка успешно загружена!")
            return True
        else:
            print(f"❌ Ошибка: {result.get('description', 'Неизвестная ошибка')}")
            return False
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        return False

if __name__ == "__main__":
    upload_bot_icon() 