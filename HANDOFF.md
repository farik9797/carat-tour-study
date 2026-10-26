# HANDOFF — Carat Tour & Study (carattourandstudy.uz)

Документ для продолжения работы в новом чате. Обновлён **23.10.2026**.

Приложить к новому чату:
1. **этот файл** `HANDOFF.md`;
2. архив **`carat-tour-study-<дата>.zip`** (исходники + готовый `build/`, без `node_modules` и `.git`) — или просто ссылку на репозиторий;
3. по желанию — исходное ТЗ и макет главной (PNG / 8K JPG).

Первое сообщение в новом чате, например:
> Продолжаем проект Carat Tour & Study. Прочитай HANDOFF.md, склонируй https://github.com/farik9797/carat-tour-study (или распакуй архив), собери проект (`npm install && python3 build.py`) и [задача].

---

## 0. Ссылки

| Что | Где |
|---|---|
| Репозиторий (public) | https://github.com/farik9797/carat-tour-study — ветка `main` |
| Демо (GitHub Pages) | https://farik9797.github.io/carat-tour-study/ — деплоится сам при push в `main` (`.github/workflows/pages.yml`, публикует `build/`) |
| Боевой домен (пока не подключён) | https://carattourandstudy.uz |
| Старый сайт клиента (источник контактов) | https://caratstudy.uz |

На GitHub Pages форма не отправляется (нет PHP) — это только демо вёрстки.

## 1. Клиент и задача

- **Клиент:** туристическое агентство Carat Tour & Study, Ташкент. Директор — Хулкар Юлдашева (Instagram @hulkar_yuldasheva_life).
- **Направления:** международные туры, туры по Узбекистану, инфо-туры (ознакомительные поездки для специалистов отрасли — отдельное направление).
- **Языки:** UZ (по умолчанию, латиница), RU, EN, 中文, العربية (с 25.10, RTL). URL: `/uz/`, `/ru/`, `/en/`, `/zh/`, `/ar/`.
- **ТЗ:** многоязычный корпоративный сайт. ТЗ рекомендовало WordPress, но 26.10.2026 решено обойтись без WP: сайт остаётся статическим. Онлайн-бронирование/оплата — вне базового объёма.
- **Ограничения ТЗ:** не публиковать вымышленные отзывы; цены/даты/программы — только по данным компании; Schema.org — по реальному типу компании.

## 2. Текущее состояние (статический сайт, работает на carattourandstudy.uz)

Путь: **макет → статический HTML (Jinja2 + Tailwind)**. Перенос на WordPress отменён 26.10.2026.

- `build.py` собирает **106 страниц**: 21 × 5 языков + `404.html`; корень `/` определяет язык браузера → `/xx/`.
- **Страницы на язык:** главная; «Туры по Узбекистану» + 5 направлений (tashkent, samarkand, bukhara, khiva, chimgan); «Международные туры» с фильтром (пляж / города / природа) + 7 стран (maldives, turkey, **egypt**, uae, thailand, **china**, europe); инфо-туры; о компании; контакты; privacy; consent; thanks (noindex).
- **Дизайн по макету:** главная — по десктопному макету; мобильная версия и внутренние страницы — адаптация стиля макета (отдельных макетов не было).
- **Попап бронирования** (`partials/booking.html`, нативный `<dialog>`): открывается кнопками `[data-booking]` (шапка, мобильное меню, финальный CTA, «Забронировать» на страницах направлений/туров — с `data-direction`/`data-type`) и поиском «Найти тур» (подставляет направление, даты, туристов → сводка в попапе). Внизу попапа — Telegram, Telegram-канал, Instagram, телефон. Esc / клик по фону закрывают. Без `<dialog>` — ссылка на `#lead`.
- **Все формы минимальные:** имя + телефон/Telegram + согласие. Направление, тип тура, даты, туристы — скрытыми полями (со страницы через `preset_dest`/`preset_type`, из поиска/кнопок через JS). Полная форма осталась: `lead_form(minimal=False)`.
- **Антиспам:** honeypot `website`, время заполнения ≥ 3 с, rate-limit 5 заявок / 10 мин по IP.
- **`send.php`:** Telegram-бот и/или email, данные не хранит. Бронь (`kind=booking`) приходит с заголовком «📌 Бронирование тура», тема письма «Бронирование тура: …», строка «👥 Туристы». Ответ JSON `{ok, error}` → редирект на `/xx/thanks/`.
- **Отзывы скрыты** (`SHOW_REVIEWS = False`) — в макете они вымышленные; вернуть, когда будут реальные с разрешением.
- **SEO:** hreflang + x-default, canonical, OG, `sitemap.xml` с альтернативами, `robots.txt`, JSON-LD (`TravelAgency` с телефоном/email/адресом/`sameAs`, `WebSite`, `BreadcrumbList`, `TouristDestination` с geo), один H1, alt.
- **`.htaccess`:** HTTPS + без www, кэш, gzip, заголовки безопасности, ErrorDocument 404.

