# HANDOFF — Carat Tour & Study (carattourandstudy.uz)

Документ для продолжения работы в новом чате. Приложить к новому чату:
1. **этот файл** `HANDOFF.md`;
2. архив **`carat-tour-study.zip`** (весь проект: исходники + готовый `build/`);
3. по желанию — исходное ТЗ (`attachment.txt`) и макет главной (PNG), если нужно сверяться с ними.

Первое сообщение в новом чате, например:
> Продолжаем проект Carat Tour & Study. Прочитай HANDOFF.md, распакуй carat-tour-study.zip, собери проект (`npm install && python3 build.py`) и [задача].

---

## 1. Клиент и задача

- **Клиент:** туристическое агентство Carat Tour & Study, Узбекистан.
- **Домен:** https://carattourandstudy.uz · **Telegram:** https://t.me/carat_tour (@carat_tour)
- **Направления деятельности:** международные туры, туры по Узбекистану, инфо-туры (ознакомительные поездки для специалистов отрасли — отдельное направление, не смешивать с турпакетами).
- **Языки:** UZ (по умолчанию, латиница), RU, EN, 中文 (упрощённый). URL: `/uz/`, `/ru/`, `/en/`, `/zh/`.
- **ТЗ:** многоязычный корпоративный сайт; в ТЗ рекомендован WordPress + Elementor Pro + CPT + мультиязычный плагин. Онлайн-бронирование/оплата — вне базового объёма.
- **Ключевые ограничения ТЗ:** не публиковать вымышленные отзывы; цены/даты/программы — только по данным компании; Schema.org — по реальному типу компании.

## 2. Что сделано (этап 1 — статическая вёрстка)

Выбран путь: **макет → статический HTML (Tailwind) → затем перенос на WordPress**.

- Генератор `build.py` (Python + Jinja2) собирает **77 страниц**: 19 страниц × 4 языка + `404.html`.
- Страницы на язык: главная; туры по Узбекистану (список + 5 направлений: tashkent, samarkand, bukhara, khiva, chimgan); международные туры (список с фильтром + 5: maldives, turkey, uae, thailand, europe); инфо-туры; о компании; контакты; privacy; consent; thanks (noindex).
- Корень `/` — автоопределение языка браузера → `/xx/` (по умолчанию UZ, запоминается в localStorage).
- **SEO:** hreflang + x-default, языковые canonical, OG, `sitemap.xml` с xhtml:link альтернативами, `robots.txt`, JSON-LD (`TravelAgency`, `WebSite`, `BreadcrumbList`, `TouristDestination` с достопримечательностями и geo), один H1, alt, lazy-load, preload LCP.
- **Поиск тура** на главной не ищет по каталогу (каталога с ценами нет) — переносит направление/даты/туристов в форму заявки и выставляет тип тура (так допускает ТЗ).
- **Форма заявки:** имя, телефон/Telegram, направление, тип тура (чипы), даты, комментарий, согласие. Валидация в JS + на сервере. Антиспам: honeypot `website`, проверка времени заполнения (≥3 с), rate-limit 5 заявок/10 мин по IP.
- **`send.php`:** отправка в Telegram-бот и/или email, данные не сохраняет. Ответы JSON `{ok, error}`; при успехе JS редиректит на `/xx/thanks/`.
- **`.htaccess`:** HTTPS + без www, кэш, gzip, заголовки безопасности, ErrorDocument 404.
- Проверено: скриншоты desktop/mobile (RU, UZ, ZH, EN), 4072 внутренние ссылки — битых 0, ошибок JS нет, поиск→форма, валидация, фильтр, ответы send.php.
- Git: локальный репозиторий, 1 коммит `033cee9` (ветка `main`). **В GitHub не залито** — из прошлой сессии нельзя было создать репозиторий. Нужно: создать пустой репо (например `farik9797/carat-tour-study`), затем `git remote add origin … && git push -u origin main`.

## 3. Структура проекта

