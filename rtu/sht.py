from pymodbus.client import AsyncModbusSerialClient

from config import RTU_BAUD, RTU_PARITY, RTU_PORT, RTU_SHT_STOPBITS


async def read_sht(device_id):
    client = AsyncModbusSerialClient(
        port=RTU_PORT,
        baudrate=RTU_BAUD,
        parity=RTU_PARITY,
        stopbits=RTU_SHT_STOPBITS,
        bytesize=8,
        timeout=1,
    )

    data = {}

    await client.connect()

    if not client.connected:
        print(f"Failed to connect to SHT {device_id}")
        return data

    try:
        t = await client.read_holding_registers(0x0001, count=1, device_id=device_id)
        h = await client.read_holding_registers(0x0002, count=1, device_id=device_id)

        if t.isError():
            print(f"Error reading SHT {device_id}: {t}")
        elif h.isError():
            print(f"Error reading SHT {device_id}: {h}")
        else:
            data = {
                "temperature": t.registers[0] / 10.0,
                "humidity": h.registers[0] / 10.0,
            }

    except Exception as e:
        print(f"Error reading SHT {device_id}: {e}")

    finally:
        client.close()

    return data
