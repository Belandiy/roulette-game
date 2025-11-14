#!/usr/bin/env python
"""
Скрипт для тестирования API рулетки.
Запуск: python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_api():
    """Тестирует все API endpoints."""
    
    print("="*60)
    print("ТЕСТИРОВАНИЕ API РУЛЕТКИ")
    print("="*60)
    
    # Тест 1: GET /
    print("\n1️⃣  Проверка главной страницы (GET /)...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✓ Главная страница загружена успешно (статус 200)")
        else:
            print(f"   ✗ Ошибка: статус {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Ошибка: не удалось подключиться к серверу")
        print("   ⚠️  Убедитесь, что приложение запущено: python app.py")
        return
    
    # Тест 2: GET /rules
    print("\n2️⃣  Проверка страницы правил (GET /rules)...")
    try:
        response = requests.get(f"{BASE_URL}/rules")
        if response.status_code == 200:
            print("   ✓ Страница правил загружена успешно (статус 200)")
        else:
            print(f"   ✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 3: POST /api/spin (без никнейма)
    print("\n3️⃣  Тест spin без никнейма (POST /api/spin)...")
    try:
        response = requests.post(f"{BASE_URL}/api/spin", json={})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Ответ получен (статус 200)")
            print(f"     - Никнейм: {data.get('nickname')}")
            print(f"     - Результат: {data.get('result')}")
            print(f"     - Очки: {data.get('score')}")
            print(f"     - Комбо: {data.get('combo')}")
        else:
            print(f"   ✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 4: POST /api/spin (с никнеймом)
    print("\n4️⃣  Тест spin с никнеймом (POST /api/spin)...")
    try:
        response = requests.post(f"{BASE_URL}/api/spin", json={"nickname": "TestPlayer"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Ответ получен (статус 200)")
            print(f"     - Никнейм: {data.get('nickname')}")
            print(f"     - Результат: {data.get('result')}")
            print(f"     - Очки: {data.get('score')}")
            print(f"     - Комбо: {data.get('combo')}")
        else:
            print(f"   ✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 5: GET /api/leaderboard
    print("\n5️⃣  Получение лидерборда (GET /api/leaderboard)...")
    try:
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Лидерборд получен (статус 200)")
            print(f"   Всего игроков: {len(data)}")
            if data:
                print("\n   ТОП-5 ИГРОКОВ:")
                for i, player in enumerate(data[:5], 1):
                    username = player.get('username', 'N/A')
                    best_score = player.get('best_score', 0)
                    first_played = player.get('first_played', 'N/A')
                    print(f"     {i}. {username:20} | Лучше: {best_score:3} | Первая игра: {first_played}")
            else:
                print("   ℹ️  Лидерборд пуст (нужны игроки в БД)")
        else:
            print(f"   ✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)


if __name__ == "__main__":
    print("⏳ Убедитесь, что приложение запущено на http://127.0.0.1:5000")
    print("   Запустить: python app.py\n")
    time.sleep(1)
    test_api()
