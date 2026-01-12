import os
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import json
import db
import scoring

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key-for-development')

# Строгое регулярное выражение для валидации никнейма (спринт 4)
# Разрешаем только: латинские буквы, кириллицу, цифры, подчеркивание и дефис
NICKNAME_PATTERN = re.compile(r'^[a-zA-Zа-яА-Я0-9_-]{3,20}$')

db.init_app(app)

@app.route("/")
def home():
    # Передаем никнейм в шаблон, если пользователь в сессии
    return render_template("index.html", nickname=session.get("nickname"))

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Регистрация нового пользователя или получение существующего по никнейму.
    """
    # Пытаемся получить данные в формате JSON
    data = request.get_json(silent=True)
    
    if data is None:
        # Если это не JSON, пробуем получить из формы
        nickname = request.form.get("nickname", "").strip()
    else:
        nickname = data.get("nickname", "").strip()
    
    # Строгая валидация никнейма (спринт 4)
    if not nickname:
        return jsonify({"error": "Никнейм не может быть пустым"}), 400
    
    # Проверка длины
    if len(nickname) < 3:
        return jsonify({"error": "Никнейм должен содержать минимум 3 символа"}), 400
    if len(nickname) > 20:
        return jsonify({"error": "Никнейм должен содержать максимум 20 символов"}), 400
    
    # Проверка по regexp
    if not NICKNAME_PATTERN.fullmatch(nickname):
        # Находим запрещенные символы для информативного сообщения
        forbidden_chars = []
        for char in nickname:
            if not re.match(r'[a-zA-Zа-яА-Я0-9_-]', char):
                if char not in forbidden_chars:
                    forbidden_chars.append(char)
        
        if forbidden_chars:
            error_msg = f"Никнейм содержит запрещенные символы: {', '.join(forbidden_chars)}. "
            error_msg += "Разрешены только буквы (латинские и русские), цифры, подчеркивание (_) и дефис (-)."
        else:
            error_msg = "Никнейм содержит недопустимые символы. Разрешены только буквы (латинские и русские), цифры, подчеркивание (_) и дефис (-)."
        
        return jsonify({"error": error_msg}), 400
    
    # Проверка на только цифры
    if nickname.isdigit():
        return jsonify({"error": "Никнейм не может состоять только из цифр"}), 400
    
    # Проверка на только знаки препинания
    if all(c in '_-' for c in nickname):
        return jsonify({"error": "Никнейм не может состоять только из знаков препинания"}), 400
    
    database = db.get_db()
    
    # Пытаемся найти существующего пользователя
    user = database.execute(
        "SELECT id FROM users WHERE nickname = ?",  # ИСПРАВЛЕНО: username → nickname
        (nickname,)
    ).fetchone()
    
    if user:
        user_id = user[0]
        message = "Пользователь уже существует"
    else:
        # Создаём нового пользователя
        cursor = database.execute(
            "INSERT INTO users (nickname) VALUES (?)",  # ИСПРАВЛЕНО: username → nickname
            (nickname,)
        )
        database.commit()
        user_id = cursor.lastrowid
        message = "Пользователь успешно зарегистрирован"
    
    # Сохраняем в сессии
    session['user_id'] = user_id
    session['nickname'] = nickname
    
    # Для API-запросов возвращаем JSON
    return jsonify({
        "success": True,
        "message": message,
        "user_id": user_id,
        "nickname": nickname
    }), 200

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Вращение рулетки и сохранение результата.
    Использует scoring.py для генерации результата и подсчета очков.
    """
    # Проверяем наличие пользователя в сессии
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Неавторизован. Сначала зарегистрируйтесь."}), 401
    
    nickname = session.get('nickname', 'anonymous')
    database = db.get_db()

    # Генерация результата через scoring.py (серверная сторона — честно)
    result = scoring.spin_reels(3)
    
    # Вычисление очков через scoring.py
    score = scoring.score(result)
    
    # Определение типа комбинации
    if result[0] == result[1] == result[2]:
        combo = "three_of_kind"
    elif len(set(result)) == 2:
        combo = "pair"
    else:
        combo = "none"

    # Сохраняем результат в БД
    reels_json = json.dumps(result)
    cursor = database.execute(
        "INSERT INTO scores (user_id, points, reels_json) VALUES (?, ?, ?)",
        (user_id, score, reels_json)
    )
    database.commit()

    # Получаем лучший результат пользователя (спринт 4: переименовано в best_points)
    best_points_row = database.execute(
        "SELECT COALESCE(MAX(points), 0) as best FROM scores WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    best_points = best_points_row['best'] if best_points_row else 0

    # Вычисление ранга пользователя (спринт 4)
    total_users_row = database.execute("SELECT COUNT(*) as total FROM users").fetchone()
    total_users = total_users_row['total'] if total_users_row else 0
    
    # Получаем ранг пользователя (сколько пользователей имеют лучший результат)
    if total_users > 0:
        rank_row = database.execute(
            """
            SELECT COUNT(*) + 1 as rank
            FROM (
                SELECT u.id, COALESCE(MAX(s.points), 0) as user_best
                FROM users u
                LEFT JOIN scores s ON u.id = s.user_id
                GROUP BY u.id
                HAVING user_best > ?
            )
            """,
            (best_points,)
        ).fetchone()
        rank = rank_row['rank'] if rank_row else 1
    else:
        rank = 1
    
    # Формируем подсказку ранга (спринт 4)
    if total_users > 0:
        if rank <= 10:
            rank_hint = f"#{rank} (в топ-10!)"
        elif rank <= 50:
            rank_hint = f"#{rank} (в топ-50)"
        elif rank <= 100:
            rank_hint = f"#{rank} (в топ-100)"
        else:
            percentile = min(99, int((rank / total_users) * 100))
            if percentile < 10:
                rank_hint = f"#{rank} (в топ-{percentile+1}%)"
            else:
                rank_hint = f"#{rank} (в топ-{percentile}%)"
    else:
        rank_hint = f"#{rank} (первый игрок!)"

    # Данные для анимации вращения барабанов
    symbol_to_index = {"🍒": 0, "🍋": 1, "⭐": 2, "🔔": 3, "7️⃣": 4}
    animation = {
        "reels": [
            {"final": symbol_to_index.get(result[i], 0), "spins": random.randint(3, 5), "duration": 0.6 + i * 0.2}
            for i in range(3)
        ],
        "total_duration": 1.2
    }

    result_indices = [symbol_to_index.get(sym, 0) for sym in result]

    return jsonify({
        "user_id": user_id,
        "nickname": nickname,
        "result": result_indices,
        "score": score,
        "combo": combo,
        "best_points": best_points,
        "rank_hint": rank_hint,
        "rank": rank,
        "total_users": total_users,
        "animation": animation
    }), 200

@app.route("/api/leaderboard")
def api_leaderboard():
    """
    Получение турнирной таблицы ТОП-10.
    Агрегация: MAX(points) по каждому пользователю.
    """
    database = db.get_db()
    
    leaderboard = database.execute(
        """
        SELECT 
            u.id as user_id,
            u.nickname as nickname, 
            COALESCE(MAX(s.points), 0) as best_points
        FROM users u
        LEFT JOIN scores s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY best_points DESC, MIN(s.created_at) ASC, u.created_at ASC
        LIMIT 10
        """
    ).fetchall()
    
    # Преобразуем в список словарей
    result = [
        {
            "user_id": row['user_id'],
            "nickname": row['nickname'],
            "best_points": row['best_points']
        }
        for row in leaderboard
    ]
    
    return jsonify(result), 200

@app.route("/api/health")
def health_check():
    """Health-check эндпоинт для мониторинга (спринт 4)"""
    try:
        db.get_db().execute("SELECT 1")
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
            "endpoints": {
                "register": "/api/register",
                "spin": "/api/spin", 
                "leaderboard": "/api/leaderboard",
                "health": "/api/health"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.cli.command("init-db")
def init_db_command():
    """CLI команда для инициализации БД (спринт 4) - идемпотентная версия"""
    db.ensure_db()
    print("База данных проверена/инициализирована.")

@app.cli.command("reset-db")
def reset_db_command():
    """CLI команда для полного сброса БД (только для разработки)"""
    confirmation = input("Вы уверены? Это удалит все данные. (y/N): ")
    if confirmation.lower() == 'y':
        db.init_db()
        print("База данных полностью сброшена.")
    else:
        print("Операция отменена.")

@app.errorhandler(400)
def bad_request(error):
    """Обработчик ошибки 400 Bad Request"""
    return jsonify({
        "error": "Некорректный запрос",
        "message": "Проверьте формат и данные запроса"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    """Обработчик ошибки 401 Unauthorized"""
    return jsonify({
        "error": "Неавторизован",
        "message": "Сначала зарегистрируйтесь или войдите в систему"
    }), 401

@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404 Not Found"""
    return jsonify({
        "error": "Ресурс не найден",
        "message": "Запрашиваемый URL не существует"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Обработчик ошибка 405 Method Not Allowed"""
    return jsonify({
        "error": "Метод не разрешен",
        "message": "Используйте правильный HTTP-метод для этого эндпоинта"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500 Internal Server Error"""
    import traceback
    print(f"Внутренняя ошибка сервера: {error}")
    print(traceback.format_exc())
    return jsonify({
        "error": "Внутренняя ошибка сервера",
        "message": "Произошла непредвиденная ошибка. Попробуйте позже."
    }), 500

if __name__ == "__main__":
    with app.app_context():
        # Инициализация БД при старте (идемпотентно)
        db.ensure_db()
    app.run(host="127.0.0.1", port=5000, debug=True)