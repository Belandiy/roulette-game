from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    abort,
)
import random
import json

import db

app = Flask(__name__)
app.secret_key = "dev_key_sprint_2"  # временный ключ для сессий

db.init_app(app)


def spin_logic():
    """
    Простая игровая логика:
    - 3 одинаковых      -> 100 очков
    - пара (2 одинаковых)-> 20 очков
    - иначе             -> 0
    """
    result = [random.randint(0, 9) for _ in range(3)]

    if result[0] == result[1] == result[2]:
        combo = "three_of_kind"
        points = 100
    elif len(set(result)) == 2:
        combo = "pair"
        points = 20
    else:
        combo = "none"
        points = 0

    return result, points, combo


@app.route("/")
def index():
    """Отображает главную страницу."""
    return render_template("index.html")


@app.route("/rules")
def rules():
    return render_template("rules.html")


@app.route("/api/spin", methods=["POST"])
def api_spin():
    """
    Полная реализация POST /api/spin для спринта 3.

    - Основной сценарий по ТЗ:
      user_id берём из сессии, крутим рулетку, пишем результат в scores.

    - Доп. сценарий для текущего фронтенда:
      если в сессии нет user_id, но в JSON-теле есть "nickname",
      считаем это «первым входом»:
        * создаём/находим пользователя по username
        * кладём user_id в сессию
        * дальше работаем как обычно.
      Если нет ни user_id в сессии, ни nickname в теле запроса -> 401.
    """
    conn = db.get_db()

    # JSON от фронтенда (MVP: { "nickname": "Player1" })
    data = request.get_json(silent=True) or {}
    body_nickname = (data.get("nickname") or "").strip() or None

    user_id = session.get("user_id")
    session_nickname = session.get("nickname")

    # Если пользователь ещё не зарегистрирован в сессии,
    # но фронтенд прислал nickname — регистрируем/логиним его.
    if user_id is None and body_nickname is not None:
        nickname = body_nickname

        cur = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (nickname,),
        )
        row = cur.fetchone()

        if row is None:
            cur = conn.execute(
                "INSERT INTO users (username) VALUES (?)",
                (nickname,),
            )
            conn.commit()
            user_id = cur.lastrowid
        else:
            user_id = row["id"]

        session["user_id"] = user_id
        session["nickname"] = nickname
        session_nickname = nickname

    # Если после всех попыток user_id всё ещё нет — неавторизован
    if user_id is None:
        abort(401)

    # Игровая логика
    result, points, combo = spin_logic()

    # Сохраняем результат в scores (points + барабаны)
    conn.execute(
        "INSERT INTO scores (user_id, points, reels_json) "
        "VALUES (?, ?, ?)",
        (user_id, points, json.dumps(result)),
    )
    conn.commit()

    response_nickname = session_nickname or body_nickname or "anonymous"

    return jsonify(
        {
            "nickname": response_nickname,
            "result": result,
            "score": points,
            "combo": combo,
        }
    ), 200


@app.route("/api/leaderboard", methods=["GET"])
def api_leaderboard():
    """
    Возвращает ТОП-10 игроков.
    Агрегация: MAX(points) по каждому пользователю.
    """
    conn = db.get_db()
    rows = conn.execute(
        """
        SELECT
            u.username AS nickname,
            MAX(s.points) AS best_score
        FROM users u
        JOIN scores s ON s.user_id = u.id
        GROUP BY u.id, u.username
        ORDER BY best_score DESC
        LIMIT 10
        """
    ).fetchall()

    leaderboard = [
        {"nickname": row["nickname"], "best_score": row["best_score"]}
        for row in rows
    ]

    return jsonify(leaderboard), 200


@app.errorhandler(401)
def handle_unauthorized(error):
    # Удобный JSON-ответ для фронтенда
    return jsonify({"error": "unauthorized"}), 401


if __name__ == "__main__":
    with app.app_context():
        db.ensure_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
