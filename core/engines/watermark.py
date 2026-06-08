# core/engines/watermark.py
from PIL import Image, ImageDraw, ImageFont

def apply_shop_watermark(canvas, text, font_style="arial.ttf"):
    """
    Menstempel watermark hak cipta nama toko di sudut kiri bawah kanvas
    dengan panel backing abu-abu semi-transparan untuk keterbacaan optimal.
    """
    if not text.strip():
        return canvas
        
    canvas_w, canvas_h = canvas.size
    draw = ImageDraw.Draw(canvas)
    
    # Skala ukuran font otomatis: 2.5% dari tinggi total kanvas produksi
    font_size = int(canvas_h * 0.025)
    try:
        font = ImageFont.truetype(font_style, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    # Ambil ukuran dimensi teks berdasarkan font terukur
    bbox = draw.textbbox((0, 0), text, font=font)
    wm_w = bbox[2] - bbox[0]
    wm_h = bbox[3] - bbox[1]
    
    # Batas margin jangkar tetap di sudut kiri bawah (20px dari tepi kanvas)
    x = 20
    y = canvas_h - wm_h - 20
    
    # Menggambar kotak latar belakang pelindung (Hitam dengan opacity ~40% / nilai alpha 100)
    draw.rectangle([x - 5, y - 5, x + wm_w + 5, y + wm_h + 5], fill=(0, 0, 0, 100))
    
    # Cetak teks watermark di atas kotak pelindung dengan warna putih redup (alpha 160)
    draw.text((x, y), text, fill=(255, 255, 255, 160), font=font)
    
    return canvas