# «Портал» (web). Python-сервер на Flask; флаги задаются через окружение.
FROM python:3.12-slim

RUN pip install --no-cache-dir "flask==3.0.3" "gunicorn==22.0.0"

RUN useradd --create-home --uid 10001 appuser \
    && touch /flag.txt && chown appuser:appuser /flag.txt

WORKDIR /opt/portal
COPY app/ /opt/portal/

USER appuser
EXPOSE 8001

# Один рабочий процесс: приложение инициализирует своё состояние при импорте модуля.
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "1", "--threads", "4", "app:app"]
