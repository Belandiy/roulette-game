from scoring import spin_reels, score, get_symbol_displa
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

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

    # Реальная логика вращения
    reels_result = spin_reels()
    points_earned = score(reels_result)
    
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
        
    # Конвертируем символы в emoji для фронтенда
    reels_display = [get_symbol_display(symbol) for symbol in reels_result]
    
    return jsonify({
        "nickname": nickname,
        "result": result,
        "score": score,
        "combo": combo,
        'reels': reels_display,
        'points': points_earned,
        'best_points': 0,  # TODO: Реализовать логику лучшего результата
        'message': 'Вы выиграли очки!' if points_earned > 0 else 'Попробуйте еще раз!'
    })

 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
