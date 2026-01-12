document.addEventListener("DOMContentLoaded", () => {
    const SYMBOLS = ["🍒", "🍋", "⭐", "🔔", "7️⃣"];

    // === 1. Инициализация DOM ===
    const spinBtn = document.getElementById("spin-btn");

    const pointsEl = document.getElementById("result-score");
    const bestEl = document.getElementById("best-points");
    const statusEl = document.getElementById("status");
    const leaderboardEl = document.getElementById("leaderboard-list");
    const comboEl = document.getElementById("result-combo");

    const nicknameForm = document.getElementById("nickname-form");
    const nickInput = document.getElementById("nickname");

    const reels = [...document.querySelectorAll(".reel")];

    // === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (Refactor Sprint 4) ===

    // Управление статусом: сообщение и тип (обычный/ошибка)
    function setStatus(message, isError = false) {
        statusEl.textContent = message;
        if (isError) {
            statusEl.style.color = "#ff4444"; // Красный для ошибок
        } else {
            statusEl.style.color = ""; // Сброс (наследуется из CSS или дефолт)
        }
    }

    // === 2. Логика регистрации ===
    if (nicknameForm) {
        nicknameForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nickname = nickInput.value.trim();

            // Валидация (RegExp из Sprint 4 бэкенда может быть строже, проверяем и тут)
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

                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Ошибка регистрации. Возможно, имя занято или недопустимо.");
                }
            } catch (error) {
                console.error("Login error:", error);
                alert("Нет связи с сервером.");
            }
        });
    }

    // === 3. Функция для загрузки лидерборда ===
    async function loadLeaderboard() {
        try {
            const response = await fetch("/api/leaderboard");
            if (!response.ok) return;

            const data = await response.json();

            leaderboardEl.innerHTML = "";

            if (data.length === 0) {
                leaderboardEl.innerHTML = "<tr><td colspan='2' style='text-align:center; color:#888;'>Пока нет рекордов</td></tr>";
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
            leaderboardEl.innerHTML = "<tr><td colspan='2' style='color:#ff4444;'>Ошибка загрузки</td></tr>";
        }
    }

    // 4. Функция анимации барабана
    function animateReel(reelElement, finalSymbolIndex, durationSeconds) {
        return new Promise((resolve) => {
            const startTime = performance.now();
            const durationMs = durationSeconds * 1000;

            const interval = setInterval(() => {
                const randomSymbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
                reelElement.textContent = randomSymbol;

                if (performance.now() - startTime >= durationMs) {
                    clearInterval(interval);
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
            setStatus("Вращение...", false); // Очистка статуса перед спином

            try {
                const response = await fetch("/api/spin", { method: "POST" });

                // UX: Обработка 401 (Сессия истекла или не вошел)
                if (response.status === 401) {
                    setStatus("Для игры необходимо ввести никнейм и нажать 'Сохранить'", true);
                    spinBtn.disabled = false;
                    return;
                }

                // UX: Обработка других ошибок сервера (500 и т.д.)
                if (!response.ok) {
                    setStatus("Ошибка сервера. Попробуйте позже.", true);
                    spinBtn.disabled = false;
                    return;
                }

                const data = await response.json();

                // Анимация (Бэкенд присылает duration для каждого барабана)
                const animations = reels.map((reel, i) => {
                    const duration = data.animation ? data.animation.reels[i].duration : 1.0;
                    const finalIndex = data.animation ? data.animation.reels[i].final : 0;
                    return animateReel(reel, finalIndex, duration);
                });

                await Promise.all(animations);

                // --- Обновление UI после остановки ---

                // Гарантированная установка финальных символов
                reels.forEach((reel, index) => {
                    const symbolIdx = data.result[index];
                    reel.textContent = SYMBOLS[symbolIdx];
                });

                pointsEl.textContent = data.score;
                if (comboEl) comboEl.textContent = data.combo;

                bestEl.textContent = data.best_points;

                // UX: Обработка Rank Hint (Фича Спринта 4 от Бэкенда)
                if (data.rank_hint) {
                    setStatus(`🎉 Вы в ТОП-10! Позиция: ${data.rank_hint}`, false);
                    statusEl.style.color = "#00ff00"; // Зеленый для успеха
                } else {
                    setStatus(""); // Очищаем, если ничего особенного
                }

                setTimeout(() => {
                    loadLeaderboard();
                }, 500);

            } catch (error) {
                setStatus("Ошибка сети / Интернет недоступен", true);
                console.error("Spin error:", error);
            } finally {
                spinBtn.disabled = false;
            }
        });
    }

    // Первичная загрузка
    loadLeaderboard();
});