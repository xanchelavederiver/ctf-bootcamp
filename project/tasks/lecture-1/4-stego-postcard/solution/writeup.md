# Разбор: Открытка (stego)

Дан один файл — `postcard.png`. В нём спрятаны четыре флага, каждый — своим способом.

Сначала посмотрим, что это за файл:

```console
$ file postcard.png
postcard.png: PNG image data, 640 x 360, 8-bit/color RGB, non-interlaced
```

## Флаг 1 — метаданные (tEXt)

PNG хранит текстовые заметки в чанках `tEXt`. Их показывает `exiftool`:

```console
$ exiftool -Comment -Title -Software postcard.png
Comment                         : BootCTF{png_text_chunk_meta}
Title                           : Postcard from Severny Mayak
Software                        : severny-mayak postcard tool
```

Поле `Comment` — первый флаг: `BootCTF{png_text_chunk_meta}`. То же нашлось бы через
`strings postcard.png | grep BootCTF` — tEXt лежит в файле открытым текстом.

*Чему учит.* Метаданные (EXIF/tEXt) — первое, что смотрят в любом файле: там часто
остаются камеры, координаты, имена, комментарии.

## Флаг 2 — бит-плоскость красного канала

Каждый пиксель — три байта (R, G, B). Если взять только один бит из байта по всем
пикселям, получится «бит-плоскость». Младшие биты обычно выглядят как шум, но сюда
можно вписать картинку. Откройте файл в **StegSolve** и листайте плоскости кнопками
`<` / `>`: на **Red plane 0** проступит белый текст на чёрном фоне — это флаг.

Без установки то же делает онлайн-сервис **Aperi'Solve**: загрузите файл и
посмотрите раздел с бит-плоскостями.

Флаг читается глазами: `BootCTF{bitplane_red_art}`.

*Чему учит.* Данные прячут не «в файле вообще», а в конкретном бите конкретного
канала. Инструмент бит-плоскостей показывает каждый такой слой отдельно.

## Флаг 3 — LSB синего канала

Здесь байты флага записаны в младшие биты (LSB) синего канала по пикселям, слева
направо и сверху вниз. Руками такое не прочитать — есть `zsteg`, который сам
перебирает каналы, биты и порядок обхода:

```console
$ zsteg -a postcard.png
...
b1,b,lsb,xy         .. text: "BootCTF{blue_lsb_row_major}"
extradata:0         .. file: Zip archive data, ...
```

Селектор `b1,b,lsb,xy` — это «1 бит, синий канал (b), младший бит, построчно (xy)».
Точечно тот же результат:

```console
$ zsteg -E b1,b,lsb,xy postcard.png
BootCTF{blue_lsb_row_major}
```

*Чему учит.* LSB-стеганография меняет изображение незаметно для глаза. `zsteg` —
первый инструмент для PNG/BMP: он находит такие тайники автоматически.

---

## Скрытый флаг (ищите дальше)

### Флаг 4 — архив после конца PNG

В отчёте `zsteg -a` есть строка `extradata:0 .. Zip archive data`: после законного
конца PNG (чанк `IEND`) к файлу дописан ZIP-архив. Файл одновременно и картинка, и
архив, поэтому его можно просто распаковать:

```console
$ unzip postcard.png
Archive:  postcard.png
warning [postcard.png]:  5522 extra bytes at beginning or within zipfile
  (attempting to process anyway)
  inflating: secret.txt
$ cat secret.txt
Скрытый флаг открытки:
BootCTF{zip_after_iend_chunk}
```

Предупреждение про «extra bytes» — это как раз байты PNG перед архивом. Флаг:
`BootCTF{zip_after_iend_chunk}`.

*Чему учит.* Формат файла определяется не только расширением. Данные, дописанные
после «конца» (IEND у PNG), штатные просмотрщики игнорируют, а `zsteg`, `unzip` и
подобные инструменты — нет.

---

**Куда дальше.** Похожие задания — в разделе Forensics/Stego на picoCTF (picoGym):
метаданные, бит-плоскости и LSB в картинках, а также данные, спрятанные «в хвосте»
файла.
