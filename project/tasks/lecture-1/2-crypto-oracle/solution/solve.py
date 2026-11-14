#!/usr/bin/env python3
"""Эталонное решение «Шифратора»: печатает все четыре флага, по одному в строке.

Флаги 1, 2 и 4 — с сервиса (TASK_HOST/TASK_PORT, по умолчанию 127.0.0.1:8002);
флаг 3 — из выданного архива public/backup.tar. Нужна библиотека
pycryptodome.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

HOST = os.environ.get("TASK_HOST", "127.0.0.1")
PORT = os.environ.get("TASK_PORT", "8002")
BASE = f"http://{HOST}:{PORT}"
TASK = Path(__file__).resolve().parent.parent


def http_get(path: str) -> str:
    with urllib.request.urlopen(BASE + path, timeout=10) as resp:
        return resp.read().decode("utf-8", "replace")


def oracle(data: bytes) -> bytes:
    """POST /encrypt: вернуть XOR данных с секретным ключом сервера."""
    body = urllib.parse.urlencode({"data": base64.b64encode(data).decode()}).encode()
    with urllib.request.urlopen(BASE + "/encrypt", data=body, timeout=10) as resp:
        return base64.b64decode(resp.read().decode().strip())


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ b[i % len(b)] for i, x in enumerate(a))


def flag1() -> str:
    html = http_get("/")
    motd = re.search(r"Сообщение дня:</b> <code>([^<]+)</code>", html).group(1)
    for k in range(26):
        guess = "".join(
            chr((ord(c) - 97 + k) % 26 + 97) if "a" <= c <= "z"
            else chr((ord(c) - 65 + k) % 26 + 65) if "A" <= c <= "Z"
            else c
            for c in motd
        )
        if guess.startswith("BootCTF{"):
            return guess
    raise RuntimeError("сдвиг Цезаря не найден")


def recover_key(length: int) -> bytes:
    # XOR нулей с ключом возвращает сам ключ (нужной длины).
    return oracle(b"\x00" * length)


def flag2() -> str:
    cipher = base64.b64decode(http_get("/flag").strip())
    key = recover_key(len(cipher))
    return xor(cipher, key).decode()


def flag3() -> str:
    tar_path = TASK / "public" / "backup.tar"
    with tarfile.open(tar_path) as tar:
        enc = tar.extractfile("report.enc").read()
        mtime = int(tar.getmember("report.enc").mtime)  # время создания ≈ время шифрования
    iv, ct = enc[:16], enc[16:]
    for seconds in range(mtime - 300, mtime + 301):  # окно ±5 минут вокруг mtime
        key = hashlib.sha256(str(seconds).encode()).digest()
        if hashlib.md5(str(seconds).encode()).digest() != iv:
            continue  # IV тоже выведен из времени — быстрый отсев
        try:
            plain = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
        except ValueError:
            continue
        m = re.search(rb"BootCTF\{[^}]+\}", plain)
        if m:
            return m.group(0).decode()
    raise RuntimeError("ключ AES в окне времени не найден")


def flag4() -> str:
    cipher = base64.b64decode(http_get("/archive").strip())
    key = recover_key(len(cipher))
    text = xor(cipher, key).decode("utf-8", "replace")
    return re.search(r"BootCTF\{[^}]+\}", text).group(0)


def main() -> None:
    for fn in (flag1, flag2, flag3, flag4):
        print(fn())


if __name__ == "__main__":
    main()
