# core/engines/preprocess.py
import numpy as np
from PIL import Image, ImageOps
from rembg import remove, new_session

# Global session to prevent reloading the model into memory multiple times
_REMBG_SESSION = None

def get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        # Using the lightweight u2net_integrated or default u2net
        _REMBG_SESSION = new_session("u2net")
    return _REMBG_SESSION

def validate_contains_object(pil_img, confidence_threshold=0.15, size_threshold=0.92):
    """
    Evaluates the image to determine if a distinct foreground product exists,
    or if it is just a background scene.
    
    Returns: (bool, string) -> (IsValid, Reason/Message)
    """
    # 1. Downsample heavily to make the verification near-instantaneous
    check_img = pil_img.copy()
    check_img.thumbnail((256, 256), Image.Resampling.LANCZOS)
    
    # 2. Get the raw mask alpha channel only
    session = get_rembg_session()
    rgba_output = remove(check_img, session=session, only_mask=True)
    mask_arr = np.array(rgba_output) / 255.0  # Normalize to [0.0, 1.0]
    
    # 3. Analyze mask characteristics
    total_pixels = mask_arr.size
    foreground_pixels = np.sum(mask_arr > 0.2)  # Pixels with baseline confidence
    foreground_ratio = foreground_pixels / total_pixels
    
    # Metric A: Empty Mask (No contrasting edges/salient points found)
    if foreground_ratio < 0.02:
        return False, "Tidak ada objek kontras terdeteksi (Gambar terlalu flat/kosong)."
        
    # Metric B: Oversaturated Mask (The entire image is treated as an object)
    # Real products have clear negative space margins. Landscapes/Backgrounds fill the frame.
    if foreground_ratio > size_threshold:
        return False, "Gambar dinilai sebagai Latar Belakang (Objek memenuhi seluruh kanvas)."
        
    # Metric C: Low Confidence Spread (Average confidence of the foreground area)
    avg_confidence = np.mean(mask_arr[mask_arr > 0.2]) if foreground_pixels > 0 else 0
    if avg_confidence < confidence_threshold:
        return False, "Tingkat keyakinan AI rendah. Objek tidak terdefinisi dengan jelas."

    return True, "Valid"

def standardize_input(image_path, target_size=1024):
    """
    Normalisasi format, kontras, dan dimensi awal citra mentah
    sebelum masuk ke dalam pipeline segmentasi AI U2-Net.
    """
    with Image.open(image_path) as img:
        # 1. Normalisasi ke RGB
        img = img.convert("RGB")
        
        # 2. Auto-Contrast
        img = ImageOps.autocontrast(img, cutoff=0.5)
        
        # 3. Validasi Konten (Object vs Background Detection)
        # Menghasilkan error jika gambar dinilai hanya latar belakang semata
        is_valid, reason = validate_contains_object(img)
        if not is_valid:
            raise ValueError(reason)
        
        # 4. Downscaling awal agar proses kalkulasi matriks U2-Net tidak membebani VRAM/RAM
        if max(img.size) > target_size:
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        return img.copy()