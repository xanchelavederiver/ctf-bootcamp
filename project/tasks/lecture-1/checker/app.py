#!/usr/bin/env python3
"""Простой проверщик флагов короткого CTF (запускает только лектор).

Одно поле ввода. Знает боевые флаги (из flags.real.env и из task.yml файловых заданий)
и показывает по каждому заданию, сколько всего флагов спрятано (включая скрытые) — но
не называет их. Ответ по умолчанию для флага локальной копии отличается от «неверно»,
чтобы студент понимал: локальный флаг на боевом стенде не засчитывается.

Коллекция заданий монтируется только на чтение в /collection.
Без учётных записей и турнирной таблицы; сравнение — в постоянное время.
"""

from __future__ import annotations

import hmac
import os
import time
from collections import defaultdict, deque
from pathlib import Path

import yaml
from flask import Flask, Response, request

COLLECTION = Path(os.environ.get("COLLECTION_DIR", "/collection"))
app = Flask(__name__)


def read_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def all_flags(meta: dict) -> list[dict]:
    flags = []
    if meta.get("flag"):
        flags.append({"id": 1, "flag": str(meta["flag"]), "env": meta.get("flag_env"),
                      "hidden": False})
    for item in meta.get("flags") or []:
        flags.append({"id": item.get("id"), "flag": str(item.get("flag", "")),
                      "env": item.get("env"), "hidden": bool(item.get("hidden"))})
    return flags


def load_tables():
    """real[value] -> (task, id);  default[value] -> task;  counts[task] -> n; titles."""
    real_env = read_env_file(COLLECTION / "flags.real.env")
    real: dict[str, tuple[str, int]] = {}
    default: dict[str, str] = {}
    counts: dict[str, int] = {}
    titles: dict[str, str] = {}
    for task_yml in sorted(COLLECTION.glob("*/task.yml")):
        meta = yaml.safe_load(task_yml.read_text(encoding="utf-8")) or {}
        task = str(meta.get("id") or task_yml.parent.name)
        titles[task] = str(meta.get("name") or task)
        flags = all_flags(meta)
        counts[task] = len(flags)
        for f in flags:
            if f["env"]:
                real_value = real_env.get(f["env"], f["flag"])
                default[f["flag"]] = task            # значение из task.yml — это умолчание
            else:
                real_value = f["flag"]               # файловый флаг: значение и есть боевое
            real[real_value] = (task, f["id"])
    return real, default, counts, titles


REAL, DEFAULT, COUNTS, TITLES = load_tables()

# Примитивное ограничение частоты: не более 30 попыток за 60 с с одного адреса.
_hits: dict[str, deque] = defaultdict(deque)


def rate_limited(addr: str) -> bool:
    now = time.time()
    q = _hits[addr]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= 30:
        return True
    q.append(now)
    return False


def match_real(submission: str):
    found = None
    # Проверяем все флаги (постоянное время, без раннего выхода).
    for value, where in REAL.items():
        if hmac.compare_digest(submission, value):
            found = where
    return found


def page(message: str = "", kind: str = "") -> str:
    rows = "".join(
        f"<tr><td>{TITLES[t]}</td><td><code>{t}</code></td><td>{COUNTS[t]}</td></tr>"
        for t in sorted(COUNTS)
    )
    color = {"ok": "#0a6", "local": "#b70", "no": "#c33"}.get(kind, "#555")
    msg = f'<p style="font-weight:600;color:{color}">{message}</p>' if message else ""
    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<title>Проверка флагов — короткий CTF</title>
<style>body{{font-family:system-ui,sans-serif;max-width:40rem;margin:3rem auto;padding:0 1rem}}
input[type=text]{{width:100%;padding:.5rem;font-family:monospace}}
table{{border-collapse:collapse;margin-top:2rem;width:100%}}
td,th{{border:1px solid #ccd;padding:.3rem .6rem;text-align:left}}
code{{background:#eef2f5;padding:.1rem .3rem}}</style></head><body>
<h1>Проверка флагов</h1>
<form method="post"><input type="text" name="flag" placeholder="BootCTF{{...}}" autofocus>
<button type="submit">Проверить</button></form>
{msg}
<p>Сколько флагов спрятано в каждом задании (включая те, что не разбираются на лекции):</p>
<table><tr><th>Задание</th><th>id</th><th>Всего флагов</th></tr>{rows}</table>
<p style="color:#889;font-size:.85rem">Ищите дальше дома — на лекции находят не всё.</p>
</body></html>"""


@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    if request.method == "GET":
        return Response(page(), mimetype="text/html")
    addr = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
    if rate_limited(addr):
        return Response(page("Слишком часто. Подождите немного.", "no"), status=429, mimetype="text/html")
    submission = (request.form.get("flag") or "").strip()
    if not submission:
        return Response(page("Введите флаг.", "no"), mimetype="text/html")
    hit = match_real(submission)
    if hit:
        task, fid = hit
        return Response(page(f"Верно — задание «{TITLES[task]}» ({task}), флаг {fid}.", "ok"),
                        mimetype="text/html")
    if submission in DEFAULT:
        return Response(page("Это флаг локальной копии: на боевом стенде флаг другой.", "local"),
                        mimetype="text/html")
    return Response(page("Неверно.", "no"), mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
