#!/usr/bin/env python3
"""Генератор «Открытки» (stego). Детерминированно собирает public/postcard.png
с четырьмя флагами:

  1. tEXt-метаданные PNG (ключ Comment);
  2. текст, нарисованный в бит-плоскости 0 красного канала (видно в StegSolve);
  3. байты в младшем бите (LSB) синего канала, построчно;
  4. ZIP, дописанный после чанка IEND (скрытый флаг).

Запуск — внутри образа ctf-toolbox (там есть Pillow):

    docker run --rm --platform linux/amd64 -v "$PWD":/w -w /w ctf-toolbox \\
        python3 -I src/generate.py

Результат воспроизводим (фиксированные значения, без случайностей в пикселях).
"""
from __future__ import annotations

import io
import struct
import zipfile
from pathlib import Path

from PIL import Image, PngImagePlugin

OUT = Path(__file__).resolve().parent.parent / "public" / "postcard.png"

FLAG1 = "BootCTF{png_text_chunk_meta}"
FLAG2 = "BootCTF{bitplane_red_art}"
FLAG3 = "BootCTF{blue_lsb_row_major}"
FLAG4 = "BootCTF{zip_after_iend_chunk}"

W, H = 640, 360

# Компактный шрифт 5x7 для флага №2. Один и тот же шрифт использует solve.py,
# поэтому чтение бит-плоскости однозначно (не требуется OCR).
FONT: dict[str, list[str]] = {
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

SCALE = 4          # размер «пикселя» шрифта
ORIGIN = (16, 28)  # левый верхний угол текста флага №2


def base_image() -> Image.Image:
    """Косметическая «открытка»: диагональный градиент и рамка."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            r = 40 + (x * 120) // W
            g = 90 + (y * 120) // H
            b = 150 + ((x + y) * 80) // (W + H)
            px[x, y] = (r, g, b)
    return img


def draw_flag2(px) -> None:
    """Флаг №2: глифы в бит-плоскости 0 красного канала.

    Сначала обнуляем младший бит красного во всём изображении (чистая плоскость),
    затем поднимаем его в точках глифов — в StegSolve видно белый текст на чёрном.
    """
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            px[x, y] = (r & ~1, g, b)
    ox, oy = ORIGIN
    advance = (5 + 1) * SCALE
    for i, ch in enumerate(FLAG2):
        glyph = FONT[ch]
        for row in range(7):
            for col in range(5):
                if glyph[row][col] != "#":
                    continue
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        x = ox + i * advance + col * SCALE + dx
                        y = oy + row * SCALE + dy
                        r, g, b = px[x, y]
                        px[x, y] = (r | 1, g, b)


def embed_flag3(px) -> None:
    """Флаг №3: байты в LSB синего канала, построчно, старший бит первым.
    После сообщения — нулевой байт-терминатор, остальные LSB синего обнулены."""
    data = FLAG3.encode() + b"\x00"
    bits = [(byte >> (7 - k)) & 1 for byte in data for k in range(8)]
    idx = 0
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            bit = bits[idx] if idx < len(bits) else 0
            px[x, y] = (r, g, (b & ~1) | bit)
            idx += 1


def build_zip() -> bytes:
    """Флаг №4: небольшой ZIP, который допишется после IEND."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("secret.txt", f"Скрытый флаг открытки:\n{FLAG4}\n")
    return buf.getvalue()


def main() -> None:
    img = base_image()
    px = img.load()
    draw_flag2(px)
    embed_flag3(px)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Title", "Postcard from Severny Mayak")
    meta.add_text("Comment", FLAG1)  # флаг №1
    meta.add_text("Software", "severny-mayak postcard tool")

    png_buf = io.BytesIO()
    img.save(png_buf, format="PNG", pnginfo=meta)
    png_bytes = png_buf.getvalue()

    # Проверка: файл заканчивается чанком IEND (0-длина + "IEND" + CRC) — после
    # него дописываем ZIP.
    assert png_bytes[-12:-8] == struct.pack(">I", 0) and png_bytes[-8:-4] == b"IEND"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(png_bytes + build_zip())
    print(f"written {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
