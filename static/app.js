document.addEventListener("DOMContentLoaded", () => {
    // === (Спринт 3) ===
    // Бэкенд теперь присылает числа (0-4), мапим их в эмодзи
    const SYMBOLS = ["🍒", "🍋", "⭐", "🔔", "7️⃣"];

    // 1. Инициализация DOM
    const spinBtn = document.getElementById("spin-btn");

    // Элементы игры (используем те же ID, что и в Спринте 2)
    const pointsEl = document.getElementById("result-score");
    const bestEl = document.getElementById("best-points");
    const statusEl = document.getElementById("status");
    const leaderboardEl = document.getElementById("leaderboard-list");

    const comboEl = document.getElementById("result-combo");

    // Элементы для регистрации (Новое в Спринте 3)
    const nicknameForm = document.getElementById("nickname-form");
    const nickInput = document.getElementById("nickname");

    const reels = [...document.querySelectorAll(".reel")];

    // 2. Логика регистрации (Спринт 3)
    if (nicknameForm) {
        nicknameForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nickname = nickInput.value.trim();

            // ПАРСИНГ/ВАЛИДАЦИЯ: Проверяем, что ник нормальный
            // Разрешаем: Латиница, Кириллица, Цифры, _ -
            // Длина: 3-16 символов
            const nickRegex = /^[a-zA-Zа-яА-Я0-9_\-]{3,16}$/;

            if (!nickRegex.test(nickname)) {
                alert("Никнейм должен содержать от 3 до 16 символов: буквы, цифры, _ или -");
                return;
            }

            try {
                const response = await fetch("/api/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ nickname: nickname })
                });

                // Бэкенд возвращает редирект или успех. Перезагружаем страницу, 
                // чтобы сервер увидел сессию и пустил в игру.
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Ошибка регистрации. Возможно, имя занято или недопустимо.");
                }
            } catch (error) {
                console.error("Login error:", error);
            }
        });
    }

    // 3. Функция для загрузки лидерборда
    async function loadLeaderboard() {
        try {
            const response = await fetch("/api/leaderboard");
            if (!response.ok) return;

            const data = await response.json();

            // console.log("Leaderboard data received:", data); 

            leaderboardEl.innerHTML = "";

            if (data.length === 0) {
                leaderboardEl.innerHTML = "<tr><td colspan='2'>Нет данных</td></tr>";
                return;
            }

            data.forEach((row) => {
                const tr = document.createElement("tr");

                const tdNick = document.createElement("td");
                tdNick.textContent = row.nickname;

                const tdScore = document.createElement("td");
                tdScore.textContent = row.best_points;

                tr.appendChild(tdNick);
                tr.appendChild(tdScore);
                leaderboardEl.appendChild(tr);
            });
        } catch (error) {
            console.error("Failed to load leaderboard:", error);
        }
    }

    // 4. Функция анимации барабана (Спринт 3)
    function animateReel(reelElement, finalSymbolIndex, durationSeconds) {
        return new Promise((resolve) => {
            const startTime = performance.now();
            const durationMs = durationSeconds * 1000;

            // Меняем символы каждые 50мс
            const interval = setInterval(() => {
                const randomSymbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
                reelElement.textContent = randomSymbol;

                // Если время вышло, останавливаемся
                if (performance.now() - startTime >= durationMs) {
                    clearInterval(interval);
                    // Ставим финальный символ (превращаем число от бэкенда в картинку)
                    reelElement.textContent = SYMBOLS[finalSymbolIndex];
                    resolve();
                }
            }, 50);
        });
    }

    // 5. Обработчик кнопки "Крутить"
    if (spinBtn) {
        spinBtn.addEventListener("click", async () => {
            spinBtn.disabled = true;
            statusEl.textContent = "Вращение...";
            statusEl.style.color = "#9ad0ff";

            try {
                const response = await fetch("/api/spin", { method: "POST" });

                // Обработка ошибки авторизации (Спринт 3)
                if (response.status === 401) {
                    statusEl.textContent = "Сначала введите никнейм и сохраните!";
                    statusEl.style.color = "red";
                    spinBtn.disabled = false;
                    return;
                }

                const data = await response.json(); // {result: [0,1,0], score: 100, animation: {...}, ...}

                // Запускаем анимацию (Спринт 3)
                // Бэкенд присылает настройки анимации для каждого барабана
                const animations = reels.map((reel, i) => {
                    const duration = data.animation ? data.animation.reels[i].duration : 1.0;
                    const finalIndex = data.animation ? data.animation.reels[i].final : 0;
                    return animateReel(reel, finalIndex, duration);
                });

                // Ждем окончания всех анимаций
                await Promise.all(animations);

                // Обновляем результаты ПОСЛЕ анимации
                // Для надежности ставим финальные символы из result
                reels.forEach((reel, index) => {
                    const symbolIdx = data.result[index];
                    reel.textContent = SYMBOLS[symbolIdx];
                });

                pointsEl.textContent = data.score;
                // Пишем комбинацию в специальное поле
                if (comboEl) comboEl.textContent = data.combo;
                // Статус просто очищаем или пишем "Готово"
                statusEl.textContent = "";

                // Теперь обновляем лучший результат (данные реальные)
                bestEl.textContent = data.best_points;

                // Обновляем таблицу лидеров
                await loadLeaderboard();

            } catch (error) {
                statusEl.textContent = "Ошибка сети";
                console.error("Spin error:", error);
            } finally {
                spinBtn.disabled = false;
            }
        });
    }

    // Первичная загрузка
    loadLeaderboard();
});