### Контакты (в `build.py` → `SITE`)
- Телефон **+998 97 409 42 00**, email **info@caratstudy.uz**, адрес «Ташкент, Чопон-ата, 39» (4 языка) — взяты с caratstudy.uz.
- **Telegram (чат менеджера):** `t.me/carat_tour` — решено пользователем, используется во всех кнопках «Написать в Telegram».
- **Telegram-канал:** `t.me/carat_tournstudy` (273 участника; на него ссылается основной Instagram) — в футере, попапе, мобильном меню, `sameAs`.
- **Instagram:** `@carat_tour` (основной, 2,2 тыс. подписчиков). Есть ещё пустой `@carat_tournstudy` (66 подп., 0 публикаций) — на сайте не используется.
- График работы — нет данных (строка не выводится).

### Проверено 23.10
- Мобильная (375 и 320 px) и десктопная (1024 / 1280 / 1440 / 1920 px) версии всех 86 страниц: без горизонтального скролла, обрезанного текста, наездов в шапке.
- Бургер-меню (было обрезано до 64 px — `backdrop-filter` шапки создавал containing block для `fixed`; меню вынесено из `<header>`), активный пункт, фокус-ловушка, Esc.
- Меню «Туры» (hover / клик / Esc), попап, поиск → попап, фильтр стран, лайтбокс галереи.
- Все ссылки и ассеты (`src`, `srcset`, `imagesrcset`) — битых 0.
- **Не проверено:** реальная отправка `send.php` (на компьютере нет PHP, на GitHub Pages PHP не работает) — проверить на хостинге с токеном бота.

### Скорость (Lighthouse mobile, live GitHub Pages) — подробно в `PERF.md`
- LCP главной 2,1–2,3 с, внутренних 1,4–2,2 с, score 95–100, CLS 0, TBT 0.
- Что дало: свои шрифты вместо Google Fonts (LCP 4,7 → 2,7 с), AVIF для мобильных LCP-картинок, лёгкие логотипы, системные CJK-шрифты для 中文 (было 10,7 с), отдельный вертикальный кадр hero для телефона.
- Бюджет: LCP ≤ 2,5 с, LCP-картинка на мобильном ≤ 40 КБ, никаких внешних CSS в `<head>`.

## 3. Структура проекта

```
carat-tour-study/
├─ build.py               # генератор + НАСТРОЙКИ: SITE (контакты), флаги, слаги, IMG_W/IMG_MOBILE, PROMO, GEO
├─ tailwind.config.js     # палитра, шрифты; corePlugins.container = false (свой .container)
├─ package.json           # tailwindcss@3, @fontsource-variable/montserrat, @fontsource/caveat
├─ HANDOFF.md · README.md · PERF.md (журнал скорости) · IMAGE-SOURCES.md (источники фото)
├─ .github/workflows/pages.yml   # автодеплой build/ на GitHub Pages
├─ src/
│  ├─ i18n/{uz,ru,en,zh}.py      # ВСЕ тексты; ru.py — эталон структуры ключей
│  ├─ templates/
│  │  ├─ base.html               # head (meta, hreflang, OG, JSON-LD, preload LCP, шрифт иконок), попап
│  │  ├─ home, uz_list, dest, intl_list, tour, info, about, contacts, legal, thanks (.html)
│  │  └─ partials/ header (+ мобильное меню вне <header>), footer, final_cta, booking (попап), macros
│  ├─ assets/css/input.css       # @font-face, Tailwind, компоненты (.btn-*, .card, .field, .chip, .social-pill, .booking-dialog…)
│  ├─ assets/js/app.js           # меню, «Туры», попап, поиск, валидация/отправка, фильтр, лайтбокс (ES5/ES2017)
│  ├─ assets/fonts/              # Montserrat (variable), Caveat, ms-<hash>.woff2 (подмножество Material Symbols)
│  ├─ assets/img/                # фото: name.webp + name-sm.webp (+ name-sm.avif для LCP), логотипы, фоны
│  └─ root/ send.php, .htaccess  # копируются в корень build/
└─ build/                 # готовый сайт для заливки на хостинг (коммитится)
```

