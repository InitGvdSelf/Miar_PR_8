from typing import Dict
from datetime import datetime
import uuid

from .schemas import CleaningTask

# простое хранилище задач в памяти
tasks: Dict[str, CleaningTask] = {}


def create_task_from_booking(
    booking_id: str,
    room_number: str,
    check_out_date: str,
) -> CleaningTask:
    planned_time = datetime.fromisoformat(check_out_date)
    task_id = str(uuid.uuid4())
    task = CleaningTask(
        id=task_id,
        room_number=room_number,
        booking_id=booking_id,
        planned_time=planned_time,
        status="pending",
    )
    tasks[task_id] = task
    return task