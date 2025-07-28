#!/usr/bin/env python3
"""
Создает простую иконку для бота с логотипом Waze
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_icon():
    """Создает простую иконку с логотипом Waze"""
    
    size = 512
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    # Цвета Waze
    waze_blue = (0, 123, 255)
    waze_yellow = (255, 193, 7)
    waze_green = (40, 167, 69)
    
    # Фон - градиент от синего к белому
    for y in range(size):
        ratio = y / size
        r = int(waze_blue[0] * (1 - ratio) + 255 * ratio)
        g = int(waze_blue[1] * (1 - ratio) + 255 * ratio)
        b = int(waze_blue[2] * (1 - ratio) + 255 * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    # Основной круг
    center = (size // 2, size // 2)
    radius = size // 3
    
    # Внешний круг
    draw.ellipse([
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius
    ], fill=waze_yellow, outline=waze_blue, width=6)
    
    # Внутренний круг
    inner_radius = radius - 30
    draw.ellipse([
        center[0] - inner_radius,
        center[1] - inner_radius,
        center[0] + inner_radius,
        center[1] + inner_radius
    ], fill=waze_blue)
    
    # Символ навигации - стрелка
    arrow_size = inner_radius - 20
    
    # Рисуем стрелку
    points = [
        (center[0], center[1] - arrow_size),  # Верх
        (center[0] - arrow_size//2, center[1] + arrow_size//2),  # Левый низ
        (center[0] + arrow_size//4, center[1] + arrow_size//4),  # Правый низ
        (center[0], center[1] - arrow_size//4),  # Острие
    ]
    
    draw.polygon(points, fill=waze_yellow)
    
    # Точка в центре
    dot_radius = 10
    draw.ellipse([
        center[0] - dot_radius,
        center[1] - dot_radius,
        center[0] + dot_radius,
        center[1] + dot_radius
    ], fill=waze_green)
    
    # Буква "W" в углу
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    draw.text((size - 100, 30), "W", fill=waze_green, font=font)
    
    # Сохраняем
    icon.save("waze_bot_icon.png", "PNG")
    print("✅ Иконка Waze создана: waze_bot_icon.png")
    print("📏 Размер: 512x512 пикселей")
    print("🎨 Цвета: Waze Blue, Yellow, Green")
    
    return "waze_bot_icon.png"

if __name__ == "__main__":
    create_simple_icon() 