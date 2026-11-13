# Plan 01 — Lecture 1 "Introduction to CTF" + mini-CTF `lecture-1`

Status: **decisions confirmed by the author on 2026-11-13; ready for implementation** (one optional gap, §10)

Self-contained: a fresh session can implement from this file plus `CLAUDE.md`.
All deliverables (slides, task statements, write-ups, READMEs) are in **Russian**; this plan is in English.

## 1. Goal and deliverables

| # | Deliverable | Location |
|---|---|---|
| D1 | Lecture slides, 90 min | `project/lectures/01-intro/slides.md` |
| D2 | Six demo tasks (web, crypto, forensics, stego, reverse, pwn) | `project/tasks/lecture-1/<category>-<name>/` |
| D3 | Write-ups: lecturer version + student version, per task | `solution/README.md`, `solution/writeup.md` in each task |
| D4 | Tooling changes: task collections, multi-flag tasks, lecture export | `project/tasks/_tools/taskctl.py`, `Makefile`, `build.mjs` |
| D5 | Student bundle: PDF + `tasks/` folder + toolbox image | `public/export/01-intro/` (+ `.zip`) |
| D6 | Lecturer hosting: all services with real flags + flag checker | `make lecture-up LECTURE=01-intro` |
| D7 | Tool installation manuals, Linux and Windows | `project/tasks/lecture-1/docs/` |

Audience: CS/IT students who can program and use a shell; no CTF experience.
Time budget: **30 min intro + 60 min mini-CTF**.

Central takeaway of the lecture (required by the writer skill): *a CTF task is a small, legal model of a real
security problem; every category is entered through a handful of basic techniques, and the student has
tried each of them once by the end of the session.*

## 2. Decisions (confirmed)

| # | Topic | Decision |
|---|---|---|
| Q1 | Student machines | x86-64 Linux: Kali VM or WSL2. No arm64 builds. |
| Q2 | Hosting | The **lecturer hosts** the service tasks with the real flags (LAN, `BIND=0.0.0.0`). Students may also run the same projects locally; their copies carry the **default flags**, which differ from the real ones. |
| Q3 | Sources and flags | Service tasks ship as project folders with sources. Flags come from `.env`: defaults are committed and shipped; the lecturer overrides them with real values. File-based tasks ship as prepared files only, without sources. |
| Q4 | Tools | A **pre-built toolbox Docker image** is exported into the bundle with short import/usage instructions. In addition: installation manuals for **Linux** and **Windows** covering every tool used. |
| Q5 | Flag checking | No offline script (it would leak flags). A **trivial checker service** is started by the lecturer on the machine that hosts the tasks and is reachable by students. |
| Q6 | Student write-ups | Cover hidden flags too; released later by the lecturer (`WRITEUPS=1`). |
| Q7 | Title slide | Lecturer, organization, year stay placeholders until provided. |

Timing: accepted as tight; some solution routes are homework by design.

## 3. Conflicts with the current repo and how they are resolved

1. **Path layout.** `taskctl.py` requires `project/tasks/<category>/<name>` with `category == parent dir`; the
   requested layout is `project/tasks/lecture-1/<category>-<name>`. → introduce *collections* (§4.1).
2. **One flag per task.** `task.yml` has a single `flag`. → optional `flags:` list (§4.2).
3. **Speaker notes leak.** `build.mjs` always passes `--pdf-notes`; notes will contain demo order and hints.
   → student PDF is built without notes (§4.4).
4. **Glossary clash.** «контейнер» is defined as a stego cover file. → use «контейнер Docker» /
   «стегоконтейнер»; add both to `references/glossary.md`, together with: внедрение в шаблон на стороне
   сервера (SSTI), оракул, образ (Docker image), boot2root, red/blue team, киберполигон, bug bounty.
5. **File mtime** (crypto, AES part) does not survive Git or zip reliably. → the timestamp lives inside a
   `.tar` built by the generator with a fixed mtime.

## 4. Phase 1 — tooling

### 4.1 Collections
- `tasks.yml`: new key `collections: [lecture-1]`.
- `check_task`: if the parent dir is a collection — `category` comes from `task.yml`, must be a declared
  category, and the dir name must start with `<category>-`; `id == dir name` as before.
