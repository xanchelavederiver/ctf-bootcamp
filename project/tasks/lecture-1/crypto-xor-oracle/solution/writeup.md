# Разбор: Шифратор (crypto)

Служба «Северного маяка» отвечает по HTTP на `http://<host>:8002/`. Всё решается
`curl` и `base64`; для резервной копии понадобится Python с `pycryptodome`.
В примерах ниже — локальная копия с учебными флагами (`BootCTF{default_...}`);
на стенде лектора флаги другие, но действия те же.

Главная страница перечисляет конечные точки и показывает «сообщение дня».

## Флаг 1 — шифр Цезаря

«Сообщение дня» выглядит как искажённый флаг: буквы перемешаны, а фигурные скобки
и подчёркивания на месте.

```console
$ curl -s http://127.0.0.1:8002/ | grep -o 'Сообщение дня:</b> <code>[^<]*</code>'
Сообщение дня:</b> <code>IvvaJAM{klmhbsa_jyfwav_jhlzhy_tvak}</code>
```

Сохранённая структура `XXXXXXX{...}` подсказывает шифр Цезаря: каждая буква сдвинута
на одно и то же число позиций. Ключей всего 25 — переберём их и найдём тот, что даёт
префикс `BootCTF{`.

```console
$ python3 - 'IvvaJAM{klmhbsa_jyfwav_jhlzhy_tvak}' <<'PY'
import sys
m = sys.argv[1]
for k in range(1, 26):
    g = "".join(chr((ord(c)-97+k)%26+97) if 'a'<=c<='z'
                else chr((ord(c)-65+k)%26+65) if 'A'<=c<='Z' else c for c in m)
    if g.startswith("BootCTF{"):
        print(f"сдвиг {k}: {g}")
PY
сдвиг 19: BootCTF{default_crypto_caesar_motd}
```

**Чему учит.** Шифр Цезаря — простейший подстановочный шифр; малое пространство
ключей ломается полным перебором, а известный префикс служит критерием отбора.

## Флаг 2 — XOR-оракул

Конечная точка `/flag` отдаёт флаг, наложенный операцией XOR с секретным ключом
(в base64):

```console
$ curl -s http://127.0.0.1:8002/flag
9ZW7JSZCNUlgvN4PoipywlfxPRNMn8VTYAgf/eHgLdsPFQ==
```

Служба `/encrypt` накладывает тот же ключ на наши данные — но расшифровать сам флаг
отказывается:

```console
$ C=$(curl -s http://127.0.0.1:8002/flag)
$ curl -s -X POST --data-urlencode "data=$C" http://127.0.0.1:8002/encrypt
служба не выдаёт сам флаг
```

Это и есть подсказка. XOR обратим, и у него есть свойство `0 ⊕ k = k`: если
отправить на `/encrypt` нули, служба вернёт сам ключ. Узнаём длину шифртекста,
посылаем столько же нулевых байт и получаем ключ, а затем XOR ключа с шифртекстом
из `/flag` даёт флаг.

```console
$ C=$(curl -s http://127.0.0.1:8002/flag)
$ LEN=$(python3 -c "import base64;print(len(base64.b64decode('$C')))"); echo $LEN
34
$ NULLS=$(python3 -c "import base64;print(base64.b64encode(b'\x00'*$LEN).decode())")
$ KEY=$(curl -s -X POST --data-urlencode "data=$NULLS" http://127.0.0.1:8002/encrypt)
$ echo "$KEY"
t/rUUWUWczIE2bhu10YGnTSDRGM48JorD3pAkpOBTrdqaA==
$ python3 - "$C" "$KEY" <<'PY'
import base64, sys
c = base64.b64decode(sys.argv[1]); k = base64.b64decode(sys.argv[2])
print(bytes(a ^ b for a, b in zip(c, k)).decode())
PY
BootCTF{default_crypto_xor_oracle}
```

base64 здесь обязательно передавать через `--data-urlencode`: символы `+` и `/`
в обычной query-строке исказились бы.

**Чему учит.** XOR с ключом — не защита, если к ключу есть доступ. Оракул, готовый
шифровать что угодно тем же ключом, фактически выдаёт ключ целиком.

---

## Домашняя часть и скрытый флаг

