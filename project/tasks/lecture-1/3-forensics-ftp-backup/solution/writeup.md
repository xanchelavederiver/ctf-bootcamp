# Разбор: Резервная копия (forensics)

Дан дамп сетевого трафика `capture.pcapng` — один сеанс работы с FTP-сервером.
Понадобятся `tshark`, `unzip`, `fcrackzip` и словарь John. Удобнее всего открыть дамп в **Wireshark** (GUI) — здесь
для воспроизводимости показан равнозначный вывод `tshark`.

```console
$ file capture.pcapng
capture.pcapng: pcapng capture file - version 1.0
```

FTP-сервер слушает стандартный порт 21, поэтому Wireshark и `tshark` сами распознают
управляющий канал как FTP.

## Флаг 1 — открытый трафик FTP

Управляющий канал FTP передаётся открытым текстом. Видны и команды, и учётные данные:

```console
$ tshark -r capture.pcapng -Y ftp.request.command \
         -T fields -e ftp.request.command -e ftp.request.arg
USER   lighthouse
PASS   Harbor-2026
TYPE   A
PASV
LIST
TYPE   I
PASV
RETR   notes.txt
TYPE   I
PASV
RETR   backup.zip
QUIT
```

Файлы передаются по отдельным соединениям данных (после каждой `PASV`). Поток с
`notes.txt` читается напрямую — в Wireshark это `Follow TCP Stream`, в `tshark`:

```console
$ tshark -r capture.pcapng -q -z follow,tcp,ascii,2
...
Флаг смены: BootCTF{ftp_traffic_in_clear}
```

Первый флаг — `BootCTF{ftp_traffic_in_clear}`. (Кириллица в режиме `ascii` выводится
точками; в Wireshark выберите «Show data as → UTF-8», и текст заметки читается целиком.)

*Чему учит.* FTP, Telnet, HTTP без TLS передают данные открытым текстом. Любой, кто
видит трафик, читает и пароли, и файлы. Отсюда — повсеместный переход на FTPS/SFTP и HTTPS.

## Флаг 2 — комментарий архива

Сохраним второй поток данных как файл. В Wireshark — `Follow TCP Stream → Save as`;
в `tshark` поток собирается из полезной нагрузки TCP:

```console
$ tshark -r capture.pcapng -Y "tcp.stream==3 && tcp.len>0" -T fields -e tcp.payload \
    | tr -d '\n:' | xxd -r -p > backup.zip
$ file backup.zip
backup.zip: Zip archive data, at least v2.0 to extract, compression method=deflate
```

ZipCrypto шифрует только содержимое файлов. Имена и комментарий архива остаются
открытыми:

```console
$ unzip -z backup.zip
Archive:  backup.zip
BootCTF{zip_comment_not_encrypted}
$ zipinfo backup.zip
Zip file size: 263 bytes, number of entries: 1
-rw-r--r--  3.0 unx       36 TX defN 26-Nov-14 05:39 flag.txt
```

Комментарий архива — второй флаг: `BootCTF{zip_comment_not_encrypted}`.

*Чему учит.* Шифрование файла не прячет его метаданные. Имена файлов, их размеры и
комментарий архива видны и без пароля — это частый источник утечки.

## Флаг 3 — пароль архива по словарю

Сам `flag.txt` зашифрован. Пароль короткий и словарный — подберём его по словарю John:

```console
$ fcrackzip -D -p /usr/share/john/password.lst -u backup.zip

PASSWORD FOUND!!!!: pw == dragon
$ unzip -P dragon backup.zip
$ cat flag.txt
BootCTF{zip_password_from_wordlist}
```

Третий флаг — `BootCTF{zip_password_from_wordlist}`.

Классический путь — `zip2john backup.zip > hash` и затем `john --wordlist=... hash`.
В стенде используется `fcrackzip`, потому что в пакете Debian `john` нет утилиты
`zip2john` (она есть в полной сборке John Jumbo).

*Чему учит.* Короткий или словарный пароль не защищает архив: перебор (brute force) по
словарю занимает секунды. Стойкий пароль — длинный и несловарный.

---

## Домашнее задание / скрытый флаг

**Флаг 4 — каталог на живом сервере.** Пароль входа на FTP мы уже подслушали в дампе
(`lighthouse` / `Harbor-2026`). Если в аудитории поднят живой сервер, войдём на него и
осмотримся — в дампе сеанс забрал файлы только из корня, а по каталогам не ходил:

```console
$ python3 - <<'PY'
import ftplib, io
f = ftplib.FTP(); f.connect("<host>", 21); f.login("lighthouse", "Harbor-2026"); f.set_pasv(True)
f.retrlines("LIST")
f.cwd("archive/old"); f.retrlines("LIST")
b = io.BytesIO(); f.retrbinary("RETR handover.txt", b.write); print(b.getvalue().decode())
PY
drwxr-xr-x   3 appuser  appuser   60 archive
-rw-r--r--   1 appuser  appuser  263 backup.zip
-rw-r--r--   1 appuser  appuser  326 notes.txt
-rw-r--r--   1 appuser  appuser  113 handover.txt
Акт приёма-передачи смены.
Флаг дежурного: BootCTF{default_forensics_4}
```

На локальной копии флаг — `BootCTF{default_forensics_4}`; на боевом стенде
лектора он другой. То же можно сделать обычным клиентом `ftp <host>` и командами
`cd archive/old`, `get handover.txt`.

*Чему учит.* Повторное использование учётных данных и «забытые» каталоги — типичная
находка на реальных сервисах: один подслушанный пароль открывает больше, чем видно на
первый взгляд.

## Что дальше

Похожие задания — категория **Forensics** на picoCTF, а также учебные дампы из
документации Wireshark. Полезно потренироваться в `Follow TCP Stream`, экспорте
объектов HTTP и разборе других текстовых протоколов.
