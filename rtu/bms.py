from pymodbus.client import AsyncModbusSerialClient

from helper.parse import parse_current

from config import RTU_BAUD, RTU_PARITY, RTU_PORT, RTU_BMS_STOPBITS


async def read_bms(device_id):
    client = AsyncModbusSerialClient(
        port=RTU_PORT,
        baudrate=RTU_BAUD,
        parity=RTU_PARITY,
        stopbits=RTU_BMS_STOPBITS,
        bytesize=8,
        timeout=1,
    )

    data = {}

    await client.connect()

    if not client.connected:
        print(f"Error reading BMS {device_id}: {e}")
        return data

    try:
        result =k await client.read_holding_registers(
            0x1000, count=16, device_id=device_id
        )

        v = result.registers[0] / 100
        i = parse_current(result.registers[1])
        cap = result.registers[2] / 100
        soc = result.registers[3]
        soh = result.registers[4]
        cycle = result.registers[5]

        data = {
            "voltage": v,
            "current": i,
            "capacity": cap,
            "state_of_charge": soc,
            "state_of_health": soh,
            "cycle_count": cycle,
        }
    except Exception as e:
        print(f"Error reading BMS {device_id}: {e}")
    finally:
        await client.close()

    return data
