#!/usr/bin/env python3
"""Генератор исходника задания «Пропуск» (reverse).

Эмитит src/check.c с тремя независимыми проверками трёх флагов:
  1) strcmp с открытой строковой константой        -> находится strings;
  2) флаг хранится XOR-шифрованным, расшифровывается в конструкторе
     до main и сверяется ручным побайтовым циклом    -> виден в gdb в main;
  3) цепочка if-ов, по одному сравнению на символ, в перемешанном порядке
     (ни строки, ни цикла)                            -> только статический анализ.

Запуск (из каталога задания):  python3 src/generate.py
Детерминирован: фиксированный seed, порядок условий воспроизводим.
"""

from __future__ import annotations

import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "check.c"

FLAG1 = "BootCTF{str1ngs_unlock_the_d00r}"
FLAG2 = "BootCTF{gdb_sees_the_c0nstruct0r}"
FLAG3 = "BootCTF{static_1f_ladder_at_h0me}"

XOR_KEY = 0x5A  # однобайтовый ключ для флага 2


def c_char(ch: str) -> str:
    """Символ как C-литерал (все символы флага — из [A-Za-z0-9_{}])."""
    return f"'{ch}'"


def main() -> None:
    enc2 = bytes(b ^ XOR_KEY for b in FLAG2.encode())
    enc2_arr = ", ".join(f"0x{b:02x}" for b in enc2)

    # Перемешанный порядок условий для флага 3: (индекс, символ).
    rnd = random.Random(1337)
    pairs = list(enumerate(FLAG3))
    rnd.shuffle(pairs)
    ifs = "\n".join(
        f"    if (s[{idx}] != {c_char(ch)}) bad = 1;" for idx, ch in pairs
    )

    code = f"""/* «Пропуск» (reverse) — СГЕНЕРИРОВАНО src/generate.py, править генератор.
 *
 * Утилита читает строку со stdin. Если она совпадает с одним из трёх
 * пропусков (флагов) — печатает "Access granted", иначе "Access denied".
 * Три проверки независимы и демонстрируют три приёма обратной разработки.
 *
 * Сборка:  gcc -O0 -no-pie -fno-stack-protector -o access-check check.c
 */
#include <stdio.h>
#include <string.h>

/* --- Флаг 1: открытая константа, сверяется strcmp (находится strings). --- */
static const char *FLAG1 = "{FLAG1}";

/* --- Флаг 2: хранится XOR-шифрованным; расшифровывается до main. --- */
static unsigned char enc2[] = {{ {enc2_arr} }};
static char dec2[sizeof(enc2) + 1];

__attribute__((constructor))
static void unlock_badge(void)
{{
    unsigned int i;
    for (i = 0; i < sizeof(enc2); i++)
        dec2[i] = (char)(enc2[i] ^ 0x{XOR_KEY:02x});
    dec2[sizeof(enc2)] = '\\0';
}}

/* Ручной побайтовый цикл вместо strcmp/memcmp: ltrace ничего не покажет. */
static int check2(const char *s)
{{
    unsigned int i;
    for (i = 0; i < sizeof(enc2); i++) {{
        if (s[i] != dec2[i]) return 0;
    }}
    return s[sizeof(enc2)] == '\\0';
}}

/* --- Флаг 3: цепочка if-ов, по одному символу, перемешанный порядок. --- */
static int check3(const char *s)
{{
    int bad = 0;
    if (strlen(s) != {len(FLAG3)}) return 0;
{ifs}
    return bad == 0;
}}

int main(void)
{{
    char buf[256];
    if (!fgets(buf, sizeof(buf), stdin)) return 1;
    buf[strcspn(buf, "\\n")] = '\\0';

    if (strcmp(buf, FLAG1) == 0 || check2(buf) || check3(buf))
        puts("Access granted");
    else
        puts("Access denied");
    return 0;
}}
"""
    OUT.write_text(code, encoding="utf-8")
    print(f"Записано: {OUT}")
    print(f"FLAG1={FLAG1}")
    print(f"FLAG2={FLAG2}")
    print(f"FLAG3={FLAG3}")


if __name__ == "__main__":
    main()
