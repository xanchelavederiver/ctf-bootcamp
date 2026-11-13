#!/usr/bin/env python3
"""Эталонное решение «Открытки»: печатает четыре флага, по одному в строке.

Запускается внутри образа ctf-toolbox (есть Pillow, zsteg) через `make tasks-verify`;
задание смонтировано только для чтения в /task. Рабочий каталог — /task.

  1. tEXt-метаданные (ключ Comment)                — PIL img.info;
  2. бит-плоскость 0 красного канала (шрифт 5x7)   — читаем глифы;
  3. LSB синего канала, построчно                  — распаковываем битовый поток;
  4. ZIP после IEND                                — stdlib zipfile по всему файлу.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from PIL import Image

TASK = Path(__file__).resolve().parent.parent
PNG = TASK / "public" / "postcard.png"

# Тот же шрифт 5x7, что и в src/generate.py: даёт однозначное чтение бит-плоскости.
FONT = {
    " ": ["     "] * 7,
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "a": ["     ", "     ", " ### ", "    #", " ####", "#   #", " ####"],
    "b": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "],
    "d": ["    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"],
    "e": ["     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "],
    "i": ["  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "],
    "l": [" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "n": ["     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "o": ["     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "],
    "p": ["     ", "     ", "#### ", "#   #", "#### ", "#    ", "#    "],
    "r": ["     ", "     ", "# ## ", "##   ", "#    ", "#    ", "#    "],
    "t": ["  #  ", "  #  ", "#####", "  #  ", "  #  ", "  #  ", "  ## "],
    "_": ["     ", "     ", "     ", "     ", "     ", "     ", "#####"],
    "{": ["  ## ", " #   ", " #   ", "#    ", " #   ", " #   ", "  ## "],
    "}": [" ##  ", "   # ", "   # ", "    #", "   # ", "   # ", " ##  "],
}
SCALE = 4
ORIGIN = (16, 28)
REVERSE = {tuple("".join(rows)): ch for ch, rows in FONT.items()}


def flag1(img: Image.Image) -> str:
    return img.info["Comment"]


def flag2(img: Image.Image) -> str:
    """Читаем бит-плоскость 0 красного канала как последовательность глифов 5x7."""
    px = img.load()
    ox, oy = ORIGIN
    advance = (5 + 1) * SCALE
    out = []
    for i in range(64):  # флаг заведомо короче 64 символов
        cells = []
        for row in range(7):
            line = ""
            for col in range(5):
                x = ox + i * advance + col * SCALE
                y = oy + row * SCALE
                line += "#" if (px[x, y][0] & 1) else " "
            cells.append(line)
        ch = REVERSE.get(tuple("".join(cells)))
        if ch is None:
            break
        out.append(ch)
        if ch == "}":
            break
    return "".join(out)


def flag3(img: Image.Image) -> str:
    """LSB синего канала, построчно, старший бит первым, до нулевого байта."""
    px = img.load()
    w, h = img.size
    bits = []
    for y in range(h):
        for x in range(w):
            bits.append(px[x, y][2] & 1)
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for k in range(8):
            byte = (byte << 1) | bits[i + k]
        if byte == 0:
            break
        out.append(byte)
    return out.decode("latin-1")


def flag4() -> str:
    """ZIP дописан после IEND; zipfile читает архив по оглавлению в конце файла."""
    with zipfile.ZipFile(PNG) as zf:
        text = zf.read("secret.txt").decode("utf-8")
    for token in text.split():
        if token.startswith("BootCTF{"):
            return token
    return text.strip().splitlines()[-1]


def main() -> None:
    img = Image.open(PNG)
    print(flag1(img))
    print(flag2(img))
    print(flag3(img))
    print(flag4())


if __name__ == "__main__":
    main()
