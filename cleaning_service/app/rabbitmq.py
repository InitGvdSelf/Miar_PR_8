import os
import json
import asyncio

import aio_pika
from dotenv import load_dotenv

from .storage import create_task_from_booking

load_dotenv()

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq//")


async def consume_booking_created() -> None:
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("booking_created", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body.decode("utf-8"))
                create_task_from_booking(
                    booking_id=data["booking_id"],
                    room_number=data["room_number"],
                    check_out_date=data["check_out_date"],
                )


async def start_consumer() -> None:
    # вечный цикл: если что-то упало — подождать и переподключиться
    while True:
        try:
            await consume_booking_created()
        except Exception:
            await asyncio.sleep(5)