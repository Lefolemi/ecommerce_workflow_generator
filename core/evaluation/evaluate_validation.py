# core/evaluation/evaluate_validation.py
import os
import sys

# =========================================================================
# PATH FIX: Menambahkan direktori root proyek ke dalam pencarian path Python
# Mundur 2 tingkat dari lokasi file ini (dari evaluation -> core -> root proyek)
# =========================================================================
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import numpy as np
from PIL import Image
from core.engines.preprocess import validate_contains_object

def run_validation_experiment():
    print("⏳ Memulai pengujian simulasi deteksi objek vs latar belakang...")
    
    # Siapkan sampel data buatan untuk simulasi unit testing
    # 1. Simulasi gambar flat/kosong (Latar belakang murni polos)
    flat_bg = Image.fromarray(np.ones((400, 400, 3), dtype=np.uint8) * 200)
    
    # 2. Simulasi gambar produk kontras (Terdapat box kotak di tengah kanvas kosong)
    product_mock = np.ones((400, 400, 3), dtype=np.uint8) * 255
    product_mock[100:300, 100:300, :] = 20 # Objek box gelap kontras tinggi
    product_mock_img = Image.fromarray(product_mock)
    
    # Jalankan eksperimen uji coba fungsi
    res_flat, reason_flat = validate_contains_object(flat_bg)
    res_prod, reason_prod = validate_contains_object(product_mock_img)

    print("\n🎉 === HASIL SKENARIO VALIDASI CITRA ===")
    print(f"📋 Kasus 1 (Latar Polos)  -> Terdeteksi Valid: {res_flat} | Alasan: {reason_flat}")
    print(f"📋 Kasus 2 (Citra Produk) -> Terdeteksi Valid: {res_prod} | Alasan: {reason_prod}")
    print("=========================================\n")

if __name__ == "__main__":
    run_validation_experiment()