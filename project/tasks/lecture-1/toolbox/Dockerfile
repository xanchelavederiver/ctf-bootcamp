# ctf-toolbox — образ с консольными инструментами для заданий лекции 01-intro.
# Сборка:   make toolbox-build
# Экспорт:  make toolbox-export   (public/export/01-intro/toolbox/ctf-toolbox.tar.gz)
# Запуск у студента описан в docs/toolbox.md.
#
# Графические инструменты (Wireshark GUI, Ghidra, StegSolve) в образ не входят —
# они ставятся на хост по инструкциям docs/install-*.md.
FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget netcat-openbsd socat ftp \
        python3 python3-pip python3-venv \
        tshark tcpdump \
        exiftool binwalk unzip zip p7zip-full xxd \
        john fcrackzip \
        ruby ruby-dev build-essential \
        binutils file gdb ltrace strace \
        ruby-rubygems \
    && rm -rf /var/lib/apt/lists/*

# В Debian john и сопутствующие утилиты лежат в /usr/sbin — добавляем в PATH.
ENV PATH="/usr/sbin:${PATH}"

# zsteg — анализ LSB в PNG; ставится как ruby-гем.
RUN gem install --no-document zsteg

# Python-библиотеки, используемые в разборах (solve.py).
# capstone фиксируем на 5.x: в 6.0 переименован CS_ARCH_ARM64 -> CS_ARCH_AARCH64,
# из-за чего ломается импорт binwalk (он рассчитан на API 5.x).
RUN pip3 install --no-cache-dir --break-system-packages \
        "capstone==5.0.1" requests pycryptodome pillow scapy pwntools

RUN useradd --create-home --uid 10001 ctf
WORKDIR /work
USER ctf

CMD ["bash"]
