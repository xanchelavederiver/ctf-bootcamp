# Образ инструментов `ctf-toolbox`

Чтобы не ставить десяток утилит по отдельности, все консольные инструменты для заданий
собраны в один образ Docker. Он поставляется файлом `toolbox/ctf-toolbox.tar.gz`
(около **1,4 ГБ**, архитектура **linux/amd64**).

Графических инструментов (Wireshark, Ghidra, StegSolve) в образе **нет** — их ставят
на основную систему по инструкциям `install-linux.md` / `install-windows.md`.

## Импорт

Из каталога, где лежит `toolbox/ctf-toolbox.tar.gz`:

```console
$ docker load -i toolbox/ctf-toolbox.tar.gz
$ docker images ctf-toolbox
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
ctf-toolbox   latest    ...            ...            1.39GB
```

## Запуск

Запускайте образ, примонтировав текущий каталог (с файлами заданий) в `/work`.
Флаг `--network host` даёт доступ к стенду преподавателя и к локальным сервисам:

```console
$ docker run --rm -it --network host -v "$PWD":/work -w /work ctf-toolbox bash
ctf@...:/work$ exiftool postcard.png
ctf@...:/work$ curl http://<host>:8001/
```

- `--rm` — удалить контейнер после выхода;
- `-it` — интерактивный терминал;
- `-v "$PWD":/work` — текущий каталог доступен внутри как `/work`;
- `--network host` — сеть как у вашей машины (нужно, чтобы дотянуться до `<host>` и до
  локальных портов 8001/8002/9001).

> **Примечание.** `--network host` работает на Linux (в том числе в WSL2). Файлы,
> изменённые внутри `/work`, остаются на диске и после выхода из контейнера.

## Что внутри

| Категория | Инструменты |
|---|---|
| web | `curl`, `python3` (`requests`) |
| crypto | `python3` (`pycryptodome`), `xxd`, `base64` |
| forensics | `tshark`, `tcpdump`, `fcrackzip`, `john`, `zip`/`unzip` |
| stego | `exiftool`, `zsteg`, `binwalk`, `xxd` |
| reverse | `gdb`, `objdump`, `strings`, `file`, `python3` (`pwntools`, `pyelftools`) |
| pwn | `python3` (`pwntools`), `socat`, `nc` |

Проверить состав можно так:

```console
$ docker run --rm ctf-toolbox bash -lc 'command -v curl tshark exiftool zsteg fcrackzip binwalk gdb socat'
$ docker run --rm ctf-toolbox python3 -c "import scapy, Crypto, PIL, pwn, requests; print('ok')"
```

> **`john`.** В образе он лежит в `/usr/sbin/john`. Для паролей ZIP-архивов проще
> использовать `fcrackzip` (в пакете Debian у `john` нет утилиты `zip2john`).

## Удаление

```console
$ docker rmi ctf-toolbox
```
