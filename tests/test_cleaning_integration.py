from fastapi.testclient import TestClient

from cleaning_service.app.main import app
from cleaning_service.app.storage import tasks, create_task_from_booking

client = TestClient(app)


def test_list_tasks_returns_created_tasks():
    """
    Интеграционный тест:
    создаём задачу напрямую через функцию create_task_from_booking,
    затем проверяем, что GET /api/tasks её возвращает.
    """
    tasks.clear()

    task = create_task_from_booking(
        booking_id="booking-123",
        room_number="301",
        check_out_date="2025-12-01",
    )

    response = client.get("/api/tasks")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    item = data[0]
    assert item["id"] == task.id
    assert item["room_number"] == "301"
    assert item["booking_id"] == "booking-123"
    assert item["status"] == "pending"


def test_update_task_status_via_api():
    """
    Интеграционный тест:
    создаём задачу, затем меняем её статус через PATCH /api/tasks/{task_id}/status.
    """
    tasks.clear()

    task = create_task_from_booking(
        booking_id="booking-456",
        room_number="302",
        check_out_date="2025-12-05",
    )

    response = client.patch(
        f"/api/tasks/{task.id}/status",
        json={"status": "completed"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["status"] == "completed"

    # проверим, что в хранилище тоже обновилось
    assert tasks[task.id].status == "completed"