- `cmd_new`: `make task-new TASK=lecture-1/web-portal` derives the category from the prefix.
- Collection-level files: `project/tasks/lecture-1/README.md` (student instructions: prerequisites, port
  table, start/stop/cleanup) and `docker-compose.yml` using `include:` of every task's
  `deploy/docker-compose.yml` (start everything with one command; each task still runs alone).

### 4.2 `task.yml` extensions
```yaml
flag: "BootCTF{...}"            # flag 1, kept for compatibility
flags:                      # optional, further flags
  - {id: 2, flag: "BootCTF{...}", points: 100, title: "..."}
  - {id: 5, flag: "BootCTF{...}", points: 150, hidden: true}   # not announced on slides
  - {id: 3, flag: "BootCTF{...}", env: WEB_FLAG_3}             # runtime flag: value here is the default
handout: [deploy]           # extra paths shipped to students besides README.md and public/
order: 1                    # position within the lecture
lecture: 01-intro           # already exists; links the task to the lecture
```
Format and leak checks apply to every flag. Update `_template/task.yml` and `project/tasks/README.md`.

### 4.3 Flags: defaults and real values

Two kinds of flags:

- **Runtime flags** (served by a container; marked with `env:`). The service reads them from environment
  variables and never hard-codes them — including values that end up in HTML, JS or files inside the
  container, which are rendered at start-up. Defaults live in the task's `deploy/.env` (committed,
  shipped to students) and equal the values in `task.yml`. Defaults are deliberately recognisable,
  e.g. `BootCTF{default_...}`, so nobody mistakes them for real ones.
- **File flags** (baked into `public/` files by the generator: pcapng, PNG, ELF, tar). One value for
  everyone; that value is the real flag. Sources and generators are not shipped.

Lecturer side: `project/tasks/lecture-1/.env.example` (committed) lists every runtime variable;
the lecturer copies it to `.env` (**git-ignored**) and sets real values. Because `${VAR:-default}` cannot
hold a default containing `}`, defaults are supplied through env files, not inline; the override order of
the collection-level env file over each task's `deploy/.env` under `include:` must be confirmed by a
test at implementation (fallback: `--env-file` on the command line).

### 4.4 New commands
- `make tasks-verify [TASK=…]` — for service tasks `docker compose up -d --build --wait` with default
  flags, run `solution/solve.py`, compare its output with **all** flags in `task.yml`, then `down -v`.
  `solve.py` prints one flag per line, in `id` order, and takes the host/port from arguments so the same
  script works against the lecturer's host.
- `make lecture-up LECTURE=01-intro` / `lecture-down` — lecturer hosting: all services of the collection
  with the real flags from `.env`, `BIND=0.0.0.0`, plus the checker (§5.8). `lecture-up` refuses to start
  if `.env` is missing or still contains a default flag.
- `make toolbox-build` / `toolbox-export` — build the toolbox image and write
  `public/export/01-intro/toolbox/ctf-toolbox.tar.gz` (`docker save | gzip`).
- `make lecture-export LECTURE=01-intro [WRITEUPS=1]` → `public/export/01-intro/`:
  ```
  01-intro.pdf                 student PDF, no speaker notes
  tasks/README.md              how to reach the lecturer's host, how to run locally, cleanup
  tasks/docker-compose.yml     start all service tasks locally (default flags)
  tasks/docs/                  install-linux.md, install-windows.md, toolbox.md
  tasks/<category>-<name>/     README.md, public/, + paths from `handout` (deploy/ for service tasks)
  toolbox/ctf-toolbox.tar.gz   pre-built image (kept outside the zip because of its size)
  writeups/<task>.md           only with WRITEUPS=1 (from solution/writeup.md)
  ```
  plus `public/export/01-intro.zip`. Tasks are selected by `lecture:` and sorted by `order`.
  Never exported: `src/`, `solution/`, `task.yml`, the lecturer's `.env`, the checker.
  The export fails if any real flag from `.env` occurs anywhere in the bundle.

### 4.5 `build.mjs`
`PDF_NOTES=0` drops `--pdf-notes`; `OUT_DIR` already exists. `lecture-export` uses both.

