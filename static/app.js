document.addEventListener("DOMContentLoaded", () => {
  // 1. Инициализация DOM: находим все HTML-элементы, с которыми будем работать.
  const spinBtn = document.getElementById("spin-btn");
  const pointsEl = document.getElementById("points");
  const bestEl = document.getElementById("best");
  const statusEl = document.getElementById("status");
  const leaderboardEl = document.getElementById("leaderboard-body");
  const reels = [...document.querySelectorAll(".reel")]; // Находим барабаны для будущего

  // 2. Функция для загрузки и отображения таблицы лидеров
  async function loadLeaderboard() {
    try {
      const response = await fetch("/api/leaderboard");
      if (!response.ok) {
        // Если сервер ответил ошибкой, просто выходим
        console.error("Failed to load leaderboard");
        return;
      }
      const data = await response.json();

      leaderboardEl.innerHTML = ""; // Очищаем старую таблицу перед отрисовкой новой
      data.top.forEach((row, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${index + 1}</td><td>${row.nickname}</td><td>${row.best_points}</td>`;
        leaderboardEl.appendChild(tr);
      });
    } catch (error) {
      // В случае сетевой ошибки, выводим ее в консоль
      console.error("Network error while loading leaderboard:", error);
    }
  }

  // 3. Обработчик клика на кнопку "Крутить"
  if (spinBtn) {
    spinBtn.addEventListener("click", async () => {
      spinBtn.disabled = true; // Отключаем кнопку, чтобы избежать повторных нажатий
      statusEl.textContent = "Крутим...";

      try {
        const response = await fetch("/api/spin", { method: "POST" });
        if (!response.ok) {
          statusEl.textContent = "Ошибка спина";
          return;
        }
        
        const data = await response.json();

        // Обновляем текстовые поля. Анимации нет, как и требуется в задаче.
        // Просто показываем результат, полученный от сервера.
        reels.forEach((reel, index) => {
          reel.textContent = data.reels[index];
        });
        pointsEl.textContent = data.points;
        bestEl.textContent = data.best_points;
        statusEl.textContent = "Готово!";
        
      } catch (error) {
        statusEl.textContent = "Сетевая ошибка";
        console.error("Network error during spin:", error);
      } finally {
        // Блок finally выполнится всегда: и после успеха, и после ошибки.
        spinBtn.disabled = false; // Включаем кнопку обратно
      }
    });
  }

  // 4. Первоначальная загрузка таблицы лидеров при открытии страницы
  loadLeaderboard();
});
