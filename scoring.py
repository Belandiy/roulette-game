import random

# Список символов для барабанов с их весами (вероятностями)
SYMBOLS = ['cherry', 'lemon', 'orange', 'plum', 'grape', 'seven']
SYMBOL_WEIGHTS = [30, 25, 20, 15, 8, 2]  # Вероятности выпадения (в процентах)

# Словарь выплат за комбинации
PAYTABLE = {
    ('seven', 'seven', 'seven'): 500,
    ('grape', 'grape', 'grape'): 100,
    ('plum', 'plum', 'plum'): 50,
    ('orange', 'orange', 'orange'): 25,
    ('lemon', 'lemon', 'lemon'): 15,
    ('cherry', 'cherry', 'cherry'): 10,
    ('cherry', 'cherry'): 5,  # Две вишни
}

def spin_reels(n=3):
    """
    Реальная логика вращения барабанов
    Возвращает случайную комбинацию символов
    """
    return [random.choices(SYMBOLS, weights=SYMBOL_WEIGHTS)[0] for _ in range(n)]

def score(reels):
    """
    Реальная логика подсчета очков
    Возвращает очки за комбинацию
    """
    # Проверяем комбинации из 3 одинаковых символов
    if reels[0] == reels[1] == reels[2]:
        return PAYTABLE.get((reels[0], reels[1], reels[2]), 0)
    
    # Проверяем комбинации из 2 одинаковых символов
    if reels[0] == reels[1]:
        return PAYTABLE.get((reels[0], reels[1]), 0)
    if reels[1] == reels[2]:
        return PAYTABLE.get((reels[1], reels[2]), 0)
    if reels[0] == reels[2]:
        return PAYTABLE.get((reels[0], reels[2]), 0)
    
    # Нет выигрышной комбинации
    return 0

def get_symbol_display(symbol):
    """
    Возвращает emoji-представление символа для фронтенда
    """
    symbol_emojis = {
        'cherry': '🍒',
        'lemon': '🍋',
        'orange': '⭐',  # или 🍊
        'plum': '🔔',   # или 🍑
        'grape': '🍇',
        'seven': '7️⃣'
    }
    return symbol_emojis.get(symbol, '❓')
