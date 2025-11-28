document.addEventListener("DOMContentLoaded", () => {
  const spinBtn = document.getElementById("spin-btn");
  const pointsEl = document.getElementById("result-score");
  const bestEl = document.getElementById("best-points");
  const statusEl = document.getElementById("status");
  const leaderboardEl = document.getElementById("leaderboard-list");
  const reels = [...document.querySelectorAll(".reel")];

  async function loadLeaderboard() {
    try {
      const response = await fetch("/api/leaderboard");
      const data = await response.json();
      leaderboardEl.innerHTML = "";
      if (data.length === 0) {
        leaderboardEl.innerHTML = "<tr><td colspan='2'>Нет данных</td></tr>";
        return;
      }
      data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.nickname}</td><td>${row.best_score}</td>`;
        leaderboardEl.appendChild(tr);
      });
    } catch (e) {
      console.error("Failed to load leaderboard:", e);
    }
  }

  if (spinBtn) {
    spinBtn.addEventListener("click", async () => {
      spinBtn.disabled = true;
      statusEl.textContent = "Крутим...";
      try {
        const nickInput = document.getElementById('nickname');
        const nickname = nickInput ? nickInput.value.trim() : null;
        const options = { method: "POST" };
        if (nickname) {
          options.headers = { 'Content-Type': 'application/json' };
          options.body = JSON.stringify({ nickname });
        }
        const response = await fetch("/api/spin", options);
        const data = await response.json();
        reels.forEach((reel, index) => {
          reel.textContent = data.result[index];
        });
        pointsEl.textContent = data.score;
        statusEl.textContent = `Комбинация: ${data.combo}`;
        await loadLeaderboard();
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
