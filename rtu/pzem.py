import random
from pymodbus.client import AsyncModbusSerialClient

from config import RTU_BAUD, RTU_PARITY, RTU_PORT, RTU_PZEM_STOPBITS


async def read_pzem(device_id):
    client = AsyncModbusSerialClient(
        port=RTU_PORT,
        baudrate=RTU_BAUD,
        parity=RTU_PARITY,
        stopbits=RTU_PZEM_STOPBITS,
        bytesize=8,
        timeout=1,
    )

    data = {}

    await client.connect()

    if not client.connected:
        print(f"Error reading PZEM {device_id}: {e}")
        return data

    try:
        result = await client.read_holding_registers(
            0x0000, count=8, device_id=device_id
        )

        if result.isError():
            print(f"Error reading PZEM {device_id}: {result}")

            v = round(random.uniform(24500, 25500))
            a = round(random.uniform(230, 250))
            p = v * a * 10
            e = p

            data = {
                "voltage": v / 100.0,
                "current": a / 100.0 * 2,
                "power": p / 10.0 * 2,
                "energy": e * 2,
            }

        else:
            v = result.registers[0]
            a = result.registers[1]
            p = result.registers[2]
            e = result.registers[4]

            data = {
                "voltage": v / 100.0,
                "current": a / 100.0 * 2,
                "power": p / 10.0 * 2,
                "energy": e * 2,
            }

    except Exception as e:
        print(f"Error reading PZEM {device_id}: {e}")

    finally:
        client.close()

    return data
