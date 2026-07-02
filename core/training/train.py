# core/training/train.py
import os
import sys

# =========================================================================
# PATH FIX: Menambahkan direktori root proyek ke dalam pencarian path Python
# Mundur 2 tingkat dari lokasi file ini (dari training -> core -> root proyek)
# =========================================================================
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision.utils import save_image

# Import komponen lokal yang sekarang aman dipanggil dari mana saja
from core.training.dataset_loader import LOLDataset
from core.models.enhancement_net import SimpleEnhanceUNet

def train_model(epochs=10, batch_size=4, lr=0.001):
    # 1. Konfigurasi Perangkat (Gunakan GPU jika tersedia untuk akselerasi)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Memulai training menggunakan perangkat: {device}")

    # 2. Inisialisasi Data Loader
    DATASET_PATH = os.path.join("lol_dataset")
    train_dataset = LOLDataset(root_dir=DATASET_PATH, split='train')
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    # 3. Inisialisasi Model, Loss Function, dan Optimizer
    model = SimpleEnhanceUNet().to(device)
    criterion = nn.L1Loss() # Efektif untuk menjaga ketajaman tepi objek dan konsistensi warna
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Buat direktori checkpoint jika belum ada
    os.makedirs(os.path.join("core", "models"), exist_ok=True)
    os.makedirs("output/sample_training", exist_ok=True)

    print("🚀 Memulai proses iterasi pelatihan AI...")
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        
        for batch_idx, (low_imgs, high_imgs) in enumerate(train_loader):
            # Pindahkan data ke GPU/CPU
            low_imgs = low_imgs.to(device)
            high_imgs = high_imgs.to(device)
            
            # Forward pass: Prediksi gambar terang dari gambar gelap
            outputs = model(low_imgs)
            loss = criterion(outputs, high_imgs)
            
            # Backward pass: Kalkulasi gradien dan perbarui bobot
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        epoch_loss = running_loss / len(train_loader)
        print(f"📊 Epoch [{epoch}/{epochs}] -> Rata-rata Loss: {epoch_loss:.4f}")
        
        # Simpan sampel gambar visual setiap 2 epoch untuk memantau perkembangan pencahayaan
        if epoch % 2 == 0:
            sample_output = torch.cat((low_imgs[0], outputs[0], high_imgs[0]), dim=2)
            save_image(sample_output, f"output/sample_training/epoch_{epoch}.png")
            print(f"📸 Sampel visual hasil peningkatan cahaya disimpan di: output/sample_training/epoch_{epoch}.png")

    # 4. Simpan Bobot Akhir Model (.pth)
    model_path = os.path.join("core", "models", "lol_enhanced_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"\n🎉 Training Selesai! File bobot model pintar disimpan di: {model_path}")

if __name__ == "__main__":
    # Jalankan training awal sebanyak 10 epoch untuk validasi alur kerja
    train_model(epochs=10, batch_size=4, lr=0.001)