#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборщик сценария «Пока смерть не разлучит нас» для Pocket Grimoire.

Генерирует:
  - icons/<id>.svg               (25 монохромных SVG-иконок)
  - poka_smert_ne_razluchit_nas_pocket_grimoire_with_embedded_images.json
  - poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json

Запуск:  python3 build.py
"""

import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(HERE, "icons")

# Цвета по командам (монохром, по одному цвету на иконку).
COLORS = {
    "townsfolk": "#1d4ed8",  # синий — Близкие
    "outsider":  "#15803d",  # зелёный — Неловкие гости
    "minion":    "#dc2626",  # красный — Интриганы
    "demon":     "#6d28d9",  # фиолетовый — Разрушители
}

# Базовый URL-плейсхолдер для внешнего варианта (заменяется после хостинга).
BASE_URL_PLACEHOLDER = "{{BASE_URL}}"


def heart(cx, cy, s):
    """Путь сердца с центром (cx,cy) и размером s."""
    return (
        f"M{cx},{cy+0.35*s:.1f} "
        f"C{cx-0.5*s:.1f},{cy-0.1*s:.1f} {cx-0.45*s:.1f},{cy-0.55*s:.1f} {cx},{cy-0.25*s:.1f} "
        f"C{cx+0.45*s:.1f},{cy-0.55*s:.1f} {cx+0.5*s:.1f},{cy-0.1*s:.1f} {cx},{cy+0.35*s:.1f} Z"
    )


# Внутреннее содержимое каждого SVG (без обёртки <svg>). Цвет наследуется.
INNER = {
    # 1. Невеста — тиара
    "nevesta": (
        '<path d="M15 66 Q50 82 85 66"/>'
        '<path d="M25 67 L35 41 L45 63"/>'
        '<path d="M40 64 L50 33 L60 64"/>'
        '<path d="M55 63 L65 41 L75 67"/>'
        '<circle cx="35" cy="41" r="3"/>'
        '<circle cx="50" cy="33" r="3.5"/>'
        '<circle cx="65" cy="41" r="3"/>'
    ),
    # 2. Свидетель — бабочка с цветком
    "svidetel": (
        '<path d="M50 62 L26 50 L26 74 Z"/>'
        '<path d="M50 62 L74 50 L74 74 Z"/>'
        '<rect x="45" y="56" width="10" height="12" rx="2"/>'
        '<circle cx="50" cy="30" r="7"/>'
        '<line x1="50" y1="37" x2="50" y2="50"/>'
    ),
    # 3. Подружка невесты — букет
    "podruzhka_nevesty": (
        '<circle cx="38" cy="30" r="9"/>'
        '<circle cx="60" cy="28" r="9"/>'
        '<circle cx="49" cy="44" r="9"/>'
        '<path d="M40 50 L48 78"/>'
        '<path d="M58 48 L51 78"/>'
        '<path d="M49 53 L50 78"/>'
        '<path d="M38 70 L60 70 L54 86 L44 86 Z"/>'
    ),
    # 4. Фотограф — фотоаппарат
    "fotograf": (
        '<rect x="18" y="38" width="64" height="44" rx="4"/>'
        '<rect x="38" y="30" width="20" height="10" rx="2"/>'
        '<circle cx="50" cy="60" r="14"/>'
        '<circle cx="50" cy="60" r="6"/>'
        '<circle cx="70" cy="47" r="2.5"/>'
    ),
    # 5. Ведущий — микрофон
    "vedushchiy": (
        '<rect x="40" y="18" width="20" height="36" rx="10"/>'
        '<line x1="41" y1="32" x2="59" y2="32"/>'
        '<line x1="41" y1="42" x2="59" y2="42"/>'
        '<path d="M30 50 Q30 70 50 70 Q70 70 70 50"/>'
        '<line x1="50" y1="70" x2="50" y2="84"/>'
        '<line x1="38" y1="84" x2="62" y2="84"/>'
    ),
    # 6. Родитель невесты — силуэт в торжественной одежде
    "roditel_nevesty": (
        '<circle cx="50" cy="28" r="13"/>'
        '<path d="M24 86 Q24 50 50 50 Q76 50 76 86"/>'
        '<path d="M50 50 L43 66 L50 72 L57 66 Z"/>'
    ),
    # 7. Ювелир — открытая коробочка с кольцом
    "yuvelir": (
        '<rect x="28" y="58" width="44" height="26" rx="3"/>'
        '<path d="M28 58 L40 42 L84 42 L72 58"/>'
        '<rect x="36" y="55" width="28" height="7" rx="3"/>'
        '<circle cx="50" cy="48" r="8"/>'
        '<path d="M44 40 L50 31 L56 40 Z"/>'
    ),
    # 8. Жених — смокинг
    "zhenih": (
        '<path d="M50 22 L34 40 L42 80"/>'
        '<path d="M50 22 L66 40 L58 80"/>'
        '<line x1="50" y1="30" x2="50" y2="80"/>'
        '<path d="M50 37 L42 32 L42 42 Z"/>'
        '<path d="M50 37 L58 32 L58 42 Z"/>'
        '<circle cx="50" cy="54" r="2"/>'
        '<circle cx="50" cy="64" r="2"/>'
    ),
    # 9. Распорядитель церемонии — свадебная арка
    "rasporyaditel_ceremonii": (
        '<line x1="28" y1="86" x2="28" y2="40"/>'
        '<line x1="72" y1="86" x2="72" y2="40"/>'
        '<path d="M28 40 Q50 16 72 40"/>'
        '<circle cx="32" cy="34" r="4"/>'
        '<circle cx="50" cy="24" r="4"/>'
        '<circle cx="68" cy="34" r="4"/>'
    ),
    # 10. Тамада — бокалы шампанского (тост)
    "tamada": (
        '<path d="M30 22 L40 22 L36 47 L34 47 Z"/>'
        '<line x1="35" y1="47" x2="35" y2="76"/>'
        '<line x1="28" y1="76" x2="42" y2="76"/>'
        '<path d="M60 22 L70 22 L66 47 L64 47 Z"/>'
        '<line x1="65" y1="47" x2="65" y2="76"/>'
        '<line x1="58" y1="76" x2="72" y2="76"/>'
        '<circle cx="50" cy="30" r="2"/>'
        '<circle cx="54" cy="20" r="1.5"/>'
    ),
    # 11. Родитель жениха — цилиндр
    "roditel_zheniha": (
        '<rect x="34" y="22" width="32" height="42" rx="2"/>'
        '<path d="M18 64 Q50 76 82 64"/>'
        '<line x1="34" y1="56" x2="66" y2="56"/>'
    ),
    # 12. Регистратор — раскрытая книга с пером
    "registrator": (
        '<path d="M16 42 Q33 34 50 42 Q67 34 84 42 L84 76 Q67 68 50 76 Q33 68 16 76 Z"/>'
        '<line x1="50" y1="42" x2="50" y2="76"/>'
        '<line x1="58" y1="64" x2="80" y2="30"/>'
        '<path d="M58 64 L56 71 L63 67 Z"/>'
    ),
    # 13. Старый друг семьи — переплетённые сердца
    "staryy_drug_semi": (
        f'<path d="{heart(40, 50, 40)}"/>'
        f'<path d="{heart(62, 52, 40)}"/>'
    ),
    # 14. Опоздавший гость — карманные часы
    "opozdavshiy_gost": (
        '<circle cx="50" cy="58" r="26"/>'
        '<rect x="45" y="20" width="10" height="9" rx="2"/>'
        '<line x1="50" y1="58" x2="50" y2="42"/>'
        '<line x1="50" y1="58" x2="62" y2="62"/>'
        '<circle cx="50" cy="58" r="2"/>'
    ),
    # 15. Пьяный дядя — бутылка и стакан
    "pyanyy_dyadya": (
        '<path d="M34 18 L44 18 L44 30 L48 38 L48 82 L30 82 L30 38 L34 30 Z"/>'
        '<line x1="30" y1="58" x2="48" y2="58"/>'
        '<path d="M58 46 L74 46 L71 82 L61 82 Z"/>'
        '<line x1="60" y1="62" x2="72" y2="62"/>'
    ),
    # 16. Брошенная бывшая — разбитое сердце
    "broshennaya_byvshaya": (
        f'<path d="{heart(50, 48, 56)}"/>'
        '<polyline points="50,28 43,46 55,56 47,74"/>'
    ),
    # 17. Нежеланный плюс-один — значок «+1»
    "nezhelannyy_plyus_odin": (
        '<circle cx="50" cy="50" r="30"/>'
        '<line x1="36" y1="50" x2="52" y2="50"/>'
        '<line x1="44" y1="42" x2="44" y2="58"/>'
        '<line x1="62" y1="42" x2="62" y2="58"/>'
        '<line x1="57" y1="46" x2="62" y2="42"/>'
    ),
    # 18. Завистливая подружка — туфля на каблуке
    "zavistlivaya_podruzhka": (
        '<path d="M24 48 Q26 60 40 60 L72 60 Q80 60 80 56 L36 51 Q26 46 24 48 Z"/>'
        '<path d="M70 60 L73 82 L79 82 L75 60 Z"/>'
    ),
    # 19. Сплетница — шепчущие губы
    "spletnica": (
        '<path d="M28 50 Q50 40 72 50 Q50 64 28 50 Z"/>'
        '<line x1="28" y1="50" x2="72" y2="50"/>'
        '<line x1="76" y1="44" x2="87" y2="42"/>'
        '<line x1="76" y1="52" x2="88" y2="55"/>'
    ),
    # 20. Свадебный аферист — карнавальная маска
    "svadebnyy_aferist": (
        '<path d="M18 42 Q18 30 34 32 Q50 36 66 32 Q82 30 82 42 Q82 60 64 62 Q50 56 36 62 Q18 60 18 42 Z"/>'
        '<ellipse cx="36" cy="44" rx="7" ry="5"/>'
        '<ellipse cx="64" cy="44" rx="7" ry="5"/>'
        '<path d="M50 34 L46 24"/>'
        '<path d="M50 34 L54 24"/>'
    ),
    # 21. Разлучник — разорванное надвое сердце
    "razluchnik": (
        '<path d="M44 30 C26 16 12 34 20 50 C26 62 36 70 42 80 L38 64 L44 54 L36 44 Z"/>'
        '<path d="M56 30 C74 16 88 34 80 50 C74 62 64 70 58 80 L62 64 L56 54 L64 44 Z"/>'
    ),
    # 22. Бывший возлюбленный — пробитое стрелой сердце
    "byvshiy_vozlyublennyy": (
        f'<path d="{heart(50, 52, 52)}"/>'
        '<line x1="22" y1="34" x2="80" y2="70"/>'
        '<path d="M80 70 L70 70"/>'
        '<path d="M80 70 L78 60"/>'
        '<path d="M22 34 L31 35"/>'
        '<path d="M22 34 L23 43"/>'
    ),
    # 23. Сбежавший жених — бегущая фигура
    "sbezhavshiy_zhenih": (
        '<circle cx="58" cy="24" r="8"/>'
        '<line x1="55" y1="32" x2="44" y2="56"/>'
        '<path d="M52 40 L66 36"/>'
        '<path d="M52 40 L38 45"/>'
        '<path d="M44 56 L56 74"/>'
        '<path d="M44 56 L30 70"/>'
    ),
    # 24. Брачный аферист — свадебный торт со спрятанным ножом
    "brachnyy_aferist": (
        '<rect x="32" y="56" width="36" height="20" rx="2"/>'
        '<rect x="38" y="40" width="24" height="16" rx="2"/>'
        '<circle cx="50" cy="34" r="4"/>'
        '<line x1="26" y1="78" x2="74" y2="78"/>'
        '<line x1="70" y1="20" x2="82" y2="48"/>'
        '<path d="M70 20 L65 24 L73 23 Z"/>'
    ),
    # 25. Подставная невеста — силуэт невесты в маске
    "podstavnaya_nevesta": (
        '<circle cx="50" cy="26" r="10"/>'
        '<path d="M40 22 Q24 30 28 72"/>'
        '<path d="M60 22 Q76 30 72 72"/>'
        '<path d="M36 80 Q36 46 50 46 Q64 46 64 80"/>'
        '<path d="M42 24 Q50 29 58 24"/>'
        '<circle cx="46" cy="25" r="1.5"/>'
        '<circle cx="54" cy="25" r="1.5"/>'
    ),
}


def wrap_svg(inner, color):
    """Полный SVG: viewBox 0 0 100 100, обводка цветом команды, без заливки."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        f'fill="none" stroke="{color}" stroke-width="5" '
        'stroke-linecap="round" stroke-linejoin="round">'
        f'{inner}</svg>'
    )


