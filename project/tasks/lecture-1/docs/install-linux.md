# Установка инструментов на Linux

Инструменты для заданий ставятся прямо в систему. Подходит для Kali, Debian и Ubuntu
(команды — для ОС с `apt`).

Почти всё устанавливается из репозиториев; после каждой группы команд установки приведены команды проверки 
корректности установки инструментов.

## Docker

```console
$ sudo apt update
$ sudo apt install -y docker.io docker-compose-plugin
$ sudo systemctl enable --now docker
$ sudo usermod -aG docker "$USER"   # затем перелогиньтесь или выполните newgrp docker
```

Проверка:

```console
$ docker run --rm hello-world
```

## Базовые утилиты

```console
$ sudo apt install -y file xxd zip unzip p7zip-full python3 python3-pip
```

Проверка: `python3 --version`.

## web — «Портал»

```console
$ sudo apt install -y curl
```

Проверка: `curl -I http://example.com`. Браузер с инструментами разработчика
(DevTools) — в любой системе уже есть (Firefox, Chromium).

## crypto — «Шифратор»

```console
$ pip3 install --user pycryptodome
```

Проверка: `python3 -c "from Crypto.Cipher import AES; print('ok')"`. `base64` и `xxd`
входят в базовые утилиты.

## forensics — «Резервная копия»

```console
$ sudo apt install -y tshark fcrackzip john
```

(GUI Wireshark — пакет `wireshark`.) Проверка:

```console
$ tshark --version | head -1
$ fcrackzip --help | head -1
```

> Словари паролей: пакет `john` ставит список `/usr/share/john/password.lst`; в Kali
> есть `rockyou.txt` (`/usr/share/wordlists/rockyou.txt.gz`).

## stego — «Открытка»

```console
$ sudo apt install -y libimage-exiftool-perl binwalk ruby
$ sudo gem install zsteg
$ pip3 install --user pillow
```

Проверка:

```console
$ exiftool -ver
$ zsteg --help | head -1
```

Графический `StegSolve` (Java) и онлайн-сервис `Aperi'Solve` — по желанию.

## reverse — «Пропуск»

```console
$ sudo apt install -y gdb binutils
$ pip3 install --user pyelftools
```

Проверка: `gdb --version | head -1`, `objdump --version | head -1`.
Дизассемблер `IDA` устанавливается отдельно, см. <https://hex-rays.com/ida-free>.

## pwn — «Турникет»

```console
$ sudo apt install -y socat
$ pip3 install --user pwntools
```

Проверка:

```console
$ socat -V | head -1
$ python3 -c "import pwn; print('ok')"
```
