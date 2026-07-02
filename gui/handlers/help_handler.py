# gui/handlers/help_handler.py
import tkinter as tk
from tkinter import ttk
from gui.config import *

class MenuHelpHandler:
    @staticmethod
    def show_instructions():
        """
        Membuka jendela panduan grafis operasional berbasis kartu untuk 
        membimbing pengguna mengoperasikan fitur-fitur antarmuka EcoImage.
        """
        # 1. Inisialisasi Window Bantuan
        help_win = tk.Toplevel()
        help_win.title("Panduan Penggunaan Aplikasi Studio EcoImage")
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
            text="📖 PANDUAN LANGKAH OPERASIONAL APLIKASI", 
            font=FONT_TITLE, 
            fg=TEXT_LIGHT, 
            bg=BG_DARK, 
            padx=20, 
            pady=20
        ).pack(side=tk.LEFT)

        # 3. Konten Utama Menggunakan Canvas + Scrollbar
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
            lbl_step = tk.Label(parent, text=f"Langkah {step_num}", font=FONT_SECTION, fg=TEXT_LIGHT, bg=color_accent, padx=8, pady=2)
            lbl_step.pack(in_=title_line, side=tk.LEFT, padx=(0, 10))
            
            # Judul Fitur
            lbl_title = tk.Label(parent, text=title, font=FONT_SECTION, fg=TEXT_DARK, bg=BG_CARD)
            lbl_title.pack(in_=title_line, side=tk.LEFT)
            
            # Badge Indikator Status
            if badge_text:
                lbl_badge = tk.Label(parent, text=badge_text, font=("Arial", 8, "bold"), fg=color_accent, bg=BG_MAIN, padx=6, pady=1, bd=1, relief="groove")
                lbl_badge.pack(in_=title_line, side=tk.RIGHT)
                
            # Garis Pembatas Internal Kartu
            divider = tk.Frame(card, height=1, bg=BG_MAIN)
            divider.pack(fill=tk.X, pady=8)
            
            # Deskripsi Instruksi Teknis
            lbl_desc = tk.Label(card, text=desc_text, font=FONT_REGULAR, fg=TEXT_DARK, bg=BG_CARD, justify=tk.LEFT, anchor="w", wraplength=750)
            lbl_desc.pack(fill=tk.X)

        # KARTU 1: IMPORT & VALIDASI ANTREAN
        create_guide_card(
            scrollable_frame,
            step_num="1",
            title="Memasukkan Gambar & Sistem Validasi Otomatis",
            badge_text="📥 INPUT FILE",
            desc_text="• Menambahkan Foto: Klik tombol biru '📁 Ambil Foto' di panel kiri untuk memilih gambar produk dari komputer Anda, atau seret langsung file/folder ke kotak abu-abu 'Seret & Lepas'.\n"
                      "• Proteksi Gambar Latar: Aplikasi hanya menerima gambar yang memiliki objek produk jelas. Jika Anda memasukkan gambar pemandangan atau ruangan kosong, sistem akan menampilkan status gagal (❌) dan menghapus gambar tersebut dari daftar secara otomatis dalam 2 detik.\n"
                      "• Manajemen Antrean: Anda dapat menghapus foto mana saja dari daftar kapan saja dengan mengklik tombol merah 'X' di sebelah nama file.",
            color_accent=COLOR_PRIMARY
        )

        # KARTU 2: RENDER & PRATINJAU
        create_guide_card(
            scrollable_frame,
            step_num="2",
            title="Memproses Gambar & Melihat Hasil Sementara",
            badge_text="⚙️ WORKSPACE PREVIEW",
            desc_text="• Memulai Proses: Klik tombol biru 'Proses' di baris file untuk memotong latar belakang satu foto, atau klik tombol ungu '🚀 Proses Semua' untuk memproses seluruh gambar sekaligus.\n"
                      "• Navigasi Foto: Klik pada nama file gambar di panel antrean kiri untuk memunculkan pratinjau hasil editannya di Layar Monitor Utama.\n"
                      "• Live Editing: Layar monitor tengah akan memperbarui tampilan secara instan setiap kali Anda mengubah pengaturan desain stiker atau warna di panel sebelah kanan.",
            color_accent=COLOR_BATCH
        )

        # KARTU 3: ATUR LATAR
        create_guide_card(
            scrollable_frame,
            step_num="3",
            title="Mengatur Ukuran, Posisi, dan Suasana Latar Belakang",
            badge_text="🖼️ TAB ATUR LATAR",
            desc_text="• Ketajaman & Rasio: Tentukan dimensi piksel akhir gambar pada kolom Spinbox, lalu pilih format bentuk kanvas (Rasio 1:1 direkomendasikan untuk marketplace).\n"
                      "• Opsi Bersih Studio: Jika memilih 'Bersih Studio', sebuah kotak pilihan warna akan muncul di bawahnya. Klik tombol kotak tersebut untuk membuka panel warna bawaan sistem untuk menentukan warna background dasar katalog.\n"
                      "• Opsi Kustom Gambar Latar: Pilih opsi 'Kustom Gambar Latar...' pada menu turun jika ingin menggunakan file gambar dekorasi ruangan Anda sendiri sebagai background.\n"
                      "• Centering Otomatis: Centang kotak 'Posisikan Otomatis di Tengah Pas' agar produk ditaruh seimbang berdasarkan pusat massa objek fisik produk.",
            color_accent="#e67e22"
        )

        # KARTU 4: BRANDING ELEMEN
        create_guide_card(
            scrollable_frame,
            step_num="4",
            title="Memasang Stiker Promo dan Watermark Toko",
            badge_text="🏷️ TAB ELEMEN BRAND",
            desc_text="• Mengisi Stiker (Maksimal 3): Ketik teks diskon atau info komersial pada kotak teks (mendukung baris baru/Enter). Stiker tidak akan muncul di gambar jika kotak teks dibiarkan kosong.\n"
                      "• Memilih Warna Stiker: Klik tombol kotak warna di samping kanan kolom teks stiker untuk membuka palet warna penentu warna background label promo.\n"
                      "• Watermark Hak Cipta: Ketik nama toko Anda pada kolom terbawah untuk menempelkan teks kepemilikan di sudut kiri bawah gambar secara otomatis.\n"
                      "• Pembersihan Massal: Klik tombol jingga 'Bersihkan Semua Kolom Tulisan' untuk mengosongkan seluruh input teks stiker dan watermark secara instan.",
            color_accent="#34495e"
        )

        # KARTU 5: MANAGEMENT EXPORT
        create_guide_card(
            scrollable_frame,
            step_num="5",
            title="Menyimpan Hasil Pengeditan Katalog Produk",
            badge_text="💾 FINISHING & EXPORT",
            desc_text="• Ekspor Satu Berkas: Klik tombol hijau 'Export' di samping nama file pada antrean kiri untuk menyimpan gambar yang aktif dalam format JPEG berkualitas tinggi.\n"
                      "• Ekspor Massal Sekaligus: Klik tombol hijau besar '💾 SIMPAN SEMUA HASIL EKSPOR' di bagian bawah panel antrean untuk membungkus seluruh gambar yang berstatus selesai (✨ Selesai) ke dalam satu file arsip kompresi .zip tunggal.",
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