# ================= CONFIG =================

POLL_INTERVAL = 60  # seconds

RTU_PORT = "/dev/ttyUSB0"
RTU_BAUD = 9600
RTU_PARITY = "N"

RTU_DDSU_STOPBITS = 1
RTU_SHT_STOPBITS = 1
RTU_PZEM_STOPBITS = 1
RTU_BMS_STOPBITS = 1

DDSU_IDS = [2, 4, 5, 6, 7, 8]
PZEM_IDS = [3]
SHT_IDS = [1]
BMS_IDS = [9]

WS_HOST = "0.0.0.0"
WS_PORT = 8765

BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8080
# =========================================