**Сборка и предпросмотр:**
```bash
npm install
pip install jinja2 --break-system-packages   # python3 3.15 из Homebrew
python3 build.py      # проверка переводов → build/ → CSS → 85 страниц
cd build && php -S localhost:8080            # с формой; без PHP: python3 -m http.server
```
Большие push с картинками: `git -c http.postBuffer=524288000 push` (иначе бывает `index-pack failed`).

**Механики build.py / шаблонов:**
- `check_langs()` — сборка падает, если ключи/длины списков в uz/en/zh не совпадают с ru.py.
- Jinja `StrictUndefined`: необязательное — через `.get()` / `is defined`.
- **Иконки:** имена собираются из HTML → `icon_font()` один раз скачивает подмножество Material Symbols в `src/assets/fonts/ms-<hash>.woff2` (нет сети и кэша → фолбэк на Google CSS). Новая иконка = новый хэш = скачать при сборке.
- **Картинки:** макрос `m.pic(name, alt, cls, sizes, …)` — `name-sm.webp` 800w + `name.webp` 2000w (галереи 700/1400). Шапки страниц (`page_hero`) и hero главной — `<picture>` с AVIF для `max-width: 767px`; preload LCP в `base.html` по `preload_img` (телефон — AVIF, `IMG_MOBILE` для отдельного кадра).
- Ссылки относительные (`url()`, `asset()`, `lang_url()`); 404 — от `<base>` (`/` на домене, `/<repo>/` на GitHub Pages).
- **Новое направление:** слаг в `UZ_SLUGS`/`INTL_SLUGS` (+ `INTL_KINDS`), тексты в `uz_dest`/`intl_dest` всех 5 языков, фото `slug.webp`, `slug-sm.webp`, `slug-sm.avif` (для UZ ещё галерея `slug-1..4`), при необходимости — мета-заголовок списка.
- Флаги: `SHOW_REVIEWS`, `SHOW_DEV_NOTES` (служебные пометки на юр. страницах).

## 4. Дизайн-система

- Цвета: navy `#0B2A7A` (900 `#062958`), accent `#FEAA23` (CTA), sky `#F4F8FD / #E4F0FD / #C9E0FA`, teal `#0FA3B1 / #027F9A`, текст `#1E2B4A`, вторичный `#5B6B8C`.
- Шрифты (свои, без Google): Montserrat variable, Caveat 600 (рукописные акценты). 中文 — системные (PingFang SC / Microsoft YaHei / Noto CJK). العربية — Cairo variable, только арабский сабсет (31 КБ, `unicode-range` — на других языках не грузится).
- `.container` — контент до 1300 px, отступы 16 / 24 / 32 px.
- Hero главной и шапки внутренних страниц — белый фон, фото справа уходит в белый (`bg-hero-fade`); на телефоне фото снизу под белым градиентом. Без фото (privacy/consent) — светлый градиент.
- Мобильная сетка карточек — 2 колонки (последняя на всю ширину или плитка «Все направления»).
- Компоненты: `.btn-accent/-navy/-ghost`, `.section-title`, `.card`, `.field`, `.chip`, `.social-pill`.
- Логотип: `logo.webp` / `logo-white.webp` 360 px (из PNG заказчика), эмблема `cta-emblem.webp`.

## 5. Что нужно от заказчика / не готово