def data_uri(svg):
    """data:image/svg+xml;utf8,<URL-encoded UTF-8>. '#' -> %23 и т.д."""
    return "data:image/svg+xml;utf8," + quote(svg, safe="")


# Метаданные ролей. Порядок = порядок в JSON.
ROLES = [
    # --- 13 Близких (townsfolk) ---
    {
        "id": "nevesta", "name": "Невеста", "team": "townsfolk",
        "ability": "Вступление: вы узнаёте, добрый ли один выбранный вами игрок. Если это Жених, вы оба узнаёте друг друга.",
        "firstNight": 40, "otherNight": 0,
        "firstNightReminder": "Невеста выбирает игрока. Покажите «добрый» или «злой». Если выбран Жених, покажите им друг друга и поставьте «Знает Жениха».",
        "otherNightReminder": "",
        "reminders": ["Проверен", "Знает Жениха"], "setup": False,
    },
    {
        "id": "svidetel", "name": "Свидетель", "team": "townsfolk",
        "ability": "Вступление: вы узнаёте двух игроков, среди которых ровно один злой.",
        "firstNight": 41, "otherNight": 0,
        "firstNightReminder": "Покажите Свидетелю двух игроков, среди которых ровно один злой.",
        "otherNightReminder": "",
        "reminders": ["Показан"], "setup": False,
    },
    {
        "id": "podruzhka_nevesty", "name": "Подружка невесты", "team": "townsfolk",
        "ability": "Каждую ночь: выберите двух игроков. Вы узнаёте, на одной ли они стороне.",
        "firstNight": 0, "otherNight": 44,
        "firstNightReminder": "",
        "otherNightReminder": "Подружка невесты выбирает двух игроков. Покажите «да», если они на одной стороне, иначе «нет».",
        "reminders": ["Выбран 1", "Выбран 2"], "setup": False,
    },
    {
        "id": "fotograf", "name": "Фотограф", "team": "townsfolk",
        "ability": "Вступление: вы узнаёте трёх игроков. Среди них есть хотя бы один Интриган.",
        "firstNight": 42, "otherNight": 0,
        "firstNightReminder": "Покажите Фотографу трёх игроков, среди которых есть хотя бы один Интриган.",
        "otherNightReminder": "",
        "reminders": ["Показан"], "setup": False,
    },
    {
        "id": "vedushchiy", "name": "Ведущий", "team": "townsfolk",
        "ability": "Каждый день: публично назовите двух игроков. Ночью вы узнаёте, ровно ли один из них злой.",
        "firstNight": 0, "otherNight": 46,
        "firstNightReminder": "",
        "otherNightReminder": "Ведущий назвал двух игроков днём. Покажите «да», если ровно один из них злой, иначе «нет».",
        "reminders": ["Назван 1", "Назван 2"], "setup": False,
    },
    {
        "id": "roditel_nevesty", "name": "Родитель невесты", "team": "townsfolk",
        "ability": "Если вас казнят: выберите игрока. Если он злой, он умирает этой ночью. Иначе он пьяный до конца игры.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Выбран", "Пьяный", "Умирает"], "setup": False,
    },
    {
        "id": "yuvelir", "name": "Ювелир", "team": "townsfolk",
        "ability": "Вступление: выберите двух соседних игроков. Если оба добрые, один из них получает верную информацию следующей ночью.",
        "firstNight": 43, "otherNight": 0,
        "firstNightReminder": "Ювелир указывает на двух соседних игроков. Если оба добрые, поставьте «Верная информация» одному из них на следующую ночь.",
        "otherNightReminder": "",
        "reminders": ["Выбран 1", "Выбран 2", "Верная информация"], "setup": False,
    },
    {
        "id": "zhenih", "name": "Жених", "team": "townsfolk",
        "ability": "Каждую ночь*: выберите живого игрока. Если его выбрал Разрушитель, он не умирает этой ночью.",
        "firstNight": 0, "otherNight": 43,
        "firstNightReminder": "",
        "otherNightReminder": "Жених выбирает живого игрока. Если этой ночью Разрушитель выбрал того же игрока, он не умирает. Поставьте «Защищён».",
        "reminders": ["Защищён"], "setup": False,
    },
    {
        "id": "rasporyaditel_ceremonii", "name": "Распорядитель церемонии", "team": "townsfolk",
        "ability": "Каждую ночь: выберите игрока. Вы узнаёте, сколько злых среди его двух живых соседей.",
        "firstNight": 0, "otherNight": 45,
        "firstNightReminder": "",
        "otherNightReminder": "Распорядитель церемонии выбирает игрока. Покажите число (0, 1 или 2) злых среди его двух живых соседей.",
        "reminders": ["Выбран"], "setup": False,
    },
    {
        "id": "tamada", "name": "Тамада", "team": "townsfolk",
        "ability": "Один раз за игру, днём: публично произнесите тост за игрока. Если он добрый, он не может умереть этой ночью. Если злой, вы умираете этой ночью.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Тост", "Защищён", "Умирает"], "setup": False,
    },
    {
        "id": "roditel_zheniha", "name": "Родитель жениха", "team": "townsfolk",
        "ability": "Когда впервые ночью умирает добрый игрок, вы узнаёте роль живого злого игрока, но не кто это.",
        "firstNight": 0, "otherNight": 51,
        "firstNightReminder": "",
        "otherNightReminder": "Если этой ночью впервые умер добрый игрок: покажите Родителю жениха роль одного живого злого игрока (не указывая, кто это). Поставьте «Сработал».",
        "reminders": ["Сработал"], "setup": False,
    },
    {
        "id": "registrator", "name": "Регистратор", "team": "townsfolk",
        "ability": "Один раз за игру, ночью: выберите двух игроков. Если один из них — Разрушитель, вы узнаёте «да», иначе «нет».",
        "firstNight": 0, "otherNight": 47,
        "firstNightReminder": "",
        "otherNightReminder": "Если способность не использована: Регистратор выбирает двух игроков. Покажите «да», если один из них Разрушитель, иначе «нет». Поставьте «Нет способности».",
        "reminders": ["Выбран 1", "Выбран 2", "Нет способности"], "setup": False,
    },
    {
        "id": "staryy_drug_semi", "name": "Старый друг семьи", "team": "townsfolk",
        "ability": "Если вы мертвы: каждую ночь вы узнаёте, был ли казнён злой игрок сегодня.",
        "firstNight": 0, "otherNight": 50,
        "firstNightReminder": "",
        "otherNightReminder": "Если Старый друг семьи мёртв: покажите «да», если сегодня был казнён злой игрок, иначе «нет».",
        "reminders": [], "setup": False,
    },
    # --- 4 Неловких гостя (outsider) ---
    {
        "id": "opozdavshiy_gost", "name": "Опоздавший гость", "team": "outsider",
        "ability": "Вы можете получать информацию на одну ночь позже. Рассказчик может показать вас как отсутствующую в игре роль.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Задержка", "Показан как роль"], "setup": False,
    },
    {
        "id": "pyanyy_dyadya", "name": "Пьяный дядя", "team": "outsider",
        "ability": "Вы не знаете, что вы Пьяный дядя. Вы считаете себя определённым Близким, но его способность не работает.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Пьяный"], "setup": True,
    },
    {
        "id": "broshennaya_byvshaya", "name": "Брошенная бывшая", "team": "outsider",
        "ability": "Если вы умираете днём, один живой Близкий становится пьяным до следующей ночи.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Пьяный"], "setup": False,
    },
    {
        "id": "nezhelannyy_plyus_odin", "name": "Нежеланный плюс-один", "team": "outsider",
        "ability": "Вы можете определяться злым, Интриганом или Разрушителем. Если вы сидите рядом с Разрушителем, он узнаёт это.",
        "firstNight": 0, "otherNight": 0,
        "firstNightReminder": "",
        "otherNightReminder": "",
        "reminders": ["Сосед Разрушителя"], "setup": False,
    },
    # --- 4 Интригана (minion) ---
    {
        "id": "zavistlivaya_podruzhka", "name": "Завистливая подружка", "team": "minion",
        "ability": "Каждую ночь: выберите игрока. Он пьяный до следующей ночи. Если это Невеста или Жених, вы узнаёте его роль.",
        "firstNight": 0, "otherNight": 42,
        "firstNightReminder": "",
        "otherNightReminder": "Завистливая подружка выбирает игрока — он пьяный до следующей ночи. Если это Невеста или Жених, покажите его роль. Поставьте «Пьяный».",
        "reminders": ["Пьяный"], "setup": False,
    },
    {
        "id": "spletnica", "name": "Сплетница", "team": "minion",
        "ability": "Каждую ночь: выберите двух игроков. Завтра первый должен публично обвинить второго, иначе может умереть.",
        "firstNight": 0, "otherNight": 48,
        "firstNightReminder": "",
        "otherNightReminder": "Сплетница выбирает двух игроков. Завтра первый должен публично обвинить второго, иначе может умереть. Поставьте «Должен обвинить», «Цель обвинения», «Может умереть».",
        "reminders": ["Должен обвинить", "Цель обвинения", "Может умереть"], "setup": False,
    },
    {
        "id": "svadebnyy_aferist", "name": "Свадебный аферист", "team": "minion",
        "ability": "Вступление: выберите добрую роль, отсутствующую в игре. До конца игры вы можете определяться как эта роль.",
        "firstNight": 44, "otherNight": 0,
        "firstNightReminder": "Свадебный аферист выбирает добрую роль не в игре. Запомните её и поставьте «Ложная роль».",
        "otherNightReminder": "",
        "reminders": ["Ложная роль"], "setup": False,
    },
    {
        "id": "razluchnik", "name": "Разлучник", "team": "minion",
        "ability": "Вступление: выберите двух соседних игроков. Пока оба живы, один из них получает ложную информацию.",
        "firstNight": 45, "otherNight": 0,
        "firstNightReminder": "Разлучник указывает на двух соседних игроков. Пока оба живы, один из них получает ложную информацию. Поставьте «Ложная информация».",
        "otherNightReminder": "",
        "reminders": ["Выбран 1", "Выбран 2", "Ложная информация"], "setup": False,
    },
    # --- 4 Разрушителя (demon) ---
    {
        "id": "byvshiy_vozlyublennyy", "name": "Бывший возлюбленный", "team": "demon",
        "ability": "Каждую ночь*: выберите игрока: он умирает. Если сегодня вас публично обвинял добрый игрок, выберите второго; один из них не умирает.",
        "firstNight": 0, "otherNight": 49,
        "firstNightReminder": "",
        "otherNightReminder": "Бывший возлюбленный выбирает игрока — он умирает. Если днём его публично обвинял добрый игрок, он выбирает второго; один из двух не умирает.",
        "reminders": ["Мёртв", "Второй выбран", "Не умирает"], "setup": False,
    },
    {
        "id": "sbezhavshiy_zhenih", "name": "Сбежавший жених", "team": "demon",
        "ability": "Каждую ночь*: выберите игрока: он умирает. Если вчера не было казни, вместо него может умереть один из его соседей.",
        "firstNight": 0, "otherNight": 49,
        "firstNightReminder": "",
        "otherNightReminder": "Сбежавший жених выбирает игрока — он умирает. Если вчера не было казни, вместо него может умереть один из его живых соседей.",
        "reminders": ["Мёртв", "Сосед умер"], "setup": False,
    },
    {
        "id": "brachnyy_aferist", "name": "Брачный аферист", "team": "demon",
        "ability": "Вступление: выберите доброго игрока — вашу жертву. Каждую ночь*: выберите игрока: он умирает. Пока жертва жива, вы можете определяться добрым.",
        "firstNight": 46, "otherNight": 49,
        "firstNightReminder": "Брачный аферист выбирает доброго игрока — жертву. Поставьте «Жертва».",
        "otherNightReminder": "Брачный аферист выбирает игрока — он умирает. Пока жертва жива, аферист может определяться добрым.",
        "reminders": ["Жертва", "Мёртв"], "setup": False,
    },
    {
        "id": "podstavnaya_nevesta", "name": "Подставная невеста", "team": "demon",
        "ability": "Каждую ночь*: выберите игрока: он умирает. Первый раз, когда вас должны казнить, вместо вас может умереть живой игрок, публично доверявший вам сегодня.",
        "firstNight": 0, "otherNight": 49,
        "firstNightReminder": "",
        "otherNightReminder": "Подставная невеста выбирает игрока — он умирает. При первой казни вместо неё может умереть живой игрок, публично доверявший ей сегодня.",
        "reminders": ["Мёртв", "Доверял", "Защита использована"], "setup": False,
    },
]

