# Установка инструментов на Linux

Альтернатива образу `ctf-toolbox`: поставить утилиты прямо в систему. Подходит для
Kali, Debian и Ubuntu (команды — для систем с `apt`). Если вы пользуетесь образом
`ctf-toolbox` (`toolbox.md`), этот файл не нужен.

Почти всё ставится из репозиториев; после каждой группы — команда «проверка»,
по которой видно, что инструмент на месте.

## Docker

```console
$ sudo apt update
$ sudo apt install -y docker.io docker-compose-plugin
$ sudo systemctl enable --now docker
$ sudo usermod -aG docker "$USER"   # затем перелогиньтесь
```

Проверка:

```console
$ docker run --rm hello-world
```

## Базовые утилиты

```console
$ sudo apt install -y curl file xxd zip unzip p7zip-full python3 python3-pip
```

Проверка: `curl --version` и `python3 --version`.

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

> `zip2john` в пакете Debian/Ubuntu отсутствует, поэтому пароль ZIP-архива подбирайте
> через `fcrackzip -D -p <словарь> -u archive.zip`. Словарь `rockyou.txt` есть в Kali
> (`/usr/share/wordlists/rockyou.txt.gz`), а в образе `ctf-toolbox` — список
> `/usr/share/john/password.lst`.

## stego — «Открытка»

```console
$ sudo apt install -y libimage-exiftool-perl binwalk ruby
$ sudo gem install zsteg
```

Проверка:

```console
$ exiftool -ver
$ zsteg --help | head -1
```

Графический `StegSolve` (Java) и онлайн-сервис `Aperi'Solve` — по желанию, для
просмотра битовых плоскостей.

## reverse — «Пропуск»

```console
$ sudo apt install -y gdb binutils
$ pip3 install --user pyelftools
```

Проверка: `gdb --version | head -1`, `objdump --version | head -1`. Декомпилятор
`Ghidra` ставится отдельно (нужна Java): страница проекта <https://ghidra-sre.org/>.

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
