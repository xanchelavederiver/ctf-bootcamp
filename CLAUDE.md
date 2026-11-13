# CTF bootcamp — материалы вводного мини-курса по CTF

Язык всех материалов (слайды, условия заданий, разборы, документация) — русский.

## Структура

- `project/lectures/<NN-имя>/slides.md` — слайды лекции (Marp Markdown); тема — `project/lectures/theme/ctf-academic.css`; образец всех типов слайдов — `project/lectures/_template/slides.md`.
- `project/tasks/<категория>/<имя>/` — демонстрационные задания; каждое самодостаточно (никаких ссылок за пределы своего каталога). Структура и правила — `project/tasks/README.md`, шаблон — `project/tasks/_template`.
- `project/tasks/<коллекция>/<категория>-<имя>/` — задания коллекции лекции (короткий CTF). Коллекция `lecture-1` относится к лекции `01-intro`; в ней также `toolbox/` (образ инструментов), `checker/` (проверщик флагов — только для лектора), `docs/` (установка инструментов), `flags.real.env.example` (шаблон боевых флагов).
- `public/` — результаты сборки, в Git не входит. Комплект студентов — `public/export/<лекция>/`.

## Команды

- `make lectures [LECTURE=<id>]` — PDF и PPTX в `public/lectures/`; `make lectures LECTURE=_template` — собрать образец.
- `make task-new TASK=<путь>`, `make tasks-check [TASK=<путь>]`, `make tasks-verify [TASK=<путь>]`, `make task-export TASK=<путь>`. Путь — `<категория>/<имя>` или `<коллекция>/<категория>-<имя>`.
- Короткий CTF: `make toolbox-build`, `make toolbox-export LECTURE=<id>`, `make lecture-up/lecture-down LECTURE=<id>` (боевой стенд из `flags.real.env`), `make lecture-export LECTURE=<id> [WRITEUPS=1]`.
- `make help` — полный список.

## Правила работы

- Любая работа над текстом слайдов — через навык `academic-presentation-writer` (стиль: академический, но не чрезмерно формальный; словарь терминов — в его `references/glossary.md`).
- После правки слайдов собрать лекцию и просмотреть PDF: переполнение слайда обрезается молча.
- Новые лекции и задания создавать из шаблонов (`make lecture-new`, `make task-new`), а не с нуля.
- Задание считается готовым, когда проходит `make tasks-check`, а `solution/solve.py` печатает флаг.
- Вывод команд, код и идентификаторы (CVE, версии) на слайдах — только проверенные; в примерах атак — только учебные задания и локальные стенды.
