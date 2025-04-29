import board
import busio
import time
from adafruit_atecc.adafruit_atecc import ATECC

i2c = busio.I2C(board.SCL, board.SDA)
atecc = ATECC(i2c)

try:
    print("📡 Waking ATECC...")
    atecc.wakeup()
    time.sleep(0.01)

    print("🔐 Serial Number:", atecc.serial_number)

    print("🔒 Locked (overall):", atecc.locked)
    print("🔧 Chip Version     :", atecc.version())

    atecc.sleep()

except Exception as e:
    print("❌ Error:", e)
