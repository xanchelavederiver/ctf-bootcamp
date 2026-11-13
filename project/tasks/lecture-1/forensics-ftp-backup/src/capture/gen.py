#!/usr/bin/env python3
"""Генерация capture.pcapng: один сеанс пассивного FTP (вход, LIST, RETR двух файлов).

Воспроизводимо и целиком в контейнере (образ из ./Dockerfile): поднимается
pyftpdlib, tcpdump пишет петлевой интерфейс, ftplib-клиент забирает файлы, затем
дамп конвертируется в pcapng. Побочно создаются notes.txt и backup.zip для стенда.

Запуск (из каталога задания):
  docker build -t ctf-forensics-gen src/capture
  docker run --rm --platform linux/amd64 --cap-add NET_RAW --cap-add NET_ADMIN \
      -v "$PWD":/task ctf-forensics-gen python3 /task/src/capture/gen.py
"""

from __future__ import annotations

import ftplib
import os
import subprocess
import time
from multiprocessing import Process
from pathlib import Path

TASK = Path("/task")
PUBLIC = TASK / "public"
SRV = TASK / "deploy" / "srv"
WORK = Path("/work/ftproot")

USER, PASSWORD = "lighthouse", "Harbor-2026"
ZIP_PASSWORD = "dragon"  # есть в /usr/share/john/password.lst
CTRL_PORT = 2121
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


def run_server() -> None:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer

    authorizer = DummyAuthorizer()
    authorizer.add_user(USER, PASSWORD, str(WORK), perm="elr")
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.masquerade_address = "127.0.0.1"
    handler.passive_ports = range(PASV_RANGE[0], PASV_RANGE[1] + 1)
    server = FTPServer(("127.0.0.1", CTRL_PORT), handler)
    server.serve_forever()


def run_client() -> None:
    ftp = ftplib.FTP()
    ftp.connect("127.0.0.1", CTRL_PORT, timeout=10)
    ftp.login(USER, PASSWORD)
    ftp.set_pasv(True)
    ftp.retrlines("LIST")
    for name in ("notes.txt", "backup.zip"):
        with open(f"/work/got_{name}", "wb") as fh:
            ftp.retrbinary(f"RETR {name}", fh.write)
    ftp.quit()


def main() -> None:
    build_files()
    srv = Process(target=run_server, daemon=True)
    srv.start()
    time.sleep(1.5)

    pcap = Path("/work/capture.pcap")
    tcpdump = subprocess.Popen(
        ["tcpdump", "-i", "lo", "-w", str(pcap), "-U",
         f"port {CTRL_PORT} or portrange {PASV_RANGE[0]}-{PASV_RANGE[1]}"],
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    run_client()
    time.sleep(1.0)
    tcpdump.terminate()
    tcpdump.wait()
    srv.terminate()

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


if __name__ == "__main__":
    main()
