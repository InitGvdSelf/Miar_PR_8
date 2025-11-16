from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from booking_service.app.main import app
from booking_service.app.database import Base, get_db


# -----------------------------
# Настраиваем тестовую БД (SQLite in-memory)
# -----------------------------

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# создаём таблицы в тестовой БД
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# подменяем зависимость FastAPI на тестовую БД
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# -----------------------------
# Интеграционные тесты
# -----------------------------

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