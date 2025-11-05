from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'dev_key_sprint_2'  # Временный ключ для сессий

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Заглушка для спина - возвращает фиксированные значения
    """
    data = request.get_json(silent=True) or {}
    nickname = data.get("nickname", "anonymous")
    
    # Заглушка - всегда возвращаем один результат
    result = [7, 7, 7]
    combo = "three_of_kind"
    score = 100

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
    app.run(host="127.0.0.1", port=5000, debug=True)
