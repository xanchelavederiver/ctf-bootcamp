#!/usr/bin/env python3
"""Управление демонстрационными заданиями мини-курса.

    taskctl.py list                       список заданий
    taskctl.py check [<путь> ...]         проверка структуры и метаданных
    taskctl.py new <путь>                 новое задание из шаблона _template
    taskctl.py export [<путь> ...]        архивы одного/всех заданий в public/tasks/
    taskctl.py verify [<путь> ...]        запуск сервиса и сверка solve.py со всеми флагами
    taskctl.py lecture-export <лекция>    комплект для студентов: PDF рядом + задания
    taskctl.py lecture-up <лекция>        поднять сервисы лекции с боевыми флагами (.env)
    taskctl.py lecture-down <лекция>      остановить сервисы лекции

«Путь» — это <категория>/<имя> (обычное задание) или <коллекция>/<N>-<категория>-<имя>
(задание внутри коллекции лекции). Структура задания — в project/tasks/README.md.
Требуется PyYAML; команды verify/lecture-* требуют Docker.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Требуется PyYAML: pip install pyyaml (или пакет python3-yaml)")

TASKS = Path(__file__).resolve().parent.parent
REPO = TASKS.parent.parent
TEMPLATE = TASKS / "_template"
CONFIG = TASKS / "tasks.yml"
LECTURES = REPO / "project" / "lectures"

REQUIRED = ("name", "id", "category", "difficulty", "points", "author", "flag")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ORDER_PREFIX = re.compile(r"^\d+-")  # необязательный номер задания в коллекции: 1-web-portal


def base_name(name: str) -> str:
    """Имя каталога задания без порядкового номера: 1-web-portal -> web-portal."""
    return ORDER_PREFIX.sub("", name)
SKIP_NAMES = {".gitkeep", ".DS_Store", "__pycache__", "node_modules", ".venv"}
PLACEHOLDER_FLAG = "BootCTF{replace_me}"


def load_config() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    cfg.setdefault("collections", [])
    return cfg


def all_tasks() -> list[Path]:
    return sorted(
        p.parent
        for p in TASKS.glob("*/*/task.yml")
        if not p.parent.parent.name.startswith("_")
    )


def resolve(names: list[str]) -> list[Path]:
    if not names:
        return all_tasks()
    tasks = []
    for name in names:
        path = TASKS / name.strip("/")
        if not (path / "task.yml").is_file():
            sys.exit(f"Задание не найдено: {name} (ожидается {path.relative_to(REPO)}/task.yml)")
        tasks.append(path)
    return tasks


def label(task: Path) -> str:
    return f"{task.parent.name}/{task.name}"


def load_meta(task: Path) -> dict:
    return yaml.safe_load((task / "task.yml").read_text(encoding="utf-8")) or {}


def task_category(task: Path, meta: dict, config: dict) -> str:
    """Категория задания: имя родительского каталога либо, внутри коллекции, поле category."""
    parent = task.parent.name
    if parent in config.get("collections", []):
        return str(meta.get("category") or "")
    return parent


def all_flags(meta: dict) -> list[dict]:
    """Единый список флагов задания: основной `flag` (id 1) + элементы `flags`.

    Каждый флаг — dict с ключами id, flag, points, title, hidden, env.
    env != None означает флаг времени выполнения (значение в task.yml — умолчание).
    """
    flags: list[dict] = []
    main = meta.get("flag")
    if main not in (None, ""):
        flags.append(
            {
                "id": 1,
                "flag": str(main),
                "points": meta.get("points"),
                "title": meta.get("name", ""),
                "hidden": False,
                "env": meta.get("flag_env"),
            }
        )
    for item in meta.get("flags") or []:
        flags.append(
            {
                "id": item.get("id"),
                "flag": str(item.get("flag", "")),
                "points": item.get("points"),
                "title": item.get("title", ""),
                "hidden": bool(item.get("hidden", False)),
                "env": item.get("env"),
            }
        )
    return flags


def files_of(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not (SKIP_NAMES & set(p.relative_to(root).parts))
    )


def handout_dirs(task: Path, meta: dict) -> list[str]:
    """Каталоги задания, выдаваемые студенту помимо README.md и public/ (поле handout)."""
    handout = meta.get("handout") or []
    if isinstance(handout, str):
        handout = [handout]
    return [str(h).strip("/") for h in handout]


def check_task(task: Path, config: dict) -> list[str]:
    errors: list[str] = []
    try:
        meta = load_meta(task)
    except yaml.YAMLError as exc:
        return [f"task.yml: ошибка разбора YAML: {exc}"]

    for key in REQUIRED:
        if meta.get(key) in (None, ""):
            errors.append(f"task.yml: не заполнено поле «{key}»")

    parent = task.parent.name
    in_collection = parent in config.get("collections", [])
    category = task_category(task, meta, config)

    if not SLUG.match(task.name):
        errors.append("имя каталога: допустимы строчные латинские буквы, цифры и дефис")
    expected_id = base_name(task.name) if in_collection else task.name
    if meta.get("id") != expected_id:
        errors.append(f"task.yml: id «{meta.get('id')}» не совпадает с именем каталога «{expected_id}»")

    if in_collection:
        # Внутри коллекции каталог называется [<номер>-]<категория>-<имя>, категория — из task.yml.
        if category not in config["categories"]:
            errors.append(f"task.yml: category «{category}» не объявлена в tasks.yml")
        elif not base_name(task.name).startswith(f"{category}-"):
            errors.append(
                f"имя каталога «{task.name}» в коллекции должно начинаться с «{category}-» (после номера) "
                "(категория из task.yml)"
            )
    else:
        if meta.get("category") != parent:
            errors.append(f"task.yml: category «{meta.get('category')}» не совпадает с каталогом «{parent}»")
        if parent not in config["categories"]:
            errors.append(f"категория «{parent}» не объявлена в tasks.yml")

    if meta.get("difficulty") not in config["difficulties"]:
        errors.append(f"task.yml: difficulty должно быть одним из {config['difficulties']}")
    if not isinstance(meta.get("points"), int) or meta.get("points", 0) <= 0:
        errors.append("task.yml: points должно быть положительным целым числом")

    flags = all_flags(meta)
    ids = [f["id"] for f in flags]
    if len(ids) != len(set(ids)):
        errors.append(f"task.yml: повторяющиеся id флагов: {ids}")
    for f in flags:
        value = f["flag"]
        if value == PLACEHOLDER_FLAG:
            errors.append(f"task.yml: флаг id={f['id']} не заменён (значение из шаблона)")
        elif value and not re.fullmatch(config["flag_format"], value):
            errors.append(f"task.yml: флаг id={f['id']} не соответствует формату {config['flag_format']}")
        if not isinstance(f["id"], int):
            errors.append(f"task.yml: id флага должно быть целым числом (встретилось {f['id']!r})")

    for required in ("README.md", "solution/README.md"):
        if not (task / required).is_file():
            errors.append(f"отсутствует {required}")

    service = meta.get("service")
    if service:
        if service.get("type") not in ("tcp", "http"):
            errors.append("task.yml: service.type должно быть tcp или http")
        if not isinstance(service.get("port"), int):
            errors.append("task.yml: service.port должно быть целым числом")
        compose = task / "deploy" / "docker-compose.yml"
        if not compose.is_file():
            errors.append("для задания с сервисом требуется deploy/docker-compose.yml")
        # Флаги времени выполнения должны иметь умолчание в deploy/flags.env.defaults.
        env_defaults = read_env_file(task / "deploy" / "flags.env.defaults")
        for f in flags:
            if f["env"]:
                if f["env"] not in env_defaults:
                    errors.append(f"deploy/flags.env.defaults: нет умолчания для {f['env']} (флаг id={f['id']})")
                elif env_defaults[f["env"]] != f["flag"]:
                    errors.append(
                        f"deploy/flags.env.defaults: {f['env']} не совпадает со значением флага id={f['id']} в task.yml"
                    )
    elif not files_of(task / "public"):
        errors.append("нет ни файлов в public/, ни сервиса: участнику нечего решать")

    # Задание должно оставаться самодостаточным: никаких ссылок за пределы каталога.
    for path in task.rglob("*"):
        if path.is_symlink() and not path.resolve().is_relative_to(task.resolve()):
            errors.append(f"{path.relative_to(task)}: символическая ссылка за пределы задания")

    # Файловый флаг не должен попадать к участникам открытым текстом. Исключение —
    # задания, где поиск флага в выданном файле и есть решение: flag_in_public: true.
    # Флаги времени выполнения (env) проверяются отдельно: их умолчания живут в deploy/.env.
    participant_files = [task / "README.md", *files_of(task / "public")]
    for h in handout_dirs(task, meta):
        participant_files += files_of(task / h)
    for f in flags:
        if f["env"] or not f["flag"] or f["flag"] == PLACEHOLDER_FLAG:
            continue
        if meta.get("flag_in_public"):
            continue
        needle = f["flag"].encode()
        for path in participant_files:
            if path.is_file() and path.name != ".env" and needle in path.read_bytes():
                errors.append(
                    f"{path.relative_to(task)}: флаг id={f['id']} открытым текстом в материалах участника "
                    "(если так задумано — flag_in_public: true)"
                )
    return errors


def read_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


# --------------------------------------------------------------------------- list / check / new


def cmd_list(_: argparse.Namespace) -> int:
    tasks = all_tasks()
    if not tasks:
        print("Заданий пока нет: make task-new TASK=<категория>/<имя>")
        return 0
    for task in tasks:
        meta = load_meta(task)
        n = len(all_flags(meta))
        print(
            f"{label(task):30} {str(meta.get('difficulty', '?')):8} "
            f"{str(meta.get('points', '?')):>5}  {n} флаг(ов)  {meta.get('name', '')}"
        )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    config = load_config()
    tasks = resolve(args.tasks)
    if not tasks:
        print("Заданий пока нет — проверять нечего.")
        return 0
    failed = 0
    for task in tasks:
        errors = check_task(task, config)
        print(f"{'ОШИБКИ' if errors else 'ok':7} {label(task)}")
        for error in errors:
            print(f"        - {error}")
        failed += bool(errors)
    return 1 if failed else 0


def cmd_new(args: argparse.Namespace) -> int:
    config = load_config()
    parts = args.task.strip("/").split("/")
    if len(parts) != 2:
        sys.exit("Ожидается <категория>/<имя> или <коллекция>/<N>-<категория>-<имя>")
    first, name = parts
    if not SLUG.match(name):
        sys.exit("Имя задания: строчные латинские буквы, цифры и дефис")

    if first in config.get("collections", []):
        # Внутри коллекции категория берётся из префикса имени: 1-web-portal -> web.
        category = base_name(name).split("-", 1)[0]
        if category not in config["categories"]:
            sys.exit(
                f"Имя «{name}» должно начинаться с категории: {', '.join(config['categories'])}"
            )
    elif first in config["categories"]:
        category = first
    else:
        sys.exit(
            f"«{first}» — не категория и не коллекция. "
            f"Категории: {', '.join(config['categories'])}; коллекции: {', '.join(config['collections']) or '—'}"
        )

    target = TASKS / first / name
    if target.exists():
        sys.exit(f"Каталог уже существует: {target.relative_to(REPO)}")
    shutil.copytree(TEMPLATE, target)
    meta = target / "task.yml"
    text = meta.read_text(encoding="utf-8")
    task_id = base_name(name) if first in config.get("collections", []) else name
    text = re.sub(r"^id: .*$", f"id: {task_id}", text, flags=re.M)
    text = re.sub(r"^category: .*$", f"category: {category}", text, flags=re.M)
    meta.write_text(text, encoding="utf-8")
    print(f"Создано: {target.relative_to(REPO)}")
    return 0


# --------------------------------------------------------------------------- export (per-task)


def write_zip(archive: Path, task: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, Path(task.name) / path.relative_to(task))


def participant_files(task: Path, meta: dict) -> list[Path]:
    files = [task / "README.md", *files_of(task / "public")]
    for h in handout_dirs(task, meta):
        files += files_of(task / h)
    return files


def cmd_export(args: argparse.Namespace) -> int:
    config = load_config()
    tasks = resolve(args.tasks)
    if not tasks:
        print("Заданий пока нет — экспортировать нечего.")
        return 0
    out = REPO / "public" / "tasks"
    out.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        errors = check_task(task, config)
        if errors:
            print(f"ОШИБКИ  {label(task)}")
            for error in errors:
                print(f"        - {error}")
            sys.exit("Экспорт остановлен: исправьте ошибки (make tasks-check).")
        meta = load_meta(task)
        base = f"{task.parent.name}-{task.name}"
        write_zip(out / f"{base}-full.zip", task, files_of(task))
        write_zip(out / f"{base}.zip", task, participant_files(task, meta))
        print(f"ok      {label(task)} -> public/tasks/{base}.zip, {base}-full.zip")
    return 0


# --------------------------------------------------------------------------- verify


def service_port(meta: dict) -> int | None:
    service = meta.get("service")
    return service.get("port") if service else None


def run_solve(task: Path, host: str, port: int | None) -> list[str]:
    """Запустить solution/solve.py системным python3 из каталога задания."""
    env = dict(os.environ, TASK_HOST=host, PYTHONUNBUFFERED="1")
    if port is not None:
        env["TASK_PORT"] = str(port)
    proc = subprocess.run(
        [sys.executable, "-I", str(task / "solution" / "solve.py")],
        cwd=task, env=env, capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"solve.py завершился с кодом {proc.returncode}:\n{proc.stderr}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def compose(task: Path, *compose_args: str, env: dict | None = None, check: bool = True):
    return subprocess.run(
        ["docker", "compose", *compose_args],
        cwd=task / "deploy",
        env=dict(os.environ, **(env or {})),
        check=check,
    )


def verify_task(task: Path, config: dict) -> list[str]:
    errors = check_task(task, config)
    if errors:
        return errors
    meta = load_meta(task)
    # Ожидаемые флаги резолвим так же, как их подставляет контейнер: умолчания из
    # flags.env.defaults, переопределённые flags.real.env коллекции, если тот есть.
    real = {}
    if task.parent.name in config.get("collections", []):
        real = read_env_file(task.parent / "flags.real.env")
    expected = set()
    for f in all_flags(meta):
        if f["env"] and f["env"] in real:
            expected.add(real[f["env"]])
        else:
            expected.add(f["flag"])
    service = meta.get("service")
    host, port = "127.0.0.1", service_port(meta)

    started = False
    try:
        if service:
            compose(task, "up", "-d", "--build", "--wait", env={"BIND": "127.0.0.1"})
            started = True
        output = run_solve(task, host, port)
    except Exception as exc:  # noqa: BLE001
        return [f"verify: {exc}"]
    finally:
        if started:
            compose(task, "down", "-v", check=False)

    out_set = set(output)
    missing = sorted(expected - out_set)
    problems = []
    if missing:
        problems.append(f"solve.py не напечатал флаги: {', '.join(missing)}")
        problems.append(f"  вывод solve.py: {output}")
    return problems


def cmd_verify(args: argparse.Namespace) -> int:
    config = load_config()
    tasks = resolve(args.tasks)
    failed = 0
    for task in tasks:
        problems = verify_task(task, config)
        print(f"{'ОШИБКИ' if problems else 'ok':7} {label(task)}")
        for p in problems:
            print(f"        - {p}")
        failed += bool(problems)
    return 1 if failed else 0


# --------------------------------------------------------------------------- lecture: collections


def lecture_tasks(lecture: str) -> list[Path]:
    """Задания, привязанные к лекции полем lecture, в порядке поля order."""
    tasks = [t for t in all_tasks() if str(load_meta(t).get("lecture", "")) == lecture]
    return sorted(tasks, key=lambda t: (load_meta(t).get("order", 999), label(t)))


def collection_dir(lecture: str, tasks: list[Path]) -> Path | None:
    parents = {t.parent for t in tasks if t.parent.name in load_config().get("collections", [])}
    return next(iter(parents)) if len(parents) == 1 else None


def cmd_lecture_export(args: argparse.Namespace) -> int:
    config = load_config()
    lecture = args.lecture
    tasks = lecture_tasks(lecture)
    if not tasks:
        sys.exit(f"Для лекции «{lecture}» не найдено заданий (поле lecture в task.yml).")

    for task in tasks:
        errors = check_task(task, config)
        if errors:
            print(f"ОШИБКИ  {label(task)}")
            for error in errors:
                print(f"        - {error}")
            sys.exit("Экспорт остановлен: исправьте ошибки (make tasks-check).")

    coll = collection_dir(lecture, tasks)
    out = REPO / "public" / "export" / lecture
    tasks_out = out / "tasks"
    if out.exists():
        shutil.rmtree(out)
    tasks_out.mkdir(parents=True)

    # PDF лекции (без заметок докладчика) должен быть уже собран Makefile'ом.
    pdf = REPO / "public" / "lectures" / f"{lecture}.pdf"
    if pdf.is_file():
        shutil.copy2(pdf, out / f"{lecture}.pdf")
    else:
        print(f"ВНИМАНИЕ: {pdf.relative_to(REPO)} не найден — PDF в комплект не вошёл.")

    # Материалы коллекции для студентов: README и docker-compose.yml. Файлы лектора
    # (checker/, flags.real.env, flags.real.env.example) в комплект не входят.
    if coll:
        for name in ("README.md", "docker-compose.yml"):
            src = coll / name
            if src.is_file():
                shutil.copy2(src, tasks_out / name)
        docs = coll / "docs"
        if docs.is_dir():
            shutil.copytree(docs, tasks_out / "docs")

    # Задания: материалы участника.
    for task in tasks:
        meta = load_meta(task)
        dest = tasks_out / task.name
        for path in participant_files(task, meta):
            target = dest / path.relative_to(task)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    # Разборы для студентов — только по запросу (WRITEUPS=1).
    if args.writeups:
        wdir = out / "writeups"
        wdir.mkdir()
        for task in tasks:
            w = task / "solution" / "writeup.md"
            if w.is_file():
                shutil.copy2(w, wdir / f"{task.parent.name}-{task.name}.md")

    # Контроль утечки боевых флагов: если у лектора есть .env, ни один его флаг не должен
    # попасть в студенческий комплект.
    leaked = scan_real_flags(coll, out) if coll else []
    if leaked:
        for item in leaked:
            print(f"УТЕЧКА  {item}")
        sys.exit("Экспорт остановлен: боевой флаг попал в студенческий комплект.")

    # Единый zip.
    archive = REPO / "public" / "export" / f"{lecture}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(out.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(out.parent))

    print(f"Готово: {out.relative_to(REPO)}/ и {archive.relative_to(REPO)}")
    return 0


def scan_real_flags(coll: Path, bundle: Path) -> list[str]:
    """Боевые флаги из flags.real.env лектора не должны встречаться в собранном комплекте."""
    env = read_env_file(coll / "flags.real.env")
    real = {v.encode() for k, v in env.items() if v.startswith("BootCTF{")}
    if not real:
        return []
    leaked = []
    for path in bundle.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_bytes()
        for needle in real:
            if needle in data:
                leaked.append(f"{path.relative_to(bundle)}: {needle.decode(errors='replace')}")
    return leaked


def service_compose_files(tasks: list[Path]) -> list[str]:
    files = []
    for task in tasks:
        compose = task / "deploy" / "docker-compose.yml"
        if compose.is_file():
            files.append(str(compose))
    return files


def cmd_lecture_up(args: argparse.Namespace) -> int:
    lecture = args.lecture
    tasks = lecture_tasks(lecture)
    coll = collection_dir(lecture, tasks)
    if not coll:
        sys.exit(f"Для лекции «{lecture}» не найдена коллекция заданий.")
    env_path = coll / "flags.real.env"
    if not env_path.is_file():
        sys.exit(
            f"Нет {env_path.relative_to(REPO)}: скопируйте flags.real.env.example в flags.real.env "
            "и впишите боевые флаги."
        )
    env = read_env_file(env_path)
    markers = ("default", "CHANGE_ME", "REPLACE", "replace_me")
    bad = [k for k, v in env.items() if any(m in v for m in markers)]
    if bad:
        sys.exit(f"В flags.real.env остались заготовки: {', '.join(bad)}. Впишите боевые значения.")

    compose = coll / "docker-compose.lecturer.yml"
    if not compose.is_file():
        sys.exit(f"Нет {compose.relative_to(REPO)}")
    # include-файл интерпретирует env_file относительно включаемого файла — поэтому
    # запускаем из каталога коллекции, а не через несколько -f (там путь иной).
    cmd = ["docker", "compose", "-f", str(compose), "-p", f"ctf-{lecture}",
           "up", "-d", "--build", "--wait"]
    print(f"Поднимаю сервисы лекции {lecture} (боевые флаги, BIND=0.0.0.0)…")
    subprocess.run(cmd, cwd=coll,
                   env=dict(os.environ, BIND="0.0.0.0", COLLECTION_HOST=str(coll)), check=True)
    print("Готово. Остановить: make lecture-down LECTURE=" + lecture)
    return 0


def cmd_lecture_down(args: argparse.Namespace) -> int:
    lecture = args.lecture
    tasks = lecture_tasks(lecture)
    coll = collection_dir(lecture, tasks)
    if not coll:
        sys.exit(f"Для лекции «{lecture}» не найдена коллекция заданий.")
    compose = coll / "docker-compose.lecturer.yml"
    cmd = ["docker", "compose", "-f", str(compose), "-p", f"ctf-{lecture}", "down", "-v"]
    subprocess.run(cmd, cwd=coll, env=dict(os.environ, COLLECTION_HOST=str(coll)), check=False)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    check = sub.add_parser("check")
    check.add_argument("tasks", nargs="*")
    check.set_defaults(func=cmd_check)
    new = sub.add_parser("new")
    new.add_argument("task")
    new.set_defaults(func=cmd_new)
    export = sub.add_parser("export")
    export.add_argument("tasks", nargs="*")
    export.set_defaults(func=cmd_export)
    verify = sub.add_parser("verify")
    verify.add_argument("tasks", nargs="*")
    verify.set_defaults(func=cmd_verify)
    lexport = sub.add_parser("lecture-export")
    lexport.add_argument("lecture")
    lexport.add_argument("--writeups", action="store_true")
    lexport.set_defaults(func=cmd_lecture_export)
    lup = sub.add_parser("lecture-up")
    lup.add_argument("lecture")
    lup.set_defaults(func=cmd_lecture_up)
    ldown = sub.add_parser("lecture-down")
    ldown.add_argument("lecture")
    ldown.set_defaults(func=cmd_lecture_down)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
