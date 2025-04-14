import time
import qrcode
import subprocess
from PIL import Image
from display import oled  

def generate_qr_for_hdkey(private_key):
    """Generates a QR Code for the HD Private Key."""

    # ✅ Ensure Private Key Exists
    private_key = private_key.strip()
    if not private_key or len(private_key) != 64:
        print("❌ Error: Invalid HD Private Key for QR!")
        return

    print(f"🔑 HD Private Key: {private_key}")

    # ✅ Create QR Code
    qr = qrcode.QRCode(
        version=10,  
        error_correction=qrcode.constants.ERROR_CORRECT_L,  
        box_size=12,  
        border=2  
    )

    qr.add_data(private_key)  # ✅ Add only the private key
    qr.make(fit=True)

    # ✅ Create QR Image
    qr_image = qr.make_image(fill="black", back_color="white").convert("1")

    # ✅ Save QR Code as PNG
    qr_image_path = "/home/admin/hd_key_qr.png"
    qr_image.save(qr_image_path)
    print(f"✅ QR Code saved at: {qr_image_path}")

    # ✅ Open the PNG file using the default viewer
    try:
        subprocess.run(["xdg-open", qr_image_path])  
    except FileNotFoundError:
        print("⚠️ No default image viewer found. Open the file manually.")

    # ✅ Display QR on OLED
    qr_image_resized = qr_image.resize((100, 100), Image.LANCZOS)
    oled_image = Image.new("1", (128, 64), "black")
    oled_image.paste(qr_image_resized, ((128 - qr_image_resized.width) // 2, (64 - qr_image_resized.height) // 2))
    oled.image(oled_image)
    oled.show()

    time.sleep(5)  # Keep OLED display for 5 seconds
