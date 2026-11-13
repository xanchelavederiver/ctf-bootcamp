#!/usr/bin/env python3
"""«Портал» — демонстрационное веб-задание мини-курса (web).

Шесть флагов, по одному приёму на каждый:
  1. base64 в HTML-комментарии главной страницы    (просмотр исходника)
  2. массив кодов символов в app.js, хоткей Ctrl+Shift+Y  (чтение JS)
  3. /api/secret: нужен POST с заголовком X-Audit-Token  (curl)
  4. /hello?name=... — SSTI, флаг в app.config          (шаблонная инъекция)
  5. заголовок ответа X-Lighthouse-Note на главной     (скрытый; curl -i)
  6. /flag.txt в контейнере, читается только через SSTI → выполнение кода (скрытый)

Флаги читаются из окружения при старте и нигде не хранятся в коде открытым текстом.
"""

from __future__ import annotations

import base64
import os

from flask import Flask, Response, abort, render_template, render_template_string, request

app = Flask(__name__)


def flag(n: int) -> str:
    value = os.environ.get(f"WEB_FLAG_{n}")
    if not value:
        raise RuntimeError(f"WEB_FLAG_{n} не задан (см. deploy/.env)")
    return value


# Флаг 6 кладётся в файл; добраться до него можно только выполнив код через SSTI (флаг 4).
with open("/flag.txt", "w", encoding="utf-8") as fh:
    fh.write(flag(6) + "\n")

# Флаг 4 — в конфигурации приложения; его показывает {{ config }} в SSTI.
app.config["AUDIT_NOTE"] = flag(4)


@app.after_request
def add_header(resp: Response) -> Response:
    # Флаг 5 (скрытый): нестандартный заголовок ответа только на главной странице.
    if request.path == "/":
        resp.headers["X-Lighthouse-Note"] = flag(5)
    return resp


@app.route("/")
def index() -> str:
    # Флаг 1: base64 в HTML-комментарии (виден в исходнике страницы).
    comment = base64.b64encode(flag(1).encode()).decode()
    return render_template("index.html", comment=comment)


@app.route("/js/app.js")
def app_js() -> Response:
    # Флаг 2: коды символов; показываются по Ctrl+Shift+Y.
    codes = ", ".join(str(b) for b in flag(2).encode())
    return Response(render_template("app.js", codes=codes), mimetype="application/javascript")


@app.route("/robots.txt")
def robots() -> Response:
    return Response("User-agent: *\nDisallow: /api/secret\n", mimetype="text/plain")


@app.route("/api/secret", methods=["GET", "POST"])
def secret() -> Response:
    # Флаг 3: POST с заголовком X-Audit-Token. GET отклоняется (405).
    if request.method == "GET":
        abort(405)
    if request.headers.get("X-Audit-Token") != "lighthouse":
        return Response(
            '{"error": "нужен заголовок X-Audit-Token (см. памятку аудитора)"}\n',
            status=403,
            mimetype="application/json",
        )
    return Response(f'{{"flag": "{flag(3)}"}}\n', mimetype="application/json")


@app.route("/hello")
def hello() -> str:
    # Флаг 4: имя подставляется в шаблон без экранирования — классическая SSTI.
    name = request.args.get("name", "гость")
    return render_template_string(f"<p>Здравствуйте, {name}!</p>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
