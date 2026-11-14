# Установка на Windows

На Windows задания удобнее решать в среде Linux внутри **WSL2**, а консольные
инструменты ставить там же, как на Linux. Графические инструменты ставятся отдельными
установщиками для Windows.

## 1. WSL2

WSL2 (Windows Subsystem for Linux) запускает настоящее ядро Linux внутри Windows.

1. Откройте PowerShell от имени администратора и выполните:

   ```powershell
   wsl --install -d Ubuntu
   ```

   Команда включает нужные компоненты и ставит дистрибутив Ubuntu. Если WSL уже стоял —
   обновите: `wsl --update`.
2. Перезагрузите компьютер, запустите «Ubuntu» из меню «Пуск», задайте имя пользователя
   и пароль.
3. Проверьте версию: в PowerShell `wsl -l -v` — у дистрибутива должно стоять `VERSION 2`.

Официальная инструкция: <https://learn.microsoft.com/windows/wsl/install>.

## 2. Docker Desktop

1. Скачайте Docker Desktop для Windows: <https://www.docker.com/products/docker-desktop/>.
2. При установке оставьте включённым пункт про использование WSL2.
3. После установки в настройках Docker Desktop (Settings → Resources → WSL integration)
   включите интеграцию с вашим дистрибутивом Ubuntu.
4. Проверьте — уже внутри Ubuntu (WSL2):

   ```console
   $ docker run --rm hello-world
   ```

## 3. Инструменты

Дальше работайте **внутри WSL2 (Ubuntu)** так же, как на Linux:

поставьте утилиты по инструкции `install-linux.md`.

Файлы заданий держите в домашнем каталоге WSL (например, `~/ctf`), а не на диске
Windows через `/mnt/c` — так быстрее и меньше проблем с правами.

## 4. Графические инструменты (установщики Windows)

Эти программы ставятся обычными установщиками Windows и запускаются как есть:

- **Wireshark** — анализ дампа трафика (forensics): <https://www.wireshark.org/download.html>.
- **IDA** — дизассемблер (reverse): <https://hex-rays.com/ida-free>.
- **StegSolve** — анализ изображений (stego), запускается через
  Java: ищите `Stegsolve.jar` на известных страницах по стеганографии. Альтернатива без
  установки — онлайн-сервис **Aperi'Solve** (<https://www.aperisolve.com/>).

> Консольные инструменты (`tshark`, `zsteg`, `fcrackzip`, `gdb`, `pwntools`, `socat`
> и прочие) ставьте в WSL2, а не в Windows напрямую.