### Флаг 3 — AES с ключом из времени (домашнее задание)

Выданный `public/backup.tar` содержит инструмент шифрования и зашифрованный отчёт:

```console
$ tar -tvf public/backup.tar
-rw-r--r-- lighthouse/lighthouse 1337 2026-11-01 09:30 encrypt.py
-rw-r--r-- lighthouse/lighthouse  560 2026-11-01 09:30 report.enc
```

Из `encrypt.py` видно, как получен `report.enc`:

```python
def derive_key(seconds: int) -> bytes:
    return hashlib.sha256(str(seconds).encode()).digest()   # ключ AES-256 из времени
...
    key = derive_key(seconds)
    iv  = hashlib.md5(str(seconds).encode()).digest()        # IV — тоже из времени
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(data, 16))
    open(path_out, "wb").write(iv + enc)                     # формат: IV ∥ шифртекст
```

Ключ и IV зависят только от числа секунд Unix-времени. Приблизительное время —
это дата создания файла в самом архиве (`2026-11-01 09:30 UTC` выше). Перебираем
секунды в окне ±5 минут, расшифровываем AES-CBC и оставляем вариант с корректным
дополнением PKCS#7 и подстрокой `BootCTF{`:

```console
$ python3 brute.py          # запущено в ctf-toolbox (есть pycryptodome)
mtime seconds=1793525400 = 2026-11-01 09:30:00 UTC
seed = 1793525400
АУДИТ БЕЗОПАСНОСТИ — ВНУТРЕННИЙ ОТЧЁТ
Объект: сервис «Шифратор», ООО «Северный маяк».
...
Внутренняя метка отчёта: BootCTF{aes_time_seed_recovered}
```

```python
# brute.py
import tarfile, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
with tarfile.open("public/backup.tar") as t:
    enc = t.extractfile("report.enc").read()
    mtime = int(t.getmember("report.enc").mtime)
iv, ct = enc[:16], enc[16:]
for s in range(mtime - 300, mtime + 301):
    key = hashlib.sha256(str(s).encode()).digest()
    if hashlib.md5(str(s).encode()).digest() != iv:
        continue
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
    except ValueError:
        continue
    if b"BootCTF{" in pt:
        print(s); print(pt.decode()); break
```

**Чему учит.** Криптографический ключ должен быть непредсказуем. Если он выводится
из времени (или любого угадываемого значения), перебор небольшого диапазона
восстанавливает ключ, несмотря на стойкий сам по себе AES.

### Флаг 4 — повтор ключа XOR (скрытый)

Кроме `/flag`, тот же ключ используется на `/archive`, но сообщение там **длиннее
ключа**, поэтому ключ повторяется:

```console
$ A=$(curl -s http://127.0.0.1:8002/archive)
$ ALEN=$(python3 -c "import base64;print(len(base64.b64decode('$A')))"); echo $ALEN
121
$ NULLS=$(python3 -c "import base64;print(base64.b64encode(b'\x00'*$ALEN).decode())")
$ KEY=$(curl -s -X POST --data-urlencode "data=$NULLS" http://127.0.0.1:8002/encrypt)
$ python3 - "$A" "$KEY" <<'PY'
import base64, sys, re
c = base64.b64decode(sys.argv[1]); k = base64.b64decode(sys.argv[2])
msg = bytes(a ^ b for a, b in zip(c, k)).decode("utf-8", "replace")
print(msg)
print("Флаг:", re.search(r"BootCTF\{[^}]+\}", msg).group())
PY
Spare access flag for the backup channel: BootCTF{default_crypto_xor_keyreuse}. Do not disclose the master key to anyone.
Флаг: BootCTF{default_crypto_xor_keyreuse}
```

Тем же приёмом с нулевыми байтами добывается полный ключ (нужной длины), и сообщение
расшифровывается целиком.

**Чему учит.** Повторное использование потокового ключа (гаммы) на разных или
длинных сообщениях — классическая ошибка: ключ «проступает» и восстанавливается.

---

**Куда двигаться дальше.** Похожие задания — в категории Crypto на picoCTF и на
тренажёре CryptoHack: классические шифры, XOR и повтор гаммы, атаки на блочные шифры.
