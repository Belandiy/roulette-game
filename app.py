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
def api_spin_stub(): 
    """
    ЗАГЛУШКА для /api/spin.
    Старый код возвращал {"result": [1,2,3], "score": 100, "combo": "..."}.
    Мы меняем его, чтобы он возвращал {"reels": ["🍒",...], "points": 10, "best_points": 120},
    потому что именно эти поля будет ожидать наш JavaScript-код.
    """
    # Вся старая логика с random и if/else больше не нужна,
    # так как мы возвращаем фиксированный ответ для удобства разработки.
    return jsonify({
        "reels": ["🍒", "🍒", "🍋"],  # Поле "reels" с символами
        "points": 10,               # Поле "points" вместо "score"
        "best_points": 120          # Добавляем поле "best_points"
    })

@app.route("/api/leaderboard")
def api_leaderboard_stub():
    """
    ЗАГЛУШКА для турнирной таблицы.
    Старый код возвращал просто список: [{"nickname": ..., "best_score": ...}].
    Финальный должен возвращать объект: {"top": [...]}.
    Также меняем "best_score" на "best_points".
    """
    # Данные для таблицы лидеров
    top_data = [
        {"nickname": "Terminator", "best_points": 999},
        {"nickname": "Player1", "best_points": 750},
        {"nickname": "Winner", "best_points": 500},
        {"nickname": "Lucky", "best_points": 240},
        {"nickname": "User123", "best_points": 100},
    ]
    
    return jsonify({"top": top_data})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
