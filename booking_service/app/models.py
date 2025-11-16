from sqlalchemy import Column, String, Date, Integer
from .database import Base
import uuid


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_number = Column(String, nullable=False)
    guest_name = Column(String, nullable=False)
    guests_count = Column(Integer, nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    status = Column(String, default="created")  # created, confirmed, cancelled
    total_price = Column(Integer, nullable=False)