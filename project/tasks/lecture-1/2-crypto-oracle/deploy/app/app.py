#!/usr/bin/env python3
"""«Шифратор» — демонстрационное крипто-задание мини-курса (crypto).

Флаги и ключ читаются из окружения при старте.
"""

from __future__ import annotations

import base64
import os

from flask import Flask, Response, request

app = Flask(__name__)

SHIFT = 7


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} не задан (см. deploy/flags.env.defaults)")
    return value


FLAG_1 = env("CRYPTO_FLAG_1")
FLAG_2 = env("CRYPTO_FLAG_2")
FLAG_HIDDEN = env("CRYPTO_FLAG_HIDDEN")
KEY = bytes.fromhex(env("CRYPTO_KEY"))


def caesar(text: str, k: int) -> str:
    out = []
    for c in text:
        if "a" <= c <= "z":
            out.append(chr((ord(c) - 97 + k) % 26 + 97))
        elif "A" <= c <= "Z":
            out.append(chr((ord(c) - 65 + k) % 26 + 65))
        else:
            out.append(c)
    return "".join(out)


def encrypt(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


MOTD = caesar(FLAG_1, SHIFT)
ARCHIVE_MSG = (
    f"Spare access flag for the backup channel: {FLAG_HIDDEN}. "
    "Do not disclose the master key to anyone."
).encode()


@app.route("/")
def index() -> Response:
    body = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Шифратор — Северный маяк</title>
<style>
:root {{ --ink: #0f1f2e; --muted: #5d6b7a; --line: #dfe6ec; --accent: #0b7a6b; --accent-dark: #075e53; --accent-soft: #e6f4f1; --navy: #0c2f4a; }}
* {{ box-sizing: border-box; }}
html {{
  min-height: 100%;
  background:
    radial-gradient(60rem 30rem at 85% -10%, #d7efe9 0%, transparent 60%),
    radial-gradient(50rem 28rem at -10% 20%, #dde9f5 0%, transparent 55%),
    #f3f6f9;
}}
body {{
  width: min(100% - 2rem, 46rem); margin: 3.5rem auto; padding: 2.25rem 2.5rem;
  font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--ink);
  background: #fff; border: 1px solid var(--line); border-radius: 1rem;
  box-shadow: 0 1px 2px rgba(15, 31, 46, .04), 0 12px 32px rgba(15, 31, 46, .08);
}}
h1 {{
  display: flex; align-items: center; gap: .7rem; margin: 0 0 1.5rem; padding-bottom: 1.25rem;
  font-size: 1.35rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.3; color: var(--navy);
  border-bottom: 1px solid var(--line);
}}
h1::before {{
  content: ""; flex: none; width: 2.1rem; height: 2.1rem; border-radius: .6rem;
  background:
    radial-gradient(circle at 50% 38%, #fff 0 16%, transparent 17%),
    linear-gradient(135deg, #12a08c, var(--navy));
  box-shadow: 0 2px 6px rgba(12, 47, 74, .25);
}}
p {{ margin: 0 0 .75rem; }}
code {{
  font: .875em ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #eef2f6; border: 1px solid var(--line); padding: .1rem .4rem; border-radius: .35rem;
}}
h1 + p {{
  margin-bottom: 1.75rem; padding: 1rem 1.15rem;
  background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: .5rem;
}}
h1 + p b {{ display: block; margin-bottom: .35rem; font-size: .8rem; letter-spacing: .06em; text-transform: uppercase; color: var(--accent-dark); }}
h1 + p code {{ background: none; border: 0; padding: 0; font-size: 1rem; color: var(--navy); overflow-wrap: anywhere; }}
ul {{ list-style: none; margin: 0 0 1.75rem; padding: 0; border: 1px solid var(--line); border-radius: .75rem; }}
li {{ padding: .75rem 1rem; font-size: .95rem; }}
li + li {{ border-top: 1px solid var(--line); }}
li > code:first-child {{ margin-right: .25rem; font-weight: 600; color: var(--navy); background: #e8eef5; border-color: #d3deea; }}
form {{ display: flex; flex-wrap: wrap; gap: .6rem; margin: 0 0 1.5rem; }}
label {{ flex-basis: 100%; font-weight: 650; color: var(--navy); }}
input[type=text] {{
  flex: 1 1 16rem; min-width: 0; padding: .65rem .9rem; color: inherit;
  font: .95rem ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #fff; border: 1px solid #c5d0da; border-radius: .6rem; outline: none;
  transition: border-color .15s, box-shadow .15s;
}}
input[type=text]::placeholder {{ color: #9aa7b4; }}
input[type=text]:focus {{ border-color: var(--accent); box-shadow: 0 0 0 4px rgba(11, 122, 107, .15); }}
button {{
  font: inherit; font-weight: 600; color: #fff; padding: .65rem 1.3rem; cursor: pointer;
  background: var(--accent); border: 0; border-radius: .6rem;
  box-shadow: 0 1px 2px rgba(7, 94, 83, .35); transition: background .15s, transform .05s;
}}
button:hover {{ background: var(--accent-dark); }}
button:active {{ transform: translateY(1px); }}
.muted {{ margin: 0; padding-top: 1.1rem; font-size: .85rem; color: var(--muted); border-top: 1px solid var(--line); }}
@media (max-width: 30rem) {{ body {{ margin: 1rem auto; padding: 1.5rem 1.25rem; }} button {{ flex: 1 1 100%; }} }}
</style></head><body>
<h1>Служба шифрования «Северный маяк»</h1>
<p><b>Сообщение дня:</b> <code>{MOTD}</code></p>
<p>Служебные конечные точки:</p>
<ul>
  <li><code>GET /flag</code> — зашифрованная секретная заметка (base64);</li>
  <li><code>POST /encrypt</code> — зашифровать тем же ключом ваши данные
      (поле <code>data</code>, base64);</li>
  <li><code>GET /archive</code> — резервное сообщение, тот же ключ (base64).</li>
</ul>
<form action="/encrypt" method="post">
  <label for="data">Зашифровать данные (base64):</label>
  <input type="text" id="data" name="data" placeholder="aGVsbG8=" autocomplete="off" required>
  <button type="submit">Зашифровать</button>
</form>
<p class="muted">Ключ хранится только на сервере.</p>
</body></html>"""
    return Response(body, mimetype="text/html")


@app.route("/flag")
def flag() -> Response:
    return Response(base64.b64encode(encrypt(FLAG_2.encode())).decode() + "\n", mimetype="text/plain")


@app.route("/archive")
def archive() -> Response:
    return Response(base64.b64encode(encrypt(ARCHIVE_MSG)).decode() + "\n", mimetype="text/plain")


@app.route("/encrypt", methods=["POST"])
def encrypt_endpoint() -> Response:
    raw = request.form.get("data")
    if raw is None:
        raw = request.get_data().decode("utf-8", "replace").strip()
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception:
        return Response("данные должны быть в base64 (поле data)\n", status=400, mimetype="text/plain")
    result = encrypt(data)
    if result == FLAG_2.encode():
        return Response("служба не выдаёт сам флаг\n", status=403, mimetype="text/plain")
    return Response(base64.b64encode(result).decode() + "\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
