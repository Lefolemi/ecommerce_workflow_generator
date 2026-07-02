# core/evaluation/evaluate_model.py
import os
import sys

# =========================================================================
# PATH FIX: Menambahkan direktori root proyek ke dalam pencarian path Python
# Mundur 2 tingkat dari lokasi file ini (dari evaluation -> core -> root proyek)
# =========================================================================
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from core.training.dataset_loader import LOLDataset
from core.models.enhancement_net import SimpleEnhanceUNet

def run_objective_evaluation():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = os.path.join("core", "models", "lol_enhanced_model.pth")
    
    # 1. Muat Dataset Khusus Evaluasi (eval15)
    DATASET_PATH = os.path.join("lol_dataset")
    if not os.path.exists(DATASET_PATH):
        print("❌ Dataset eval15 tidak ditemukan. Evaluasi dibatalkan.")
        return
        
    eval_dataset = LOLDataset(root_dir=DATASET_PATH, split='eval')
    eval_loader = DataLoader(dataset=eval_dataset, batch_size=1, shuffle=False)
    
    # 2. Inisialisasi Model & Ambil Bobot Akhir
    model = SimpleEnhanceUNet().to(device)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
    else:
        print("❌ Bobot model .pth tidak ditemukan untuk dievaluasi.")
        return

    criterion_l1 = nn.L1Loss()
    total_l1_loss = 0.0
    
    print(f"📊 Menghitung nilai MAE/L1 Loss pada {len(eval_dataset)} sampel gambar uji...")
    with torch.no_grad():
        for low_tensors, high_tensors in eval_loader:
            low_tensors = low_tensors.to(device)
            high_tensors = high_tensors.to(device)
            
            outputs = model(low_tensors)
            loss = criterion_l1(outputs, high_tensors)
            total_l1_loss += loss.item()
            
    avg_l1_loss = total_l1_loss / len(eval_loader)
    print("\n🎉 === HASIL EVALUASI OBJEKTIF MODEL AI ===")
    print(f"✨ Rata-rata MAE / L1 Loss Citra: {avg_l1_loss:.4f}")
    print("============================================\n")

if __name__ == "__main__":
    run_objective_evaluation()