| # | Что | Где менять |
|---|---|---|
| 1 | **Свои фото** команды, офиса, прошлых инфо-туров. Сейчас — Unsplash (`IMAGE-SOURCES.md`) с нейтральными заголовками «Планируем ваше путешествие» / «Как проходят инфо-туры» — после замены вернуть прежние | `src/assets/img/`, `pages.about.team_title`, `pages.info.gallery_title` |
| 2 | Логотип в SVG (сейчас растр из PNG) | `src/assets/img/`, header/footer |
| 3 | Подтвердить контакты, полный адрес, **график работы** | `build.py` → `SITE` |
| 4 | **Токен Telegram-бота, chat_id, email для заявок** — без них форма не работает | `src/root/send.php` или env `CARAT_TG_TOKEN`, `CARAT_TG_CHAT`, `CARAT_MAIL_TO` |
| 5 | Реальные отзывы с разрешением → `SHOW_REVIEWS = True` | `src/i18n/*.py` → `reviews`, `build.py` |
| 6 | Политика и согласие — согласовать с юристом | `pages.privacy/consent` |
| 7 | Финальный список стран, программы, даты, цены (сейчас «по запросу») | `INTL_SLUGS`, `intl_dest`, `tour.html` |
| 8 | Инфо-туры: даты, условия | `pages.info` |
| 9 | Тексты о компании (история, команда) | `pages.about` |
| 10 | **Вычитка UZ / EN / 中文 / العربية** носителями (в т.ч. новые тексты: Египет, Китай, попап, Telegram-канал) | `src/i18n/` |
| 11 | ~~Доступ к хостингу, SSL~~ (25.10); Search Console, Яндекс Вебмастер | — |

## Арабский язык и RTL (25.10.2026)

- `src/i18n/ar.py` — перевод (литературный арабский, **нужна вычитка носителем**). `RTL = {"ar"}` в `build.py` → `<html dir="rtl">`.
- Вёрстка переведена на **логические классы** Tailwind: `ms-/me-/ps-/pe-/start-/end-/text-start/text-end/border-s/border-e` вместо `ml-/mr-/pl-/pr-/left-/right-/text-left/text-right/border-l/border-r`. **В новых шаблонах писать только логические**, иначе в арабской версии поедет.
- Исключения, оставлены физическими сознательно: дропдаун «Туры» (`left-1/2 -translate-x-1/2` — центрирование), слоган на hero главной (`right-8`, как в макете), hero главной — фото не зеркалим (на изразцах арабская каллиграфия), блок текста в RTL уходит на светлую левую часть (`lg:rtl:ms-auto`).
- `rtl-flip` (CSS `scaleX(-1)` при `dir=rtl`): стрелки `arrow_forward/arrow_back/arrow_outward` (макрос `icon` ставит сам) и подложка hero внутренних страниц.
- Телефоны и `@ник` в контактах — в `<bdi dir="ltr">`, иначе «+» и «@» уезжают в конец.
- Межбуквенный интервал (`tracking-*`) для `:lang(ar)` обнулён — он рвёт связки арабских букв.
- Honeypot формы: был `absolute -left-[9999px]` → в RTL давал страницу шириной 10 000 px (горизонтальный скролл). Теперь `sr-only`.

## Появление при прокрутке (25.10.2026)

- `app.js` → блок «Плавное появление»: секции `main > section` кроме первой (hero); прямые дети `.container` (или сам контейнер, если он сетка). В сетках (`grid`/`flex-wrap`, 3+ детей) — каждая карточка с задержкой 80 мс × индекс (до 6).
- Помечается **только то, что ниже первого экрана** при загрузке → LCP и первый экран не трогаются, без мигания. Пропускаются `position: absolute/fixed` и `aria-hidden` (фоны и декор со своей прозрачностью).
- CSS `.reveal` / `.reveal.is-visible` в конце `input.css`, только при `prefers-reduced-motion: no-preference`; только opacity + transform (без CLS). После анимации классы снимаются — ховеры карточек работают как раньше.
- Без JS и в старых браузерах без IntersectionObserver — всё просто видно.
- Тестирование в Claude-браузере: при пакетных действиях вкладка может не рисовать кадры (`requestAnimationFrame` не вызывается) → IO молчит и кажется, что блоки «застряли». Проверять прокруткой со скриншотами.

## Хостинг (с 25.10.2026)