### 4.6 Docs
Add the lecturer `.env` to `.gitignore`. Update `CLAUDE.md` (structure, commands), `README.md`, `project/tasks/README.md`, `project/lectures/README.md`.

### 4.7 Flag format `BootCTF{...}`
The repo currently uses `ctf{...}`; no tasks exist yet, so the switch is done once, before any task:
- `project/tasks/tasks.yml`: `flag_format: 'BootCTF\{[A-Za-z0-9_!?.+-]{4,64}\}'`;
- `taskctl.py`: `PLACEHOLDER_FLAG = "BootCTF{replace_me}"`;
- `_template/task.yml`, `_template/README.md`, `_template/solution/README.md`: examples updated;
- slides (flag-format slide in section 1), statements and write-ups use `BootCTF{...}` only.

## 5. Phase 2 — the mini-CTF

Common rules:
- Flag format **`BootCTF{...}`** (see §4.7). Tasks have **announced** flags (on slides); web, crypto,
  forensics and stego also have **hidden** ones. "Class" = intended to be reached during the lecture.
- Flags served by a container are runtime flags, flags inside handout files are file flags (§4.3).
  On slides and in statements the address is written as `<host>`: the lecturer's machine in class,
  `localhost` for a local copy.
- One light legend links the tasks: an audit of a fictional small company («Северный маяк»).
- Service tasks: `deploy/docker-compose.yml`, build context inside `deploy/`, port
  `${BIND:-127.0.0.1}:<port>`, non-root user, `read_only`, `cap_drop: [ALL]`, `no-new-privileges`,
  pids/memory limits, healthcheck (needed by `--wait`).
- Everything in `public/` is produced by a generator in `src/` (run in a pinned Docker image, fixed seeds)
  and committed.
- Created with `make task-new`, done when `make tasks-check` and `make tasks-verify` pass.

Ports: checker 8000 · web 8001 · crypto 8002 · forensics FTP 2121 + passive 30000–30009 · pwn 9001.
The FTP server's advertised passive address comes from `.env` (the lecturer's LAN address in class).
Shared hosting means students can interfere with each other; services are stateless, per-connection
and resource-limited, and `make lecture-up` can be re-run to reset them.

### 5.1 `web-portal` — «Портал» (Flask + Jinja2, plain HTML/CSS/JS)

| Flag | Where | Technique | When |
|---|---|---|---|
| 1 | Base64 string in an HTML comment of the main page | view source, `base64 -d` | class |
| 2 | JS handler on a key combination shows the flag in a pop-up; flag stored as a char-code array | read `static/app.js`, DevTools console | class |
| 3 | `/api/secret`, listed in `robots.txt`: GET → 405, POST without a header → hint, POST with the header → flag | `curl -X POST -H` | class |
| 4 | `/hello?name=` renders input via `render_template_string`; flag in `app.config` | SSTI: `{{7*7}}` → `{{config}}` | class, demo |
| hidden A | custom HTTP response header on one page | `curl -i` | home |
| hidden B | `/flag.txt` in the container, reachable only through SSTI → command execution | SSTI to RCE | home |

### 5.2 `crypto-xor-oracle` — «Шифратор» (Flask, usable with `curl` + `base64` only)

| Flag | Where | Technique | When |
|---|---|---|---|
| 1 | "message of the day" on the main page, Caesar with an unknown shift | known prefix `BootCTF{` gives the shift; try all 25 | class |
| 2 | `GET /flag` returns the flag XORed with a secret key (Base64). `POST /encrypt` XORs anything with the same key, but refuses if the result equals the flag | XOR is its own inverse; bypass by appending one byte, or send zero bytes to read the key | class |
| 3 | `/backup.tar` (also in `public/`): `encrypt.py` + `report.enc`; AES-CBC key = SHA-256 of `int(time.time())` | mtime inside the tar ≈ seed; search a ±5 min window, validate by padding and `BootCTF{` | home |
| hidden | a second message encrypted with the same XOR key, longer than the key (key repeats) | recover the full key with flag 2's method, notice the repetition | home |

Key is longer than flag 2, so repetition is not needed for it. Base64 in form data must be sent with
`--data-urlencode` (`+` would be mangled) — stated in the statement.

