#!/usr/bin/env python3
"""«Шифратор» — демонстрационное крипто-задание мини-курса (crypto).

Три флага обслуживает сервис (решается одним curl + base64), четвёртый — в
выданном архиве backup.tar (см. задание).

  Флаг 1  GET /          «сообщение дня», зашифровано шифром Цезаря (сдвиг неизвестен)
  Флаг 2  GET /flag      флаг, наложенный XOR с секретным ключом (base64)
          POST /encrypt  XOR произвольных данных тем же ключом; отказывается выдавать
                         результат, равный флагу (это и подсказка)
  Скрытый GET /archive   второе сообщение тем же ключом, длиннее ключа (ключ повторяется)

Флаги и ключ читаются из окружения при старте.
"""

from __future__ import annotations

import base64
import os

from flask import Flask, Response, request

app = Flask(__name__)

SHIFT = 7  # сдвиг шифра Цезаря для «сообщения дня» (участник подбирает перебором 25 вариантов)


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} не задан (см. deploy/flags.env.defaults)")
    return value


FLAG_1 = env("CRYPTO_FLAG_1")
FLAG_2 = env("CRYPTO_FLAG_2")
FLAG_HIDDEN = env("CRYPTO_FLAG_HIDDEN")
KEY = bytes.fromhex(env("CRYPTO_XOR_KEY"))  # секретный ключ XOR (длиннее флага 2)


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


def xor(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


MOTD = caesar(FLAG_1, SHIFT)
# Длиннее ключа: ключ повторяется, и внимательный участник заметит повтор (скрытый флаг).
ARCHIVE_MSG = (
    f"Spare access flag for the backup channel: {FLAG_HIDDEN}. "
    "Do not disclose the master key to anyone."
).encode()


@app.route("/")
def index() -> Response:
    body = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Шифратор — Северный маяк</title>
<style>body{{font-family:system-ui,sans-serif;max-width:44rem;margin:3rem auto;padding:0 1rem}}
code{{background:#eef2f5;padding:.1rem .3rem;border-radius:.2rem}}</style></head><body>
<h1>Служба шифрования «Северный маяк»</h1>
<p><b>Сообщение дня:</b> <code>{MOTD}</code></p>
<p>Служебные конечные точки:</p>
<ul>
  <li><code>GET /flag</code> — секретная заметка, наложенная XOR с ключом (base64);</li>
  <li><code>POST /encrypt</code> — наложить XOR тем же ключом на ваши данные
      (поле <code>data</code>, base64); выдать сам флаг служба отказывается;</li>
  <li><code>GET /archive</code> — резервное сообщение, тот же ключ (base64).</li>
</ul>
<p class="muted">Ключ хранится только на сервере.</p>
</body></html>"""
    return Response(body, mimetype="text/html")


@app.route("/flag")
def flag() -> Response:
    return Response(base64.b64encode(xor(FLAG_2.encode())).decode() + "\n", mimetype="text/plain")


@app.route("/archive")
def archive() -> Response:
    return Response(base64.b64encode(xor(ARCHIVE_MSG)).decode() + "\n", mimetype="text/plain")


@app.route("/encrypt", methods=["POST"])
def encrypt() -> Response:
    raw = request.form.get("data")
    if raw is None:
        raw = request.get_data().decode("utf-8", "replace").strip()
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception:
        return Response("данные должны быть в base64 (поле data)\n", status=400, mimetype="text/plain")
    result = xor(data)
    if result == FLAG_2.encode():
        return Response("служба не выдаёт сам флаг\n", status=403, mimetype="text/plain")
    return Response(base64.b64encode(result).decode() + "\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
