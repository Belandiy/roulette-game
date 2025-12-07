from flask import Flask, render_template, request, jsonify, session
import random
import json
import db

app = Flask(__name__)
app.secret_key = 'dev_key_sprint_2'  # Временный ключ для сессий

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Крутить рулетку и сохранить результат в БД.
    
    Request JSON:
      { "nickname": "Player1" }
    
    Response JSON:
      { "nickname":"Player1", "result":[1,2,3], "score":0, "combo":"none" }
    """
    data = request.get_json(silent=True) or {}
    nickname = data.get("nickname", "anonymous")

    # Генерация результата (серверная сторона — честно)
    result = [random.randint(0, 9) for _ in range(3)]

    # Простая логика очков без ставки
    if result[0] == result[1] == result[2]:
        combo = "three_of_kind"
        score = 100
    elif len(set(result)) == 2:
        combo = "pair"
        score = 20
    else:
        combo = "none"
        score = 0

    # Сохраняем результат в БД
    database = db.get_db()
    
    # Получаем или создаём пользователя
    cursor = database.execute(
        "SELECT id FROM users WHERE nickname = ?",
        (nickname,)
    )
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
    else:
        # Создаём нового пользователя
        database.execute(
            "INSERT INTO users (nickname) VALUES (?)",
            (nickname,)
        )
        database.commit()
        user_id = database.lastrowid
    
    # Сохраняем результат игры
    import json
    database.execute(
        "INSERT INTO scores (user_id, points, reels_json) VALUES (?, ?, ?)",
        (user_id, score, json.dumps(result))
    )
    database.commit()

    return jsonify({
        "nickname": nickname,
        "result": result,
        "score": score,
        "combo": combo
    }), 200

@app.route("/api/leaderboard")
def api_leaderboard():
    """
    Получить турнирную таблицу ТОП-10 игроков.
    Сортировка: лучший результат DESC, время первой игры ASC.
    
    Returns:
        JSON список игроков с полями:
        - nickname: имя игрока
        - best_points: лучший результат
        - first_played: дата первой игры
    """
    # Получаем топ-10 игроков из БД с правильной сортировкой
    leaderboard = db.get_top_players(limit=10)
    
    return jsonify(leaderboard), 200

if __name__ == "__main__":
    with app.app_context(): # Инициализация БД пр старте
        db.ensure_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
