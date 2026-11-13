#!/usr/bin/env python3
"""Генератор backup.tar для задания «Шифратор» (флаг 3).

Воспроизводимо: фиксированное «время шифрования» T задаёт и ключ AES, и mtime
файлов в архиве (именно время создания выдаёт приблизительный момент шифрования).

Запуск в образе ctf-toolbox (там есть pycryptodome):
  docker run --rm --platform linux/amd64 -v "$PWD":/w -w /w ctf-toolbox \
      python3 -I src/generate.py
"""

from __future__ import annotations

import io
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # для запуска с python3 -I (каталог скрипта не в sys.path)
from encrypt import encrypt  # noqa: E402  соседний src/encrypt.py

TASK = HERE.parent
PUBLIC = TASK / "public"

# Фиксированный момент «шифрования»: 2026-11-01 09:30:00 UTC.
T = 1793525400
FLAG_3 = "BootCTF{aes_time_seed_recovered}"

REPORT = f"""АУДИТ БЕЗОПАСНОСТИ — ВНУТРЕННИЙ ОТЧЁТ
Объект: сервис «Шифратор», ООО «Северный маяк».

Найдено: ключ шифрования резервных копий выводится из системного времени.
Любой, кто знает приблизительное время создания файла, восстановит ключ перебором.

Внутренняя метка отчёта: {FLAG_3}
"""


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)
    scratch = Path("/tmp")
    report_txt = scratch / "report.txt"
    report_enc = scratch / "report.enc"
    report_txt.write_text(REPORT, encoding="utf-8")
    # Шифруем фиксированным временем T (так результат воспроизводим).
    encrypt(str(report_txt), str(report_enc), seconds=T)

    # Собираем tar: encrypt.py (инструмент) + report.enc (шифртекст). Оба с mtime = T.
    enc_bytes = report_enc.read_bytes()
    tool_bytes = (HERE / "encrypt.py").read_bytes()

    tar_path = PUBLIC / "backup.tar"
    with tarfile.open(tar_path, "w") as tar:
        for name, data in (("encrypt.py", tool_bytes), ("report.enc", enc_bytes)):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = T
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = "lighthouse"
            tar.addfile(info, io.BytesIO(data))

    # Промежуточные файлы в репозиторий не кладём.
    report_txt.unlink()
    report_enc.unlink()
    print(f"Записан {tar_path.relative_to(TASK)} (T={T}, flag3={FLAG_3})")


if __name__ == "__main__":
    main()
