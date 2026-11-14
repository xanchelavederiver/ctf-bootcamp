# «Портал» (web). Python-сервер на Flask; флаги задаются через окружение.
FROM python:3.12-slim

RUN pip install --no-cache-dir "flask==3.0.3" "gunicorn==22.0.0"

RUN useradd --create-home --uid 10001 appuser \
    && touch /flag.txt && chown appuser:appuser /flag.txt

COPY watchdog.py /usr/local/bin/watchdog.py
WORKDIR /opt/portal
COPY app/ /opt/portal/

USER appuser
EXPOSE 8001

# --preload: модуль приложения импортируется один раз в главном процессе, рабочие
# процессы получают его готовым. Наружу сервис публикуется через nginx (proxy).
# watchdog.py перезапускает контейнер, если gunicorn перестал отвечать.
CMD ["python3", "/usr/local/bin/watchdog.py", \
     "gunicorn", "--bind", "0.0.0.0:8001", "--preload", \
     "--workers", "3", "--threads", "8", "--graceful-timeout", "5", "app:app"]
