from fastapi import FastAPI

from .database import Base, engine
from .routers import router as booking_router

# создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking service")

app.include_router(booking_router)