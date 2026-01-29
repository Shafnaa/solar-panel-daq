from pymodbus.client import AsyncModbusSerialClient

from helper.decode import decode_float

from config import RTU_BAUD, RTU_PARITY, RTU_PORT, RTU_DDSU_STOPBITS


async def read_ddsu(device_id):
    client = AsyncModbusSerialClient(
        port=RTU_PORT,
        baudrate=RTU_BAUD,
        parity=RTU_PARITY,
        stopbits=RTU_DDSU_STOPBITS,
        bytesize=8,
        timeout=1,
    )

    data = {}

    await client.connect()

    if not client.connected:
        print(f"Error reading DDSU {device_id}: {e}")
        return data

    try:
        result = await client.read_holding_registers(
            0x2000, count=16, device_id=device_id
        )

        v = result.registers[0:2]
        a = result.registers[2:4]
        p = result.registers[4:6]
        pr = result.registers[6:8]
        pf = result.registers[10:12]
        freq = result.registers[14:16]

        data = {
            "voltage": decode_float(v),
            "current": decode_float(a),
            "power": decode_float(p) * 1000,
            "reactive_power": decode_float(pr) * 1000,
            "power_factor": decode_float(pf),
            "frequency": decode_float(freq),
        }
    except Exception as e:
        print(f"Error reading DDSU {device_id}: {e}")
    finally:
        await client.close()

    return data
