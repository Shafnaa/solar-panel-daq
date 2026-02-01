# ================= CONFIG =================

POLL_INTERVAL = 10  # seconds

RTU_PORT = "/dev/ttyUSB0"
RTU_BAUD = 9600
RTU_PARITY = "N"

RTU_DDSU_STOPBITS = 2
RTU_SHT_STOPBITS = 1
RTU_PZEM_STOPBITS = 1
RTU_BMS_STOPBITS = 1

DDSU_IDS = [1, 2, 3, 4, 5, 6]
PZEM_IDS = [7]
SHT_IDS = [8]
BMS_IDS = [9, 10]

WS_HOST = "0.0.0.0"
WS_PORT = 8765

BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8080
# =========================================
