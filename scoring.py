from secrets import choice

# символы и веса выпадения
SYMBOL_WEIGHTS = {
    "🍒": 3, 
    "🍋": 3, 
    "⭐": 2, 
    "🔔": 1, 
    "7️⃣": 1, 
}

# подготовим «барабан» для простого выбора
DECK = [sym for sym, w in SYMBOL_WEIGHTS.items() for _ in range(w)]


def spin_reels(n=3):
    """
    Генерация n случайных символов с учётом весов из DECK.
    Теперь работает с настоящим RNG.
    """
    return [choice(DECK) for _ in range(n)]

def score(reels):
    """
    Подсчёт очков на основе комбинации символов.
    Правила:
    - Три одинаковых (three_of_kind): 100 очков
    - Две одинаковых (pair): 20 очков
    - Остальное (none): 0 очков
    """
    if reels[0] == reels[1] == reels[2]:
        return 100
    elif len(set(reels)) == 2:
        return 20
    else:
        return 0

# Тестовый блок
if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ SCORING.PY ===")
    
    # Тест спина
    print("1. Тест спина:")
    test_reels = spin_reels(3)
    print(f"spin_reels() вернул: {test_reels}")
    test_score = score(test_reels)
    print(f"score({test_reels}) вернул: {test_score}")
    
    print(f"Список символов: {SYMBOL_WEIGHTS}")
