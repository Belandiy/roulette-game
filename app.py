from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import json
import db
import scoring

app = Flask(__name__)
app.secret_key = 'dev_key_sprint_2'  # Временный ключ для сессий

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html", nickname=session.get("nickname"))
    return render_template("index.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Регистрация нового пользователя или получение существующего по никнейму.
    Request JSON:
      { "nickname": "Player1" }
    Response: редирект на главную страницу после успешной регистрации
    """
    data = request.get_json(silent=True) or {}
    nickname = data.get("nickname", "").strip()
    
    if not nickname or len(nickname) < 1 or len(nickname) > 50:
        return jsonify({"error": "Nickname must be between 1 and 50 characters"}), 400
    
    database = db.get_db()
    
    # Пытаемся найти существующего пользователя
    user = database.execute(
        "SELECT id FROM users WHERE username = ?",
        (nickname,)
    ).fetchone()
    
    if user:
        user_id = user[0]
    else:
        # Создаём нового пользователя
        cursor = database.execute(
            "INSERT INTO users (username) VALUES (?)",
            (nickname,)
        )
        database.commit()
        user_id = cursor.lastrowid
    
    # Сохраняем в сессию
    session['user_id'] = user_id
    session['nickname'] = nickname
    
    # Редирект после успешной регистрации
    return redirect(url_for('home'))

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Вращение рулетки и сохранение результата.
    Использует scoring.py для генерации результата и подсчета очков.
    Request JSON:
      { "nickname": "Player1" }  # без поля bet
    Response JSON:
      { 
        "user_id": 1,
        "nickname":"Player1",
        "result":["🍒","🍋","⭐"],  # символы из scoring.py
        "score":0,
        "combo":"none",
        "best_score": 100,
        "animation": {
          "reels": [
            {"final": 0, "spins": 3, "duration": 0.6},
            {"final": 1, "spins": 4, "duration": 0.8},
            {"final": 2, "spins": 5, "duration": 1.0}
          ],
          "total_duration": 1.2
        }
      }
    """
    # Проверяем наличие пользователя в сессии
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized. Register first."}), 401
    
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

    # Получаем лучший результат пользователя
    best_score_row = database.execute(
        "SELECT MAX(points) as best FROM scores WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    best_score = best_score_row['best'] if best_score_row and best_score_row['best'] else 0

    # Данные для анимации вращения барабанов
    # Используем индексы символов для анимации (для совместимости с фронтендом)
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
        "best_score": best_score,
        "animation": animation
    }), 200

@app.route("/api/leaderboard")
def api_leaderboard():
    """
    Получение турнирной таблицы ТОП-10.
    Агрегация: MAX(points) по каждому пользователю.
    Response JSON:
      [
        {"user_id": 1, "nickname": "Player1", "best_score": 100},
        {"user_id": 2, "nickname": "Player2", "best_score": 50},
        ...
      ]
    """
    database = db.get_db()
    
    leaderboard = database.execute(
        """
        SELECT 
            u.id as user_id,
            u.username as nickname,
            MAX(s.points) as best_score
        FROM users u
        LEFT JOIN scores s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY best_score DESC, u.created_at ASC
        LIMIT 10
        """
    ).fetchall()
    
    # Преобразуем в список словарей
    result = [
        {
            "user_id": row['user_id'],
            "nickname": row['nickname'],
            "best_score": row['best_score'] if row['best_score'] else 0
        }
        for row in leaderboard
    ]
    
    return jsonify(result), 200

if __name__ == "__main__":
    with app.app_context(): # Инициализация БД пр старте
        db.ensure_db()
    app.run(host="127.0.0.1", port=5000, debug=True)

@app.errorhandler(401)
def unauthorized(error):
    """Обработчик ошибки 401 Unauthorized"""
    return jsonify({"error": "Unauthorized"}), 401