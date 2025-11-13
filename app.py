from flask import Flask, render_template, request, jsonify, session
import random
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
    Request JSON:
      { "nickname": "Player1" }  # без поля bet
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

    return jsonify({
        "nickname": nickname,
        "result": result,
        "score": score,
        "combo": combo
    }), 200

@app.route("/api/leaderboard")
def api_leaderboard():
    """
    Заглушка для турнирной таблицы
    """
    # Возвращаем фиктивные данные
    leaderboard = [
        {"nickname": "Player1", "best_score": 100},
        {"nickname": "Player2", "best_score": 50},
        {"nickname": "Player3", "best_score": 20}
    ]
    
    return jsonify(leaderboard), 200

if __name__ == "__main__":
    with app.app_context(): # Инициализация БД пр старте
        db.ensure_db()
    app.run(host="127.0.0.1", port=5000, debug=True)