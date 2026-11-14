# Пропуск

> Категория: reverse · Сложность: easy · 100 очков

Аудит ООО «Северный маяк» нашёл в архиве подрядчика маленькую утилиту проверки
пропусков `access-check`. Она спрашивает пропуск и отвечает `Access granted`
или `Access denied`. Говорят, у неё три рабочих пропуска, а не один. Найдите все три:
каждый пропуск — отдельный флаг.

**Файлы:** `public/access-check` — исполняемый файл ELF для Linux x86-64. Запуск:
`chmod +x access-check && ./access-check`, затем ввести пропуск.

**Инструменты:**

- отладчик `gdb` и `binutils` (`objdump`) — `sudo apt install gdb binutils`;
- дизассемблер [IDA Free](https://hex-rays.com/ida-free) — по желанию.

**Формат флага:** `BootCTF{...}`
