from pydantic import BaseModel
from datetime import datetime


class CleaningTask(BaseModel):
    id: str
    room_number: str
    booking_id: str
    planned_time: datetime
    status: str  # pending, in_progress, completed


class StatusUpdate(BaseModel):
    status: str