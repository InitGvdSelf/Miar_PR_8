import asyncio

from fastapi import FastAPI

from .routers import router as cleaning_router
from .rabbitmq import start_consumer

app = FastAPI(title="Cleaning service")

app.include_router(cleaning_router)


@app.on_event("startup")
async def startup_event():
    # запускаем асинхронного консьюмера RabbitMQ в фоне
    asyncio.create_task(start_consumer())