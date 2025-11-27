import sqlite3
from flask import g

DATABASE = "database.db"


def get_db():
    """Получает соединение с базой данных для текущего контекста приложения.
    Использует Flask's g объект для хранения соединения между запросами."""
    if "db" not in g:
        # Открываем соединение с проверкой типов и включаем возвращение строк как dict-like
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row  # Возвращает результаты как словари
        # Включаем enforcement внешних ключей для каждого соединения
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def init_db():
    """Инициализирует базу данных, создавая таблицы из schema.sql.
    Выполняется при первом запуске приложения."""
    # Создаем или перезаписываем файл базы данных схемой
    conn = sqlite3.connect(DATABASE)
    try:
        # Включаем WAL для лучшей конкурентности и включаем FK
        conn.execute('PRAGMA journal_mode = WAL')
        conn.execute('PRAGMA foreign_keys = ON')
        with open("schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    finally:
        conn.close()

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


def close_db(e=None):
    """Закрывает соединение с базой данных для текущего контекста приложения."""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    """Регистрация хуков приложения Flask для корректной работы с БД."""
    # Закрываем соединение после запроса
    app.teardown_appcontext(close_db)