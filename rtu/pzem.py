import asyncio
import random
import time

from helper.simulation import get_simulated_scenario


async def read_pzem(device_id):
    await asyncio.sleep(0.05)
    sim = get_simulated_scenario()

    p3 = sim["p3"] if device_id == 3 else 0

    return {
        "voltage": round(random.uniform(228.0, 232.0), 2),
        "current": round(p3 / 230, 2),
        "power": round(p3, 2),
        "energy": 5000 + (int(time.time()) % 1000),  # Accumulating
    }
