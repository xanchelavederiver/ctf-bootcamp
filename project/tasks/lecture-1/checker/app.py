#!/usr/bin/env python3
"""Простой проверщик флагов короткого CTF (запускает только лектор).

Одно поле ввода. Знает боевые флаги (из flags.real.env и из task.yml файловых заданий)
и показывает по каждому заданию, сколько всего флагов спрятано (включая скрытые) — но
не называет их. Ответ по умолчанию для флага локальной копии отличается от «неверно»,
чтобы студент понимал: локальный флаг на боевом стенде не засчитывается.

После отправки флага сервер отвечает перенаправлением на главную (Post/Redirect/Get), а
результат проверки передаёт одноразовой cookie: обновление страницы не отправляет флаг
повторно и не показывает прошлый результат.

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
from flask import Flask, Response, redirect, request

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
    """real[value] -> (task, id);  default[value] -> task;  counts[task] -> n; titles; dirs."""
    real_env = read_env_file(COLLECTION / "flags.real.env")
    real: dict[str, tuple[str, int]] = {}
    default: dict[str, str] = {}
    counts: dict[str, int] = {}
    titles: dict[str, str] = {}
    dirs: dict[str, str] = {}
    metas = [(yaml.safe_load(p.read_text(encoding="utf-8")) or {}, p.parent.name)
             for p in COLLECTION.glob("*/task.yml")]
    # Порядок заданий — как на лекции (поле order).
    for meta, dirname in sorted(metas, key=lambda m: (m[0].get("order", 999), m[1])):
        task = str(meta.get("id") or dirname)
        titles[task] = str(meta.get("name") or task)
        dirs[task] = dirname
        flags = all_flags(meta)
        counts[task] = len(flags)
        for f in flags:
            if f["env"]:
                real_value = real_env.get(f["env"], f["flag"])
                default[f["flag"]] = task            # значение из task.yml — это умолчание
            else:
                real_value = f["flag"]               # файловый флаг: значение и есть боевое
            real[real_value] = (task, f["id"])
    return real, default, counts, titles, dirs


REAL, DEFAULT, COUNTS, TITLES, DIRS = load_tables()

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


STYLE = """
:root { --ink: #0f1f2e; --muted: #5d6b7a; --line: #dfe6ec; --accent: #0b7a6b; --accent-dark: #075e53; --navy: #0c2f4a; }
* { box-sizing: border-box; }
html {
  min-height: 100%;
  background:
    radial-gradient(60rem 30rem at 85% -10%, #d7efe9 0%, transparent 60%),
    radial-gradient(50rem 28rem at -10% 20%, #dde9f5 0%, transparent 55%),
    #f3f6f9;
}
body {
  width: min(100% - 2rem, 44rem); margin: 3.5rem auto; padding: 2.25rem 2.5rem;
  font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--ink);
  background: #fff; border: 1px solid var(--line); border-radius: 1rem;
  box-shadow: 0 1px 2px rgba(15, 31, 46, .04), 0 12px 32px rgba(15, 31, 46, .08);
}
h1 {
  display: flex; align-items: center; gap: .7rem; margin: 0 0 1.5rem; padding-bottom: 1.25rem;
  font-size: 1.35rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.3; color: var(--navy);
  border-bottom: 1px solid var(--line);
}
h1::before {
  content: ""; flex: none; width: 2.1rem; height: 2.1rem; border-radius: .6rem;
  background:
    radial-gradient(circle at 50% 38%, #fff 0 16%, transparent 17%),
    linear-gradient(135deg, #12a08c, var(--navy));
  box-shadow: 0 2px 6px rgba(12, 47, 74, .25);
}
p { margin: 0 0 .75rem; }
code {
  font: .875em ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #eef2f6; border: 1px solid var(--line); padding: .1rem .4rem; border-radius: .35rem;
}
form { display: flex; flex-wrap: wrap; gap: .6rem; margin: 0 0 1.25rem; }
input[type=text] {
  flex: 1 1 16rem; min-width: 0; padding: .65rem .9rem; color: inherit;
  font: .95rem ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #fff; border: 1px solid #c5d0da; border-radius: .6rem; outline: none;
  transition: border-color .15s, box-shadow .15s;
}
input[type=text]::placeholder { color: #9aa7b4; }
input[type=text]:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(11, 122, 107, .15); }
button {
  font: inherit; font-weight: 600; color: #fff; padding: .65rem 1.3rem; cursor: pointer;
  background: var(--accent); border: 0; border-radius: .6rem;
  box-shadow: 0 1px 2px rgba(7, 94, 83, .35); transition: background .15s, transform .05s;
}
button:hover { background: var(--accent-dark); }
button:active { transform: translateY(1px); }
.result { margin: 0 0 1.5rem; padding: .8rem 1rem; font-weight: 600; border-left: 3px solid; border-radius: .5rem; }
.result.ok { color: #075e53; background: #e6f4f1; border-color: #0b7a6b; }
.result.local { color: #8a5300; background: #fdf3df; border-color: #d9930d; }
.result.no { color: #a32020; background: #fdecec; border-color: #d64545; }
table { width: 100%; margin-top: 1rem; border-collapse: separate; border-spacing: 0; border: 1px solid var(--line); border-radius: .75rem; overflow: hidden; }
th, td { padding: .65rem 1rem; text-align: left; font-size: .95rem; }
th { font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); background: #f6f8fa; }
td { border-top: 1px solid var(--line); }
td:first-child, th:first-child { width: 3rem; color: var(--muted); }
td:last-child, th:last-child { text-align: right; font-variant-numeric: tabular-nums; }
td:last-child { font-weight: 600; color: var(--navy); }
@media (max-width: 30rem) { body { margin: 1rem auto; padding: 1.5rem 1.25rem; } button { flex: 1 1 100%; } }
"""

RESULT_COOKIE = "check_result"


def result_message(code: str) -> tuple[str, str]:
    """Одноразовый код результата из cookie -> (текст, вид сообщения)."""
    kind, _, rest = code.partition(":")
    if kind == "ok":
        task, _, fid = rest.partition(":")
        if task in TITLES and fid.isdigit():
            return f"Верно — задание «{TITLES[task]}», флаг {fid}.", "ok"
        return "", ""
    return {
        "local": ("Это флаг локальной копии: на боевом стенде флаг другой.", "local"),
        "no": ("Неверно.", "no"),
        "empty": ("Введите флаг.", "no"),
        "rate": ("Слишком часто. Подождите немного.", "no"),
    }.get(kind, ("", ""))


def page(message: str = "", kind: str = "") -> str:
    rows = "".join(
        f"<tr><td>{n}</td><td>{TITLES[t]} <code>{DIRS[t]}</code></td><td>{COUNTS[t]}</td></tr>"
        for n, t in enumerate(COUNTS, 1)
    )
    msg = f'<p class="result {kind}">{message}</p>' if message else ""
    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Проверка флагов — короткий CTF</title>
<style>{STYLE}</style></head><body>
<h1>Проверка флагов</h1>
<form method="post"><input type="text" name="flag" placeholder="BootCTF{{...}}" autocomplete="off" autofocus>
<button type="submit">Проверить</button></form>
{msg}
<p>Сколько флагов спрятано в каждом задании:</p>
<table><tr><th>№</th><th>Задание</th><th>Всего флагов</th></tr>{rows}</table>
</body></html>"""


def check(submission: str, addr: str) -> str:
    """Проверить флаг и вернуть код результата (см. result_message)."""
    if rate_limited(addr):
        return "rate"
    if not submission:
        return "empty"
    hit = match_real(submission)
    if hit:
        task, fid = hit
        return f"ok:{task}:{fid}"
    if submission in DEFAULT:
        return "local"
    return "no"


@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    if request.method == "POST":
        addr = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
        code = check((request.form.get("flag") or "").strip(), addr)
        # Post/Redirect/Get: результат уезжает в одноразовой cookie, страница — обычный GET.
        resp = redirect("/", code=303)
        resp.set_cookie(RESULT_COOKIE, code, max_age=60, httponly=True, samesite="Lax")
        return resp
    message, kind = result_message(request.cookies.get(RESULT_COOKIE, ""))
    resp = Response(page(message, kind), mimetype="text/html")
    resp.headers["Cache-Control"] = "no-store"
    resp.delete_cookie(RESULT_COOKIE)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
