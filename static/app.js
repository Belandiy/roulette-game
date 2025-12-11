async function spinRequest(nickname) {
  const res = await fetch('/api/spin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nickname })
  });
  if (!res.ok) {
    const j = await res.json().catch(() => ({}));
    throw new Error(j.error || 'Server error');
  }
  return await res.json();
}

function renderResult(data) {
  document.getElementById('result-values').textContent = data.result.join(' - ');
  document.getElementById('result-score').textContent = data.score;
  document.getElementById('result-combo').textContent = data.combo;
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('spin-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    const nick = document.getElementById('nickname').value || 'anonymous';
    btn.disabled = true;
    btn.textContent = 'Крутим...';
    try {
      const data = await spinRequest(nick);
      renderResult(data);
    } catch (err) {
      alert('Ошибка: ' + err.message);
      console.error(err);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Крутить';
    }
  });
});
