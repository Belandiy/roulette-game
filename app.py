from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random

# (СПРИНТ 3)
# Реальная логика БД и подсчета очков находится в PR бэкенд-разработчика.
# Здесь только имитируем ответы API, чтобы проверить работу JS.
# При слиянии реального бэкенда этот файл не нужен.

app = Flask(__name__)
app.secret_key = 'frontend_testing_key'


# db.init_app(app) 

@app.route("/")
def home():
    # Важно: передаем nickname, чтобы проверить скрытие формы в HTML
    return render_template("index.html", nickname=session.get("nickname"))

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Имитация регистрации.
    Вместо записи в БД просто сохраняем в сессию и делаем редирект.
    """
    data = request.get_json(silent=True) or {}
    nickname = data.get("nickname", "Player")
    
    # Имитируем успешный вход
    session['user_id'] = 999 
    session['nickname'] = nickname
    
    # Бэкендер сделал редирект, мы повторяем это поведение
    return redirect(url_for('home'))

@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Имитация спина с анимацией.
    Возвращаем структуру данных, которую ожидает новый app.js.
    """
    # Проверка авторизации (чтобы протестировать ошибку 401 на фронте)
    if not session.get('user_id'):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Генерируем индексы символов (0-4), как это делает реальный бэкенд
    result_indices = [random.randint(0, 4) for _ in range(3)]
    
    # Фейковая анимация для проверки JS
    animation = {
        "reels": [
            {"final": result_indices[0], "spins": 3, "duration": 1.0},
            {"final": result_indices[1], "spins": 4, "duration": 1.4},
            {"final": result_indices[2], "spins": 5, "duration": 1.8}
        ],
        "total_duration": 1.8
    }

    return jsonify({
        "nickname": session.get("nickname"),
        "result": result_indices, # JS ждет индексы
        "score": random.choice([0, 10, 50, 100]), # Случайные очки
        "combo": "test_combo",
        "best_score": 999, # Фейковый рекорд для проверки UI
        "animation": animation # Данные для анимации
    }), 200

@app.route("/api/leaderboard")
def api_leaderboard():
    """
    Имитация данных лидерборда с правильными полями (best_score)
    """
    return jsonify([
        {"nickname": "Leader1", "best_score": 5000},
        {"nickname": "Leader2", "best_score": 3000},
        {"nickname": "Leader3", "best_score": 1500}
    ])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
