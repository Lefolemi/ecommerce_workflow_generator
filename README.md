# PANDUAN INSTALASI DAN MENJALANKAN ECOIMAGE

Dalam Google Drive dan GitHUb, projek bernama "ecommerce_workflow_generator"

Ikuti langkah-langkah berikut untuk menyiapkan lingkungan virtual Python, memasang seluruh dependensi AI/GUI yang dibutuhkan, dan menjalankan aplikasi Studio Desain Produk EcoImage.

Prasyarat Sistem

* Python: Versi 3.10 hingga 3.12 (Direkomendasikan 3.11).
* Sistem Operasi: Windows 10/11, macOS, atau Linux (Ubuntu/Debian).
* Koneksi Internet: Diperlukan pada instalasi awal untuk mengunduh model AI U2-Net (rembg).

Langkah 1: Klon atau Siapkan Direktori Proyek
Pastikan struktur folder Anda sudah lengkap seperti di bawah ini sebelum memulai:
EcoImage/
├── assets/
│   ├── backgrounds/
│   └── logo/
├── core/
│   ├── engines/
│   ├── evaluation/
│   ├── models/
│   └── training/
├── gui/
│   └── handlers/
├── output/
├── main.py
└── requirements.txt

Langkah 2: Buat & Aktifkan Virtual Environment
Buka Terminal (Linux/macOS) atau Command Prompt/PowerShell (Windows) di dalam direktori proyek EcoImage/, lalu jalankan perintah berikut:

Windows:
python -m venv venv
venv\Scripts\activate

Linux / macOS:
python3 -m venv venv
source venv/bin/activate

Langkah 3: Perbarui PIP & Pasang Dependensi
Setelah virtual environment aktif (ditandai dengan munculnya teks (venv) di depan baris terminal), pasang seluruh paket dependensi sesuai spesifikasi environment freeze:

python -m pip install --upgrade pip
pip install -r requirements.txt

Langkah 4: Konfigurasi Aset & Bobot Model AI (Penting)

1. Bobot Jaringan Low-Light (EnhancementNet)
Aplikasi membutuhkan berkas bobot pre-trained untuk fitur pencerah gambar otomatis. Pastikan file bobot sudah diletakkan pada jalur berikut:
Jalur File: core/models/lol_enhanced_model.pth
Catatan: Jika file tidak ditemukan, sistem akan berjalan dalam mode fallback menggunakan algoritma peningkatan kecerahan standar Pillow.
2. Unduh Otomatis Model Segmentasi (U2-Net)
Saat aplikasi pertama kali dijalankan dan memproses gambar, pustaka rembg akan mengunduh model u2net.onnx secara otomatis dari server internet ke direktori home cache pengguna. Pastikan koneksi internet Anda stabil pada proses pertamanya.

Langkah 5: Jalankan Aplikasi Utama
Eksekusi skrip induk main.py menggunakan interpreter Python dari virtual environment:

python main.py

Setelah perintah dijalankan, jendela antarmuka grafis EcoImage Studio akan terbuka secara otomatis dengan ukuran layar maksimal, siap menerima drag-and-drop file gambar produk untuk diproses.

Troubleshooting (Penyelesaian Masalah)

1. Masalah TclError / TkinterDnD pada Windows/Linux
Jika terminal memunculkan pesan error terkait tkinterdnd2 tidak dapat dimuat, pastikan pustaka dasar Tkinter sistem Anda sudah terpasang dengan benar. Di Ubuntu/Debian, jalankan perintah "sudo apt-get install python3-tk" sebelum mengaktifkan venv.
2. Memaksa Pemrosesan Menggunakan CPU / GPU (CUDA)
Logika pemrosesan low-light pada core/engines/enhance.py akan otomatis mendeteksi kartu grafis jika driver NVIDIA CUDA terpasang. Jika Anda mengalami crash akibat VRAM penuh, pastikan aplikasi berjalan pada mode CPU dengan memeriksa ketersediaan perangkat keras di terminal log saat inisialisasi awal.