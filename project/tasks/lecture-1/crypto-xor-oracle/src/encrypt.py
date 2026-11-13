#!/usr/bin/env python3
"""Шифрование отчёта (внутренний инструмент «Северного маяка»).

Этот файл выдаётся участнику внутри backup.tar: по нему видно, как получен
report.enc. Ключ выводится из текущего времени в секундах — в этом и слабость.
"""

import hashlib
import sys
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def derive_key(seconds: int) -> bytes:
    # Ключ AES-256 — SHA-256 от числа секунд Unix-времени.
    return hashlib.sha256(str(seconds).encode()).digest()


def encrypt(path_in: str, path_out: str, seconds: int | None = None) -> None:
    seconds = int(time.time()) if seconds is None else seconds
    key = derive_key(seconds)
    iv = hashlib.md5(str(seconds).encode()).digest()  # 16 байт, детерминирован от времени
    data = open(path_in, "rb").read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = cipher.encrypt(pad(data, AES.block_size))
    # Формат report.enc: IV (16 байт) + шифртекст.
    open(path_out, "wb").write(iv + enc)


if __name__ == "__main__":
    encrypt(sys.argv[1], sys.argv[2])
    print("report.enc записан")
