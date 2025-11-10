import sqlite3
from flask import g

DATABASE = "database.db"


def get_db():
    """Получает соединение с базой данных для текущего контекста приложения.
    Использует Flask's g объект для хранения соединения между запросами."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row # Возвращает результаты как словари
    return g.db


def init_db():
    """Инициализирует базу данных, создавая таблицы из schema.sql.
    Выполняется при первом запуске приложения."""
    db = sqlite3.connect(DATABASE)
    with open("schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.close()

def ensure_db():
    """Проверяет существование таблиц в базе данных.
    Если таблицы не существуют, вызывает init_db() для их создания.
    Это обеспечивает корректную работу приложения при первом запуске."""    
    try:
        # Пытаемся выполнить запрос к таблице users
        db = get_db()
        db.execute("SELECT 1 FROM users LIMIT 1")
    except sqlite3.OperationalError:
        init_db()