### 5.3 `forensics-ftp-backup` — «Резервная копия» (pcapng + live FTP server)

`public/capture.pcapng`: one passive-mode FTP session — login, `LIST`, `RETR notes.txt`, `RETR backup.zip`.
Generated by `src/capture/` (compose: `pyftpdlib` server + scripted client + `tcpdump`, converted to pcapng).

| Flag | Where | Technique | When |
|---|---|---|---|
| 1 | `notes.txt` transferred in clear | Wireshark: Follow TCP Stream / Export Objects → FTP-DATA | class |
| 2 | archive comment of `backup.zip` (encrypted ZipCrypto archive; comment and file names are not encrypted) | carve the zip from the stream, `unzip -z` / `zipinfo` | class |
| 3 | `flag.txt` inside the zip; password is in John's bundled `password.lst` | `zip2john` + `john` | home (class if time) |
| hidden | live FTP server (same credentials as in the capture) has a directory the captured session never visited | `ftp`/`curl ftp://…`, look around | home |

Both routes to the files are shown: from the TCP stream, and by logging in to the live server with the
sniffed password. The password must be verified against the wordlist of the John version in the toolbox.

### 5.4 `stego-postcard` — «Открытка» (one PNG, procedurally generated, no third-party imagery)

| Flag | Where | Technique | When |
|---|---|---|---|
| 1 | PNG `tEXt` metadata | `exiftool`, `strings` | class |
| 2 | text drawn in bit plane 0 of the red channel | StegSolve plane browser, or Aperi'Solve online | class |
| 3 | bytes in LSB of the blue channel, row order | `zsteg` (`b1,b,lsb,xy`) | class/home |
| hidden | zip appended after `IEND` | `zsteg` warns about extra data; `binwalk -e` | home |

Tool answer to the open question in the brief: **`zsteg`** is the better-suited tool for PNG LSB (detects
the payload automatically); **StegSolve** stays for showing bit planes visually; **Aperi'Solve** needs no
installation and runs both ideas online. All three go on the slide, in that order of "what it is for".

### 5.5 `reverse-access-check` — «Пропуск» (C, ELF x86-64, `-O0 -no-pie`, not stripped)

Three independent checks; any accepted flag prints `Access granted`, otherwise `Access denied`.

| Flag | How it is checked | Technique | When |
|---|---|---|---|
| 1 | `strcmp` with a plaintext constant | `strings` (`flag_in_public: true`) | class |
| 2 | stored XORed, decrypted by a constructor before `main`; compared by a hand-written loop (so `ltrace` does not give it away) | `gdb`: break in `main`, print the buffer | class, demo |
| 3 | no plaintext anywhere and no loop: the input is checked by a **series of `if` statements**, one condition per character, in shuffled order | static analysis: read the conditions in the disassembly or in Ghidra and assemble the string by index | **homework** |

No hidden flag: flag 3 is left as homework; in class only flags 1 and 2 are covered. The task is file-based, so all three are file flags.

### 5.6 `pwn-<name>` — the most trivial task of the category

As in the brief: the simplest stack buffer overflow, used to steer execution to the function that prints
the flag; the binary runs behind `socat` in a docker-compose project. One flag, a runtime flag read from
the environment on the server. Handout: the binary and its C source. Statement gives the connection
command (`nc <host> 9001`). No hidden flag. Kept this small on purpose; name, compiler options and the
exact reference solution are fixed during implementation and verified by `make tasks-verify`.

### 5.7 Toolbox image and installation manuals (Q4)

`project/tasks/lecture-1/toolbox/` — `Dockerfile` for one image, `ctf-toolbox`, `linux/amd64`, with the
command-line tools the tasks need (HTTP/FTP/TCP clients, Python with the libraries used in the
write-ups, traffic, archive, image and binary analysis tools, a debugger). GUI tools (Wireshark, Ghidra,
StegSolve) are not in the image; they are covered by the manuals. Image size is measured after the build
and stated in the docs; if it is too large to hand out, trim before shipping rather than after.

`project/tasks/lecture-1/docs/` (Russian, every command run before it is written down):

- `toolbox.md` — import (`docker load -i ctf-toolbox.tar.gz`), start with the tasks folder mounted,
  reaching the lecturer's host and local services from inside, removal.
