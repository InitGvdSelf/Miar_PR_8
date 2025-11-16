from fastapi import APIRouter, HTTPException

from .storage import tasks
from .schemas import CleaningTask, StatusUpdate

router = APIRouter(prefix="/api", tags=["cleaning"])


@router.get("/tasks", response_model=list[CleaningTask])
def list_tasks():
    return list(tasks.values())


@router.get("/tasks/{task_id}", response_model=CleaningTask)
def get_task(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.patch("/tasks/{task_id}/status", response_model=CleaningTask)
def update_status(task_id: str, data: StatusUpdate):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.status = data.status
    tasks[task_id] = task
    return task