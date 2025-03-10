import time
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
from display import show_text_highlighted

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={'format': 'RGB888', 'size': (640, 480)}))
picam2.start()

def scan_qr_code():
    """Scans a QR code using PiCamera2"""
    show_text_highlighted(["Scanning...", "Please wait"], -1)
    qr_data = None

    while not qr_data:
        frame = picam2.capture_array()
        decoded_objects = decode(frame)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            show_text_highlighted(["Scanned QR:", qr_data[:10]], -1)
            time.sleep(5)
            return qr_data

    return None
