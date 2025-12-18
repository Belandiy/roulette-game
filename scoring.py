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

TRIPLE_SCORES = { 
    "7️⃣": 500, 
}
PAIR_SCORE = 10


def spin_reels(n=3):
    return [choice(DECK) for _ in range(n)]

def score(reels):
    a, b, c = reels
    if a == b == c:
        return TRIPLE_SCORES.get(a, 0)
    if a == b or a == c or b == c:
        return PAIR_SCORE
    return 0

# Тестовый блок
if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ SCORING.PY ===")
    
    # Тест спина
    print("1. Тест спина:")
    test_reels = spin_reels(3)
    print(f"   Результат: {test_reels}")
    print(f"   Очки: {score(test_reels)}")
