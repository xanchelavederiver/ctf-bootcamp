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
<style>body{{font-family:system-ui,sans-serif;max-width:44rem;margin:3rem auto;padding:0 1rem}}
code{{background:#eef2f5;padding:.1rem .3rem;border-radius:.2rem}}
form{{margin:1.5rem 0}} label{{display:block;margin-bottom:.4rem}}
input[type=text]{{font:inherit;padding:.35rem .5rem;border:1px solid #9ab;border-radius:.25rem;width:24rem;max-width:65%}}
button{{font:inherit;padding:.35rem .9rem;border:0;border-radius:.25rem;background:#084;color:#fff;cursor:pointer}}
.muted{{color:#667}}</style></head><body>
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
