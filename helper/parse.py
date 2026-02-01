def parse_current(value):
    """Converts UINT16 to signed float for Charge/Discharge current."""
    # If the value is > 32767, it's a negative value (discharging)
    if value > 32767:
        value -= 65536
    return value / 10.0  # Standard scaling for BMS current
