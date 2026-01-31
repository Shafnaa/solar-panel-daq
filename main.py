import asyncio
import json
import time
import aiohttp
import websockets


from rtu.ddsu import read_ddsu
from rtu.pzem import read_pzem
from rtu.sht import read_sht


from config import (
    BACKEND_HOST,
    BACKEND_PORT,
    DDSU_IDS,
    POLL_INTERVAL,
    PZEM_IDS,
    SHT_IDS,
    WS_HOST,
    WS_PORT,
)


http_session: aiohttp.ClientSession | None = None


async def get_http_session():
    global http_session
    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
    return http_session


async def post_json(url: str, payload: dict):
    session = await get_http_session()
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status >= 400:
                body = await resp.text()
                print(f"POST failed {resp.status}: {body}")
    except Exception as e:
        print("HTTP error:", e)


clients = set()
latest_data = {}

# =========================
# Data Format
# ========================
# {
#   "ts": 1697049600,
#   "data": [
#       "{
#           "id": 1,
#           "type": "DDSU",
#           "data": {
#               "voltage": 230.5,
#               "current": 5.2,
#               "power": 1200.0,
#               "energy": 15000.0,
#               "frequency": 50.0,
#               "power_factor": 0.95
#           },
#       },
#       ...,
#       {
#           "id": 7,
#           "type": "PZEM",
#           "data": {
#               "voltage": 230.5,
#               "current": 5.2,
#               "power": 1200.0,
#               "energy": 15000.0,
#           },
#       },
#       {
#           "id": 7,
#           "type": "PZEM",
#           "data": {
#               "voltage": 230.5,
#               "current": 5.2,
#               "power": 1200.0,
#               "energy": 15000.0,
#           },
#       },
#       {
#           "id": 8,
#           "type": "SHT",
#           "data": {
#               "temperature": 25.5,
#               "humidity": 60.0
#           },
#       },
#   ]
# }
# =========================

hour_bucket = {}

# =========================
# Data Format
# ========================
# {
#   "ts": 1697049600,
#   "count": 12,
#   "data": [
#       "{
#           "id": 1,
#           "type": "DDSU",
#           "data": {
#               "voltage": 2766,
#               "current": 62.4,
#               "power": 14400.0,
#               "energy": 360000.0,
#               "frequency": 6000,
#               "power_factor": 11.4,
#           },
#       },
#       ...,
#       {
#           "id": 7,
#           "type": "PZEM",
#           "data": {
#               "voltage": 2766,
#               "current": 62.4,
#               "power": 14400.0,
#               "energy": 360000.0,
#           },
#       },
#       {
#           "id": 7,
#           "type": "PZEM",
#           "data": {
#               "voltage": 2766,
#               "current": 62.4,
#               "power": 14400.0,
#               "energy": 360000.0,
#           },
#       },
#       {
#           "id": 8,
#           "type": "SHT",
#           "data": {
#               "temperature": 255,
#               "humidity": 600
#           },
#       },
#   ]
# }
# =========================


async def flush_bucket(bucket):
    count = bucket["count"]
    ts = bucket["ts"]

    for entry in bucket["data"]:
        data = entry["data"]

        averaged = {k: round(v / count, 3) for k, v in data.items()}

        payload = {
            "device_id": entry["id"],
            **averaged,
            "timestamp": ts,
        }

        if entry["type"] == "DDSU":
            url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1/ddsus/create"

        elif entry["type"] == "PZEM":
            url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1/pzems/create"

        elif entry["type"] == "SHT":
            url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1/shts/create"

        else:
            continue

        await post_json(url, payload)


async def update_bucket(payload):
    global hour_bucket

    timestamp = int(time.time())
    hour_start = timestamp - (timestamp % 3600)

    if hour_start != hour_bucket.get("ts"):
        # Flush previous hour bucket
        if hour_bucket.get("count", 0) > 0:
            await flush_bucket(hour_bucket)

        hour_bucket = {"ts": hour_start, "count": 0, "data": []}

    # =========================
    # Accumulate current sample
    # =========================
    hour_bucket["count"] += 1

    for incoming in payload["data"]:
        found = False

        for stored in hour_bucket["data"]:
            if stored["id"] == incoming["id"] and stored["type"] == incoming["type"]:
                for k, v in incoming["data"].items():
                    stored["data"][k] += v
                found = True
                break

        if not found:
            hour_bucket["data"].append(
                {
                    "id": incoming["id"],
                    "type": incoming["type"],
                    "data": incoming["data"].copy(),
                }
            )


# =========================
# Modbus Polling Logic
# =========================


async def modbus_reader():
    timestamp = int(time.time())

    while True:
        try:
            data = []

            # Read DDSU meters
            for sid in DDSU_IDS:
                ddsu_data = await read_ddsu(sid)
                data.append({"id": sid, "type": "DDSU", "data": ddsu_data})

            # Read PZEM meter
            for sid in PZEM_IDS:
                pzem_data = await read_pzem(sid)
                data.append({"id": sid, "type": "PZEM", "data": pzem_data})

            # Read SHT sensor
            for sid in SHT_IDS:
                sht_data = await read_sht(sid)
                data.append({"id": sid, "type": "SHT", "data": sht_data})

            global latest_data
            latest_data = {"ts": timestamp, "data": data}

            await update_bucket(latest_data)

            # Broadcast latest data to WebSocket clients
            if latest_data:
                await broadcast(latest_data)

        except Exception as e:
            print(f"Error in modbus_reader: {e}")

        await asyncio.sleep(POLL_INTERVAL)


# =========================
# WebSocket Logic
# =========================
async def broadcast(message):
    if not clients:
        return

    payload = json.dumps(message)
    await asyncio.gather(
        *[client.send(payload) for client in clients], return_exceptions=True
    )


async def ws_handler(websocket):
    clients.add(websocket)
    print("🔌 Client connected")

    try:
        # Send last known data immediately
        if latest_data:
            await websocket.send(json.dumps(latest_data))

        async for _ in websocket:
            pass  # No incoming messages needed
    finally:
        clients.remove(websocket)
        print("❌ Client disconnected")


# =========================
# Main
# =========================
async def main():
    ws_server = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    print(f"🚀 WebSocket running at ws://{WS_HOST}:{WS_PORT}")

    await asyncio.gather(modbus_reader(), ws_server.wait_closed())


if __name__ == "__main__":
    asyncio.run(main())
