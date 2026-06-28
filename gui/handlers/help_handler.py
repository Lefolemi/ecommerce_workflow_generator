# gui/handlers/help_handler.py
import tkinter as tk
from tkinter import ttk
from gui.config import *

class MenuHelpHandler:
    @staticmethod
    def show_instructions():
        """
        Membuka jendela panduan grafis modern (Toplevel) dengan tata letak 
        berbasis kartu untuk membimbing pengguna mengoperasikan Studio EcoImage.
        """
        # 1. Inisialisasi Window Bantuan
        help_win = tk.Toplevel()
        help_win.title("Panduan Operasional & Fitur Studio EcoImage")
        help_win.geometry("850x650")
        help_win.configure(bg=BG_MAIN)
        help_win.transient() # Mengunci posisi di atas window utama
        help_win.grab_set()   # Fokus penuh pada window panduan
        
        # 2. Header Branding
        header_frame = tk.Frame(help_win, bg=BG_DARK, height=70)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="📖 PANDUAN FITUR & ALUR KERJA STUDIO", 
            font=FONT_TITLE, 
            fg=TEXT_LIGHT, 
            bg=BG_DARK, 
            padx=20, 
            pady=20
        ).pack(side=tk.LEFT)

        # 3. Konten Utama Menggunakan Canvas + Scrollbar agar Fleksibel
        container = tk.Frame(help_win, bg=BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_MAIN)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- FUNGSI HELPER UNTUK MEMBUAT KARTU PANDUAN VISUAL ---
        def create_guide_card(parent, step_num, title, badge_text, desc_text, color_accent):
            card = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", padx=15, pady=15)
            card.pack(fill=tk.X, pady=8, padx=5)
            
            # Baris Judul Kartu
            title_line = tk.Frame(card, bg=BG_CARD)
            title_line.pack(fill=tk.X, pady=(0, 5))
            
            # Nomor Langkah / Badge
            lbl_step = tk.Label(title_line, text=f"Langkah {step_num}", font=FONT_SECTION, fg=TEXT_LIGHT, bg=color_accent, padx=8, pady=2)
            lbl_step.pack(side=tk.LEFT, padx=(0, 10))
            
            # Judul Fitur
            lbl_title = tk.Label(title_line, text=title, font=FONT_SECTION, fg=TEXT_DARK, bg=BG_CARD)
            lbl_title.pack(side=tk.LEFT)
            
            # Badge Indikator AI / Status
            if badge_text:
                lbl_badge = tk.Label(title_line, text=badge_text, font=("Arial", 8, "bold"), fg=color_accent, bg=BG_MAIN, padx=6, pady=1, bd=1, relief="groove")
                lbl_badge.pack(side=tk.RIGHT)
                
            # Garis Pembatas Internal Kartu
            divider = tk.Frame(card, height=1, bg=BG_MAIN)
            divider.pack(fill=tk.X, pady=8)
            
            # Deskripsi Instruksi Teknis
            lbl_desc = tk.Label(card, text=desc_text, font=FONT_REGULAR, fg=TEXT_DARK, bg=BG_CARD, justify=tk.LEFT, anchor="w", wraplength=750)
            lbl_desc.pack(fill=tk.X)

        # 4. KARTU 1: PIPELINE RESTORASI OTOMATIS
        create_guide_card(
            scrollable_frame,
            step_num="1",
            title="Suntik Data & Antrean Foto Produk",
            badge_text="⚡ AUTOMATIC BLENDING AI",
            desc_text="• Ambil File: Tekan '📁 Ambil Foto' atau langsung seret (Drag & Drop) folder berisi banyak gambar ke area Workspace.\n"
                      "• Restorasi Kecerahan Adaptif: Sistem otomatis membaca histogram Luminance gambar masukan. Jika foto terdeteksi redup/gelap, mesin berbasis LOL Dataset akan langsung melakukan pencampuran cahaya (Alpha Blending) secara otomatis agar detail produk muncul sebelum latar belakang dipotong murni.\n"
                      "• Penghematan RAM: Gambar di atas 1024px otomatis diturunkan skalanya via Lanczos Resampling demi mencegah memory leak.",
            color_accent=COLOR_PRIMARY
        )

        # 5. KARTU 2: SEGMENTASI OBJEK
        create_guide_card(
            scrollable_frame,
            step_num="2",
            title="Eksekusi Pemotongan Latar AI (U2-Net)",
            badge_text="🧠 DEEP LEARNING SEGMENTATION",
            desc_text="• Eksekusi Pipeline: Klik tombol 'Proses' di baris file untuk memicu inferensi gambar tunggal, atau tombol '🚀 Proses Semua' untuk eksekusi antrean asinkron (Batch Worker).\n"
                      "• Asynchronous Threading: Proses kalkulasi AI berjalan di latar belakang (background thread) sehingga interface desktop Anda tidak akan membeku (Not Responding).\n"
                      "• Cache Memory: Hasil transparan RGBA disimpan dalam RAM sementara murni agar Live Refresh berjalan instan saat Anda mengubah elemen desain di panel kanan.",
            color_accent=COLOR_BATCH
        )

        # 6. KARTU 3: STUDIO DESAIN
        create_guide_card(
            scrollable_frame,
            step_num="3",
            title="Kustomisasi Latar Belakang & Bayangan Studio",
            badge_text="🎨 GEOMETRY ENGINE",
            desc_text="• Bentuk Ukuran Kanvas: Ubah rasio aspek gambar katalog pada Tab Latar (Rasio 1:1 direkomendasikan penuh untuk Shopee & Tokopedia).\n"
                      "• Posisikan Tengah Pas (Image Moments): Jika aktif, posisi produk ditaruh seimbang berdasarkan pusat massa sebaran piksel objek, bukan sekadar tengah matematis kotak.\n"
                      "• Drop Shadow Realistis: Efek bayangan jatuh otomatis digenerasikan dari siluet asli channel alpha produk dengan kepekatan opasitas 40% murni apabila Anda memilih kustom suasana latar ruangan.",
            color_accent="#e67e22"
        )

        # 7. KARTU 4: BRANDING ELEMEN
        create_guide_card(
            scrollable_frame,
            step_num="4",
            title="Konfigurasi Label Stiker & Proteksi Hak Cipta",
            badge_text="🏷️ MARKETPLACE DESIGNS",
            desc_text="• Stiker Promo Kotak (Maksimal 3): Masukkan teks diskon komersial (Mendukung baris baru / Enter). Lebar kotak luar dan dalam (wireframe) akan menyamakan skala secara otomatis (Unified Stack Block) berdasarkan teks terpanjang.\n"
                      "• Watermark Toko: Ketik nama toko Anda untuk menstempel hak cipta di sudut kiri bawah kanvas. Dilengkapi dengan panel backing abu-abu semi-transparan (Opacity 40%) agar teks tetap terbaca tajam di jenis latar apa pun.",
            color_accent="#34495e"
        )

        # 8. KARTU 5: MANAJEMEN EKSPOR
        create_guide_card(
            scrollable_frame,
            step_num="5",
            title="Penyimpanan Akhir & Ekspor Massal Archive",
            badge_text="💾 PRODUCTION FINISHING",
            desc_text="• Ekspor Tunggal: Klik tombol 'Export' di samping nama file untuk menyimpan satu gambar katalog dalam format JPEG kualitas tinggi 95% murni.\n"
                      "• Ekspor Massal (ZIP): Klik tombol hijau besar '💾 SIMPAN SEMUA HASIL EKSPOR'. Seluruh matriks gambar berstatus selesai akan dikompresi langsung di dalam buffer RAM murni menjadi satu file arsip .zip tunggal tanpa mengotori ruang penyimpanan lokal komputer Anda.",
            color_accent=COLOR_SUCCESS
        )

        # Footer Jendela Panduan
        footer = tk.Frame(scrollable_frame, bg=BG_MAIN, pady=15)
        footer.pack(fill=tk.X)
        btn_close = tk.Button(
            footer, 
            text="Dimengerti, Kembali ke Studio", 
            command=help_win.destroy, 
            bg=COLOR_SUCCESS, 
            fg="white", 
            font=FONT_SECTION, 
            bd=0, 
            padx=20, 
            pady=8, 
            cursor="hand2"
        )
        btn_close.pack(anchor="center")