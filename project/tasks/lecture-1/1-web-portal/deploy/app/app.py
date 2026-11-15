#!/usr/bin/env python3
"""«Портал» — демонстрационное веб-задание мини-курса (web).

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
        raise RuntimeError(f"WEB_FLAG_{n} не задан (см. flags.env.defaults)")
    return value


with open("/flag.txt", "w", encoding="utf-8") as fh:
    fh.write(flag(6) + "\n")

app.config["AUDIT_NOTE"] = flag(4)


@app.after_request
def add_header(resp: Response) -> Response:
    if request.path == "/":
        resp.headers["X-Lighthouse-Note"] = flag(5)
    return resp


@app.route("/")
def index() -> str:
    comment = base64.b64encode(flag(1).encode()).decode()
    return render_template("index.html", comment=comment)


@app.route("/js/app.js")
def app_js() -> Response:
    codes = ", ".join(str(b) for b in flag(2).encode())
    return Response(render_template("app.js", codes=codes), mimetype="application/javascript")


@app.route("/robots.txt")
def robots() -> Response:
    return Response("User-agent: *\nDisallow: /api/secret\n", mimetype="text/plain")


@app.route("/api/secret", methods=["GET", "POST"])
def secret() -> Response:
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
    name = request.args.get("name") or "гость"
    page = (
        '{% extends "base.html" %}{% block content %}\n'
        f'    <p class="greeting">Здравствуйте, {name}!</p>\n'
        '    <p><a href="/">← На главную</a></p>\n'
        "{% endblock %}"
    )
    return render_template_string(page)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
