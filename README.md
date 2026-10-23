# Carat Tour & Study — статический сайт (UZ / RU / EN / 中文)

Вёрстка сайта туристического агентства **carattourandstudy.uz** по ТЗ и макету главной.
Готовый сайт — в папке `build/` (можно заливать на хостинг как есть), исходники — в `src/`.

## Состав

| Раздел | URL (для каждого языка `/uz/`, `/ru/`, `/en/`, `/zh/`) |
|---|---|
| Главная | `/{lang}/` |
| Туры по Узбекистану | `/{lang}/uzbekistan/` |
| Направления (5) | `/{lang}/uzbekistan/{tashkent,samarkand,bukhara,khiva,chimgan}/` |
| Международные туры + фильтр | `/{lang}/international/` |
| Страницы туров (5) | `/{lang}/international/{maldives,turkey,uae,thailand,europe}/` |
| Инфо-туры | `/{lang}/info-tours/` |
| О компании | `/{lang}/about/` |
| Контакты | `/{lang}/contacts/` |
| Политика / Согласие | `/{lang}/privacy/`, `/{lang}/consent/` |
| Заявка отправлена | `/{lang}/thanks/` (noindex) |
| 404 | `/404.html` |

Корень `/` определяет язык браузера и перенаправляет на нужную версию (по умолчанию UZ).

## Что реализовано

- 4 языка, переключатель сохраняет текущую страницу; `hreflang` + `x-default`, языковые `canonical`, Open Graph.
- `sitemap.xml` с альтернативными языковыми ссылками, `robots.txt`, JSON-LD: `TravelAgency`, `WebSite`, `BreadcrumbList`, `TouristDestination`.
- Один H1 на страницу, ЧПУ, alt у изображений, lazy-load ниже первого экрана, preload LCP-картинки.
- Tailwind CSS скомпилирован и минифицирован (~50 КБ), иконки Material Symbols грузятся сабсетом только используемых.
- Поиск тура на главной передаёт направление, даты и число туристов в форму заявки (тип тура выставляется автоматически).
- Формы: валидация (имя, телефон/Telegram, согласие), honeypot, проверка времени заполнения, rate-limit по IP.
- `send.php` — отправка заявки в Telegram-бот и/или на email, данные на сервере не сохраняются.
- Фильтр международных направлений, лайтбокс галереи, мобильное меню, `prefers-reduced-motion`.
- `.htaccess`: HTTPS + без www, кэширование, gzip, заголовки безопасности.

## Перед публикацией (заполнить от заказчика)

1. **Фото** — сейчас в `src/assets/img/` вырезки из макета (плейсхолдеры низкого разрешения). Заменить на оригиналы ~1600 px, WebP, имена файлов те же.
2. **Логотип** — `logo.webp` / `logo-white.webp` заменить на SVG/качественный PNG.
3. **Контакты** — `build.py` → `SITE`: `phones`, `email`, `address`, `hours`.
4. **Отзывы** — `DEMO_REVIEWS = False`, пока нет реальных отзывов с разрешением (по ТЗ вымышленные отзывы публиковать нельзя).
5. **Заявки** — в `send.php` (или переменными окружения `CARAT_TG_TOKEN`, `CARAT_TG_CHAT`, `CARAT_MAIL_TO`) указать токен бота, chat_id и email.
6. **Юр. тексты** — согласовать политику и согласие, затем `SHOW_DEV_NOTES = False`.
7. Тексты на UZ / EN / 中文 — вычитать носителем языка.
8. Пустые слоты «Место для фото агентства» (галереи, инфо-туры, команда) заполнить фотографиями.

## Сборка

```bash
npm install                 # Tailwind CLI
pip install jinja2
python3 build.py            # → build/
cd build && php -S localhost:8080    # предпросмотр с рабочей формой
```

Структура: тексты — `src/i18n/{uz,ru,en,zh}.py` (структура ключей сверяется при сборке), шаблоны — `src/templates/`, стили — `src/assets/css/input.css` + `tailwind.config.js`, скрипт — `src/assets/js/app.js`.

Дальше по ТЗ — перенос на WordPress: шаблоны 1:1 переходят в `header.php` / `footer.php` / `front-page.php` и шаблоны CPT (направления, туры, инфо-туры, отзывы), тексты — в ACF/Polylang.
