#!/usr/bin/env python3
"""Генерация capture.pcapng: один сеанс пассивного FTP (вход, LIST, RETR двух файлов).

Воспроизводимо и целиком в Docker: сервер и клиент — два контейнера с разными
адресами в отдельной сети (см. ./docker-compose.yml: сервер 10.10.20.5, клиент
10.10.20.23). В контейнере сервера поднимается pyftpdlib, а tcpdump пишет его сетевой
интерфейс; контейнер клиента забирает файлы через ftplib. Затем дамп конвертируется
в pcapng. Побочно создаются notes.txt и backup.zip для стенда.

Запуск (из каталога задания):
  HOST_UID=$(id -u) HOST_GID=$(id -g) \
      docker compose -f src/capture/docker-compose.yml up --build
  docker compose -f src/capture/docker-compose.yml down

Роль контейнера задаётся аргументом: gen.py server | gen.py client.
"""

from __future__ import annotations

import ftplib
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

TASK = Path("/task")
PUBLIC = TASK / "public"
SRV = TASK / "deploy" / "srv"
WORK = Path("/work/ftproot")

USER, PASSWORD = "lighthouse", "Harbor-2026"
ZIP_PASSWORD = "dragon"  # есть в /usr/share/john/password.lst
CTRL_PORT = 21
SYNC_PORT = 9999  # служебный канал «клиент готов / клиент закончил»; в дамп не попадает
SERVER_IP = os.environ.get("SERVER_IP", "10.10.20.5")
PASV_RANGE = (30000, 30009)

FLAG_1 = "BootCTF{ftp_traffic_in_clear}"           # notes.txt (открыто в трафике)
FLAG_2 = "BootCTF{zip_comment_not_encrypted}"      # комментарий архива
FLAG_3 = "BootCTF{zip_password_from_wordlist}"     # flag.txt внутри зашифрованного архива

NOTES = f"""Внутренняя заметка смены (ООО «Северный маяк»).

Резервные копии выгружаются на FTP по расписанию. Канал пока без шифрования —
вынесено в отчёт аудита.

Флаг смены: {FLAG_1}
"""


def build_files() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "notes.txt").write_text(NOTES, encoding="utf-8")
    # Зашифрованный архив: ZipCrypto (zip -P) + незашифрованный комментарий (zip -z).
    flag_txt = Path("/work/flag.txt")
    flag_txt.write_text(FLAG_3 + "\n", encoding="utf-8")
    backup = WORK / "backup.zip"
    if backup.exists():
        backup.unlink()
    subprocess.run(["zip", "-j", "-P", ZIP_PASSWORD, str(backup), str(flag_txt)], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(["zip", str(backup), "-z"], input=FLAG_2 + "\n", text=True, check=True,
                   stdout=subprocess.DEVNULL)
    flag_txt.unlink()


def start_ftp_server() -> None:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer

    authorizer = DummyAuthorizer()
    authorizer.add_user(USER, PASSWORD, str(WORK), perm="elr")
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.masquerade_address = SERVER_IP
    handler.passive_ports = range(PASV_RANGE[0], PASV_RANGE[1] + 1)
    server = FTPServer(("0.0.0.0", CTRL_PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def wait_client_done() -> None:
    """Ждать от клиента слова done по служебному каналу (пустые подключения — проверка готовности)."""
    with socket.create_server(("0.0.0.0", SYNC_PORT)) as sync:
        while True:
            conn, _ = sync.accept()
            with conn:
                if conn.recv(16).strip() == b"done":
                    return


def run_server() -> None:
    build_files()
    pcap = Path("/work/capture.pcap")
    tcpdump = subprocess.Popen(
        ["tcpdump", "-i", "eth0", "-w", str(pcap), "-U",
         f"port {CTRL_PORT} or portrange {PASV_RANGE[0]}-{PASV_RANGE[1]}"],
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    start_ftp_server()
    wait_client_done()
    time.sleep(1.0)
    tcpdump.terminate()
    tcpdump.wait()

    PUBLIC.mkdir(exist_ok=True)
    SRV.mkdir(parents=True, exist_ok=True)
    # Конвертация в pcapng (формат по умолчанию у editcap).
    subprocess.run(["editcap", "-F", "pcapng", str(pcap), str(PUBLIC / "capture.pcapng")], check=True)
    # Те же файлы — в стенд живого FTP-сервера (альтернативный маршрут к ним).
    for name in ("notes.txt", "backup.zip"):
        (SRV / name).write_bytes((WORK / name).read_bytes())
    # Чиним владельца (контейнер работает под root, монтирование — от хоста).
    uid, gid = int(os.environ.get("HOST_UID", "1001")), int(os.environ.get("HOST_GID", "1001"))
    for p in [PUBLIC / "capture.pcapng", SRV / "notes.txt", SRV / "backup.zip"]:
        os.chown(p, uid, gid)
    print(f"capture.pcapng: {(PUBLIC / 'capture.pcapng').stat().st_size} байт")


def run_client() -> None:
    # Ждём готовности сервера по служебному каналу, чтобы в дамп не попали неудачные попытки.
    for _ in range(60):
        try:
            socket.create_connection((SERVER_IP, SYNC_PORT), timeout=2).close()
            break
        except OSError:
            time.sleep(0.5)
    else:
        sys.exit("сервер не поднялся")
    time.sleep(0.5)

    ftp = ftplib.FTP()
    ftp.connect(SERVER_IP, CTRL_PORT, timeout=10)
    ftp.login(USER, PASSWORD)
    ftp.set_pasv(True)
    ftp.retrlines("LIST")
    for name in ("notes.txt", "backup.zip"):
        with open(f"/work/got_{name}", "wb") as fh:
            ftp.retrbinary(f"RETR {name}", fh.write)
    ftp.quit()

    with socket.create_connection((SERVER_IP, SYNC_PORT), timeout=5) as conn:
        conn.sendall(b"done")


if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else ""
    if role == "server":
        run_server()
    elif role == "client":
        run_client()
    else:
        sys.exit("Использование: gen.py server | gen.py client (см. docker-compose.yml)")
