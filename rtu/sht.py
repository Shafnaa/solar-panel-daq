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
        result = await client.read_input_registers(
            0x0001, count=2, device_id=device_id
        )

        if result.isError():
            print(f"Error reading SHT {device_id}: {result}")

        else:
            t = result.registers[0]
            h = result.registers[1]

            data = {
                "temperature": t / 10.0,
                "humidity": h / 10.0,
            }

    except Exception as e:
        print(f"Error reading SHT {device_id}: {e}")

    finally:
        client.close()

    return data
