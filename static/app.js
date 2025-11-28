document.addEventListener("DOMContentLoaded", () => {
  // 1. ╨Ш╨╜╨╕╤Ж╨╕╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П DOM: ╨╜╨░╤Е╨╛╨┤╨╕╨╝ ╤Н╨╗╨╡╨╝╨╡╨╜╤В╤Л ╨┐╨╛ ╨╕╤Е ╨Э╨Ю╨Т╨л╨Ь id ╨╕╨╖ ╨▓╨╡╤А╤Б╤В╨║╨╕
  const spinBtn = document.getElementById("spin-btn");
  
  // ╨Ш╨Ч╨Ь╨Х╨Э╨Х╨Э╨Ю: id ╨┐╨╛╨╗╤П ╨╛╤З╨║╨╛╨▓ ╤В╨╡╨┐╨╡╤А╤М 'result-score'
  const pointsEl = document.getElementById("result-score");
  
  // ╨Ш╨Ч╨Ь╨Х╨Э╨Х╨Э╨Ю: id ╨┐╨╛╨╗╤П ╨╗╤Г╤З╤И╨╡╨│╨╛ ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В╨░ ╤В╨╡╨┐╨╡╤А╤М 'best-points'
  const bestEl = document.getElementById("best-points");
  
  const statusEl = document.getElementById("status");
  
  // ╨Ш╨Ч╨Ь╨Х╨Э╨Х╨Э╨Ю: id ╤В╨╡╨╗╨░ ╤В╨░╨▒╨╗╨╕╤Ж╤Л ╤В╨╡╨┐╨╡╤А╤М 'leaderboard-list'
  const leaderboardEl = document.getElementById("leaderboard-list");
  
  const reels = [...document.querySelectorAll(".reel")];

// 2. ╨д╤Г╨╜╨║╤Ж╨╕╤П ╨┤╨╗╤П ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ ╨╗╨╕╨┤╨╡╤А╨▒╨╛╤А╨┤╨░
  async function loadLeaderboard() {
    try {
      // ╨Э╨░ ╤Н╤В╨░╨┐╨╡ ╨б╨┐╤А╨╕╨╜╤В╨░ 2 ╤Б╨╡╤А╨▓╨╡╤А ╨▓╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╤В ╤Б╤В╨░╤В╨╕╤З╨╡╤Б╨║╨╕╨╡ ╨┤╨░╨╜╨╜╤Л╨╡ ╨╖╨░╨│╨╗╤Г╤И╨║╤Г.
      // ╨а╨╡╨░╨╗╤М╨╜╨╛╨╡ ╤Б╨╛╤Е╤А╨░╨╜╨╡╨╜╨╕╨╡ ╨╕ ╤З╤В╨╡╨╜╨╕╨╡ ╨┐╨╗╨░╨╜╨╕╤А╨╛╨▓╨░╨╗╨╛╤Б╤М ╤А╨╡╨░╨╗╨╕╨╖╨╛╨▓╨░╤В╤М ╨╜╨░ ╨▒╤Н╨║╨╡╨╜╨┤╨╡ ╨▓ ╨б╨┐╤А╨╕╨╜╤В╨╡ 3.
      const response = await fetch("/api/leaderboard");
      const data = await response.json(); 
      
      console.log("Leaderboard data received:", data); // ╨Ы╨╛╨│ ╨┤╨╗╤П ╨┤╨╡╨╝╨╛╨╜╤Б╤В╤А╨░╤Ж╨╕╨╕ ╤А╨░╨▒╨╛╤В╤Л

      // ╨а╨░╨▒╨╛╤В╨░╨╡╨╝ ╤Б ╨╜╨╛╨▓╤Л╨╝ ID 'leaderboard-list'
      leaderboardEl.innerHTML = "";
      
      // ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨╜╨░ ╤Б╨╗╤Г╤З╨░╨╣, ╨╡╤Б╨╗╨╕ ╨┤╨░╨╜╨╜╤Л╤Е ╨╜╨╡╤В
      if (data.length === 0) {
        leaderboardEl.innerHTML = "<tr><td colspan='2'>╨Э╨╡╤В ╨┤╨░╨╜╨╜╤Л╤Е</td></tr>";
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

  // 3. ╨Ю╨▒╤А╨░╨▒╨╛╤В╤З╨╕╨║ ╨║╨╜╨╛╨┐╨║╨╕ "╨Ъ╤А╤Г╤В╨╕╤В╤М"
  if (spinBtn) {
    spinBtn.addEventListener("click", async () => {
      spinBtn.disabled = true;
      statusEl.textContent = "╨Ъ╤А╤Г╤В╨╕╨╝...";

      try {
        const response = await fetch("/api/spin", { method: "POST" });
        const data = await response.json(); // ╨Ю╨╢╨╕╨┤╨░╨╡╨╝ {result: [...], score: N, combo: "..."}

        // ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ DOM ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨┐╨╛╨╗╤Г╤З╨╡╨╜╨╜╤Л╤Е ╨┤╨░╨╜╨╜╤Л╤Е
        reels.forEach((reel, index) => {
          reel.textContent = data.result[index];
        });

        // ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ ╨╛╤З╨║╨╕ ╨╖╨░ ╤Б╨┐╨╕╨╜ ╨▓ ╤Н╨╗╨╡╨╝╨╡╨╜╤В╨╡ ╤Б id 'result-score'
        pointsEl.textContent = data.score;
        statusEl.textContent = `╨Ъ╨╛╨╝╨▒╨╕╨╜╨░╤Ж╨╕╤П: ${data.combo}`;

        // ╨Я╨╛╨╗╨╡ 'best-points' ╨┐╨╛╨║╨░ ╨╜╨╡ ╨╛╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝, ╤В╨░╨║ ╨║╨░╨║ API ╨▒╤Н╨║╨╡╨╜╨┤╨╡╤А╨░
        // ╨╜╨╡ ╨▓╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╤В ╤Б╨╛╨╛╤В╨▓╨╡╤В╤Б╤В╨▓╤Г╤О╤Й╨╡╨╡ ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡.

      } catch (error) {
        statusEl.textContent = "╨Ю╤И╨╕╨▒╨║╨░ ╤Б╨┐╨╕╨╜╨░";
        console.error("Spin error:", error);
      } finally {
        spinBtn.disabled = false;
      }
    });
  }

  loadLeaderboard();
});
