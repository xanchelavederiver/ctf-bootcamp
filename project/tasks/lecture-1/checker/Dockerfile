# Проверщик флагов (запускает только лектор). Коллекция монтируется в /collection.
FROM python:3.12-slim
RUN pip install --no-cache-dir "flask==3.0.3" "pyyaml==6.0.2" "gunicorn==22.0.0"
RUN useradd --create-home --uid 10001 appuser
COPY app.py /opt/checker/app.py
WORKDIR /opt/checker
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app:app"]
