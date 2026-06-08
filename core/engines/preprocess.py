# core/engines/preprocess.py
import cv2
import numpy as np
from PIL import Image, ImageOps

def standardize_input(image_path, target_size=1024):
    """
    Normalisasi format, kontras, dan dimensi awal citra mentah
    sebelum masuk ke dalam pipeline segmentasi AI U2-Net.
    """
    with Image.open(image_path) as img:
        # 1. Normalisasi ke RGB (Menghapus color profile kustom ICC atau format CMYK)
        img = img.convert("RGB")
        
        # 2. Auto-Contrast (Histogram Stretching) untuk memperjelas batas objek
        # Cutoff 0.5% membuang piksel ekstrem luar untuk hasil kontras yang matang
        img = ImageOps.autocontrast(img, cutoff=0.5)
        
        # 3. Downscaling awal agar proses kalkulasi matriks U2-Net tidak membebani VRAM/RAM
        if max(img.size) > target_size:
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Membuat salinan murni dari objek gambar agar aman dilepas dari block context 'with'
        return img.copy()