#!/usr/bin/env python3
"""Заливка build/ на хостинг по FTP (без сторонних пакетов).

Доступы — только из переменных окружения, в репозиторий не попадают:
  FTP_HOST=… FTP_USER=… FTP_PASS=… FTP_DIR=carattourandstudy.uz/public_html python3 deploy_ftp.py

Флаги: --dry (только список), --tls (FTPS). Заливает только изменившиеся по размеру файлы,
кроме HTML/PHP/.htaccess — их перезаливает всегда. Лишнее на сервере не удаляет.
"""
import ftplib
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "build"
ALWAYS = {".html", ".php", ".xml", ".txt", ""}


def connect():
    host, user, pw = (os.environ.get(k, "") for k in ("FTP_HOST", "FTP_USER", "FTP_PASS"))
    if not (host and user and pw):
        sys.exit("нужны FTP_HOST, FTP_USER, FTP_PASS (и FTP_DIR)")
    ftp = ftplib.FTP_TLS(host, timeout=25) if "--tls" in sys.argv else ftplib.FTP(host, timeout=25)
    ftp.login(user, pw)
    if isinstance(ftp, ftplib.FTP_TLS):
        ftp.prot_p()
    ftp.encoding = "utf-8"
    return ftp


def remote_sizes(ftp, path):
    """{имя: размер} для файлов в папке; None — если папки нет."""
    try:
        return {name: int(facts.get("size", -1)) for name, facts in ftp.mlsd(path) if facts.get("type") == "file"}
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            return None
        # сервер без MLSD — заливаем всё
        return {}


class Conn:
    """FTP с переподключением: у некоторых хостингов пассивные data-соединения иногда висят."""

    def __init__(self):
        self.ftp = connect()

    def call(self, fn, *a, tries=6):
        for i in range(tries):
            try:
                return fn(self.ftp, *a)
            except (TimeoutError, OSError, EOFError, ftplib.error_temp, ftplib.error_reply, ftplib.error_proto) as e:
                print(f"  ! {type(e).__name__}, повтор {i + 1}")
                time.sleep(2 + i * 2)
                try:
                    self.ftp.close()
                except Exception:
                    pass
                self.ftp = connect()
        raise RuntimeError("не удалось после повторов")


def _stor(ftp, target, path):
    with path.open("rb") as fh:
        ftp.storbinary(f"STOR {target}", fh)


def main():
    dry = "--dry" in sys.argv
    base = os.environ.get("FTP_DIR", "").strip("/")
    ftp = None if dry else Conn()
    sent = skipped = 0
    for d in sorted({p.parent for p in ROOT.rglob("*") if p.is_file()} | {ROOT}):
        rel = d.relative_to(ROOT).as_posix()
        rdir = "/".join(x for x in (base, "" if rel == "." else rel) if x)
        rdir = "/" + rdir if rdir else "/"
        files = sorted(p for p in d.iterdir() if p.is_file())
        if not files:
            continue
        sizes = {}
        if ftp:
            sizes = ftp.call(remote_sizes, rdir)
            if sizes is None:
                cur = ""
                for part in rdir.strip("/").split("/"):
                    cur += "/" + part
                    try:
                        ftp.call(lambda f, c: f.mkd(c), cur)
                    except ftplib.error_perm:
                        pass
                sizes = {}
        for f in files:
            if f.suffix not in ALWAYS and f.name != ".htaccess" and sizes.get(f.name) == f.stat().st_size:
                skipped += 1
                continue
            target = f"{rdir.rstrip('/')}/{f.name}"
            print("→", target)
            if ftp:
                ftp.call(_stor, target, f)
            sent += 1
    if ftp:
        ftp.ftp.quit()
    print(f"✓ залито {sent}, без изменений {skipped}")


if __name__ == "__main__":
    main()
