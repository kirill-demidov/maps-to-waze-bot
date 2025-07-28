#!/usr/bin/env python3
"""
Скрипт для создания иконки бота
Генерирует квадратное изображение с символами навигации
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_bot_icon():
    """Создает иконку для бота"""
    
    # Размер иконки (рекомендуется 512x512)
    size = 512
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    # Цвета
    primary_color = (0, 123, 255)  # Синий
    secondary_color = (255, 193, 7)  # Желтый
    accent_color = (40, 167, 69)  # Зеленый
    
    # Фон - градиент
    for y in range(size):
        alpha = int(255 * (1 - y / size))
        color = (primary_color[0], primary_color[1], primary_color[2], alpha)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Основной круг
    circle_center = (size // 2, size // 2)
    circle_radius = size // 3
    draw.ellipse([
        circle_center[0] - circle_radius,
        circle_center[1] - circle_radius,
        circle_center[0] + circle_radius,
        circle_center[1] + circle_radius
    ], fill=secondary_color, outline=primary_color, width=8)
    
    # Символ навигации (компас)
    inner_radius = circle_radius - 40
    draw.ellipse([
        circle_center[0] - inner_radius,
        circle_center[1] - inner_radius,
        circle_center[0] + inner_radius,
        circle_center[1] + inner_radius
    ], fill=primary_color, outline=secondary_color, width=4)
    
    # Стрелки компаса
    arrow_length = inner_radius - 20
    # Север
    draw.line([
        (circle_center[0], circle_center[1] - arrow_length),
        (circle_center[0], circle_center[1] + arrow_length)
    ], fill=secondary_color, width=6)
    # Восток
    draw.line([
        (circle_center[0] - arrow_length, circle_center[1]),
        (circle_center[0] + arrow_length, circle_center[1])
    ], fill=secondary_color, width=6)
    
    # Точка в центре
    dot_radius = 8
    draw.ellipse([
        circle_center[0] - dot_radius,
        circle_center[1] - dot_radius,
        circle_center[0] + dot_radius,
        circle_center[1] + dot_radius
    ], fill=accent_color)
    
    # Текст "W" в углу
    try:
        # Попробуем использовать системный шрифт
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
    except:
        # Fallback на стандартный шрифт
        font = ImageFont.load_default()
    
    draw.text((size - 80, 20), "W", fill=accent_color, font=font)
    
    # Сохраняем иконку
    icon.save("bot_icon.png", "PNG")
    print("✅ Иконка создана: bot_icon.png")
    print("📏 Размер: 512x512 пикселей")
    print("🎨 Цвета: синий, желтый, зеленый")
    
    return "bot_icon.png"

if __name__ == "__main__":
    create_bot_icon() 