#!/usr/bin/env python3
"""
Скрипт для тестирования всех типов ссылок Google Maps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from maps_to_waze_bot import extract_coordinates_from_input

def test_all_url_types():
    """Тестирует все типы ссылок Google Maps"""
    
    test_cases = [
        # 1. Короткие ссылки
        ("https://maps.app.goo.gl/7Kbykswh6r89ybX78", "Короткая ссылка"),
        
        # 2. Прямые координаты
        ("40.7128, -74.0060", "Прямые координаты"),
        ("59.286887, 24.648914", "Прямые координаты"),
        ("31.7683, 35.2137", "Прямые координаты"),
        ("-33.8688, 151.2093", "Прямые координаты (отрицательные)"),
        
        # 3. DMS координаты
        ("31°44'49.8\"N 35°01'46.6\"E", "DMS координаты"),
        ("40°42'46\"N 74°00'22\"W", "DMS координаты"),
        ("59°17'12\"N 24°38'56\"E", "DMS координаты"),
        
        # 4. Полные ссылки с координатами
        ("https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z", "Полная ссылка с @"),
        ("https://www.google.com/maps/place/Tallinn,+Estonia/@59.286887,24.648914,15z", "Полная ссылка с @"),
        ("https://www.google.com/maps/place/Jerusalem,+Israel/@31.7683,35.2137,15z", "Полная ссылка с @"),
        
        # 5. Ссылки с параметром @
        ("https://www.google.com/maps/@40.7128,-74.0060,15z", "Ссылка с @"),
        ("https://www.google.com/maps/@59.286887,24.648914,15z", "Ссылка с @"),
        ("https://www.google.com/maps/@31.7683,35.2137,15z", "Ссылка с @"),
        
        # 6. Ссылки с параметром ll
        ("https://maps.google.com/maps?ll=40.7128,-74.0060&z=15", "Ссылка с ll"),
        ("https://maps.google.com/maps?ll=59.286887,24.648914&z=15", "Ссылка с ll"),
        ("https://maps.google.com/maps?ll=31.7683,35.2137&z=15", "Ссылка с ll"),
        
        # 7. Ссылки с параметром q
        ("https://maps.google.com/?q=40.7128,-74.0060", "Ссылка с q"),
        ("https://maps.google.com/?q=59.286887,24.648914", "Ссылка с q"),
        ("https://maps.google.com/?q=31.7683,35.2137", "Ссылка с q"),
        
        # 8. Ссылки с поиском
        ("https://www.google.com/maps/search/New+York+City", "Ссылка с поиском"),
        ("https://www.google.com/maps/search/Tallinn,+Estonia", "Ссылка с поиском"),
        ("https://www.google.com/maps/search/Jerusalem,+Israel", "Ссылка с поиском"),
        
        # 9. Ссылки с !3d!4d
        ("https://www.google.com/maps?q=New+York+City&ll=40.7128,-74.0060&z=15&!3d40.7128!4d-74.0060", "Ссылка с !3d!4d"),
        ("https://www.google.com/maps?q=Tallinn&ll=59.286887,24.648914&z=15&!3d59.286887!4d24.648914", "Ссылка с !3d!4d"),
        
        # 10. Ссылки с consent.google.com
        ("https://consent.google.com/m?continue=https://www.google.com/maps/search/59.286887,%2B24.648914", "Consent ссылка"),
        ("https://consent.google.com/m?continue=https://www.google.com/maps/search/40.7128,-74.0060", "Consent ссылка"),
        
        # 11. Ссылки с направлением
        ("https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851", "Ссылка с направлением"),
        ("https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574", "Ссылка с направлением"),
        
        # 12. Ссылки с улицей
        ("https://www.google.com/maps/place/Times+Square,+New+York,+NY,+USA/@40.7580,-73.9855,17z", "Ссылка с улицей"),
        ("https://www.google.com/maps/place/Old+Town+Square,+Tallinn,+Estonia/@59.436962,24.753574,17z", "Ссылка с улицей"),
        
        # 13. Ссылки с бизнесом
        ("https://www.google.com/maps/place/Starbucks/@40.7128,-74.0060,15z", "Ссылка с бизнесом"),
        ("https://www.google.com/maps/place/McDonald's/@59.286887,24.648914,15z", "Ссылка с бизнесом"),
        
        # 14. Ссылки с просмотром улиц
        ("https://www.google.com/maps/@40.7128,-74.0060,3a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с просмотром улиц"),
        ("https://www.google.com/maps/@59.286887,24.648914,3a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с просмотром улиц"),
        
        # 15. Ссылки с кастомными картами
        ("https://www.google.com/maps/d/viewer?mid=1BQ8w33tQCdYJxiN0n_xHx1qXqXk&ll=40.7128,-74.0060&z=15", "Ссылка с кастомной картой"),
        ("https://www.google.com/maps/d/viewer?mid=1ABC123DEF456&ll=59.286887,24.648914&z=15", "Ссылка с кастомной картой"),
        
        # 16. Ссылки с временными метками
        ("https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m2!3m1!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62", "Ссылка с временными метками"),
        ("https://www.google.com/maps/place/Tallinn,+Estonia/@59.286887,24.648914,15z/data=!4m2!3m1!1s0x4692946a80b5b8c7:0x400f1781360cb60", "Ссылка с временными метками"),
        
        # 17. Ссылки с отзывами
        ("https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m8!3m7!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62!5m2!4m1!1i2!8m2!3d40.7128!4d-74.0060", "Ссылка с отзывами"),
        
        # 18. Ссылки с фотографиями
        ("https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z/data=!4m8!3m7!1s0x89c24fa5d33f083b:0xc80b8f06e177fe62!5m2!4m1!1i2!8m2!3d40.7128!4d-74.0060!6m1!1e1", "Ссылка с фотографиями"),
        
        # 19. Ссылки с велосипедными маршрутами
        ("https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e1", "Ссылка с велосипедным маршрутом"),
        ("https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e1", "Ссылка с велосипедным маршрутом"),
        
        # 20. Ссылки с общественным транспортом
        ("https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e3", "Ссылка с общественным транспортом"),
        ("https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e3", "Ссылка с общественным транспортом"),
        
        # 21. Ссылки с пешеходными маршрутами
        ("https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e2", "Ссылка с пешеходным маршрутом"),
        ("https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e2", "Ссылка с пешеходным маршрутом"),
        
        # 22. Ссылки с маршрутами на автомобиле
        ("https://www.google.com/maps/dir/40.7128,-74.0060/40.7589,-73.9851/data=!4m2!4m1!3e0", "Ссылка с маршрутом на автомобиле"),
        ("https://www.google.com/maps/dir/59.286887,24.648914/59.436962,24.753574/data=!4m2!4m1!3e0", "Ссылка с маршрутом на автомобиле"),
        
        # 23. Ссылки с аэрофотоснимками
        ("https://www.google.com/maps/@40.7128,-74.0060,15a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с аэрофотоснимками"),
        ("https://www.google.com/maps/@59.286887,24.648914,15a,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с аэрофотоснимками"),
        
        # 24. Ссылки с гибридными картами
        ("https://www.google.com/maps/@40.7128,-74.0060,15h,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с гибридными картами"),
        ("https://www.google.com/maps/@59.286887,24.648914,15h,75y,0h,90t/data=!3m6!1e1!3m4!1s!2e0!7i16384!8i8192", "Ссылка с гибридными картами"),
    ]
    
    print("🧪 Тестирование всех типов ссылок Google Maps")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (url, description) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. {description}")
        print(f"    URL: {url}")
        
        try:
            lat, lng = extract_coordinates_from_input(url)
            if lat is not None and lng is not None:
                print(f"    ✅ УСПЕХ: {lat}, {lng}")
                waze_url = f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"
                print(f"    🔗 Waze: {waze_url}")
                success_count += 1
            else:
                print(f"    ❌ НЕУДАЧА: Координаты не найдены")
        except Exception as e:
            print(f"    ❌ ОШИБКА: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 РЕЗУЛЬТАТЫ:")
    print(f"   Успешно: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"   Неудачно: {total_count-success_count}/{total_count} ({(total_count-success_count)/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")

if __name__ == "__main__":
    test_all_url_types() 