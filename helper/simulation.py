# rtu/sim_state.py
import random
import time


def get_simulated_scenario():
    """
    Returns a coordinated set of power values (Watts)
    to ensure flow rules are triggered naturally.
    """
    # Use time to toggle scenarios (e.g., every 2 minutes)
    toggle = (int(time.time()) // 120) % 3

    # Base loads for servers (IDs 4-8)
    server_powers = {i: random.uniform(200, 500) for i in range(4, 9)}
    p4_8 = sum(server_powers.values())

    if toggle == 0:  # SCENARIO: Grid + Solar (Grid covers the gap)
        p3 = random.uniform(100, 300)  # Solar (PZEM ID 3)
        p2 = p4_8 + p3 + random.uniform(50, 100)  # Grid (DDSU ID 2) > Solar
    elif toggle == 1:  # SCENARIO: Solar Only (Off-grid)
        p3 = p4_8 + random.uniform(200, 500)
        p2 = 0  # No Grid
    else:  # SCENARIO: Grid Heavy (Charging battery)
        p3 = 0
        p2 = p4_8 + 1000  # High Grid usage

    return {"p2": p2, "p3": p3, "servers": server_powers, "p4_8": p4_8}
