import time
import re
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
from display import show_text_highlighted

def extract_eth_address(qr_data):
    match = re.search(r'0x[a-fA-F0-9]{40}', qr_data)
    return match.group(0) if match else None

def scan_qr_code(timeout=15):
    picam2 = None

    try:
        # ✅ Reset Camera if previously failed
        try:
            Picamera2.global_instance = None  # Force clear any global cam instance
        except:
            pass

        # ✅ Initialize new instance cleanly
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration(main={'format': 'RGB888', 'size': (640, 480)}))
        picam2.start()

        show_text_highlighted(["📷 Scanning QR", "Hold QR steady..."], -1)
        start_time = time.time()

        while time.time() - start_time < timeout:
            frame = picam2.capture_array()
            decoded_objects = decode(frame)

            if decoded_objects:
                raw_data = decoded_objects[0].data.decode('utf-8')
                print(f"\n[QR DATA] Raw: {raw_data}")

                address = extract_eth_address(raw_data)
                if address:
                    print(f"[QR DATA] Extracted Address: {address}")
                    show_text_highlighted(["✅ QR Scanned", address[:20]], -1)
                    time.sleep(2)
                    return address
                else:
                    show_text_highlighted(["❌ Invalid QR", "No valid address"], -1)
                    time.sleep(2)
                    return None

            time.sleep(0.2)

        show_text_highlighted(["❌ Timeout", "QR Not Found"], -1)
        return None

    except Exception as e:
        show_text_highlighted(["⚠️ Camera Error", str(e)[:20]], -1)
        print(f"[Camera Error] {e}")
        return None

    finally:
        if picam2:
            try:
                picam2.stop()
                picam2.close()
                Picamera2.global_instance = None
                print("[Camera] Fully stopped and closed.")
            except Exception as e:
                print(f"[Cleanup Error] {e}")
