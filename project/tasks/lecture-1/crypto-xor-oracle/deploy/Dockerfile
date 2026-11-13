# «Шифратор» (crypto). Python-сервер на Flask; флаги и ключ — через окружение.
FROM python:3.12-slim

RUN pip install --no-cache-dir "flask==3.0.3" "gunicorn==22.0.0"

RUN useradd --create-home --uid 10001 appuser
WORKDIR /opt/oracle
COPY app/ /opt/oracle/

USER appuser
EXPOSE 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "--workers", "1", "--threads", "4", "app:app"]
