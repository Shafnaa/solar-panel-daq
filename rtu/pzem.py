import asyncio
import random
import time

from helper.simulation import get_simulated_scenario


async def read_pzem(device_id):
    await asyncio.sleep(0.05)
    sim = get_simulated_scenario()

    p7 = sim["p7"] if device_id == 7 else 0

    return {
        "voltage": round(random.uniform(228.0, 232.0), 2),
        "current": round(p7 / 230, 2),
        "power": round(p7, 2),
        "energy": 5000 + (int(time.time()) % 1000),  # Accumulating
    }
