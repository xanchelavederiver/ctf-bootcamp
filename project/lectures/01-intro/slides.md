---
marp: true
theme: ctf-academic
lang: ru
paginate: true
title: Введение в CTF
author: Мини-курс «Введение в CTF»
---

<!-- _class: title -->
<!-- _paginate: false -->

# Лекция 1

## Введение в CTF

Мини-курс «Введение в CTF»
Лектор · организация · 2026

<!--
90 минут: около 25 минут — вводная часть, около 60 — короткий CTF из шести заданий
(по одному на категорию). Главная мысль: задание CTF — небольшая законная модель
настоящей проблемы безопасности.
Заполнить на титуле имя лектора, организацию и год перед сборкой.
-->

---

# CTF — соревнование, где ответ — скрытая строка

**CTF (Capture the Flag)** — соревнования по практической информационной безопасности.

- ответ на задание — **флаг (flag)**: строка, спрятанная в уязвимом сервисе или файле;
- у флага фиксированный формат, у нас — `BootCTF{...}`;
- проверка мгновенна и однозначна: флаг либо принят, либо нет;
- после соревнования публикуют **разборы (write-up)** — по ним удобно учиться.

> Флаг — доказательство, что уязвимость не только найдена, но и доведена до результата.

<!--
Увидели строку вида BootCTF{...} — вы у цели. Зачем участвовать: практика в законной
среде, быстрая обратная связь, распространённый вход в профессию.
-->

---

# Два формата: решать задания или защищать сервисы

<div class="cols">
<div>

**Task-based (jeopardy)**

- независимые задания по категориям;
- за каждое — флаг и очки;
- можно решать в одиночку.

Наш практикум — этого формата.

</div>
<div>

**Attack-defense (AD)**

- у каждой команды одинаковый уязвимый сервис;
- свой защищают, чужие атакуют;
- нужны команда и инфраструктура.

На вводном курсе не разбираем.

</div>
</div>

<div class="note">

