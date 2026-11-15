# «Шифратор» (crypto). Python-сервер на Flask; флаги и ключ — через окружение.
FROM python:3.12-slim

RUN pip install --no-cache-dir "flask==3.0.3" "gunicorn==22.0.0"

RUN useradd --create-home --uid 10001 appuser
COPY watchdog.py /usr/local/bin/watchdog.py
WORKDIR /opt/oracle
COPY app/ /opt/oracle/

USER appuser
EXPOSE 8002

# Наружу сервис публикуется через nginx (proxy).
# watchdog.py перезапускает контейнер, если gunicorn перестал отвечать.
CMD ["python3", "/usr/local/bin/watchdog.py", \
     "gunicorn", "--bind", "0.0.0.0:8002", "--preload", \
     "--workers", "3", "--threads", "8", "--graceful-timeout", "5", "app:app"]
