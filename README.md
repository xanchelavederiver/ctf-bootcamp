# Введение в CTF — материалы мини-курса

Исходные материалы вводного мини-курса по соревнованиям CTF:

| Каталог | Содержимое |
|---|---|
| [`project/lectures`](project/lectures/README.md) | лекционные слайды (Markdown → PDF, PPTX) и материалы к ним |
| [`project/tasks`](project/tasks/README.md) | демонстрационные задания по категориям; коллекция `lecture-1` — короткий CTF вводной лекции |
| `public/` | результаты сборки: слайды, архивы заданий, комплект студентов (в Git не входит) |

Первая лекция `01-intro` и её короткий CTF (6 заданий: web, crypto, forensics, stego,
reverse, pwn) лежат в `project/lectures/01-intro/` и `project/tasks/lecture-1/`.

## Быстрый старт

```sh
make setup                               # зависимости сборки слайдов
make lectures                            # public/lectures/*.pdf, *.pptx
make task-new TASK=crypto/xor-intro      # новое задание из шаблона
make tasks-check                         # проверка заданий
make tasks-verify                        # поднять сервисы и сверить решения со всеми флагами
make help                                # все команды
```

Короткий CTF лекции (нужен Docker):

```sh
make lecture-up LECTURE=01-intro         # боевой стенд (флаги из flags.real.env)
make lecture-export LECTURE=01-intro     # комплект для студентов: public/export/01-intro/
```

Требования: GNU Make, Node.js 20+, Chrome или Chromium (сборка слайдов),
Python 3 с PyYAML (инструменты заданий), Docker (задания с сервисами, verify, короткий CTF).
Задания рассчитаны на x86-64 Linux (или Windows + WSL2).
