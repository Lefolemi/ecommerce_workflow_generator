# core/engines/enhance.py
import os
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

from core.models.enhancement_net import SimpleEnhanceUNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_MODEL_INSTANCE = None

def load_enhanced_model():
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE

    model_path = os.path.join("core", "models", "lol_enhanced_model.pth")
    model = SimpleEnhanceUNet().to(device)
    
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
        _MODEL_INSTANCE = model
        print("➡️ [AI Pencerah] Berhasil memuat bobot adaptif 'lol_enhanced_model.pth'.")
    else:
        print(f"⚠️ Peringatan: File bobot tidak ditemukan di {model_path}. Mengaktifkan mode fallback.")
        _MODEL_INSTANCE = "FALLBACK"
        
    return _MODEL_INSTANCE

def calculate_blend_alpha(pil_img, low_bound=30, high_bound=120):
    """
    Menghitung bobot pencampuran (alpha) secara linier berdasarkan kecerahan gambar.
    low_bound : Batas bawah di mana AI akan bekerja 100% (gambar gelap gulita)
    high_bound: Batas atas di mana AI tidak akan bekerja sama sekali (gambar sudah terang)
    """
    gray_img = pil_img.convert("L")
    mean_brightness = np.mean(np.array(gray_img))
    
    if mean_brightness <= low_bound:
        return 1.0
    elif mean_brightness >= high_bound:
        return 0.0
    else:
        # Interpolasi linier untuk mendapatkan nilai di antara 0.0 hingga 1.0
        return (high_bound - mean_brightness) / (high_bound - low_bound)

def apply_lol_enhancement(pil_img):
    """
    Mengeksekusi restorasi pencahayaan adaptif menggunakan pencampuran matriks gambar.
    """
    # 1. Hitung nilai alpha berdasarkan kondisi riil pencahayaan gambar masukan
    alpha = calculate_blend_alpha(pil_img)
    
    # Jika gambar sudah dinilai cukup terang (alpha = 0), langsung loloskan tanpa beban komputasi AI
    if alpha == 0.0:
        return pil_img

    model = load_enhanced_model()
    if model == "FALLBACK":
        from PIL import ImageEnhance
        # Fallback adaptif menggunakan perkalian parameter alpha
        factor = 1.0 + (0.6 * alpha)
        return ImageEnhance.Brightness(pil_img).enhance(factor)

    # 2. Proses Gambar Melalui Model AI Colab
    transform = transforms.ToTensor()
    input_tensor = transform(pil_img).unsqueeze(0).to(device)

    with torch.no_grad():
        output_tensor = model(input_tensor)
    
    output_tensor = output_tensor.squeeze(0).cpu()
    to_pil = transforms.ToPILImage()
    enhanced_pil = to_pil(output_tensor)

    # 3. CORE ADJUSTMENT: Alpha Blending (Menggabungkan gambar asli dengan gambar hasil AI)
    # rumus: hasil = (alpha * hasil_AI) + ((1 - alpha) * gambar_asli)
    final_img = Image.blend(pil_img, enhanced_pil, alpha)
    
    print(f"📊 [Adjustment] Kecerahan terdeteksi. Menyuntikkan efek AI sebesar: {alpha * 100:.1f}%")
    return final_img