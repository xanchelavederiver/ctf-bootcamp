#!/usr/bin/env python3
"""Сторож сервиса: запускает переданную команду (gunicorn) и опрашивает приложение.

Если приложение несколько раз подряд не ответило, сторож завершает контейнер с
ненулевым кодом, и Docker перезапускает его по политике restart. Так зависший
сервис восстанавливается сам, без доступа к Docker API.
"""

from __future__ import annotations

import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8001/"
INTERVAL = 5   # секунд между проверками
TIMEOUT = 3    # секунд на ответ
FAILS = 3      # подряд неудачных проверок до перезапуска


def log(msg: str) -> None:
    print(f"watchdog: {msg}", file=sys.stderr, flush=True)


def alive() -> bool:
    try:
        urllib.request.urlopen(URL, timeout=TIMEOUT).close()
    except urllib.error.HTTPError:
        return True  # любой HTTP-ответ означает, что сервер отвечает
    except Exception as exc:  # noqa: BLE001
        log(f"нет ответа: {exc}")
        return False
    return True


def main() -> int:
    proc = subprocess.Popen(sys.argv[1:])
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda s, _f: proc.send_signal(s))

    fails = 0
    while proc.poll() is None:
        time.sleep(INTERVAL)
        if proc.poll() is not None:
            break
        fails = 0 if alive() else fails + 1
        if fails >= FAILS:
            log(f"сервис не отвечает {FAILS} проверки подряд — перезапуск контейнера")
            proc.kill()
            return 1
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
