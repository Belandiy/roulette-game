document.addEventListener("DOMContentLoaded", () => {
  // 1. Инициализация DOM (находим все нужные элементы по их id)
  const spinBtn = document.getElementById("spin-btn");
  const pointsEl = document.getElementById("points");
  const bestEl = document.getElementById("best");
  const statusEl = document.getElementById("status");
  const leaderboardEl = document.getElementById("leaderboard-body");
  const reels = [...document.querySelectorAll(".reel")];

  // 2. Функция для загрузки лидерборда
  async function loadLeaderboard() {
    try {
      const response = await fetch("/api/leaderboard");
      const data = await response.json(); // Ожидаем "голый" массив: [ {nickname: ..., best_score: ...} ]

      leaderboardEl.innerHTML = "";
      // Работаем напрямую с data, так как нет ключа "top"
      data.forEach((row, index) => {
        const tr = document.createElement("tr");
        // Используем ключ best_score, от бэкенда
        tr.innerHTML = `<td>${index + 1}</td><td>${row.nickname}</td><td>${row.best_score}</td>`;
        leaderboardEl.appendChild(tr);
      });
    } catch (error) {
      console.error("Failed to load leaderboard:", error);
    }
  }

  // 3. Обработчик кнопки "Крутить"
  if (spinBtn) {
    spinBtn.addEventListener("click", async () => {
      spinBtn.disabled = true;
      statusEl.textContent = "Крутим...";

      try {
        const response = await fetch("/api/spin", { method: "POST" });
        const data = await response.json(); // Ожидаем {result: [...], score: N, combo: "..."}

        // Обновляем DOM на основе полученных данных
        // Отображаем числа из поля "result"
        reels.forEach((reel, index) => {
          reel.textContent = data.result[index];
        });

        // Обновляем очки за спин из поля "score"
        pointsEl.textContent = data.score;
        statusEl.textContent = `Комбинация: ${data.combo}`;

        // API бэкендера не возвращает поле best_points,
        // невозможно обновить "Ваш лучший результат".

      } catch (error) {
        statusEl.textContent = "Ошибка спина";
        console.error("Spin error:", error);
      } finally {
        spinBtn.disabled = false;
      }
    });
  }

  loadLeaderboard();
});
