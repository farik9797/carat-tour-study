<?php
/**
 * Carat Tour & Study — обработчик заявок.
 * Отправляет заявку в Telegram (бот) и/или на email. Персональные данные на сервере НЕ сохраняются.
 *
 * Настройка:
 *  1. Создать бота через @BotFather → токен в TG_BOT_TOKEN.
 *  2. Добавить бота в чат/группу менеджеров, узнать chat_id (например, через @getidsbot) → TG_CHAT_ID.
 *  3. MAIL_TO — email ответственного сотрудника (пусто — письмо не отправляется).
 *  Лучше задать значения через переменные окружения хостинга, а не в файле.
 */
declare(strict_types=1);

const TG_BOT_TOKEN = '';                  // getenv('CARAT_TG_TOKEN') ниже имеет приоритет
const TG_CHAT_ID   = '';                  // getenv('CARAT_TG_CHAT')
const MAIL_TO      = '';                  // getenv('CARAT_MAIL_TO'), например info@carattourandstudy.uz
const MAIL_FROM    = 'noreply@carattourandstudy.uz';
const MIN_FILL_SEC = 3;                   // антиспам: форма заполнена быстрее — бот
const RATE_LIMIT   = 5;                   // заявок с одного IP за RATE_WINDOW
const RATE_WINDOW  = 600;                 // секунд

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

function out(bool $ok, string $error = '', int $code = 200): void {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}
function field(string $k, int $max = 200): string {
    $v = isset($_POST[$k]) && is_string($_POST[$k]) ? trim($_POST[$k]) : '';
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    return mb_substr($v, 0, $max);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(false, 'method', 405);

// Проверка источника (same-origin)
$host = $_SERVER['HTTP_HOST'] ?? '';
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
if ($origin && $host && parse_url($origin, PHP_URL_HOST) !== $host) out(false, 'origin', 403);

// Антиспам: honeypot + время заполнения
if (field('website') !== '') out(true); // молча «успех» для бота
$ts = (int) field('ts', 20);
if ($ts > 0 && (microtime(true) * 1000 - $ts) < MIN_FILL_SEC * 1000) out(false, 'too_fast', 429);

// Rate limit по IP (хэш IP во временном файле, без персональных данных)
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$rlFile = sys_get_temp_dir() . '/carat_rl_' . hash('sha256', $ip . __FILE__);
$hits = array_filter(@json_decode((string) @file_get_contents($rlFile), true) ?: [], fn($t) => $t > time() - RATE_WINDOW);
if (count($hits) >= RATE_LIMIT) out(false, 'rate', 429);
$hits[] = time();
@file_put_contents($rlFile, json_encode(array_values($hits)), LOCK_EX);

// Данные
$name      = field('name', 80);
$contact   = field('contact', 60);
$direction = field('direction', 120);
$typeMap   = ['intl' => 'Международный', 'uz' => 'По Узбекистану', 'info' => 'Информационный'];
$type      = $typeMap[field('tour_type', 10)] ?? '—';
$dates     = field('dates', 80);
$comment   = field('comment', 1000);
$search    = field('search', 200);
$lang      = strtoupper(field('lang', 5));
$page      = filter_var(field('page', 300), FILTER_VALIDATE_URL) ?: '';
$consent   = field('consent', 2) === '1';

if (mb_strlen($name) < 2) out(false, 'name', 422);
$isPhone = preg_match('/^\+?[\d\s\-()]{9,20}$/', $contact) && strlen(preg_replace('/\D/', '', $contact)) >= 9;
$isTg    = preg_match('~^(@|(https?://)?t\.me/)?[A-Za-z][A-Za-z0-9_]{4,31}$~', $contact);
if (!$isPhone && !$isTg) out(false, 'contact', 422);
if (!$consent) out(false, 'consent', 422);

// Сообщение
$lines = [
    '🧳 Новая заявка — Carat Tour & Study',
    '',
    '👤 Имя: ' . $name,
    '📞 Контакт: ' . $contact,
    '📍 Направление: ' . ($direction ?: '—'),
    '🏷 Тип тура: ' . $type,
    '📅 Даты: ' . ($dates ?: '—'),
    '💬 Комментарий: ' . ($comment ?: '—'),
];
if ($search) $lines[] = '🔎 Поиск: ' . $search;
$lines[] = '';
$lines[] = '🌐 ' . $lang . ' · ' . $page;
$lines[] = '🕒 ' . date('d.m.Y H:i');
$text = implode("\n", $lines);

$token = getenv('CARAT_TG_TOKEN') ?: TG_BOT_TOKEN;
$chat  = getenv('CARAT_TG_CHAT') ?: TG_CHAT_ID;
$mail  = getenv('CARAT_MAIL_TO') ?: MAIL_TO;
$sent  = false;

if ($token && $chat) {
    $ch = curl_init("https://api.telegram.org/bot{$token}/sendMessage");
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => http_build_query(['chat_id' => $chat, 'text' => $text, 'disable_web_page_preview' => 'true']),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
    ]);
    $res = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $sent = $res !== false && $code === 200;
}

if ($mail) {
    $subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта: ' . $name) . '?=';
    $headers = "From: Carat Tour <" . MAIL_FROM . ">\r\nContent-Type: text/plain; charset=UTF-8\r\nMIME-Version: 1.0";
    $sent = @mail($mail, $subject, $text, $headers) || $sent;
}

$sent ? out(true) : out(false, 'delivery', 502);
