-- Создаем таблицу пользователей
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- Уникальный идентификатор
    nickname TEXT UNIQUE NOT NULL,                 -- Никнейм пользователя (уникальное)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата создания записи
);

-- Создаем таблицу результатов игр
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- Уникальный идентификатор
    user_id INTEGER NOT NULL,                      -- Ссылка на пользователя
    points INTEGER NOT NULL,                       -- Количество очков
    reels_json TEXT NOT NULL DEFAULT '[]',         -- JSON-представление барабанов
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,-- Дата создания записи
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для ускорения выборок
CREATE INDEX IF NOT EXISTS idx_scores_user ON scores(user_id);
CREATE INDEX IF NOT EXISTS idx_scores_points ON scores(points DESC);
