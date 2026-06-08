# core/engines/shadow.py
from PIL import Image, ImageFilter

def apply_realistic_shadow(canvas, resized_obj, offset, new_size):
    """
    Menghasilkan bayangan jatuh (drop-shadow) yang halus dan natural 
    di bawah produk berdasarkan bentuk asli channel alpha-nya.
    """
    canvas_w, canvas_h = canvas.size
    
    # 1. Isolasi channel alpha (siluet murni dari bentuk geometri produk)
    product_alpha = resized_obj.split()[3]
    
    # 2. Membuat layer bayangan hitam solid dengan dimensi setara kanvas utama
    shadow_layer = Image.new("RGB", (canvas_w, canvas_h), (0, 0, 0))
    
    # 3. Simulasi arah lampu studio top-down (2% kanan, 4% bawah dari skala produk)
    shadow_shift_x = int(new_size[0] * 0.02)
    shadow_shift_y = int(new_size[1] * 0.04)
    shadow_offset = (offset[0] + shadow_shift_x, offset[1] + shadow_shift_y)
    
    # 4. Membuat hitam-putih mask dasar bayangan menggunakan tipe matriks 8-bit L
    shadow_layer_mask = Image.new("L", (canvas_w, canvas_h), 0)
    shadow_layer_mask.paste(product_alpha, shadow_offset)
    
    # 5. Berikan efek blur Gaussian yang lembut proporsional (4%) terhadap ukuran produk
    blur_radius = max(5, int(max(new_size) * 0.04))
    shadow_layer_mask = shadow_layer_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 6. Kontrol Opacity: Blend dengan kanvas kosong untuk mengunci kepekatan bayangan di 40%
    blank_mask = Image.new("L", (canvas_w, canvas_h), 0)
    shadow_final_mask = Image.blend(blank_mask, shadow_layer_mask, 0.40)
    
    # 7. Komposisikan layer bayangan ke atas kanvas background sebelum produk utama ditimpa
    canvas.paste(shadow_layer, (0, 0), mask=shadow_final_mask)
    return canvas