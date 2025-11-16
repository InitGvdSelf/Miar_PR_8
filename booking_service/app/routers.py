from datetime import date
import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from .database import get_db
from .models import Booking
from .schemas import BookingCreate, BookingOut, BookingCancel
from .rabbitmq import send_booking_created

router = APIRouter(prefix="/api", tags=["booking"])


@router.post("/bookings", response_model=BookingOut)
def create_booking(
    data: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # вложенная функция для расчёта стоимости
    def calculate_total_price(check_in: date, check_out: date, guests_count: int) -> int:
        nights = (check_out - check_in).days
        if nights <= 0:
            raise HTTPException(status_code=400, detail="Некорректный диапазон дат")
        base_price_per_night = 3000
        extra_guest = max(0, guests_count - 1)
        return nights * (base_price_per_night + extra_guest * 500)

    total_price = calculate_total_price(
        data.check_in_date,
        data.check_out_date,
        data.guests_count,
    )

    booking = Booking(
        id=str(uuid.uuid4()),
        room_number=data.room_number,
        guest_name=data.guest_name,
        guests_count=data.guests_count,
        check_in_date=data.check_in_date,
        check_out_date=data.check_out_date,
        total_price=total_price,
        status="created",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # отправка события для сервиса уборки (через фоновые задачи FastAPI)
    background_tasks.add_task(
        send_booking_created,
        booking.id,
        booking.room_number,
        booking.check_out_date,
    )

    return booking


@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    return booking


@router.post("/bookings/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: str,
    cancel_data: BookingCancel,
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    # здесь можно логировать cancel_data.reason / initiator, если добавить поля в модель
    return booking


@router.get("/bookings", response_model=list[BookingOut])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()