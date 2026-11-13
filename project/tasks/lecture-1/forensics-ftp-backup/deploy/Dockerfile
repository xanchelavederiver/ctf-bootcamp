# Живой FTP-сервер «Резервная копия» (forensics). Скрытый флаг — через окружение.
FROM python:3.12-slim

RUN pip install --no-cache-dir "pyftpdlib==1.5.10"

RUN useradd --create-home --uid 10001 appuser
COPY srv/ /opt/srv/
COPY server.py /opt/server.py

USER appuser
EXPOSE 2121 30000-30009

CMD ["python3", "/opt/server.py"]