```
carat/
├─ build.py               # генератор + НАСТРОЙКИ (SITE, флаги, слаги, промо)
├─ tailwind.config.js     # палитра и шрифты
├─ package.json           # tailwindcss@3 (CLI)
├─ README.md              # краткая инструкция
├─ HANDOFF.md             # этот файл
├─ src/
│  ├─ i18n/{uz,ru,en,zh}.py   # ВСЕ тексты; ru.py — эталон структуры ключей
│  ├─ templates/
│  │  ├─ base.html             # head: meta, hreflang, OG, JSON-LD, шрифты
│  │  ├─ home.html, uz_list.html, dest.html, intl_list.html, tour.html,
│  │  │  info.html, about.html, contacts.html, legal.html, thanks.html (+404)
│  │  └─ partials/ header.html, footer.html, final_cta.html, macros.html
│  ├─ assets/css/input.css     # Tailwind + компоненты (.btn-*, .card, .field, .chip…)
│  ├─ assets/js/app.js         # меню, поиск→форма, валидация, отправка, фильтр, лайтбокс
│  ├─ assets/img/*.webp        # ПЛЕЙСХОЛДЕРЫ, вырезанные из макета + favicon.svg
│  └─ root/ send.php, .htaccess  # копируются в корень build/
└─ build/                 # готовый сайт для заливки на хостинг
```

**Сборка и предпросмотр:**
```bash
npm install                # tailwindcss@3
pip install jinja2
python3 build.py           # сверяет структуру переводов, собирает build/, компилирует CSS
cd build && php -S localhost:8080   # с рабочей формой; без PHP: python3 -m http.server
```

**Важные механики build.py:**
- `check_langs()` — сборка падает, если ключи/длины списков в uz/en/zh не совпадают с ru.py.
- Jinja с `StrictUndefined`: необязательные поля брать через `.get()` / `is defined`.
- Иконки Material Symbols: собираются из HTML и подставляются в URL шрифта (`icon_names=`) — только используемые.
- Ссылки относительные (`url()`, `asset()`, `lang_url()`); 404 — относительные от `<base>` (`/` на домене, `/<repo>/` на GitHub Pages).
- `PROMO` — ссылка/картинка промоблока; `INTL_KINDS` — категории для фильтра; `GEO` — координаты для JSON-LD.

## 4. Дизайн-система (с макета)

- Цвета: navy `#0B2A7A` (900 `#062958` — футер/тёмные блоки), accent/оранжевый `#FEAA23` (кнопки CTA), sky `#F4F8FD/#E4F0FD/#C9E0FA`, teal `#0FA3B1/#027F9A`, текст ink `#1E2B4A`, вторичный `#5B6B8C`.
- Шрифты: Montserrat 400–800 (Noto Sans SC для 中文), рукописный акцент Caveat 600 («Больше, чем просто путешествия», «Новые впечатления рядом»).
- Компоненты: `.btn-accent`, `.btn-navy`, `.btn-ghost`, `.btn-outline-light`, `.section-title` (оранжевая полоска слева), `.card`, `.field`, `.chip`, `.photo-slot` (пустое место под фото).
- Скругления 2xl/3xl, мягкие тени `shadow-card/soft/float`.
- Шрифты свои: Montserrat (variable) и Caveat из npm `@fontsource*` → `src/assets/fonts/` (@font-face в `input.css`); иконки Material Symbols — `build.py → icon_font()` скачивает подмножество в `src/assets/fonts/ms-<hash>.woff2` (без сети — фолбэк на Google). 中文 — системные шрифты (PingFang/YaHei/Noto CJK).
- LCP-картинки: `name-sm.avif` (телефон, `<picture>`), `name-sm.webp`/`name.webp` (srcset). Журнал скорости — `PERF.md`.
- `.container` — свой (core-плагин Tailwind отключён): контент до 1300px, отступы 16/24/32px (`input.css`).

## 5. Что НЕ готово / нужно от заказчика

