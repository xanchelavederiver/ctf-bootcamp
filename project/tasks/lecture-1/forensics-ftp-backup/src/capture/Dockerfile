# Образ только для генерации capture.pcapng (не входит в стенд).
# Берём ctf-toolbox (tcpdump, editcap, zip, python) и добавляем FTP-сервер.
FROM ctf-toolbox:latest
USER root
RUN pip3 install --no-cache-dir --break-system-packages pyftpdlib
WORKDIR /work
