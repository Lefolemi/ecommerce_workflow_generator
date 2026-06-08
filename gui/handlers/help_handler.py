# gui/handlers/help_handler.py
import tkinter as tk
from tkinter import messagebox

class MenuHelpHandler:
    @staticmethod
    def show_instructions():
        """
        Menampilkan pop-up dialog berisi petunjuk penggunaan aplikasi secara linear,
        membimbing pemilik toko dari proses import data hingga ekspor hasil jadi.
        """
        guide_text = (
            "👋 Selamat Datang di Studio Desain Massal Katalog Produk!\n\n"
            "Gunakan aplikasi ini secara berurutan lewat menu Navigasi Top Bar di atas:\n\n"
            "1. HALAMAN OPSI 1 (Upload & Antrian):\n"
            "   - Tekan tombol '📁 Ambil File Foto Produk' untuk memilih satu atau beberapa gambar.\n"
            "   - Anda juga bisa langsung menyeret & melepas (Drag & Drop) folder berisi banyak foto ke area putih.\n"
            "   - Klik tombol ungu '🚀 Mulai Proses Semua Foto sekaligus' untuk menjalankan pemotongan latar belakang AI.\n\n"
            "2. HALAMAN OPSI 2 (Atur Background):\n"
            "   - Tentukan resolusi ketajaman akhir (Disarankan: 1000 hingga 1200 pixel).\n"
            "   - Pilih Aspek Rasio (Rasio 1:1 Kotak sangat direkomendasikan untuk Tokopedia dan Shopee).\n"
            "   - Pilih kustom suasana latar belakang ruangan tempat produk Anda bersandar.\n\n"
            "3. HALAMAN OPSI 3 (Desain Label Stiker):\n"
            "   - Masukkan tulisan diskon pada kolom stiker promo (Contoh: 'Diskon\\n50%!' atau '100%\\nOriginal!').\n"
            "   - Masukkan nama toko Anda pada kolom Watermark untuk mengunci hak cipta foto agar aman dari pencurian.\n\n"
            "4. PROSES PENYIMPANAN AKHIR:\n"
            "   - Kembali ke halaman 1, lalu tekan tombol hijau '💾 Simpan Semua Hasil Foto'.\n"
            "   - Seluruh hasil komposit komersial akan langsung tersimpan rapi di dalam folder 'output'."
        )
        
        messagebox.showinfo("Bantuan & Petunjuk Operasional", guide_text)