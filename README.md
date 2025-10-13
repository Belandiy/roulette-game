# Веб-приложение «Рулетка с турнирной таблицей»

Учебный проект для демонстрации работы в команде.  
Веб-приложение реализовано на **Python** с использованием **SQLite** для хранения данных.  
Игрок крутит рулетку из 3 цилиндров, получает очки за комбинации, формируется турнирная таблица с ТОП-10 игроков.  

---

## 🚀 Установка и запуск

1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Запуск приложения:
```bash
python app.py
```

3. Открыть в браузере:
- Главная: http://127.0.0.1:5000/
- Правила: http://127.0.0.1:5000/rules

---

API — POST /api/spin

Описание. Сервер честно генерирует «вращение» — 3 числа (0–9) и возвращает результат и начисленные очки. MVP: ничего не сохраняется (нет БД).
```
Endpoint: POST /api/spin
```
```
Content-Type: application/json
```
```
Request
{
  "nickname": "Player1"
}
```

nickname — необязательное. Если не передано, будет anonymous.
```bash
Response — 200 OK
{
  "nickname": "Player1",
  "result": [4, 4, 4],
  "score": 100,
  "combo": "three_of_kind"
}
```

Пояснения

result — массив из 3 чисел (0..9).

combo — одна из строк: "three_of_kind", "pair", "none".

score — начисленные очки (MVP-правила: три одинаковых = 100, пара = 20, иначе = 0).

Errors

400 Bad Request — неверный формат JSON или структура запроса:
```
{ "error": "bad request" }
```
Примеры вызовов
```curl
curl -s -X POST http://127.0.0.1:5000/api/spin \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Player1"}'
```
```bash
JavaScript (fetch)
async function spin(nickname = 'anonymous') {
  const res = await fetch('/api/spin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nickname })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Server error');
  }
  return await res.json();
}

// пример использования
spin('Player1').then(data => console.log(data)).catch(e => console.error(e));
```
Python (requests)
```bash
import requests

r = requests.post('http://127.0.0.1:5000/api/spin', json={"nickname":"Player1"})
print(r.status_code, r.json())
```

---

## 👥 Состав команды

- Баранов Александр (GitHub: Blond-beard-catboy) — Backend (Flask + API)  
- Белых Андрей (GitHub: Belandiy) — Документация + DevOps + БД
- Савчук Виталий (GitHub: vitek4k) — Верстальщик / UI-дизайнер
- Яшков Андрей (GitHub: Lomikk) — Фронтенд (JS)
- Джураев Фазлиддин (GitHub: Fazliddin4999) — Игровая логика

---

## 📌 Функционал

- Рулетка с 3 цилиндрами и анимацией вращения.  
- Кнопка **«Крутить»** для запуска игры.  
- Подсчёт очков за комбинации.  
- Сохранение результатов в базе данных.  
- Отображение турнирной таблицы (ТОП-10 игроков).  
- Страница «Правила игры».  
- Минимальная регистрация игрока (никнейм).  

---

## 📌 Документация

- [Техническое задание](tech-task.md)