| # | Что | Где менять |
|---|---|---|
| 1 | Фото: 23.10 заменены на реальные с Unsplash (направления, галереи по 4 фото, «О компании», инфо-туры) — список в `IMAGE-SOURCES.md`. Hero и фото озера — от заказчика. Фото команды/офиса/прошлых инфо-туров агентства по-прежнему нужны: сейчас там нейтральные стоковые блоки «Планируем ваше путешествие» / «Как проходят инфо-туры» | `src/assets/img/`, `IMAGE-SOURCES.md` |
| 2 | Логотип SVG — желательно. Сейчас `logo.webp` (прозрачный фон) и `logo-white.webp` (navy→белый, для футера) сделаны из PNG заказчика 2103×748, 757×220 px | `src/assets/img/`, header/footer |
| 3 | Контакты взяты с caratstudy.uz (23.10): +998 97 409 42 00, info@caratstudy.uz, «Tashkent, Cho'ponota, №39», Instagram @carat_tour. Нужно подтвердить; график работы — нет данных. Telegram — `t.me/carat_tour` (решено 23.10; ссылку-приглашение с caratstudy.uz не используем) | `build.py` → `SITE` |
| 4 | Токен Telegram-бота, chat_id менеджеров, email для заявок | `src/root/send.php` или env `CARAT_TG_TOKEN`, `CARAT_TG_CHAT`, `CARAT_MAIL_TO` |
| 5 | Реальные отзывы с разрешением. Блок отзывов скрыт (`SHOW_REVIEWS = False`, 23.10) — вписать отзывы в `reviews` и включить | `build.py`, `src/i18n/*.py` → `reviews` |
| 6 | Согласовать политику и согласие с юристом (служебные пометки уже скрыты: `SHOW_DEV_NOTES = False`, 23.10) | `build.py`, `src/i18n/*.py` → `pages.privacy/consent` |
| 7 | Точный список зарубежных стран, программы, даты, цены (сейчас «по запросу») | `INTL_SLUGS`, `intl_dest`, шаблон `tour.html` |
| 8 | Данные по инфо-турам: даты, условия, фото прошлых поездок | `pages.info`, `info.html` |
| 9 | Тексты о компании (история, команда, фото) | `pages.about`, `about.html` |
| 10 | Вычитка UZ / EN / 中文 носителями | `src/i18n/` |
| 11 | Доступы к домену/хостингу, Search Console, Яндекс Вебмастер | — |

## 6. Следующие шаги (варианты)

1. **Залить в GitHub** (создать пустой репо → push).
2. **Деплой статики** на хостинг клиента (build/ целиком, PHP нужен только для `send.php`) — проверить форму с реальным ботом.
3. **Перенос на WordPress** по ТЗ (основной путь из ТЗ):
   - тема: `header.php` / `footer.php` / `front-page.php` из шаблонов; Tailwind — скомпилированный `app.css` (или config inline в `wp_head` prio 1);
   - CPT: `uz_destination`, `intl_destination`, `tour_offer`, `info_tour`, `review`; таксономия «тип отдыха» (beach/city/nature) для фильтра;
   - ACF: поля направлений (tag, desc, sights repeater, gallery, duration/dates/price), ACF Options Page с явным `menu_slug` — контакты, промоблок, Telegram;
   - мультиязычность: Polylang (или WPML) — 4 языка, отдельные SEO-метаданные (Yoast/Rank Math), hreflang;
   - форма: перенести логику `send.php` в REST-endpoint/обработчик WP (или CF7/Fluent Forms + Telegram-уведомления), сохранить антиспам;
   - Schema.org: тот же набор JSON-LD.
4. Дополнительные страницы/шаблоны по мере появления контента (карточки конкретных туров с ценами, страница отдельного инфо-тура).

## 7. Инструменты (установлены 23.10.2026, профиль пользователя Claude Code)

- **agent-skills** (addyosmani, 25 скиллов) и **скиллы Strix** (9) — `~/.claude/skills`; применены performance-optimization (журнал в `PERF.md`) и 21st-ui-review.
- **context7** — HTTP MCP, подключён (без ключа, лимиты ниже).
- **21st.dev** — CLI `21st` + скиллы; MCP `magic` добавлен, но ждёт ключ: `21st login` или переменная `API_KEY_21ST`.
- **Graphify** — `~/.local/bin/graphify` (venv `~/.venvs/graphify`), граф проекта: `graphify update .` → `graphify-out/` (в .gitignore).
- **Strix CLI** 1.7.0 — `~/.strix/bin/strix`; для скана нужен запущенный Docker и LLM-ключ (`STRIX_LLM`, `LLM_API_KEY`).
- Побочный эффект: прерванный `brew install uv` обновил системный python3 до 3.15 → jinja2 переустановлен (`pip install jinja2 --break-system-packages`).

## 8. Известные нюансы

- В песочнице прошлой сессии Google Fonts были недоступны — скриншоты делались с подменой шрифтов (Playwright route → локальные woff2 из npm `material-symbols`, `@fontsource/montserrat`, `@fontsource/caveat`). На реальном хостинге шрифты грузятся с Google Fonts.
- Иконка в шапке и мобильном меню — inline SVG Telegram (макрос `m.tg()`), остальные — Material Symbols Rounded.
- На мобильных карточки направлений — горизонтальный скролл со snap; на ≥sm — сетка.
- `.htaccess` без правила «добавлять слэш» (было удалено намеренно, Apache и так отдаёт index.html каталога).
