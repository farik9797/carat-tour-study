#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carat Tour & Study — генератор статического многоязычного сайта.

    python3 build.py            # собрать в ./build
    python3 -m http.server -d build 8080   # предпросмотр: http://localhost:8080/ru/

Контент: src/i18n/{uz,ru,en,zh,ar}.py   Шаблоны: src/templates   Ассеты: src/assets
"""
import datetime as dt
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "src", ROOT / "build"

# ---------------------------------------------------------------- НАСТРОЙКИ
SITE = {
    "domain": "https://carattourandstudy.uz",
    "telegram": "https://t.me/carat_tour",
    "telegram_handle": "@carat_tour",          # рабочий чат менеджера
    "telegram_channel": "https://t.me/carat_tournstudy",   # публичный канал (на него ссылается Instagram)
    # Контакты — с действующего сайта caratstudy.uz (23.10.2026); пустой список / None — блок не выводится
    "phones": ["+998 97 409 42 00"],
    "email": "info@caratstudy.uz",
    "address": {"uz": "Toshkent, Cho'ponota, 39", "ru": "Ташкент, Чопон-ата, 39",
                "en": "Tashkent, Cho'ponota, 39", "zh": "塔什干，Cho'ponota 39号",
                "ar": "طشقند، شارع تشوبون أتا، 39"},
    "hours": None,                      # на caratstudy.uz не указаны; пример: {"ru": "Пн–Сб 9:00–18:00", ...}
    "instagram": "https://www.instagram.com/carat_tour/",
    "instagram_handle": "@carat_tour",
}
LANGS = ["uz", "ru", "en", "zh", "ar"]
DEFAULT_LANG = "uz"
HREFLANG = {"uz": "uz", "ru": "ru", "en": "en", "zh": "zh-Hans", "ar": "ar"}
LANG_LABEL = {"uz": "UZ", "ru": "RU", "en": "EN", "zh": "中文", "ar": "عربي"}
LANG_OG = {"uz": "uz_UZ", "ru": "ru_RU", "en": "en_US", "zh": "zh_CN", "ar": "ar_AR"}
RTL = {"ar"}   # языки с письмом справа налево: <html dir="rtl">, вёрстка на логических классах (ms-/pe-/start-/text-end)

SHOW_REVIEWS = False    # True — когда в src/i18n/*.py → reviews будут реальные отзывы клиентов (с их разрешением)
SHOW_DEV_NOTES = False  # True — показать служебные пометки на юр. страницах (для согласования с юристом)

UZ_SLUGS = ["tashkent", "samarkand", "bukhara", "khiva", "chimgan"]
INTL_SLUGS = ["maldives", "turkey", "egypt", "uae", "thailand", "china", "europe"]
INTL_KINDS = {"maldives": ["beach", "nature"], "turkey": ["beach", "city"], "uae": ["beach", "city"],
              "thailand": ["beach", "nature"], "europe": ["city"], "egypt": ["beach", "city"], "china": ["city", "nature"]}
IMG_W = {"hero-home": (1200, 2400)}
IMG_MOBILE = {"hero-home": "hero-home-m"}   # своя картинка для телефона (иначе name-sm)
PROMO = {"href": "uzbekistan/chimgan/", "img": "promo.webp"}
GEO = {"tashkent": (41.3111, 69.2797), "samarkand": (39.6542, 66.9597), "bukhara": (39.7747, 64.4286),
       "khiva": (41.3783, 60.3639), "chimgan": (41.5333, 70.0167)}
VERSION = dt.datetime.now().strftime("%Y%m%d%H%M")
ICONS_TOKEN = "__ICON_NAMES__"
ICON_FONT_RE = re.compile(r"<!--ICON-FONT:([^>]*?)-->")
GOOGLE_ICONS = ("https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:"
                "opsz,wght,FILL,GRAD@20..48,400,0..1,0&icon_names={}&display=block")


# ---------------------------------------------------------------- ЗАГРУЗКА ЯЗЫКОВ
def load_lang(code):
    spec = importlib.util.spec_from_file_location(f"i18n_{code}", SRC / "i18n" / f"{code}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.S


def shape(obj):
    """Структура ключей для сверки языков."""
    if isinstance(obj, dict):
        return {k: shape(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [shape(v) for v in obj]
    return type(obj).__name__


def check_langs(data):
    ref = shape(data["ru"])
    ok = True
    for l in LANGS:
        if shape(data[l]) != ref:
            ok = False
            diff(ref, shape(data[l]), l)
    if not ok:
        sys.exit("✗ Структура переводов не совпадает с ru.py")


def diff(a, b, lang, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                print(f"  [{lang}] ключ {path}.{k}: {'нет в ' + lang if k not in b else 'лишний'}")
            else:
                diff(a[k], b[k], lang, f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            print(f"  [{lang}] {path}: длина списка {len(b)} ≠ {len(a)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, lang, f"{path}[{i}]")
    elif a != b:
        print(f"  [{lang}] {path}: тип {b} ≠ {a}")


# ---------------------------------------------------------------- СТРАНИЦЫ
def page_list(S):
    """(path, template, section, extra-context)"""
    P = S["pages"]
    pages = [
        ("", "home.html", "home", dict(meta_title=S["home"]["meta_title"], meta_desc=S["home"]["meta_desc"],
                                       preload_img="hero-home.webp", lead=True)),
        ("uzbekistan/", "uz_list.html", "uz", dict(P=P["uz"], meta_title=P["uz"]["meta_title"], preload_img="hero-samarkand.webp",
                                                     meta_desc=P["uz"]["meta_desc"], lead=True,
                                                     crumbs=[P["uz"]["h1"]])),
    ]
    for d in uz_list(S):
        pages.append((f"uzbekistan/{d['slug']}/", "dest.html", "uz", dict(
            P=P["dest"], D=d, lead=True, og_image=f"{d['slug']}.webp", preload_img=f"{d['slug']}.webp",
            meta_title=P["dest"]["meta_title"].format(name=d["name"]),
            meta_desc=cut(d["desc"]), crumbs=[S["nav"]["uz"], d["name"]])))
    pages.append(("international/", "intl_list.html", "intl", dict(
        P=P["intl"], meta_title=P["intl"]["meta_title"], meta_desc=P["intl"]["meta_desc"], lead=True,
        crumbs=[P["intl"]["h1"]], preload_img="europe.webp")))
    for d in intl_list(S):
        pages.append((f"international/{d['slug']}/", "tour.html", "intl", dict(
            P=P["tour"], D=d, lead=True, og_image=f"{d['slug']}.webp", preload_img=f"{d['slug']}.webp",
            meta_title=P["tour"]["meta_title"].format(name=d["name"]),
            meta_desc=cut(d["desc"]), crumbs=[S["nav"]["intl"], d["name"]])))
    pages += [
        ("info-tours/", "info.html", "info", dict(P=P["info"], meta_title=P["info"]["meta_title"],
                                                  meta_desc=P["info"]["meta_desc"], lead=True,
                                                  crumbs=[P["info"]["h1"]], preload_img="infotour.webp",
                                                  og_image="infotour.webp")),
        ("about/", "about.html", "about", dict(P=P["about"], meta_title=P["about"]["meta_title"],
                                               meta_desc=P["about"]["meta_desc"], lead=True, preload_img="bukhara.webp",
                                               crumbs=[P["about"]["h1"]])),
        ("contacts/", "contacts.html", "contacts", dict(P=P["contacts"], meta_title=P["contacts"]["meta_title"],
                                                        meta_desc=P["contacts"]["meta_desc"], lead=True, preload_img="tashkent.webp",
                                                        crumbs=[P["contacts"]["h1"]])),
        ("privacy/", "legal.html", "legal", dict(P=P["privacy"], meta_title=P["privacy"]["meta_title"],
                                                 meta_desc=cut(P["privacy"]["body"][0][1]), crumbs=[P["privacy"]["h1"]])),
        ("consent/", "legal.html", "legal", dict(P=P["consent"], meta_title=P["consent"]["meta_title"],
                                                 meta_desc=cut(P["consent"]["body"][0][1]), crumbs=[P["consent"]["h1"]])),
        ("thanks/", "thanks.html", "thanks", dict(P=P["thanks"], meta_title=P["thanks"]["meta_title"],
                                                  meta_desc="", noindex=True, icon_name="check_circle")),
    ]
    return pages


def uz_list(S):
    return [dict(slug=s, **S["uz_dest"][s]) for s in UZ_SLUGS]


def intl_list(S):
    return [dict(slug=s, kinds=INTL_KINDS[s], **S["intl_dest"][s]) for s in INTL_SLUGS]


def cut(text, n=158):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0].rstrip(",.;:—–") + "…"


def abs_url(lang, path):
    return f"{SITE['domain']}/{lang}/{path}"


# ---------------------------------------------------------------- JSON-LD
def jsonld_for(S, L, path, section, ctx):
    org = {
        "@context": "https://schema.org", "@type": "TravelAgency", "@id": f"{SITE['domain']}/#agency",
        "name": "Carat Tour & Study", "url": abs_url(L, ""), "logo": f"{SITE['domain']}/assets/img/logo.webp",
        "image": f"{SITE['domain']}/assets/img/hero-samarkand.webp", "description": S["footer"]["about"],
        "sameAs": [SITE["telegram"]] + [SITE[k] for k in ("telegram_channel", "instagram") if SITE.get(k)], "areaServed": ["UZ", "Worldwide"],
        "availableLanguage": LANGS,
    }
    if SITE["phones"]:
        org["telephone"] = SITE["phones"][0]
    if SITE["email"]:
        org["email"] = SITE["email"]
    if SITE["address"] and SITE["address"].get(L):
        org["address"] = {"@type": "PostalAddress", "streetAddress": SITE["address"][L], "addressCountry": "UZ"}
    out = []
    if section == "home":
        out.append(org)
        out.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Carat Tour & Study",
                    "url": abs_url(L, ""), "inLanguage": HREFLANG[L], "publisher": {"@id": org["@id"]}})
        return out
    if section == "contacts":
        out.append(org)
    crumbs = ctx.get("crumbs") or []
    if crumbs:
        items = [{"@type": "ListItem", "position": 1, "name": S["common"]["home_crumb"], "item": abs_url(L, "")}]
        parts = path.strip("/").split("/")
        for i, name in enumerate(crumbs):
            sub = "/".join(parts[: i + 1]) + "/"
            items.append({"@type": "ListItem", "position": i + 2, "name": name, "item": abs_url(L, sub)})
        out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    D = ctx.get("D")
    if D:
        dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": D["name"],
                "description": D["desc"], "url": abs_url(L, path),
                "image": f"{SITE['domain']}/assets/img/{D['slug']}.webp", "inLanguage": HREFLANG[L]}
        if "sights" in D:
            dest["containedInPlace"] = {"@type": "Country", "name": "Uzbekistan"}
            dest["includesAttraction"] = [{"@type": "TouristAttraction", "name": s[0], "description": s[1]} for s in D["sights"]]
            if D["slug"] in GEO:
                lat, lng = GEO[D["slug"]]
                dest["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
        out.append(dest)
    return out


# ---------------------------------------------------------------- СБОРКА
def main():
    data = {l: load_lang(l) for l in LANGS}
    check_langs(data)

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copytree(SRC / "assets" / "img", OUT / "assets" / "img")
    shutil.copytree(SRC / "assets" / "js", OUT / "assets" / "js")
    for f in (SRC / "root").iterdir():
        shutil.copy(f, OUT / f.name)

    env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    base_ctx = dict(SITE=SITE, LANGS=LANGS, DEFAULT_LANG=DEFAULT_LANG, HREFLANG=HREFLANG, LANG_LABEL=LANG_LABEL,
                    LANG_OG=LANG_OG, RTL=RTL, YEAR=dt.date.today().year, VERSION=VERSION, ICON_NAMES=ICONS_TOKEN,
                    PROMO=PROMO, IMG_W=IMG_W, IMG_MOBILE=IMG_MOBILE, SHOW_DEV_NOTES=SHOW_DEV_NOTES, abs_url=abs_url)

    rendered = {}
    sitemap = []
    for L in LANGS:
        S = data[L]
        for path, tpl, section, extra in page_list(S):
            rendered[f"{L}/{path}index.html"] = render(env, base_ctx, S, L, path, tpl, section, extra)
            if not extra.get("noindex"):
                sitemap.append((L, path))

    # 404 (корень; ссылки от <base>, см. root_base в base.html)
    S = data[DEFAULT_LANG]
    e = S["pages"]["e404"]
    rendered["404.html"] = render(env, base_ctx, S, DEFAULT_LANG, "", "thanks.html", "e404",
                                  dict(P=e, meta_title=e["meta_title"], meta_desc="", noindex=True,
                                       icon_name="explore_off", show_langs=True), root_abs=True)

    # Иконки Material Symbols — только используемые (сабсет шрифта)
    icons = set()
    for html in rendered.values():
        icons |= set(re.findall(r'material-symbols-rounded[^"]*"[^>]*>([a-z0-9_]+)<', html))
    icon_param = ",".join(sorted(icons))
    font = icon_font(icon_param)
    shutil.copytree(SRC / "assets" / "fonts", OUT / "assets" / "fonts")
    for rel, html in rendered.items():
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        html = ICON_FONT_RE.sub(lambda mm: icon_font_head(font, mm.group(1), icon_param), html)
        p.write_text(html.replace(ICONS_TOKEN, icon_param), encoding="utf-8")

    write_root_index()
    write_sitemap(sitemap)
    write_robots()
    build_css()
    print(f"✓ {len(rendered)} страниц, {len(icons)} иконок → {OUT}")


def render(env, base_ctx, S, L, path, tpl, section, extra, root_abs=False):
    # root_abs (404): ссылки относительные от <base> — "/" на домене, /<repo>/ на GitHub Pages (base.html)
    depth = 0 if root_abs else len(f"{L}/{path}".strip("/").split("/"))
    prefix = "../" * depth

    def url(p):
        if p.startswith("#"):
            return p
        return f"{prefix}{L}/{p}"

    def lang_url(l):
        return f"{prefix}{l}/{path}"

    def asset(p):
        return f"{prefix}assets/{p}"

    ctx = dict(base_ctx)
    ctx.update(S=S, L=L, path=path, section=section, url=url, lang_url=lang_url, asset=asset,
               rel_root=prefix, UZ=uz_list(S), INTL=intl_list(S),
               REVIEWS=S["reviews"] if SHOW_REVIEWS else [],
               meta_desc="", noindex=False, og_image=None, preload_img=None, show_langs=False,
               icon_name="check_circle", D=None, P=None, root_base=root_abs)
    ctx.update(extra)
    ctx["cta_href"] = "#lead" if extra.get("lead") else url("contacts/") + "#lead"
    ctx["jsonld"] = [] if ctx["noindex"] else jsonld_for(S, L, path, section, ctx)
    ctx["js_i18n"] = {"sending": S["lead"]["sending"], "submit": S["lead"]["submit"],
                      "search_note": S["lead"]["search_note"], "error": S["lead"]["error"]}
    return env.get_template(tpl).render(**ctx)


def write_root_index():
    """Корень: определение языка браузера → /xx/. Без JS — ссылки на все версии."""
    links = "".join(f'<a href="{l}/" hreflang="{HREFLANG[l]}">{LANG_LABEL[l]}</a> ' for l in LANGS)
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{abs_url(l, "")}">' for l in LANGS)
    html = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Carat Tour &amp; Study</title><meta name="robots" content="noindex, follow">
<link rel="canonical" href="{abs_url(DEFAULT_LANG, '')}">{alts}
<link rel="alternate" hreflang="x-default" href="{abs_url(DEFAULT_LANG, '')}">
<script>(function(){{var s={json.dumps(LANGS)},l=(navigator.languages||[navigator.language||""]),t="{DEFAULT_LANG}";
for(var i=0;i<l.length;i++){{var c=(l[i]||"").slice(0,2).toLowerCase();if(s.indexOf(c)>-1){{t=c;break}}}}
try{{var m=localStorage.getItem("carat_lang");if(s.indexOf(m)>-1)t=m}}catch(e){{}}location.replace(t+"/");}})();</script>
<noscript><meta http-equiv="refresh" content="0; url={DEFAULT_LANG}/"></noscript>
<style>body{{font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0;color:#0B2A7A}}a{{margin:0 .4rem;color:#0B2A7A;font-weight:700}}</style>
</head><body><p>Carat Tour &amp; Study — {links}</p></body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_sitemap(entries):
    today = dt.date.today().isoformat()
    paths = sorted({p for _, p in entries}, key=lambda x: (x.count("/"), x))
    rows = []
    for p in paths:
        for l in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG[a]}" href="{escape(abs_url(a, p))}"/>' for a in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{escape(abs_url(DEFAULT_LANG, p))}"/>'
            prio = "1.0" if p == "" else ("0.8" if p.count("/") == 1 and p not in ("privacy/", "consent/") else "0.6")
            if p in ("privacy/", "consent/"):
                prio = "0.2"
            rows.append(f"<url><loc>{escape(abs_url(l, p))}</loc><lastmod>{today}</lastmod><priority>{prio}</priority>{alts}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    (OUT / "sitemap.xml").write_text(xml, encoding="utf-8")


def icon_font(names):
    """Подмножество Material Symbols (только используемые иконки) — скачивается один раз и хранится
    в src/assets/fonts/ms-<hash>.woff2, чтобы сайт не ходил на Google Fonts. None — нет сети и кэша."""
    path = SRC / "assets" / "fonts" / f"ms-{hashlib.sha1(names.encode()).hexdigest()[:10]}.woff2"
    if not path.exists():
        try:
            ua = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
            css = urllib.request.urlopen(urllib.request.Request(GOOGLE_ICONS.format(names), headers=ua), timeout=20).read().decode()
            url = re.search(r"url\((https://[^)]+)\)", css).group(1)
            data = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=20).read()
        except Exception as e:  # noqa: BLE001 — сборка не должна падать без сети
            print(f"! шрифт иконок не скачан ({e}) — подключаю с Google Fonts")
            return None
        for old in path.parent.glob("ms-*.woff2"):
            old.unlink()
        path.write_bytes(data)
    return path.name


def icon_font_head(font, prefix, names):
    if not font:
        return f'<link rel="stylesheet" href="{GOOGLE_ICONS.format(names)}">'
    return ("<style>@font-face{font-family:'Material Symbols Rounded';font-style:normal;font-weight:400;"
            f"font-display:block;src:url({prefix}{font}) format('woff2')}}</style>")


def write_robots():
    txt = (f"User-agent: *\nAllow: /\nDisallow: /send.php\n" +
           "".join(f"Disallow: /{l}/thanks/\n" for l in LANGS) +
           f"\nSitemap: {SITE['domain']}/sitemap.xml\nHost: {SITE['domain']}\n")
    (OUT / "robots.txt").write_text(txt, encoding="utf-8")


def build_css():
    cmd = ["npx", "tailwindcss", "-c", str(ROOT / "tailwind.config.js"), "-i", str(SRC / "assets/css/input.css"),
           "-o", str(OUT / "assets/css/app.css"), "--minify"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("✗ Tailwind: " + r.stderr)


if __name__ == "__main__":
    main()