Очки зависят от сложности: чем меньше команд решило задание, тем оно обычно дороже.
Календарь соревнований и рейтинг — [CTFtime](https://ctftime.org/) и [CTF News](https://ctfnews.ru/calendar/).

</div>

<!--
Часто отборочный тур проходит в формате task-based, а финал — AD. Схему начисления очков
задаёт организатор: перед соревнованием читайте правила.
-->

---

# Шесть категорий — и где учиться каждой

| Категория | О чём задания | На русском | Международный ресурс |
|---|---|---|---|
| `web` | уязвимости веб-приложений | [SPbCTF Web Kids](https://web-kids20.forkbomb.ru/) | [PortSwigger Academy](https://portswigger.net/web-security) |
| `crypto` | слабые шифры, ошибки использования | [SPbCTF Crypto Kids](https://crypto-kids20.forkbomb.ru/) | [CryptoHack](https://cryptohack.org/) |
| `forensics` | дампы трафика, образы, файлы | [SPbCTF Forensics Kids](https://for-kids20.forkbomb.ru/) | [Wireshark](https://www.wireshark.org/docs/) |
| `stego` | данные, скрытые в изображении | [SPbCTF Forensics Kids](https://for-kids20.forkbomb.ru/) | [zsteg](https://github.com/zed-0xff/zsteg) |
| `reverse` | анализ программы без исходного кода | [SPbCTF Reverse Kids](https://rev-kids20.forkbomb.ru/) | [Ghidra](https://github.com/NationalSecurityAgency/ghidra) |
| `pwn` | переполнения, перехват управления | [SPbCTF Pwn](https://pwn.spbctf.ru/tasks) | [pwn.college](https://pwn.college/dojos) |

Категория определяет приём, которым добывается флаг. Бывают и другие: `osint`, `misc`.

<!--
Эти шесть категорий — костяк почти любого task-based CTF и структура практикума:
по одному заданию на каждую.
-->

---

# Приёмы законны только на разрешённых целях

- **Можно:** учебные задания, свои стенды, площадки, которые сами приглашают к атаке.
- **Нельзя:** чужие сайты, сервисы и устройства без письменного разрешения владельца.

> **Правило курса.** Нашли похожую уязвимость в реальном сервисе — не проверяйте её, а сообщите владельцу.

<!--
Разница не в приёме, а в том, есть ли разрешение на цель. Говорим один раз и дальше
не повторяем.
-->

---

# Те же навыки тренируют не только на CTF

| Формат | Что это | Пример |
|---|---|---|
| wargames | уровни с нарастающей сложностью | [OverTheWire](https://overthewire.org/wargames/) |
| учебные машины | уязвимая система, цель — права `root` | [TryHackMe](https://tryhackme.com/free-rooms), [Hack The Box](https://academy.hackthebox.com/) |
| киберполигон | модель инфраструктуры предприятия | [Standoff 365](https://standoff365.com/) |
| bug bounty | поиск уязвимостей за вознаграждение | только по правилам программы |

<!--
CTF даёт отдельный приём в чистом виде, учебные машины — цепочку от разведки до root,
киберполигон — ещё и защиту. Всё это — продолжение после вводного курса.
-->

---

# С чего начать: пять ресурсов

- [**CyLab Security Academy**](https://cylabacademy.org/) (бывший picoCTF) — учебные маршруты и набор заданий по всем категориям; начните с [CTF Primer](https://primer.cylabacademy.org/).
- [**SPbCTF / Forkbomb**](https://forkbomb.ru/) — на русском: учебные сезоны, задания и записи разборов.
- [**30.ctf.su**](https://30.ctf.su/tasks) — на русском: короткие разминочные задания.
- [**CTF 101**](https://ctf101.org/) — краткий справочник по форматам, категориям и инструментам.
- [**Codeby Academy**](https://codeby.academy/) — на русском: курсы по безопасности (многие платные).

<!--
Слайд, который стоит сфотографировать. Полный список ссылок — на слайдах «Источники»
в конце колоды.
-->

---

# Дальше — по шагам

1. **Командная строка:** первые 10–15 уровней [OverTheWire Bandit](https://overthewire.org/wargames/bandit/).
2. **Первые флаги:** простые задания [CyLab](https://cylabacademy.org/), [SPbCTF](https://forkbomb.ru/), [30.ctf.su](https://30.ctf.su/tasks).
3. **Категории:** [CyberChef](https://gchq.github.io/CyberChef/), [CryptoHack](https://cryptohack.org/courses/intro/), [PortSwigger Academy](https://portswigger.net/web-security).
4. **Программы и память:** вводные модули [pwn.college](https://pwn.college/dojos).
5. **Соревнование:** календари [CTF News](https://ctfnews.ru/calendar/) и [CTFtime](https://ctftime.org/).

<div class="note">

Сначала решайте сами, потом читайте разборы. Записывайте гипотезы, команды и результаты.
Основы безопасности на русском — [курс HackerDom](https://ulearn.me/Course/Hackerdom).

</div>

<!--
Не ставьте все инструменты сразу: командная строка, Python и инструменты разработчика
в браузере покрывают первые задания.
-->

---

# Стенд: каждое задание — контейнер Docker

<div class="cols c-3-2">
<div>

```console
$ cd 1-web-portal/deploy
$ docker compose up --build
...
web-portal-1  | Listening at: http://0.0.0.0:8001
```

```console
$ docker compose down        # остановить
$ docker compose down -v     # и удалить данные
```

</div>
<div>

- на лекции сервисы с боевыми флагами поднимает лектор;
- у себя те же задания — с учебными флагами;
- Docker нужен только для заданий с сервисом.

</div>
</div>

Инструменты ставятся в систему: `docs/install-linux.md`, `docs/install-windows.md`.

<!--
Показать вживую: поднять web-портал, открыть в браузере, затем down. Флаги проверяет
проверочный сервис лектора; он же показывает, сколько флагов в каждом задании.
-->

---

# web «Портал»: типовые промахи веб-приложения

**Доступ:** `http://<хост>:8001` · **Инструменты:** браузер, `curl`, `base64`

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | исходный код главной страницы | строка в `base64` в комментарии |
| 2 | файл `app.js` | сочетание клавиш запускает обработчик |
| 3 | служебный API из `robots.txt` | запрос нужным методом и с заголовком |
| 4 | страница приветствия `/hello` | ввод подставляется в шаблон на сервере |

<div class="warn">

**Дома.** В задании спрятано ещё два флага — ищите глубже.

</div>

<!--
Легенда всех заданий — аудит вымышленной компании «Северный маяк». Флаг 4 — внедрение
в шаблон (SSTI): /hello?name={{7*7}} даёт 49, дальше {{config}}. Скрытые флаги:
заголовок ответа и выход к выполнению кода.
-->

---

# crypto «Шифратор»: шифрование с ошибками

**Доступ:** `http://<хост>:8002`, файл `backup.tar` · **Инструменты:** `curl`, `base64`, Python, [CyberChef](https://gchq.github.io/CyberChef/)

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | «сообщение дня» на главной | шифр Цезаря: перебрать 25 сдвигов |
| 2 | `GET /flag` и `POST /encrypt` | XOR с повторно используемым ключом |
| 3 | файл `backup.tar` | ключ AES выведен из времени создания файла |

<div class="warn">

**Дома.** Флаг 3 и ещё один, скрытый.

</div>

<!--
На лекции — флаги 1 и 2. Флаг 2: отправив нули, получаем сам ключ. base64 в теле запроса
отправлять через curl --data-urlencode. Скрытый флаг — повтор ключа на /archive.
-->

---

# forensics «Резервная копия»: разбор дампа трафика

**Доступ:** файл `capture.pcapng`, FTP `<хост>:21` · **Инструменты:** Wireshark, `unzip`, `fcrackzip`

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | `notes.txt` в дампе | файл передан открытым текстом |
| 2 | архив `backup.zip` из дампа | комментарий архива не шифруется |
| 3 | файл внутри `backup.zip` | пароль архива — по словарю |

<div class="warn">

**Дома.** Флаг 3 и каталог на живом сервере, в который сеанс из дампа не заходил.

</div>

<!--
FTP передаёт логин, пароль и файлы открытым текстом. Показать Follow TCP Stream и
unzip -z. Логин и пароль из дампа открывают живой сервер; скрытый флаг — в archive/old.
-->

---

# stego «Открытка»: данные, скрытые в изображении

**Доступ:** файл `postcard.png` · **Инструменты:** `exiftool`, `zsteg`, StegSolve

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | метаданные PNG | текстовое поле `tEXt` (`exiftool`) |
| 2 | битовая плоскость красного канала | текст виден в нулевой плоскости |
| 3 | младшие биты синего канала | извлечь **LSB** по строкам (`zsteg`) |

<div class="warn">

**Дома.** После `IEND` в файл дописан архив — найдите его.

</div>

<!--
Порядок: exiftool, просмотр плоскостей, zsteg. Скрытый флаг — zip после маркера конца
PNG; zsteg предупреждает о лишних данных, binwalk извлекает.
-->

---

# reverse «Пропуск»: программа без исходного кода

**Доступ:** файл `access-check` (ELF x86-64) · **Инструменты:** `strings`, `gdb`, Ghidra

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | строки файла | сравнение с открытой строкой (`strings`) |
| 2 | память при запуске | строка расшифровывается до `main` (`gdb`) |
| 3 | сравнения в дизассемблере | цепочка проверок по одному символу |

<div class="warn">

**Дома.** Флаг 3: только статический анализ — читать условия сравнения в Ghidra.

</div>

<!--
Статический анализ (strings, Ghidra) — что программа может сделать; динамический (gdb) —
что она делает при запуске. На лекции — флаги 1 и 2 (точка останова в main).
-->

---

# pwn «Турникет»: переполнение буфера на стеке

**Доступ:** `nc <хост> 9001`, программа `gatekeeper` с исходным кодом · **Инструменты:** `pwntools`, `gdb`, `checksec`

| Флаг | Где искать | Приём |
|---|---|---|
| 1 | вывод программы после переполнения | переписать адрес возврата на функцию флага |

1. `checksec` — какие защиты отключены.
2. Найти смещение до адреса возврата (циклический образец `pwntools`).
3. Отправить «заполнитель + адрес функции флага».

<div class="warn">

**Ограничение.** Канарейка и PIE отключены намеренно; на реальных целях защиты включены.

</div>

<!--
Показать весь путь: небезопасное чтение в исходном коде, checksec, поиск смещения,
короткий скрипт pwntools. Дальше в категории — обход канарейки, ASLR, ROP.
-->

---

# Выводы

- **CTF — законная модель настоящих проблем безопасности:** ломать можно только учебные цели и свои стенды.
- **Категория — это приём:** исходный код и SSTI, XOR, разбор трафика, LSB, статический и динамический анализ, переполнение буфера.
- **Каждый приём вы уже попробовали руками.**

> **Домашняя работа.** Доведите начатые флаги до конца и найдите скрытые: проверочный сервис показывает, сколько флагов в каждом задании.

<!--
Разборы для студентов лектор выдаёт позже.
-->

---

<!-- _class: sources -->

# Источники: общие материалы и площадки

<div class="cols">
<div>

**Обучение и методика**

- Codeby Academy (рус.) — <https://codeby.academy/>
- Курс HackerDom (рус.) — <https://ulearn.me/Course/Hackerdom>
- Курс CTF МФТИ (рус.) — <https://github.com/xairy/mipt-ctf>
- Материалы ВШЭ (рус.) — <https://vsosh.miem.hse.ru/prepare>
- CTF 101 — <https://ctf101.org/>
- CyLab Primer — <https://primer.cylabacademy.org/>
- CTF Wiki — <https://ctf-wiki.org/en/>
- CTF Field Guide — <https://trailofbits.github.io/ctf/>
- HackTricks — <https://book.hacktricks.wiki/>
- Python Tutorial — <https://docs.python.org/3/tutorial/>

</div>
<div>

**Площадки и wargames**

- SPbCTF / Forkbomb (рус.) — <https://forkbomb.ru/>
- 30.ctf.su (рус.) — <https://30.ctf.su/tasks>
- Архив HackerDom (рус.) — <https://2019.hackerdom.ru/>
- TaipanByte CTF (рус.) — <https://ctf.taipanbyte.ru/>
- DUCKERZ (рус.) — <https://duckerz.ru/>
- HackerLab (рус.) — <https://hackerlab.pro/>
- CyLab Security Academy — <https://cylabacademy.org/>
- OverTheWire — <https://overthewire.org/wargames/>
- Root-Me — <https://www.root-me.org/>
- pwn.college — <https://pwn.college/dojos>
- TryHackMe — <https://tryhackme.com/free-rooms>
- Hack The Box Academy — <https://academy.hackthebox.com/>

</div>
</div>

---

<!-- _class: sources -->

# Источники: web, crypto, forensics и stego

<div class="cols">
<div>

**Web**

- SPbCTF Web Kids (рус.) — <https://web-kids20.forkbomb.ru/>
- HackerDom SQL Training (рус.) — <https://sql.training.hackerdom.ru/>
- Stepik, «Аудит безопасности веб-проектов» (рус.) — <https://stepik.org/course/127>
- PortSwigger Academy — <https://portswigger.net/web-security>
- OWASP Testing Guide — <https://wstg.owasp.org/>
- OWASP Juice Shop — <https://juice-shop.github.io/>
- OWASP WebGoat — <https://owasp.org/projects/webgoat>
- OWASP Top 10 — <https://owasp.org/projects/top-ten>
- MDN HTTP — <https://developer.mozilla.org/en-US/docs/Web/HTTP>

</div>
<div>

**Crypto**

- SPbCTF Crypto Kids (рус.) — <https://crypto-kids20.forkbomb.ru/>
- CryptoHack — <https://cryptohack.org/>
- Cryptopals — <https://cryptopals.com/>
- CyberChef — <https://gchq.github.io/CyberChef/>

**Forensics и stego**

- SPbCTF Forensics Kids (рус.) — <https://for-kids20.forkbomb.ru/>
- Wireshark — <https://www.wireshark.org/docs/>
- ExifTool — <https://exiftool.org/>
- Binwalk — <https://github.com/ReFirmLabs/binwalk>
- Volatility 3 — <https://volatility3.readthedocs.io/en/latest/>
- Autopsy — <https://www.autopsy.com/>
- zsteg — <https://github.com/zed-0xff/zsteg>

</div>
</div>

---

<!-- _class: sources -->

# Источники: reverse, pwn, сообщество

<div class="cols">
<div>

**Reverse**

- SPbCTF Reverse Kids (рус.) — <https://rev-kids20.forkbomb.ru/>
- Ghidra — <https://github.com/NationalSecurityAgency/ghidra>
- GDB — <https://sourceware.org/gdb/documentation/>
- OpenSecurityTraining2, x86-64 Assembly — <https://p.ost2.fyi/courses/course-v1:OpenSecurityTraining2+Arch1001_x86-64_Asm+2021_v1/>

**Pwn**

- SPbCTF Pwn (рус.) — <https://pwn.spbctf.ru/tasks>
- ROP Emporium — <https://ropemporium.com/>
- Exploit Education, Phoenix — <https://exploit.education/phoenix/>
- pwntools — <https://docs.pwntools.com/en/stable/>
- Pwndbg — <https://github.com/pwndbg/pwndbg>

</div>
<div>

**Сообщество и соревнования**

- CTF News (рус.) — <https://ctfnews.ru/>
- Календарь CTF News (рус.) — <https://ctfnews.ru/calendar/>
- Каталог ресурсов CTF News (рус.) — <https://ctfnews.ru/news/tools/>
- Кубок CTF России — <https://ctfcup.ru/>
- RuCTF — <https://ructf.org/>
- HackerDom — <https://hackerdom.ru/>
- Standoff 365 — <https://standoff365.com/>
- CTFtime — <https://ctftime.org/>

**OSINT**

- Bellingcat Toolkit — <https://github.com/bellingcat/toolkit>

</div>
</div>