- `install-linux.md` — Kali / Debian / Ubuntu: Docker, then the tools per category, with a check
  command for each ("how to see it works").
- `install-windows.md` — WSL2 + Docker Desktop, the Linux tools inside WSL2, and native Windows
  installers for the GUI tools.

The toolbox is also the environment in which `make tasks-verify` runs the reference solutions here.

### 5.8 Flag checker (Q5) — `project/tasks/lecture-1/checker/`

A deliberately trivial web page run only by the lecturer, next to the services: one input field, answer
"верно — `<task>`, флаг N" or "неверно". It knows the real runtime flags from the lecturer's `.env` and
the file flags from a lecturer-side list generated from `task.yml`. It shows per task how many flags
exist in total, hidden ones included, without naming them — this is the "keep looking" tease. Stateless
(no accounts, no scoreboard), compares in constant time, basic rate limit per address. Default flags are
answered with "это флаг локальной копии", so students see why a local flag is not accepted.
Not exported to students.

## 6. Phase 3 — write-ups (D3)

Per task, two files, both in Russian:

- `solution/README.md` — **lecturer**: idea, full solution for every flag including hidden ones, timing for
  the in-class part, a ladder of hints (from vague to direct), typical student mistakes, link to the
  lecture slide numbers, what to show live and in which order.
- `solution/writeup.md` — **student**: step-by-step walkthrough with real command output, one section per
  flag, a short "what this teaches / where it appears in real systems" paragraph, links to the analogous
  practice tasks. Hidden flags sit in a clearly separated last section (Q6).
- `solution/solve.py` — prints every flag, one per line.

All command output in write-ups comes from actual runs (toolbox or host), not from memory.

## 7. Phase 4 — slides (D1)

Created with `make lecture-new LECTURE=01-intro`; **all text goes through the
`academic-presentation-writer` skill** (read `references/glossary.md` first). Deck scheme is fixed by the
skill: title → plan → numbered sections with repeated section titles → «Выводы» → «Источники», `_footer`
source notes on content slides, thesis-style headings, speaker notes in trailing comments.

Timing and outline (≈ 60 slides including repeated section titles):

| § | Section | Min | Content slides |
|---|---|---|---|
| 1 | Что такое CTF и зачем он нужен | 12 | definition, flag and flag format · why: skills, community, career · ethical and legal frame (only permitted targets; mandatory in lecture 1) · formats: task-based, attack-defense, mixed · categories overview (table) · rules of a typical event · scoring: static vs dynamic, first blood, AD points, CTFtime rating |
| 2 | За пределами CTF | 5 | boot2root machines and wargames · red / blue / purple teaming · cyber ranges (киберполигоны) · bug bounty — one comparison table "format / goal / what it trains" |
| 3 | С чего начать и где учиться | 8 | 3.1 «С чего начать» — **one slide**, 5–6 links · 3.2 general CS · 3.3 general CTF: tutorial portals, endless platforms, machine platforms · 3.4 per-category references (one compact table per two categories) |
| 4 | Стенд: задания в Docker | 8 | why server tasks ship as docker-compose projects · image vs container · install (Linux, Windows/WSL2; details in the manuals) · in class: the lecturer's host and the checker · at home: start one task / all tasks locally, default flags · logs, stop, cleanup · importing and using the toolbox image |
| 5–10 | web · crypto · forensics · stego · reverse · pwn | ~8–9 each | **slide A**: legend · access (handout file names, URL/port, start command) · tools with links and install commands · additional info. **slide B (+C if needed)**: announced flags as a table "flag / what to look at / points" — no flag values, no solutions · analogous practice tasks · the line «дома ищите дальше — найдено не всё» |
| 11 | Выводы | 2 | takeaway · homework: finish announced flags, look for hidden ones, the checker and how long it stays available |
| — | Источники | — | numbered list, matches `_footer` notes |

Solutions are not on slides; the live demonstration order per task is in speaker notes and in
`solution/README.md`. In class the realistic target is **one or two flags per task**, lecturer-led; the
rest is homework. A "prepare before the lecture" note (install Docker, unpack the bundle, build images)
goes on the Docker section and into `tasks/README.md`, to be sent to students in advance.

