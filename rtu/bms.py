import asyncio
import random


async def read_bms(device_id):
    # Simulate a small network delay
    await asyncio.sleep(0.05)

    return {
        "voltage": round(random.uniform(48.0, 54.0), 2),
        "current": round(random.uniform(-20.0, 20.0), 2),
        "capacity": round(random.uniform(100.0, 200.0), 2),
        "state_of_charge": 85,
        "state_of_health": round(random.uniform(80.0, 100.0), 2),
        "cycle_count": random.randint(100, 1000),
    }
