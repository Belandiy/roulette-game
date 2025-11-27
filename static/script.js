async function spinRequest(nick) {
  const res = await fetch('/api/spin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nick })
  });
  if (!res.ok) {
    const j = await res.json().catch(() => ({}));
    throw new Error(j.error || 'Server error');
  }
  return await res.json();
}

async function loadLeaderboard() {
  try {
    const res = await fetch('/api/leaderboard');
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById('leaderboard-list');
    if (!tbody) return;
    tbody.innerHTML = data.map(row => 
      `<tr><td>${row.nickname}</td><td>${row.best_score}</td></tr>`
    ).join('');
  } catch (err) {
    console.error('Ошибка загрузки лидерборда:', err);
  }
}

function renderResult(data) {
  document.getElementById('result-values').textContent = data.result.join(' - ');
  document.getElementById('result-score').textContent = data.score;
  document.getElementById('result-combo').textContent = data.combo;
}

document.addEventListener('DOMContentLoaded', () => {
  // Загрузить таблицу лидеров при загрузке страницы
  loadLeaderboard();

  const btn = document.getElementById('spin-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    const nick = document.getElementById('nickname').value || 'anonymous';
    btn.disabled = true;
    btn.textContent = 'Крутим...';
    try {
      const data = await spinRequest(nick);
      renderResult(data);
      // Обновить таблицу лидеров после спина
      loadLeaderboard();
    } catch (err) {
      alert('Ошибка: ' + err.message);
      console.error(err);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Крутить';
    }
  });
});
