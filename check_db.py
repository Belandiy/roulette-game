#!/usr/bin/env python
"""
Скрипт для проверки содержимого БД.
Запуск: python check_db.py
"""

import sqlite3
import json

DATABASE = "database.db"


def check_db():
    """Проверяет содержимое БД и показывает статистику."""
    
    try:
        conn = sqlite3.connect(DATABASE)
        # conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        
        print("="*70)
        print("ПРОВЕРКА БАЗЫ ДАННЫХ")
        print("="*70)
        
        # Проверяем существование таблиц
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('users', 'scores')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'users' not in tables or 'scores' not in tables:
            print("\n✗ БД не инициализирована!")
            print("  Запустите: python init_test_db.py")
            conn.close()
            return
        
        print("\n✓ Таблицы существуют: users, scores\n")
        
        # Проверяем количество пользователей
        cursor = conn.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Пользователей в БД: {user_count}")
        
        # Проверяем количество результатов
        cursor = conn.execute("SELECT COUNT(*) as count FROM scores")
        score_count = cursor.fetchone()[0]
        print(f"📊 Результатов игр: {score_count}\n")
        
        # Выводим информацию о пользователях
        print("="*70)
        print("ПОЛЬЗОВАТЕЛИ И ИХ РЕЗУЛЬТАТЫ")
        print("="*70 + "\n")
        
        cursor = conn.execute("""
            SELECT 
                u.id,
                u.username,
                COUNT(s.id) as total_games,
                COALESCE(MAX(s.points), 0) as best_score,
                COALESCE(MIN(s.created_at), 'Нет игр') as first_game
            FROM users u
            LEFT JOIN scores s ON u.id = s.user_id
            GROUP BY u.id
            ORDER BY best_score DESC, first_game ASC
        """)
        
        print(f"{'#':3} {'Никнейм':25} {'Игр':5} {'Лучше':6} {'Первая игра'}")
        print("-" * 70)
        
        for i, row in enumerate(cursor.fetchall(), 1):
            user_id = row[0]
            username = row[1]
            total_games = row[2]
            best_score = row[3]
            first_game = row[4]
            print(f"{i:<3} {username:25} {total_games:5} {best_score:6} {first_game}")
        
        # Выводим все результаты
        print("\n" + "="*70)
        print("ВСЕ РЕЗУЛЬТАТЫ ИГРОКОВ")
        print("="*70 + "\n")
        
        cursor = conn.execute("""
            SELECT 
                u.username,
                s.id,
                s.points,
                s.reels_json,
                s.created_at
            FROM scores s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
            LIMIT 20
        """)
        
        print(f"{'Никнейм':25} {'ID':3} {'Очки':6} {'Барабаны':20} {'Дата'}")
        print("-" * 70)
        
        for row in cursor.fetchall():
            username = row[0]
            score_id = row[1]
            points = row[2]
            reels = json.loads(row[3])
            created_at = row[4]
            print(f"{username:25} {score_id:<3} {points:6} {str(reels):20} {created_at}")
        
        # Проверяем индексы
        print("\n" + "="*70)
        print("ИНДЕКСЫ")
        print("="*70 + "\n")
        
        cursor = conn.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND tbl_name IN ('users', 'scores')
        """)
        
        for row in cursor.fetchall():
            index_name = row[0]
            index_sql = row[1]
            if index_sql:
                print(f"✓ {index_name}")
                print(f"  {index_sql}\n")
        
        # Проверяем PRAGMA WAL
        print("="*70)
        print("РЕЖИМЫ И ПАРАМЕТРЫ БД")
        print("="*70 + "\n")
        
        cursor = conn.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"✓ Journal Mode: {journal_mode}")
        
        cursor = conn.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        print(f"✓ Foreign Keys: {'включены' if fk_enabled else 'отключены'}")
        
        print("\n" + "="*70)
        print("✓ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*70)
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"\n✗ Ошибка БД: {e}")
        print("  БД не инициализирована.")
        print("  Запустите: python init_test_db.py")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")


if __name__ == "__main__":
    check_db()
