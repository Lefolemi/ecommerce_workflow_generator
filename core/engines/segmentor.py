# core/engines/segmentor.py
from rembg import remove
from PIL import Image
import io

def remove_background(pil_img):
    """
    Menggunakan arsitektur U2-Net untuk segmentasi objek salient
    dan memisahkan produk dari latar belakang bawaannya.
    """
    # 1. Konversi objek PIL ke format bytes menggunakan context manager
    with io.BytesIO() as buf:
        pil_img.save(buf, format="PNG")
        input_bytes = buf.getvalue()
    
    # 2. Proses pemisahan objek dari latar belakang via U2-Net
    output_bytes = remove(input_bytes)
    
    # 3. Konversi kembali bytes hasil segmentasi ke objek PIL RGBA
    with io.BytesIO(output_bytes) as res_buf:
        rgba_image = Image.open(res_buf).convert("RGBA")
        # Copy data ke memori agar aman setelah buffer biner ditutup
        return rgba_image.copy()