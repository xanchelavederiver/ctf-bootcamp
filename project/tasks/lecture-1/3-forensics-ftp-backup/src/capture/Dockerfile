# Образ только для генерации capture.pcapng (не входит в стенд); запуск — docker-compose.yml.
# Нужны tcpdump, editcap (пакет tshark), zip, python и FTP-сервер pyftpdlib.
FROM debian:12-slim
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip tcpdump tshark zip \
    && apt-get clean
RUN pip3 install --no-cache-dir --break-system-packages pyftpdlib
WORKDIR /work
