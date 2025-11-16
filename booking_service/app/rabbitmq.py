import os
import json
from datetime import date

import aio_pika
from dotenv import load_dotenv

load_dotenv()

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq//")


async def send_booking_created(booking_id: str, room_number: str, check_out_date: date) -> None:
    message = {
        "booking_id": booking_id,
        "room_number": room_number,
        "check_out_date": check_out_date.isoformat(),
    }

    connection = await aio_pika.connect_robust(AMQP_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("booking_created", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode("utf-8")),
            routing_key=queue.name,
        )