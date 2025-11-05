import sqlite3
from flask import g

DATABASE = "database.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(DATABASE)
    with open("schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.close()
