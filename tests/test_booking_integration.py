import os

# 1. Подменяем URL базы данных ДО импорта приложения
os.environ["POSTGRES_URL"] = "sqlite:///./test_booking.db"

from fastapi.testclient import TestClient

from booking_service.app.main import app
from booking_service.app.database import Base, engine, SessionLocal, get_db
from booking_service.app import rabbitmq as booking_rabbitmq
from booking_service.app import routers as booking_routers


# 2. Создаём таблицы в тестовой SQLite-БД
Base.metadata.create_all(bind=engine)


def override_get_db():
    """
    Тестовая версия зависимости get_db:
    используем SessionLocal, который смотрит в SQLite.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 3. Подменяем зависимость FastAPI на тестовую БД
app.dependency_overrides[get_db] = override_get_db


# 4. Глушим отправку сообщений в RabbitMQ во время тестов
async def dummy_send_booking_created(*args, **kwargs):
    # Ничего не делаем – просто заглушка
    return None


# подменяем и в модуле rabbitmq, и в модуле routers,
# чтобы background_tasks.add_task(send_booking_created, ...) использовал заглушку
booking_rabbitmq.send_booking_created = dummy_send_booking_created
booking_routers.send_booking_created = dummy_send_booking_created


# 5. Создаём TestClient
client = TestClient(app)


def test_create_booking_success():
    """
    Интеграционный тест:
    вызываем POST /api/bookings и проверяем,
    что бронь создаётся и total_price считается корректно.
    """

    payload = {
        "room_number": "101",
            "guest_name": "Иван Иванов",
            "guests_count": 2,
            "check_in_date": "2025-11-20",
            "check_out_date": "2025-11-23"
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["room_number"] == "101"
    assert data["guest_name"] == "Иван Иванов"

    # 3 ночи, 2 гостя:
    # базовая цена 3000 за ночь
    # + 500 за второго гостя
    # (3000 + 500) * 3 = 10500
    assert data["total_price"] == 10500
    assert data["status"] == "created"


def test_create_booking_invalid_dates():
    """
    Интеграционный тест:
    проверяем, что при некорректных датах (0 ночей)
    сервис возвращает 400 и сообщение об ошибке.
    """

    payload = {
        "room_number": "102",
        "guest_name": "Петр Петров",
        "guests_count": 1,
        "check_in_date": "2025-11-20",
        "check_out_date": "2025-11-20"
    }

    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Некорректный диапазон дат" in data["detail"]