META = {
    "id": "_meta",
    "name": "Пока смерть не разлучит нас",
    "author": "fan script",
    "logo": "",
}


def build_role(role, image_value):
    """Полная JSON-структура персонажа в формате Pocket Grimoire."""
    return {
        "id": role["id"],
        "edition": "custom",
        "firstNight": role["firstNight"],
        "firstNightReminder": role["firstNightReminder"],
        "otherNight": role["otherNight"],
        "otherNightReminder": role["otherNightReminder"],
        "reminders": role["reminders"],
        "remindersGlobal": [],
        "setup": role["setup"],
        "name": role["name"],
        "team": role["team"],
        "ability": role["ability"],
        "image": image_value,
    }


def main():
    os.makedirs(ICONS_DIR, exist_ok=True)

    ids = [r["id"] for r in ROLES]
    missing = [i for i in ids if i not in INNER]
    if missing:
        raise SystemExit(f"Нет SVG для: {missing}")

    # 1) SVG-файлы
    for role in ROLES:
        svg = wrap_svg(INNER[role["id"]], COLORS[role["team"]])
        with open(os.path.join(ICONS_DIR, role["id"] + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)

    # 2) Встроенный (embedded) JSON
    embedded = [META]
    for role in ROLES:
        svg = wrap_svg(INNER[role["id"]], COLORS[role["team"]])
        embedded.append(build_role(role, data_uri(svg)))

    with open(os.path.join(HERE, "poka_smert_ne_razluchit_nas_pocket_grimoire_with_embedded_images.json"),
              "w", encoding="utf-8") as f:
        json.dump(embedded, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 3) Внешний (external) JSON — image указывает на отдельные SVG-файлы
    external = [META]
    for role in ROLES:
        url = f"{BASE_URL_PLACEHOLDER}/icons/{role['id']}.svg"
        external.append(build_role(role, url))

    with open(os.path.join(HERE, "poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json"),
              "w", encoding="utf-8") as f:
        json.dump(external, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Готово: {len(ROLES)} ролей, {len(ids)} иконок.")
    print("Команды:", {t: sum(1 for r in ROLES if r["team"] == t) for t in COLORS})


if __name__ == "__main__":
    main()
