# core/engines/sticker.py
from PIL import Image, ImageDraw, ImageFont

def apply_promo_sticker(canvas, text, font_style="arial.ttf"):
    """
    Menggambar stiker promosi/diskon rounded rectangle di sudut kanan atas kanvas.
    Mendukung multiline menggunakan penanda '\n' atau '\\n'.
    """
    if not text.strip():
        return canvas
        
    canvas_w, canvas_h = canvas.size
    draw = ImageDraw.Draw(canvas)
    
    # Skala ukuran font dinamis: 3.5% dari tinggi kanvas produksi
    font_size = int(canvas_h * 0.035)
    try:
        font = ImageFont.truetype(font_style, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    # Normalisasi baris baru dan pecah teks menjadi list per baris
    text_lines = text.replace("\\n", "\n").split("\n")
    max_line_w = 0
    total_height = 0
    
    # Kalkulasi bounding box untuk menentukan ukuran wadah stiker
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        max_line_w = max(max_line_w, line_w)
        total_height += line_h + 5
        
    # Tambahkan padding dalam wadah stiker
    padding = 15
    box_w = max_line_w + (padding * 2)
    box_h = total_height + (padding * 2)
    
    # Penentuan koordinat jangkar (Anchor) di sudut kanan atas dengan margin 30px
    margin = 30
    x1 = canvas_w - box_w - margin
    y1 = margin
    x2 = canvas_w - margin
    y2 = margin + box_h
    
    # Gambar badan utama stiker (Warna Oranye Shopee khas e-commerce) dengan border putih
    draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill="#ee4d2d", outline="white", width=2)
    
    # Render teks secara merata di tengah-tengah wadah stiker (Center Aligned)
    current_y = y1 + padding
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        
        # Hitung offset X agar teks berada tepat di tengah lebar stiker
        text_x = x1 + (box_w - line_w) // 2
        draw.text((text_x, current_y), line, fill="white", font=font)
        current_y += line_h + 5
        
    return canvas