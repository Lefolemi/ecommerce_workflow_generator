# core/training/dataset_loader.py
import os
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

class LOLDataset(Dataset):
    def __init__(self, root_dir, split='train', transform=None):
        """
        root_dir: Jalur ke folder 'lol_dataset'
        split: 'train' untuk menggunakan folder our485, 'eval' untuk eval15
        """
        self.split_dir = "our485" if split == 'train' else "eval15"
        self.low_dir = os.path.join(root_dir, self.split_dir, "low")
        self.high_dir = os.path.join(root_dir, self.split_dir, "high")
        
        if not os.path.exists(self.low_dir):
            raise FileNotFoundError(f"Direktori tidak ditemukan: {self.low_dir}")
            
        self.file_names = [f for f in os.listdir(self.low_dir) if f.lower().endswith('.png')]
        self.transform = transform if transform else transforms.ToTensor()

    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, idx):
        file_name = self.file_names[idx]
        
        low_img_path = os.path.join(self.low_dir, file_name)
        high_img_path = os.path.join(self.high_dir, file_name)
        
        low_img = Image.open(low_img_path).convert("RGB")
        high_img = Image.open(high_img_path).convert("RGB")
        
        low_tensor = self.transform(low_img)
        high_tensor = self.transform(high_img)
        
        return low_tensor, high_tensor

# =========================================================================
# BAGIAN RUNNER: Blok ini berjalan jika skrip ini dieksekusi langsung
# =========================================================================
if __name__ == "__main__":
    # Tentukan jalur ke folder lol_dataset Anda (sesuaikan jika letaknya berbeda)
    # Asumsi struktur: proyek_anda/lol_dataset/
    DATASET_PATH = os.path.join("lol_dataset")
    
    print("⏳ Menginisialisasi LOL Dataset Loader...")
    try:
        # 1. Instansiasi objek dataset kustom
        train_dataset = LOLDataset(root_dir=DATASET_PATH, split='train')
        
        # 2. Bungkus ke dalam DataLoader PyTorch untuk batching & shuffling
        train_loader = DataLoader(dataset=train_dataset, batch_size=4, shuffle=True)
        
        print(f"✅ Dataset berhasil dimuat!")
        print(f"📊 Total sampel gambar low-light untuk training: {len(train_dataset)}")
        print(f"📦 Total batch (dengan batch_size=4): {len(train_loader)}\n")
        
        # 3. Ambil satu batch sampel untuk memastikan dimensi tensor sudah benar
        print("🔄 Mencoba mengambil 1 batch data sampel...")
        sample_low, sample_high = next(iter(train_loader))
        
        # Dimensi PyTorch Tensor: [Batch_Size, Channels, Height, Width]
        print(f"📐 Dimensi Tensor Gambar Gelap (Low): {sample_low.shape}")
        print(f"📐 Dimensi Tensor Gambar Terang (High): {sample_high.shape}")
        print("\n🎉 Sukses! Dataset Loader siap digunakan untuk Training Loop AI.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Pastikan folder dataset sudah ditaruh di dalam folder lol_dataset/ dengan benar.")
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")