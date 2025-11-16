from pydantic import BaseModel
from datetime import date
from typing import Optional


class BookingCreate(BaseModel):
    room_number: str
    guest_name: str
    guests_count: int
    check_in_date: date
    check_out_date: date


class BookingCancel(BaseModel):
    reason: str
    comment: Optional[str] = None
    initiator: str  # guest, admin, system


class BookingOut(BaseModel):
    id: str
    room_number: str
    guest_name: str
    guests_count: int
    check_in_date: date
    check_out_date: date
    status: str
    total_price: int

    class Config:
        orm_mode = True