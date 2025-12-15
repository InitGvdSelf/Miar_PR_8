from fastapi import FastAPI

from .database import Base, engine
from .routers import router as booking_router
from prometheus_fastapi_instrumentator import Instrumentator
# создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking service")


# после создания app
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(booking_router)