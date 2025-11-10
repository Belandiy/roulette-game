-- Удаляем таблицу users если она существует (для очистки при пересоздании)
DROP TABLE IF EXISTS users;

-- Создаем таблицу пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- Уникальный идентификатор
    username TEXT UNIQUE NOT NULL,                 -- Имя пользователя (уникальное)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата создания записи
);

-- Удаляем таблицу scores если она существует
DROP TABLE IF EXISTS scores;

-- Создаем таблицу результатов игр
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- Уникальный идентификатор
    user_id INTEGER NOT NULL,                      -- Ссылка на пользователя
    points INTEGER NOT NULL,                       -- Количество очков
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата создания записи
);
