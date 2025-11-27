document.addEventListener("DOMContentLoaded", () => {
  // 1. Инициализация DOM: находим элементы по их НОВЫМ id из верстки
  const spinBtn = document.getElementById("spin-btn");
  
  // ИЗМЕНЕНО: id поля очков теперь 'result-score'
  const pointsEl = document.getElementById("result-score");
  
  // ИЗМЕНЕНО: id поля лучшего результата теперь 'best-points'
  const bestEl = document.getElementById("best-points");
  
  const statusEl = document.getElementById("status");
  
  // ИЗМЕНЕНО: id тела таблицы теперь 'leaderboard-list'
  const leaderboardEl = document.getElementById("leaderboard-list");
  
  const reels = [...document.querySelectorAll(".reel")];

// 2. Функция для загрузки лидерборда
  async function loadLeaderboard() {
    try {
      // На этапе Спринта 2 сервер возвращает статические данные заглушку.
      // Реальное сохранение и чтение планировалось реализовать на бэкенде в Спринте 3.
      const response = await fetch("/api/leaderboard");
      const data = await response.json(); 
      
      console.log("Leaderboard data received:", data); // Лог для демонстрации работы

      // Работаем с новым ID 'leaderboard-list'
      leaderboardEl.innerHTML = "";
      
      // Проверка на случай, если данных нет
      if (data.length === 0) {
        leaderboardEl.innerHTML = "<tr><td colspan='2'>Нет данных</td></tr>";
        return;
      }

      data.forEach((row, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.nickname}</td><td>${row.best_score}</td>`;
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
        reels.forEach((reel, index) => {
          reel.textContent = data.result[index];
        });

        // Обновляем очки за спин в элементе с id 'result-score'
        pointsEl.textContent = data.score;
        statusEl.textContent = `Комбинация: ${data.combo}`;

        // После спина обновляем таблицу лидеров, так как очки могли измениться
        await loadLeaderboard(); 

        // Поле 'best-points' пока не обновляем, так как API бэкендера
        // не возвращает соответствующее значение.

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
