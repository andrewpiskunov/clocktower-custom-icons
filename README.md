# Пока смерть не разлучит нас

Фанатский свадебный сценарий для **Blood on the Clocktower** в формате
**Pocket Grimoire** / BOTC Script Tool.

25 кастомных ролей с оригинальными монохромными SVG-иконками (официальные иконки
BOTC **не используются**).

| Категория в мире сценария | Техническая команда | Кол-во | Цвет иконок |
|---------------------------|---------------------|:------:|-------------|
| Близкие                   | `townsfolk`         | 13     | синий       |
| Неловкие гости            | `outsider`          | 4      | зелёный     |
| Интриганы                 | `minion`            | 4      | красный     |
| Разрушители               | `demon`             | 4      | фиолетовый  |

## Файлы

```
clocktower-custom-icons/
├── poka_smert_ne_razluchit_nas_pocket_grimoire_with_embedded_images.json   # иконки встроены (data URI)
├── poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json   # иконки по URL (нужен хостинг)
├── icons/                                                                  # 25 SVG-иконок
│   ├── nevesta.svg
│   └── …
├── validate_pocket_grimoire_script.py                                      # валидатор сценария
├── build.py                                                                # пересборка всех файлов
└── README.md
```

## Какой файл использовать

1. **`…_with_embedded_images.json`** — рекомендуемый вариант.
   Все иконки встроены прямо в JSON как `data:image/svg+xml;utf8,…`.
   Никакого хостинга не нужно — импортируйте файл и сразу играйте.

2. **`…_with_external_images.json`** — запасной вариант на случай, если ваша
   сборка Pocket Grimoire не отображает `data:`-иконки. Здесь поле `image`
   указывает на отдельные SVG-файлы из папки `icons/`. Требует выложить папку
   `icons/` на статический хостинг (см. ниже).

## Импорт в Pocket Grimoire

Pocket Grimoire — <https://www.pocketgrimoire.co.uk/> (и форки).

1. Откройте Pocket Grimoire в браузере.
2. Нажмите **«Select Edition / Characters»** → **«Custom Script»**
   (в некоторых сборках: «Add custom characters» / «Homebrew»).
3. Выберите способ загрузки:
   - **Upload file** — загрузите
     `poka_smert_ne_razluchit_nas_pocket_grimoire_with_embedded_images.json`;
   - либо **Paste URL** — если файл выложен в интернете, вставьте ссылку на него;
   - либо **Paste JSON** — откройте файл, скопируйте всё содержимое и вставьте.
4. Подтвердите. Появятся 25 ролей с иконками, объект `_meta` задаёт название
   сценария «Пока смерть не разлучит нас».
5. Жетоны и ночные порядки подставятся автоматически из полей `firstNight`,
   `otherNight`, `firstNightReminder`, `otherNightReminder`, `reminders`.

> Тот же JSON совместим с официальным **BOTC Script Tool**
> (<https://script.bloodontheclocktower.com/>) через **Import → Custom JSON**.

## Если Pocket Grimoire не показывает `data:image/svg+xml`

Некоторые старые сборки или строгие настройки CSP не рендерят встроенные
data-URI. Тогда:

1. Выложите папку `icons/` на статический хостинг (GitHub Pages и т.п. — ниже).
2. Используйте `…_with_external_images.json`, заменив в нём плейсхолдер
   `{{BASE_URL}}` на реальный адрес (см. «Автозамена базового URL»).
3. Импортируйте получившийся файл в Pocket Grimoire тем же способом.

## Хостинг иконок на GitHub Pages

```bash
# 1. Закоммитьте и запушьте репозиторий с папкой icons/
git add icons poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json README.md
git commit -m "Add wedding script icons"
git push origin main

# 2. На GitHub: Settings → Pages → Source: "Deploy from a branch",
#    Branch: main, Folder: / (root). Сохраните.
#    Через 1–2 минуты иконки будут доступны по адресу вида:
#    https://<username>.github.io/clocktower-custom-icons/icons/nevesta.svg
```

Любой другой статический хостинг (Netlify, Cloudflare Pages, GitLab Pages,
обычный веб-сервер) работает так же — важно лишь, чтобы файлы
`icons/<id>.svg` отдавались по публичному HTTPS-адресу.

## Автозамена базового URL

В файле `…_with_external_images.json` каждый `image` имеет вид
`{{BASE_URL}}/icons/<id>.svg`. После публикации иконок подставьте свой адрес
**одной командой** (без хвостового слэша):

```bash
BASE_URL="https://<username>.github.io/clocktower-custom-icons"
sed -i '' "s#{{BASE_URL}}#${BASE_URL}#g" \
  poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json   # macOS

# Linux:
# sed -i "s#{{BASE_URL}}#${BASE_URL}#g" poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json
```

После этого все ссылки станут абсолютными, например
`https://<username>.github.io/clocktower-custom-icons/icons/nevesta.svg`.

## Проверка сценария

```bash
python3 validate_pocket_grimoire_script.py
# по умолчанию проверяет встроенный (embedded) JSON
# можно указать другой файл:
python3 validate_pocket_grimoire_script.py poka_smert_ne_razluchit_nas_pocket_grimoire_with_external_images.json
```

Валидатор проверяет: ровно 25 ролей, наличие `_meta`, отсутствие роли
`patriarh`, обязательные поля (`id`, `name`, `team`, `ability`, `image`),
уникальность `id`, распределение команд 13/4/4/4 и формат встроенных
data-URI (`data:image/svg+xml`).

## Пересборка

`build.py` заново генерирует все 25 SVG, оба JSON-файла и папку `icons/`
из единого источника:

```bash
python3 build.py
```

## Ночной порядок

**Первая ночь:** Закат → Интриганы → Разрушитель → Невеста → Свидетель →
Фотограф → Ювелир → Свадебный аферист → Разлучник → Брачный аферист → Рассвет.

**Последующие ночи:** Закат → Завистливая подружка → Жених → Подружка невесты →
Распорядитель церемонии → Ведущий → Регистратор → Сплетница → Разрушитель →
Старый друг семьи → Родитель жениха → Рассвет.