- **Timeweb**, виртуальный хостинг (vh320.timeweb.ru, IP 87.249.38.253). Папка сайта: `/carattourandstudy.uz/public_html`. На этом аккаунте лежат и **другие сайты** — трогать только эту папку.
- FTP: отдельный пользователь `cy62326_claude` (только FTP, SSH закрыт). Пароль у владельца, в репозиторий не кладём.
- **Грабли FTP:** Timeweb режет data-соединения с одного IP (пассивные порты начинают висеть минутами, ответы обрезаются; частые повторы продлевают блок). Пофайловая заливка 209 файлов не проходит. Рабочий способ: по FTP — только крошечный одноразовый приёмник `_ct_recv_<токен>.php`, а zip `build/` — кусками по 900 КБ по HTTPS (`?a=chunk&off=…`, повтор безопасен), затем `?a=finish&size&sha1` — сверка, распаковка, приёмник удаляет архив и себя. Одиночный файл (например `.htaccess`) — обычный STOR. `deploy_ftp.py` годится для мелких обновлений (только изменённые файлы, с повторами).
- **SSL:** Let's Encrypt выпущен клиентом 25.10.2026 (`carattourandstudy.uz` + `www`, до 23.01.2027, продление — автоматически в панели Timeweb). HTTPS и HSTS включены. nginx Timeweb сам редиректит http → https и проксирует в Apache по http (`%{HTTPS}` всегда off — правило `%{HTTPS} off` даёт бесконечный редирект). В `.htaccess` страховочный редирект только при явном `X-Forwarded-Proto: http`.
- Проверено после заливки: все разделы всех языков → 200, 404 → своя страница, `send.php` GET → 405, все `src`/`srcset`/шрифты → 200, www → без www.

## 6. Следующие шаги

1. ~~Деплой на хостинг~~ — **сделано 25.10.2026**, см. «Хостинг» ниже. SSL и HTTPS — сделано 25.10. Осталось: токен бота → проверить реальную отправку заявки и брони.
2. **Безопасность:** ручной аудит `send.php`, `.htaccess` и хостинга сделан 26.10 — критичных проблем нет. CI-скан Strix на каждый PR настроен (`.github/workflows/security.yml`), ждёт секретов `STRIX_LLM` и `LLM_API_KEY`.
3. ~~Перенос на WordPress~~ — **отменён 26.10.2026**, сайт остаётся статическим. Черновик темы убран из репозитория в `~/Projects/carat/_archive/`.
4. Новые страницы по мере контента (конкретные туры с ценами, отдельный инфо-тур).

## 7. Инструменты Claude Code (установлены 23.10, профиль пользователя)

- **agent-skills** (25) и **скиллы Strix** (9) — `~/.claude/skills`; применены performance-optimization и 21st-ui-review.
- **context7** — HTTP MCP, работает без ключа.
- **21st.dev** — CLI `21st` + скиллы; MCP `magic` ждёт ключ (`21st login` или `API_KEY_21ST`).
- **Graphify** — `~/.local/bin/graphify` (venv `~/.venvs/graphify`); `graphify update .` → `graphify-out/` (в .gitignore).
- **Strix CLI** 1.7.0 — `~/.strix/bin/strix` (не в PATH); нужны Docker и LLM-ключ.
- Не ставить через `brew` то, что тянет LLVM (macOS 13 собирает из исходников часами); прерванный `brew install uv` обновил python3 до 3.15.
- Higgsfield: 0 кредитов — генерация/апскейл картинок недоступны.

## 8. Нюансы и грабли

- **`backdrop-filter` на шапке** делает её containing block для `position: fixed` — всё полноэкранное (меню, оверлеи) держать вне `<header>`.
- Mobile-first сетки: в одноколоночных `grid` на телефоне ставить `grid-cols-1` (иначе `auto`-колонка растягивается по самому широкому элементу — так было на 320 px).
- Скриншоты в браузерной панели при эмуляции 1920 px иногда показывают пустую картинку — проверять `naturalWidth`/`currentSrc`, а не только глазами.
- Telegram в шапке/меню — inline SVG (`m.tg()`), Instagram — `m.ig()`, остальное — Material Symbols.
- Unsplash: API закрыт anti-bot (Anubis) — искать через страницу поиска в браузере, качать с `images.unsplash.com` (CDN доступен из curl).
- `.htaccess` без правила «добавлять слэш» — намеренно.
- `app.js` — без `?.` / `??` (поддержка старых браузеров), проверка: `npx acorn --ecma2017`.
