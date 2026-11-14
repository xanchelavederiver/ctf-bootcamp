.DEFAULT_GOAL := help

NPM ?= npm
PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
LECTURES := $(ROOT)/project/lectures
TASKS := $(ROOT)/project/tasks
TASKCTL := $(PYTHON) "$(TASKS)/_tools/taskctl.py"

LECTURE ?=
TASK ?=


.PHONY: help setup lectures lectures-pdf lectures-pptx lectures-list lecture-dev lecture-new \
	tasks-list tasks-check tasks-verify task-new task-export tasks-export \
	lecture-up lecture-down lecture-export

help:
	@echo 'Слайды (Markdown -> public/lectures/*.pdf, *.pptx):'
	@echo '  make setup                           установить зависимости сборки (npm ci)'
	@echo '  make lectures [LECTURE=<id>]         PDF и PPTX: все лекции или одна'
	@echo '  make lectures-pdf | lectures-pptx    только один формат'
	@echo '  make lectures-list                   список лекций'
	@echo '  make lecture-new LECTURE=<id>        новая лекция из шаблона _template'
	@echo '  make lecture-dev LECTURE=<id>        предпросмотр в браузере с автообновлением'
	@echo ''
	@echo 'Задания (project/tasks/<категория-или-коллекция>/<задание>):'
	@echo '  make tasks-list                      список заданий'
	@echo '  make tasks-check [TASK=<путь>]       проверка структуры и метаданных'
	@echo '  make tasks-verify [TASK=<путь>]      поднять сервис и сверить solve.py со всеми флагами'
	@echo '  make task-new TASK=<путь>            новое задание из шаблона _template'
	@echo '  make task-export TASK=<путь>         архивы задания в public/tasks/'
	@echo '  make tasks-export                    архивы всех заданий'
	@echo ''
	@echo 'Короткий CTF лекции (коллекция lecture-1):'
	@echo '  make lecture-up LECTURE=<id>         поднять сервисы с боевыми флагами (flags.real.env)'
	@echo '  make lecture-down LECTURE=<id>       остановить сервисы'
	@echo '  make lecture-export LECTURE=<id>     комплект для студентов: PDF, задания, разборы'

setup:
	$(NPM) --prefix "$(LECTURES)" ci

lectures:
	$(NPM) --prefix "$(LECTURES)" run --silent build -- $(LECTURE)

lectures-pdf:
	$(NPM) --prefix "$(LECTURES)" run --silent build -- --pdf $(LECTURE)

lectures-pptx:
	$(NPM) --prefix "$(LECTURES)" run --silent build -- --pptx $(LECTURE)

lectures-list:
	@$(NPM) --prefix "$(LECTURES)" run --silent list

lecture-dev:
	@test -n "$(LECTURE)" || { echo 'Usage: make lecture-dev LECTURE=<id>' >&2; exit 2; }
	$(NPM) --prefix "$(LECTURES)" run --silent build -- --serve $(LECTURE)

lecture-new:
	@test -n "$(LECTURE)" || { echo 'Usage: make lecture-new LECTURE=<id>, например 01-intro' >&2; exit 2; }
	@test ! -e "$(LECTURES)/$(LECTURE)" || { echo 'Каталог $(LECTURE) уже существует' >&2; exit 1; }
	cp -r "$(LECTURES)/_template" "$(LECTURES)/$(LECTURE)"
	@echo 'Создано: project/lectures/$(LECTURE)/slides.md'

tasks-list:
	@$(TASKCTL) list

tasks-check:
	@$(TASKCTL) check $(TASK)

task-new:
	@test -n "$(TASK)" || { echo 'Usage: make task-new TASK=<категория>/<имя>' >&2; exit 2; }
	@$(TASKCTL) new $(TASK)

task-export:
	@test -n "$(TASK)" || { echo 'Usage: make task-export TASK=<категория>/<имя>' >&2; exit 2; }
	@$(TASKCTL) export $(TASK)

tasks-export:
	@$(TASKCTL) export

tasks-verify:
	$(TASKCTL) verify $(TASK)

lecture-up:
	@test -n "$(LECTURE)" || { echo 'Usage: make lecture-up LECTURE=<id>' >&2; exit 2; }
	$(TASKCTL) lecture-up $(LECTURE)

lecture-down:
	@test -n "$(LECTURE)" || { echo 'Usage: make lecture-down LECTURE=<id>' >&2; exit 2; }
	$(TASKCTL) lecture-down $(LECTURE)

lecture-export:
	@test -n "$(LECTURE)" || { echo 'Usage: make lecture-export LECTURE=<id>' >&2; exit 2; }
	PDF_NOTES=0 $(NPM) --prefix "$(LECTURES)" run --silent build -- --pdf $(LECTURE)
	$(TASKCTL) lecture-export $(LECTURE)
