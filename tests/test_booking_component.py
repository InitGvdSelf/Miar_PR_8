import os
import sys
from pathlib import Path

# Гарантируем, что корень проекта (папка PR7_MIAR) есть в sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Подменяем URL базы данных ДО импорта приложения
os.environ["POSTGRES_URL"] = "sqlite:///./test_booking.db"

from fastapi.testclient import TestClient

from booking_service.app.main import app
from booking_service.app.database import Base, engine, SessionLocal, get_db
from booking_service.app import rabbitmq as booking_rabbitmq
from booking_service.app import routers as booking_routers
from booking_service.app.models import Booking


# Создаём таблицы в тестовой SQLite-БД (если ещё не созданы)
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


# Подменяем зависимость FastAPI на тестовую БД
app.dependency_overrides[get_db] = override_get_db


# Глушим отправку сообщений в RabbitMQ во время тестов
async def dummy_send_booking_created(*args, **kwargs):
    # Ничего не делаем – просто заглушка
    return None


# подменяем и в модуле rabbitmq, и в модуле routers,
# чтобы background_tasks.add_task(send_booking_created, ...) использовал заглушку
booking_rabbitmq.send_booking_created = dummy_send_booking_created
booking_routers.send_booking_created = dummy_send_booking_created


# 5. Создаём TestClient
client = TestClient(app)


def clear_bookings():
    """
    Удаляем все бронирования из тестовой БД,
    чтобы каждый тест начинал с чистого состояния.
    """
    db = SessionLocal()
    try:
        db.query(Booking).delete()
        db.commit()
    finally:
        db.close()


# ====================== КОМПОНЕНТНЫЕ ТЕСТЫ ======================

def test_get_booking_returns_existing_booking():
    """
    Компонентный тест:
    создаём бронь через POST /api/bookings,
    затем получаем её через GET /api/bookings/{id}.
    """
    clear_bookings()

    payload = {
        "room_number": "301",
        "guest_name": "Тестер Тестов",
        "guests_count": 1,
        "check_in_date": "2025-11-20",
        "check_out_date": "2025-11-22",
    }

    create_resp = client.post("/api/bookings", json=payload)
    assert create_resp.status_code == 200

    created = create_resp.json()
    booking_id = created["id"]

    get_resp = client.get(f"/api/bookings/{booking_id}")
    assert get_resp.status_code == 200

    data = get_resp.json()
    assert data["id"] == booking_id
    assert data["room_number"] == payload["room_number"]
    assert data["guest_name"] == payload["guest_name"]
    assert data["guests_count"] == payload["guests_count"]


def test_cancel_booking_changes_status_only_for_target_booking():
    """
    Компонентный тест:
    создаём две брони, отменяем одну,
    проверяем что:
    - у нужной статус 'cancelled',
    - у второй бронь осталась 'created'.
    """
    clear_bookings()

    payload1 = {
        "room_number": "401",
        "guest_name": "Первый Гость",
        "guests_count": 2,
        "check_in_date": "2025-11-20",
        "check_out_date": "2025-11-23",
    }
    payload2 = {
        "room_number": "402",
        "guest_name": "Второй Гость",
        "guests_count": 1,
        "check_in_date": "2025-11-21",
        "check_out_date": "2025-11-24",
    }

    resp1 = client.post("/api/bookings", json=payload1)
    resp2 = client.post("/api/bookings", json=payload2)

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    booking1_id = resp1.json()["id"]
    booking2_id = resp2.json()["id"]

    cancel_payload = {
        "reason": "client_request",
        "comment": "Поменялись планы",
        "initiator": "guest",
    }

    cancel_resp = client.post(
        f"/api/bookings/{booking1_id}/cancel",
        json=cancel_payload,
    )
    assert cancel_resp.status_code == 200
    cancelled = cancel_resp.json()
    assert cancelled["id"] == booking1_id
    assert cancelled["status"] == "cancelled"

    # Первая бронь реально отменена
    get1 = client.get(f"/api/bookings/{booking1_id}")
    assert get1.status_code == 200
    assert get1.json()["status"] == "cancelled"

    # Вторая бронь должна остаться созданной
    get2 = client.get(f"/api/bookings/{booking2_id}")
    assert get2.status_code == 200
    assert get2.json()["status"] == "created"


def test_list_bookings_returns_all_created_bookings():
    """
    Компонентный тест:
    создаём две брони и проверяем, что
    GET /api/bookings возвращает обе.
    """
    clear_bookings()

    payload1 = {
        "room_number": "501",
        "guest_name": "Гость Один",
        "guests_count": 1,
        "check_in_date": "2025-11-20",
        "check_out_date": "2025-11-21",
    }
    payload2 = {
        "room_number": "502",
        "guest_name": "Гость Два",
        "guests_count": 3,
        "check_in_date": "2025-11-22",
        "check_out_date": "2025-11-25",
    }

    r1 = client.post("/api/bookings", json=payload1)
    r2 = client.post("/api/bookings", json=payload2)
    assert r1.status_code == 200
    assert r2.status_code == 200

    list_resp = client.get("/api/bookings")
    assert list_resp.status_code == 200

    data = list_resp.json()
    assert len(data) == 2

    room_numbers = {b["room_number"] for b in data}
    assert room_numbers == {payload1["room_number"], payload2["room_number"]}