### 7.1 References — candidates

**Every URL is opened and checked at implementation time** (page exists, content matches the description,
still free/accessible); anything that fails is dropped rather than guessed. Names below are candidates.

- **«С чего начать» (one slide, beginner-first, RU included):** picoCTF / picoGym; OverTheWire Bandit;
  PortSwigger Web Security Academy; TryHackMe introductory paths; a Russian beginner course or platform
  (candidates: SPbCTF materials, HackerLab / Codeby Games, «Курс молодого бойца CTF»); CTFtime calendar.
- **General CS:** CS50 (incl. Russian translation); MIT "The Missing Semester" (incl. Russian
  translation); Linux Journey; Andrey Sozykin's «Компьютерные сети» (RU); a Python tutorial.
- **General CTF:** CTF101; Trail of Bits CTF Field Guide; CTFtime write-ups; Russian community resources
  (SPbCTF, HackerDom/RuCTF training materials, CTF News, Habr CTF hub); endless platforms (picoGym,
  Root-Me, HackerLab, FreeHackQuest); machine platforms (TryHackMe, Hack The Box, Standoff 365 for the
  cyber-range format); utilities (CyberChef, dCode).
- **Per category:** web — PortSwigger Academy, Hacker101; crypto — CryptoHack, Cryptopals; forensics —
  Wireshark documentation and sample captures, CyberDefenders; stego — Aperi'Solve, a stego checklist;
  reverse — Ghidra documentation, crackmes.one, Nand2Tetris/CS:APP for background; pwn — pwn.college,
  the pwntools tutorial. One Russian-language item per category where a solid one exists.
- **Analogous practice tasks (slide B of each task):** candidates from picoGym are picked per flag and
  each is confirmed to exist under that exact name before it goes on a slide.

## 8. Phase 5 — export and clean-room test (D5)

1. `make lectures LECTURE=01-intro`; read the PDF page by page — overflow is clipped silently.
2. `make tasks-check`, `make tasks-verify`.
3. `make lecture-export LECTURE=01-intro` and `… WRITEUPS=1`.
4. Clean-room test: copy `public/export/01-intro/` to a scratch directory, follow `tasks/README.md`
   literally (load the toolbox image, build, start all, solve one flag per task from the student
   materials only, stop, clean up). Confirm no `solution/`, `src/`, `task.yml` or speaker notes leaked,
   and that Docker leaves no containers, images or volumes behind after the documented cleanup.
5. Lecturer rehearsal: `make lecture-up` with a test `.env`; run every `solve.py` against it and
   submit the results to the checker; confirm real flags are accepted, default flags are recognised as
   local, and no real flag occurs in the student bundle.
6. Follow `install-linux.md` in a clean container; `install-windows.md` cannot be executed here and is
   marked as not machine-verified unless the author tests it.
7. Every console block on slides and in write-ups is re-checked against a real run.

## 9. Order of work and risks

Order: Phase 1 tooling → toolbox → checker → tasks in lecture order (independent of each other, can be built in
parallel) → write-ups → slides (they quote real ports, file names and command output, so they come after
the tasks) → export and clean-room test. First step of all: confirm the Docker daemon is usable here.

| Risk | Mitigation |
|---|---|
| 60 minutes for six tasks is tight | one or two flags per task in class, lecturer-led; the rest is homework by design |
| Tool installation eats class time | toolbox image; bundle and "prepare before the lecture" note sent in advance |
| Classroom network | services are lecturer-hosted, so students need no builds in class; the bundle and toolbox image are sent in advance |
| Shared services disturbed by one student | stateless, limited containers; quick reset with `make lecture-up` |
| Toolbox image too large to distribute | measure after build; CLI tools only |
| Windows manual not testable on this machine | flagged in the manual; author tests once |
| Links rot or are inaccessible | verify at implementation, prefer stable roots over deep links |
| Real flags leak into the bundle or Git | `.env` git-ignored; export scans the bundle for real flags and fails |

## 10. Open points

- Q7: lecturer name, organization and year for the title slide.
- The lecturer's LAN address is needed only at lecture time (`.env`), not for implementation.
