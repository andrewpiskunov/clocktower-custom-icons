#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валидатор сценария «Пока смерть не разлучит нас» для Pocket Grimoire.

Проверяет:
  * всего ровно 25 ролей (без учёта _meta);
  * присутствует объект _meta;
  * нет роли с id "patriarh";
  * у каждой роли есть id, name, team, ability, image;
  * все id уникальны;
  * команды распределены как 13 townsfolk, 4 outsider, 4 minion, 4 demon;
  * все встроенные (embedded) image начинаются с "data:image/svg+xml".

Использование:
    python3 validate_pocket_grimoire_script.py
    python3 validate_pocket_grimoire_script.py путь/к/script.json
"""

import json
import os
import sys

DEFAULT_FILE = "poka_smert_ne_razluchit_nas_pocket_grimoire_with_embedded_images.json"

REQUIRED_FIELDS = ("id", "name", "team", "ability", "image")
EXPECTED_TEAMS = {"townsfolk": 13, "outsider": 4, "minion": 4, "demon": 4}
EXPECTED_TOTAL = 25


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), DEFAULT_FILE
    )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("ОШИБКА: корень JSON должен быть массивом.")
        return 1

    errors = []

    # _meta
    metas = [x for x in data if isinstance(x, dict) and x.get("id") == "_meta"]
    if not metas:
        errors.append("отсутствует объект _meta.")

    roles = [x for x in data if isinstance(x, dict) and x.get("id") != "_meta"]

    # всего 25 ролей
    if len(roles) != EXPECTED_TOTAL:
        errors.append(f"ролей {len(roles)}, ожидается {EXPECTED_TOTAL}.")

    # нет patriarh
    if any(r.get("id") == "patriarh" for r in roles):
        errors.append('найдена запрещённая роль "patriarh".')

    # обязательные поля
    for r in roles:
        rid = r.get("id", "<без id>")
        for field in REQUIRED_FIELDS:
            value = r.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                errors.append(f'роль "{rid}": отсутствует или пусто поле "{field}".')

    # уникальность id
    ids = [r.get("id") for r in roles]
    seen, dup = set(), set()
    for rid in ids:
        if rid in seen:
            dup.add(rid)
        seen.add(rid)
    if dup:
        errors.append(f"повторяющиеся id: {sorted(dup)}.")

    # распределение команд
    counts = {}
    for r in roles:
        counts[r.get("team")] = counts.get(r.get("team"), 0) + 1
    if counts != EXPECTED_TEAMS:
        errors.append(f"распределение команд {counts}, ожидается {EXPECTED_TEAMS}.")

    # embedded image начинается с data:image/svg+xml
    embedded = [r for r in roles if isinstance(r.get("image"), str)
                and r["image"].startswith("data:")]
    if embedded:
        bad = [r.get("id") for r in embedded
               if not r["image"].startswith("data:image/svg+xml")]
        if bad:
            errors.append(f"data-URI не начинается с data:image/svg+xml: {bad}.")

    if errors:
        print(f"ВАЛИДАЦИЯ НЕ ПРОЙДЕНА ({path}):")
        for e in errors:
            print("  -", e)
        return 1

    print(f"OK: {path}")
    print(f"  ролей: {len(roles)} (+ _meta)")
    print(f"  команды: {counts}")
    print(f"  embedded data-URI иконок: {len(embedded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
