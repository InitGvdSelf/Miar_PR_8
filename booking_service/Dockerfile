FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# зависимости
COPY booking_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir prometheus-fastapi-instrumentator

# код сервиса
COPY booking_service /app/booking_service

# ВАЖНО: поправь module:app под твой реальный entrypoint
# Пример для FastAPI: booking_service.app.main:app
CMD ["sh", "-c", "uvicorn booking_service.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]