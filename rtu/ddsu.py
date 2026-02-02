import asyncio
import random

from helper.simulation import get_simulated_scenario


async def read_ddsu(device_id):
    # Simulate a small network delay
    await asyncio.sleep(0.05)
    sim = get_simulated_scenario()

    # Map logic
    power = sim["p2"] if device_id == 2 else sim["servers"].get(device_id, 0)

    return {
        "voltage": round(random.uniform(228.0, 232.0), 2),
        "current": round(power / 230, 2),
        "power": round(power, 2),
        "energy": round(power * 0.1, 2),
        "power_factor": round(random.uniform(0.95, 0.99), 2),
        "frequency": round(random.uniform(49.9, 50.1), 2),
    }
