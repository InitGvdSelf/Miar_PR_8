FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY cleaning_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir prometheus-fastapi-instrumentator

COPY cleaning_service /app/cleaning_service

# ВАЖНО: поправь module:app под твой entrypoint
CMD ["sh", "-c", "uvicorn cleaning_service.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]