import sqlite3
from flask import g
import click
from flask.cli import with_appcontext

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


def get_top_players(limit=10):
    """Получить топ игроков по лучшему результату для лидерборда.
    
    Args:
        limit: максимальное количество игроков (по умолчанию 10)
    
    Returns:
        Список словарей с полями: nickname, best_score, first_played
    """
    db = get_db()
    query = """
    SELECT 
        u.username,
        MAX(s.points) as best_score,
        MIN(s.created_at) as first_played
    FROM users u
    LEFT JOIN scores s ON u.id = s.user_id
    GROUP BY u.id
    ORDER BY best_score DESC, first_played ASC
    LIMIT ?
    """
    rows = db.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]


def init_app(app):
    """Регистрация хуков приложения Flask для корректной работы с БД.
    Регистрирует teardown для закрытия соединений и CLI команду init-db."""
    # Закрываем соединение после запроса
    app.teardown_appcontext(close_db)

    @app.cli.command('init-db')
    @with_appcontext
    def init_db_command():
        """Инициализировать базу данных по schema.sql"""
        init_db()
        click.echo('Initialized the database.')