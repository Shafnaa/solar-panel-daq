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

    # Base loads for servers (IDs 2-6)
    server_powers = {i: random.uniform(200, 500) for i in range(2, 7)}
    p2_6 = sum(server_powers.values())

    if toggle == 0:  # SCENARIO: Grid + Solar (Grid covers the gap)
        p7 = random.uniform(100, 300)  # Solar (PZEM ID 7)
        p1 = p2_6 + p7 + random.uniform(50, 100)  # Grid (DDSU ID 1) > Solar
    elif toggle == 1:  # SCENARIO: Solar Only (Off-grid)
        p7 = p2_6 + random.uniform(200, 500)
        p1 = 0  # No Grid
    else:  # SCENARIO: Grid Heavy (Charging battery)
        p7 = 0
        p1 = p2_6 + 1000  # High Grid usage

    return {"p1": p1, "p7": p7, "servers": server_powers, "p2_6": p2_6}
