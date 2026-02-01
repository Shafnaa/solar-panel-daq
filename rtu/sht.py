import asyncio
import random


async def read_sht(device_id):
    await asyncio.sleep(0.1)

    return {
        "temperature": round(random.uniform(24.0, 32.0), 1),
        "humidity": round(random.uniform(40.0, 70.0), 1),
    }
