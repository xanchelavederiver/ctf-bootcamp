#!/usr/bin/env python3
"""Живой FTP-сервер стенда «Резервная копия».

Отдаёт те же notes.txt и backup.zip, что и в дампе трафика (альтернативный маршрут
к файлам), и дополнительно содержит каталог, в который сеанс из дампа не заходил:
archive/old/handover.txt со скрытым флагом. Учётные данные — как в дампе.

Скрытый флаг читается из окружения (FORENSICS_FLAG_4). Адрес для пассивного
режима задаётся через FTP_PASV_ADDRESS (у лектора — адрес его машины в сети).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

USER, PASSWORD = "lighthouse", "Harbor-2026"  # те же, что видны в дампе трафика
SRC = Path("/opt/srv")                         # notes.txt и backup.zip (зашиты в образ)
ROOT = Path("/tmp/ftproot")                    # рабочий каталог (tmpfs, доступен на запись)


def hidden_flag() -> str:
    value = os.environ.get("FORENSICS_FLAG_4")
    if not value:
        raise RuntimeError("FORENSICS_FLAG_4 не задан (см. deploy/flags.env.defaults)")
    return value


def build_root() -> None:
    old = ROOT / "archive" / "old"
    old.mkdir(parents=True, exist_ok=True)
    for name in ("notes.txt", "backup.zip"):
        shutil.copy2(SRC / name, ROOT / name)
    (old / "handover.txt").write_text(
        "Акт приёма-передачи смены.\n"
        f"Флаг дежурного: {hidden_flag()}\n",
        encoding="utf-8",
    )


def main() -> None:
    build_root()
    authorizer = DummyAuthorizer()
    authorizer.add_user(USER, PASSWORD, str(ROOT), perm="elr")
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.masquerade_address = os.environ.get("FTP_PASV_ADDRESS", "127.0.0.1")
    handler.passive_ports = range(30000, 30010)
    FTPServer(("0.0.0.0", 21), handler).serve_forever()


if __name__ == "__main__":
    main()
