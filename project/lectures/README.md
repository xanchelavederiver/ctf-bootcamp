# Лекции

Слайды пишутся в Markdown ([Marp](https://marp.app/)) и собираются в PDF и PPTX.

```
project/lectures/
├── _template/slides.md      образец колоды со всеми типами слайдов
├── <NN-имя>/
│   ├── slides.md            слайды лекции
│   └── assets/              изображения и прочие материалы лекции
├── theme/ctf-academic.css   тема оформления
└── scripts/build.mjs        сборка
```

## Сборка

Требуются Node.js 20+ и Chrome или Chromium. Команды выполняются из корня репозитория:

```sh
make setup                        # один раз: установить зависимости
make lecture-new LECTURE=01-intro # новая лекция из образца
make lectures                     # все лекции: PDF и PPTX
make lectures LECTURE=01-intro    # одна лекция
make lectures-pdf LECTURE=01-intro
make lecture-dev LECTURE=01-intro # предпросмотр с автообновлением
make lectures LECTURE=_template   # собрать образец
```

Результат — `public/lectures/<id>.pdf` и `<id>.pptx` (каталог `public/` в Git не входит).
Шрифты Inter и JetBrains Mono встраиваются при сборке, сеть не нужна.

`PDF_NOTES=0 make lectures-pdf LECTURE=<id>` собирает PDF без заметок докладчика —
такой вариант уходит студентам (его же кладёт `make lecture-export`).

Браузер ищется автоматически (системный Chrome/Chromium, затем Chromium из кэша
Playwright); путь можно задать явно: `CHROME_PATH=/path/to/chrome make lectures`.

### О формате PPTX

По умолчанию каждый слайд PPTX — изображение, в точности совпадающее с PDF; заметки
докладчика сохраняются. Такой файл открывается и показывается в PowerPoint, Keynote
и LibreOffice, но текст слайдов в нём не редактируется — правки вносятся в `slides.md`.
Редактируемый PPTX (экспериментальный режим Marp, нужен установленный LibreOffice,
оформление переносится приблизительно): `PPTX_EDITABLE=1 make lectures-pptx`.

## Оформление слайдов

Все приёмы показаны в `_template/slides.md`. Слайды — краткие: один тезис на слайд, без
титулов разделов и слайда «План». Кратко:

| Приём | Запись |
|---|---|
| Разделитель слайдов | строка `---` |
| Тип слайда | `<!-- _class: title \| sources \| dense -->` |
| Ссылка на слайде | `[название](https://example.org)` — кликабельна в PDF |
| Ссылка в «Источниках» | `<https://example.org>` — URL показан полностью |
| Заметки докладчика | HTML-комментарий в конце слайда |
| Транскрипт терминала | блок кода `console` |
| Две колонки | `<div class="cols">` с двумя вложенными `<div>` (варианты `c-2-3`, `c-3-2`) |
| Примечание / ограничение | `<div class="note">`, `<div class="warn">` |
| Определение, ключевой тезис | цитата `>` |

Текст, не поместившийся на слайде, обрезается без предупреждения — после правок
просматривайте собранный PDF.
