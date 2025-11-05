from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route("/")
def home():
    """Главная страница приложения.
    Возвращает HTML шаблон с игровым интерфейсом."""
    return render_template("index.html")

@app.route("/rules")
def rules():
    """Страница с правилами игры.
    Возвращает HTML шаблон с описанием правил."""
    return render_template("rules.html")

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """API endpoint для выполнения вращения в игре.
    
    Принимает JSON с ником пользователя:
      { "nickname": "Player1" }
    
    Возвращает JSON с результатом вращения:
      { 
        "nickname": "Player1", 
        "result": [1,2,3], 
        "score": 0, 
        "combo": "none" 
      }
    
    Логика расчета очков:
      - Три одинаковых числа: 100 очков
      - Два одинаковых числа: 20 очков
      - Все разные: 0 очков"""
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
