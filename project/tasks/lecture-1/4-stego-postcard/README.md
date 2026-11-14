# Открытка

> Категория: stego · Сложность: easy · 100 очков

В ходе аудита ООО «Северный маяк» на корпоративном файловом сервере нашлась
безобидная с виду открытка — картинка `postcard.png`. Сотрудник службы безопасности
уверен, что в ней что-то спрятано: слишком уж аккуратно она сделана. Исследуйте
изображение: в нём спрятано несколько флагов.

**Файлы:** `public/postcard.png`

**Инструменты:**

- `exiftool`, `binwalk` — `sudo apt install libimage-exiftool-perl binwalk`;
- `zsteg` — `sudo apt install ruby && sudo gem install zsteg`;
- Python 3 с библиотекой `pillow` — `pip install pillow`.

**Формат флага:** `BootCTF{...}`
