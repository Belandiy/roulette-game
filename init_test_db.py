#!/usr/bin/env python
"""
Скрипт инициализации и заполнения БД тестовыми данными для проверки работы.
Запуск: python init_test_db.py
"""

import sqlite3
import json
from datetime import datetime, timedelta

DATABASE = "database.db"


def init_and_populate_db():
    """Инициализирует БД и заполняет её тестовыми данными."""
    
    # Инициализируем схему
    conn = sqlite3.connect(DATABASE)
    try:
        # Включаем WAL и FK
        conn.execute('PRAGMA journal_mode = WAL')
        conn.execute('PRAGMA foreign_keys = ON')
        
        # Читаем и выполняем schema.sql
        with open("schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        print("✓ Схема БД инициализирована")
        
        # Добавляем тестовых пользователей и результаты
        conn.row_factory = sqlite3.Row
        
        # Вставляем тестовых пользователей
        users = [
            ("Player1",),
            ("Player2",),
            ("Player3",),
            ("Champion",),
            ("NewbieGamer",),
        ]
        
        conn.executemany("INSERT INTO users (username) VALUES (?)", users)
        print(f"✓ Добавлено {len(users)} пользователей")
        
        # Получаем ID пользователей
        cursor = conn.execute("SELECT id, username FROM users ORDER BY id")
        user_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Добавляем тестовые результаты игр
        now = datetime.now()
        scores_data = [
            # Player1: несколько игр с разными результатами
            (user_map["Player1"], 100, json.dumps([7, 7, 7]), now - timedelta(hours=5)),
            (user_map["Player1"], 20, json.dumps([5, 5, 3]), now - timedelta(hours=4)),
            (user_map["Player1"], 0, json.dumps([1, 2, 3]), now - timedelta(hours=3)),
            (user_map["Player1"], 100, json.dumps([3, 3, 3]), now - timedelta(hours=2)),
            
            # Player2: высокие результаты
            (user_map["Player2"], 500, json.dumps([7, 7, 7]), now - timedelta(hours=6)),
            (user_map["Player2"], 20, json.dumps([9, 9, 1]), now - timedelta(hours=5)),
            (user_map["Player2"], 100, json.dumps([4, 4, 4]), now - timedelta(hours=1)),
            
            # Player3: низкие результаты
            (user_map["Player3"], 0, json.dumps([1, 2, 3]), now - timedelta(hours=7)),
            (user_map["Player3"], 20, json.dumps([6, 6, 1]), now - timedelta(hours=4)),
            
            # Champion: лучший игрок
            (user_map["Champion"], 500, json.dumps([7, 7, 7]), now - timedelta(hours=10)),
            (user_map["Champion"], 100, json.dumps([5, 5, 5]), now - timedelta(hours=8)),
            (user_map["Champion"], 20, json.dumps([8, 8, 2]), now - timedelta(hours=6)),
            
            # NewbieGamer: только начинает
            (user_map["NewbieGamer"], 0, json.dumps([2, 3, 4]), now - timedelta(hours=1)),
        ]
        
        conn.executemany(
            """
            INSERT INTO scores (user_id, points, reels_json, created_at) 
            VALUES (?, ?, ?, ?)
            """,
            scores_data
        )
        print(f"✓ Добавлено {len(scores_data)} результатов игр")
        
        conn.commit()
        
        # Показываем информацию о БД
        print("\n" + "="*50)
        print("СОДЕРЖИМОЕ БАЗЫ ДАННЫХ")
        print("="*50 + "\n")
        
        # Выводим пользователей и их лучшие результаты
        cursor = conn.execute("""
            SELECT 
                u.username,
                MAX(s.points) as best_score,
                COUNT(s.id) as total_games,
                MIN(s.created_at) as first_game
            FROM users u
            LEFT JOIN scores s ON u.id = s.user_id
            GROUP BY u.id
            ORDER BY best_score DESC, first_game ASC
        """)
        
        print("ТОП-10 ИГРОКОВ (ЛИДЕРБОРД):\n")
        for i, row in enumerate(cursor.fetchall(), 1):
            username = row[0]
            best_score = row[1] or 0
            total_games = row[2] or 0
            first_game = row[3] or "Нет игр"
            print(f"{i}. {username:20} | Лучше: {best_score:3} | Игр: {total_games} | Первая: {first_game}")
        
        print("\n" + "="*50)
        print("ВСЕ РЕЗУЛЬТАТЫ ИГРОКОВ:\n")
        
        cursor = conn.execute("""
            SELECT u.username, s.points, s.reels_json, s.created_at
            FROM scores s
            JOIN users u ON s.user_id = u.id
            ORDER BY u.username, s.created_at DESC
        """)
        
        for row in cursor.fetchall():
            username = row[0]
            points = row[1]
            reels = json.loads(row[2])
            created = row[3]
            print(f"{username:20} | {points:3} очков | Барабаны: {reels} | {created}")
        
        print("\n" + "="*50)
        print("✓ БД успешно инициализирована и заполнена тестовыми данными!")
        print("="*50)
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_and_populate_db()
