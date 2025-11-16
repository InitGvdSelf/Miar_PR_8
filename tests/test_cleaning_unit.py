from datetime import datetime

from cleaning_service.app.storage import create_task_from_booking, tasks


def test_create_task_from_booking_creates_task():
    """
    Юнит-тест: функция create_task_from_booking должна
    создать задачу и положить её в словарь tasks.
    """
    tasks.clear()  # очищаем хранилище перед тестом

    booking_id = "test-booking-id"
    room_number = "201"
    checkout_date = "2025-11-30"

    task = create_task_from_booking(
        booking_id=booking_id,
        room_number=room_number,
        check_out_date=checkout_date,
    )

    # задача должна появиться в хранилище
    assert task.id in tasks
    assert tasks[task.id] == task

    # поля должны совпадать с входными
    assert task.booking_id == booking_id
    assert task.room_number == room_number
    assert task.status == "pending"

    # planned_time должен быть сконвертирован из строки
    assert isinstance(task.planned_time, datetime)
    assert task.planned_time.date().isoformat() == checkout_date