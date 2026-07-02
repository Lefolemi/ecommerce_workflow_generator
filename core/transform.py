# core/transform.py
import os
import cv2
import numpy as np
from PIL import Image

# Import terpisah dari subfolder sub-engines kustom
from core.engines.shadow import apply_realistic_shadow
from core.engines.sticker import apply_promo_sticker
from core.engines.watermark import apply_shop_watermark

def process_to_packshot(pil_image, max_target_size=1000, aspect_ratio_str="1:1", do_centering=True, bg_template_path=None, stickers_list=None, watermark_text="", custom_bg_color="#ffffff"):
    """
    Orkestrator Utama: Mengatur konfigurasi geometri kanvas, skala objek, 
    dan menyusun komposisi berlapis (Sandwich Layer) hasil akhir foto katalog.
    Menerima objek pil_image transparan (RGBA) yang telah melalui penyesuaian pencahayaan.
    """
    np_image = np.array(pil_image.convert("RGBA"))
    alpha = np_image[:, :, 3]
    
    # 1. Product Bounding Box Extraction
    coords = cv2.findNonZero(alpha)
    if coords is None: return pil_image
    
    x, y, w_obj, h_obj = cv2.boundingRect(coords)
    cropped_obj = pil_image.crop((x, y, x + w_obj, y + h_obj))
    
    # 2. Canvas Geometry Configurations (1:1, 4:3, 16:9)
    if aspect_ratio_str == "4:3":
        ratio_w, ratio_h = 4, 3
    elif aspect_ratio_str == "16:9":
        ratio_w, ratio_h = 16, 9
    else:
        ratio_w, ratio_h = 1, 1

    if ratio_w >= ratio_h:
        canvas_w = max_target_size
        canvas_h = int((max_target_size * ratio_h) / ratio_w)
    else:
        canvas_h = max_target_size
        canvas_w = int((max_target_size * ratio_w) / ratio_w)

    # 3. Scale Calculation (20% Safe Margin Boundary)
    max_safe_w = canvas_w * 0.8
    max_safe_h = canvas_h * 0.8
    scale = min(max_safe_w / w_obj, max_safe_h / h_obj)
    
    new_size = (int(w_obj * scale), int(h_obj * scale))
    resized_obj = cropped_obj.resize(new_size, Image.Resampling.LANCZOS)

    # 4. Layer 1: Background Initialization
    if bg_template_path and os.path.exists(bg_template_path):
        canvas = Image.open(bg_template_path).convert("RGB")
        canvas = canvas.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    else:
        # Konversi warna String Hex (#ffffff) ke format Tuple RGB tuple(R, G, B)
        hex_str = custom_bg_color.lstrip('#')
        rgb_tuple = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        
        # Buat kanvas kosong studio berdasarkan warna pilihan pengguna
        canvas = Image.new("RGB", (canvas_w, canvas_h), rgb_tuple)
    
    # 5. Spatial Positioning Offsets (Centering Logic via Image Moments)
    if do_centering:
        M = cv2.moments(alpha)
        cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else w_obj // 2
        cY = int(M["m01"] / M["m00"]) if M["m00"] != 0 else h_obj // 2
        new_cX = int((cX - x) * scale)
        new_cY = int((cY - y) * scale)
        offset = ((canvas_w // 2) - new_cX, (canvas_h // 2) - new_cY)
    else:
        offset = ((canvas_w - new_size[0]) // 2, (canvas_h - new_size[1]) // 2)

    # 6. Layer 2: Soft Drop Shadow Generation (Hanya aktif jika pakai kustom latar ruangan)
    if bg_template_path:
        canvas = apply_realistic_shadow(canvas, resized_obj, offset, new_size)

    # 7. Layer 3: Main Product Overlay
    canvas.paste(resized_obj, offset, resized_obj)
    
    # 8. Layer 4 & 5: Marketing Elements Overlay (Stiker Diskon & Watermark Pemilik Toko)
    font_target = "arial.ttf"
    canvas = apply_promo_sticker(canvas, stickers_list, font_target)
    canvas = apply_shop_watermark(canvas, watermark_text, font_target)
    
    return canvas