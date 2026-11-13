#!/usr/bin/env python3
"""Эталонное решение «Пропуска»: печатает три флага, по одному в строке.

Флаги извлекаются СТАТИЧЕСКИ из public/access-check, без запуска бинарника:
  1) открытая строка            — regex по байтам файла;
  2) XOR-шифр в enc2            — читаем символ enc2 через pyelftools,
     перебираем однобайтовый ключ до префикса BootCTF{;
  3) цепочка if-ов             — разбираем дизассемблер check3 (objdump),
     собираем пары (индекс, символ) и упорядочиваем по индексу.

Запускается внутри образа ctf-toolbox (есть objdump, pyelftools). Бинарник —
только для чтения; результат печатается в stdout.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

TASK = Path(__file__).resolve().parent.parent
BIN = TASK / "public" / "access-check"


def flag1() -> str:
    data = BIN.read_bytes()
    return re.search(rb"BootCTF\{[ -~]{3,}?\}", data).group().decode()


def flag2() -> str:
    from elftools.elf.elffile import ELFFile

    with BIN.open("rb") as fh:
        elf = ELFFile(fh)
        symtab = elf.get_section_by_name(".symtab")
        sym = symtab.get_symbol_by_name("enc2")[0]
        addr, size = sym["st_value"], sym["st_size"]
        for sec in elf.iter_sections():
            start = sec["sh_addr"]
            if start and start <= addr < start + sec["sh_size"]:
                off = addr - start
                enc = sec.data()[off:off + size]
                break
    for key in range(256):
        dec = bytes(b ^ key for b in enc)
        if dec.startswith(b"BootCTF{") and dec.endswith(b"}"):
            return dec.decode()
    raise RuntimeError("ключ XOR для флага 2 не найден")


def flag3() -> str:
    dump = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", str(BIN)],
        capture_output=True, text=True, check=True,
    ).stdout
    body = re.search(r"<check3>:\n(.*?)\n\n", dump, re.S).group(1)

    pairs: dict[int, str] = {}
    index = 0
    for line in body.splitlines():
        m_add = re.search(r"add\s+\$0x([0-9a-f]+),%rax", line)
        m_mov = re.search(r"mov\s+-0x[0-9a-f]+\(%rbp\),%rax", line)
        m_cmp = re.search(r"cmp\s+\$0x([0-9a-f]+),%al", line)
        if m_mov:
            index = 0                      # перезагрузка указателя s -> индекс 0
        elif m_add:
            index = int(m_add.group(1), 16)  # add $k,%rax -> s[k]
        elif m_cmp:
            pairs[index] = chr(int(m_cmp.group(1), 16))
    return "".join(pairs[i] for i in sorted(pairs))


def main() -> None:
    print(flag1())
    print(flag2())
    print(flag3())


if __name__ == "__main__":
    main()
