import time
import qrcode
from PIL import Image, ImageDraw
from display import oled

def generate_qr_code(data="Shakil"):
    """Generates and displays a QR code"""
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill="black", back_color="white").convert("1")
    qr_image = qr_image.resize((50, 50), Image.NEAREST)

    oled_image = Image.new("1", (128, 64), "black")
    oled_image.paste(qr_image, ((128 - qr_image.width) // 2, (64 - qr_image.height) // 2))

    oled.image(oled_image)
    oled.show()
    time.sleep(5)
