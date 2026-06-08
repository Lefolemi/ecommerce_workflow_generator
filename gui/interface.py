# gui/interface.py
import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
from gui.config import *

class UnifiedWorkspace:
    def __init__(self, root, upload_cb, process_single_cb, run_queue_cb, save_all_cb, save_single_cb, drop_cb, preview_item_cb, help_cb):
        self.root = root
        self.root.title("Aplikasi Studio Desain Produk UMKM - Unified Edition")
        self.root.geometry("1400x800")
        
        self.cbs = {
            "upload": upload_cb, "process_single": process_single_cb, "run_queue": run_queue_cb,
            "save_all": save_all_cb, "save_single": save_single_cb, "drop": drop_cb, "preview": preview_item_cb
        }
        
        # STATE REGISTRY GLOBAL
        self.res_var = tk.StringVar(value="1000")
        self.ratio_var = tk.StringVar(value="1:1 (Kotak Tokopedia/Shopee)")
        self.bg_var = tk.StringVar(value="Putih Bersih Studio")
        self.center_var = tk.BooleanVar(value=True)
        self.sticker_var = tk.StringVar(value="100%\\nOriginal!")
        self.watermark_var = tk.StringVar(value="")

        # Dictionary to track row widgets: {item_id: {"status_lbl": Label, "btn_proc": Button, "btn_exp": Button}}
        self.row_widgets = {}

        # 1. HEADER BRANDING TOP BAR (Bersih dari duplikasi pack)
        header = tk.Frame(self.root, bg=BG_DARK, height=50)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        # Penampung Logo + Teks di sisi kiri header
        brand_frame = tk.Frame(header, bg=BG_DARK)
        brand_frame.pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        try:
            # Memuat logo putih kustom dan memperkecil secara proporsional ke 32x32 piksel
            logo_img = Image.open(os.path.join("assets", "logo", "logo_white.png"))
            logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.header_logo = ImageTk.PhotoImage(logo_img)
            
            lbl_logo = tk.Label(brand_frame, image=self.header_logo, bg=BG_DARK)
            lbl_logo.pack(side=tk.LEFT, pady=9)
        except Exception as e:
            # Fallback menggunakan emoji jika file logo fisik tidak ditemukan di direktori
            print(f"Gagal memuat logo header: {e}")
            tk.Label(brand_frame, text="🌱", font=FONT_TITLE, fg=TEXT_LIGHT, bg=BG_DARK).pack(side=tk.LEFT)
            
        # Mengganti teks lama menjadi "EcoImage" sesuai instruksi kustom baru
        tk.Label(brand_frame, text="EcoImage", font=FONT_TITLE, fg=TEXT_LIGHT, bg=BG_DARK, padx=8).pack(side=tk.LEFT)

        tk.Button(header, text="❓ Panduan Fitur", command=help_cb, bg="#e74c3c", font=FONT_SECTION, fg="white", bd=0, padx=15, cursor="hand2").pack(side=tk.RIGHT, fill=tk.Y)

        # FRAME UTAMA WORKSPACE
        main_layout = tk.Frame(self.root, bg=BG_MAIN)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 2. KOLOM KIRI: PANEL ANTRIAN FILE (WEB-CONVERTER ROW STYLE)
        left_panel = tk.Frame(main_layout, width=420, bg=BG_CARD, bd=1, relief="solid", padx=10, pady=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="📋 DAFTAR ANTRIAN FOTO", font=FONT_SECTION, bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w", pady=(0, 5))
        
        btn_f = tk.Frame(left_panel, bg=BG_CARD)
        btn_f.pack(fill=tk.X, pady=5)
        tk.Button(btn_f, text="📁 Ambil Foto", command=self.open_file, bg=COLOR_PRIMARY, fg="white", font=FONT_REGULAR, bd=0, padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        tk.Button(btn_f, text="🚀 Proses Semua", command=self.cbs["run_queue"], bg=COLOR_BATCH, fg="white", font=FONT_REGULAR, bd=0, padx=10, pady=5, cursor="hand2").pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Drop Zone
        self.drop_zone = tk.Label(left_panel, text="➕ Seret & Lepas Folder/File ke Sini", font=FONT_ITALIC, bg=BG_PREVIEW, fg=TEXT_MUTED, bd=1, relief="groove", pady=12)
        self.drop_zone.pack(fill=tk.X, pady=5)
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.parse_drop_event)

        # Scrollable Container for Rows
        scroll_container = tk.Frame(left_panel, bg=BG_PREVIEW, bd=1, relief="solid")
        scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        self.queue_canvas = tk.Canvas(scroll_container, bg=BG_PREVIEW, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.queue_canvas.yview)
        self.queue_rows_frame = tk.Frame(self.queue_canvas, bg=BG_PREVIEW)
        
        self.queue_rows_frame.bind("<Configure>", lambda e: self.queue_canvas.configure(scrollregion=self.queue_canvas.bbox("all")))
        self.queue_canvas.create_window((0, 0), window=self.queue_rows_frame, anchor="nw", width=395)
        self.queue_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.queue_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Global Actions Bottom
        self.btn_save = tk.Button(left_panel, text="💾 SIMPAN SEMUA HASIL EKSPOR", command=self.cbs["save_all"], bg=COLOR_SUCCESS, fg="white", font=FONT_SECTION, bd=0, pady=8, state="disabled", cursor="hand2")
        self.btn_save.pack(fill=tk.X, pady=(5, 0))

        self.status_lbl = tk.Label(left_panel, text="Aplikasi Siap...", font=FONT_REGULAR, fg=TEXT_DARK, bg=BG_CARD, anchor="w")
        self.status_lbl.pack(fill=tk.X, pady=(5, 0))
        self.progress_bar = ttk.Progressbar(left_panel, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(2, 0))

        # 3. KOLOM TENGAH: MONITOR MONITOR UTAMA
        center_panel = tk.Frame(main_layout, bg=BG_MAIN, padx=10)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        studio_frame = tk.Frame(center_panel, bd=1, relief="solid", bg=BG_CARD)
        studio_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(studio_frame, text="💻 LAYAR MONITOR UTAMA", font=FONT_SECTION, bg=BG_CARD, fg=TEXT_DARK).pack(pady=5)
        self.canvas_res = tk.Label(studio_frame, bg=BG_PREVIEW, text="Silakan ambil gambar untuk melihat pratinjau live studio.")
        self.canvas_res.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # 4. KOLOM KANAN: PANEL NAVIGASI ATAS UNTUK FITUR
        right_panel = tk.Frame(main_layout, width=340, bg=BG_DARK, padx=5, pady=5)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TopMenu.TNotebook", background=BG_DARK, borderwidth=0, padding=0)
        style.configure("TopMenu.TNotebook.Tab", font=FONT_SECTION, padding=[20, 8], background="#34495e", foreground=TEXT_LIGHT, borderwidth=0, focuscolor="")
        style.map("TopMenu.TNotebook.Tab", background=[("selected", COLOR_PRIMARY)], foreground=[("selected", "white")], padding=[("selected", [20, 8])], expand=[("selected", [0, 0, 0, 0])])
        style.configure("TFrame", background=BG_DARK)

        self.notebook = ttk.Notebook(right_panel, style="TopMenu.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # TAB 1: LATAR
        tab_bg = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_bg, text="🖼️ Atur Latar")
        tk.Label(tab_bg, text="Ketajaman Gambar (Pixel):", fg=TEXT_LIGHT, bg=BG_DARK, font=FONT_REGULAR).pack(anchor="w", pady=(10, 0))
        tk.Spinbox(tab_bg, from_=400, to=4000, increment=100, textvariable=self.res_var, font=FONT_REGULAR, bg=BG_MAIN, fg=TEXT_DARK, bd=0).pack(fill=tk.X, pady=4)
        tk.Label(tab_bg, text="Bentuk Ukuran Kanvas:", fg=TEXT_LIGHT, bg=BG_DARK, font=FONT_REGULAR).pack(anchor="w", pady=(10, 0))
        ttk.Combobox(tab_bg, textvariable=self.ratio_var, values=["1:1 (Kotak Tokopedia/Shopee)", "4:3 (Standar HP)", "16:9 (Memanjang Landscape)"], state="readonly").pack(fill=tk.X, pady=4)
        tk.Label(tab_bg, text="Suasana Latar Belakang:", fg=TEXT_LIGHT, bg=BG_DARK, font=FONT_REGULAR).pack(anchor="w", pady=(10, 0))
        self.bg_opt = ttk.Combobox(tab_bg, textvariable=self.bg_var, state="readonly")
        self.bg_opt.pack(fill=tk.X, pady=4)
        tk.Checkbutton(tab_bg, text="Posisikan Otomatis di Tengah Pas", variable=self.center_var, fg=TEXT_LIGHT, bg=BG_DARK, selectcolor=BG_DARK, activebackground=BG_DARK, activeforeground=TEXT_LIGHT, font=FONT_REGULAR).pack(anchor="w", pady=15)

        # TAB 2: BRANDING
        tab_brand = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_brand, text="🏷️ Elemen Brand")
        tk.Label(tab_brand, text="Tulisan Teks Stiker Promo (Gunakan \\n):", fg=TEXT_LIGHT, bg=BG_DARK, font=FONT_REGULAR).pack(anchor="w", pady=(10, 0))
        tk.Entry(tab_brand, textvariable=self.sticker_var, font=FONT_REGULAR, bg=BG_MAIN, fg=TEXT_DARK, bd=0).pack(fill=tk.X, pady=4)
        tk.Label(tab_brand, text="Nama Watermark Pemilik Toko:", fg=TEXT_LIGHT, bg=BG_DARK, font=FONT_REGULAR).pack(anchor="w", pady=(10, 0))
        tk.Entry(tab_brand, textvariable=self.watermark_var, font=FONT_REGULAR, bg=BG_MAIN, fg=TEXT_DARK, bd=0).pack(fill=tk.X, pady=4)
        tk.Button(tab_brand, text="🧹 Bersihkan Semua Kolom Tulisan", command=self.clear_texts, bg="#e67e22", fg="white", bd=0, pady=6, font=FONT_REGULAR, cursor="hand2").pack(fill=tk.X, pady=25)

        self._bind_traces()

    def add_item_row(self, item_id, filename):
        """Spawns an isolated web-style row entry with separate action buttons."""
        row_frame = tk.Frame(self.queue_rows_frame, bg=BG_CARD, pady=6, padx=8, bd=1, relief="groove")
        row_frame.pack(fill=tk.X, pady=2, padx=2)

        # Clickable File Meta area (triggers middle monitor preview selection)
        meta_click_area = tk.Frame(row_frame, bg=BG_CARD, cursor="hand2")
        meta_click_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        meta_click_area.bind("<Button-1>", lambda e, uid=item_id: self.cbs["preview"](uid))

        lbl_name = tk.Label(meta_click_area, text=filename, font=FONT_REGULAR, fg=TEXT_DARK, bg=BG_CARD, anchor="w")
        lbl_name.pack(side=tk.TOP, fill=tk.X)
        lbl_name.bind("<Button-1>", lambda e, uid=item_id: self.cbs["preview"](uid))

        lbl_status = tk.Label(meta_click_area, text="⏳ Siap", font=FONT_ITALIC, fg=TEXT_MUTED, bg=BG_CARD, anchor="w")
        lbl_status.pack(side=tk.TOP, fill=tk.X)
        lbl_status.bind("<Button-1>", lambda e, uid=item_id: self.cbs["preview"](uid))

        # Inline Converter Action Buttons Panel
        actions_panel = tk.Frame(row_frame, bg=BG_CARD)
        actions_panel.pack(side=tk.RIGHT, fill=tk.Y)

        btn_proc = tk.Button(actions_panel, text="Proses", command=lambda: self.cbs["process_single"](item_id), bg=COLOR_PRIMARY, fg="white", font=("Arial", 9, "bold"), bd=0, padx=6, pady=3, cursor="hand2")
        btn_proc.pack(side=tk.LEFT, padx=2)

        btn_exp = tk.Button(actions_panel, text="Export", command=lambda: self.cbs["save_single"](item_id), bg=COLOR_SUCCESS, fg="white", font=("Arial", 9, "bold"), bd=0, padx=6, pady=3, state="disabled", cursor="hand2")
        btn_exp.pack(side=tk.LEFT, padx=2)

        # Store widgets reference map to allow live status/button swapping from main thread
        self.row_widgets[item_id] = {
            "frame": row_frame,
            "status_lbl": lbl_status,
            "btn_proc": btn_proc,
            "btn_exp": btn_exp
        }

    def update_item_row_state(self, item_id, status_text, state_mode="ready"):
        """Dynamically updates the row layout configuration like a free converter site."""
        if item_id not in self.row_widgets: return
        wdg = self.row_widgets[item_id]
        
        if state_mode == "processing":
            wdg["status_lbl"].config(text=status_text, fg="#e67e22", font=FONT_ITALIC)
            wdg["btn_proc"].config(state="disabled", bg="#bdc3c7")
        elif state_mode == "completed":
            wdg["status_lbl"].config(text=status_text, fg="#27ae60", font=FONT_REGULAR)
            wdg["btn_proc"].config(text="Re-Bake", state="normal", bg="#34495e")
            wdg["btn_exp"].config(state="normal", bg=COLOR_SUCCESS)
        elif state_mode == "failed":
            wdg["status_lbl"].config(text=status_text, fg="#c0392b", font=FONT_REGULAR)
            wdg["btn_proc"].config(text="Retry", state="normal", bg=COLOR_PRIMARY)

    def _bind_traces(self):
        self.res_var.trace_add("write", lambda *args: self.trigger_live_refresh())
        self.ratio_var.trace_add("write", lambda *args: self.trigger_live_refresh())
        self.bg_var.trace_add("write", lambda *args: self.trigger_live_refresh())
        self.center_var.trace_add("write", lambda *args: self.trigger_live_refresh())
        self.sticker_var.trace_add("write", lambda *args: self.trigger_live_refresh())
        self.watermark_var.trace_add("write", lambda *args: self.trigger_live_refresh())

    def open_file(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if paths: self.cbs["upload"](list(paths))

    def parse_drop_event(self, event):
        raw_data = event.data
        paths = []
        if "{" in raw_data:
            items = raw_data.split("}")
            for item in items:
                cleaned = item.replace("{", "").strip()
                if cleaned: paths.append(cleaned)
        else:
            paths = [p.strip() for p in raw_data.split(" ") if p.strip()]
        if paths: self.cbs["drop"](paths)

    def clear_texts(self):
        self.sticker_var.set("")
        self.watermark_var.set("")

    def trigger_live_refresh(self):
        # Fallback callback proxy to allow settings configuration trace updates on focused frame
        if hasattr(self.root, 'wf_controller') and self.root.wf_controller.active_preview_id:
            try:
                val_res = self.res_var.get()
                ratio_clean = self.ratio_var.get().split(" ")[0]
                if val_res:
                    self.cbs["process_single"](self.root.wf_controller.active_preview_id, silent_refresh=True)
            except ValueError: pass

    def update_progress(self, current, total, text_status):
        percent = (current / total) * 100
        self.progress_bar.configure(value=percent)
        self.status_lbl.config(text=text_status)
        self.root.update_idletasks()

    def show_result(self, pil_img):
        if pil_img is None:
            self.canvas_res.config(image="", text="Gunakan opsi 'Proses' di baris file untuk render.")
            return
        cw, ch = self.canvas_res.winfo_width(), self.canvas_res.winfo_height()
        if cw < 50 or ch < 50: cw, ch = 550, 550
        preview_copy = pil_img.copy()
        preview_copy.thumbnail((cw - 20, ch - 20), Image.Resampling.LANCZOS)
        tk_photo = ImageTk.PhotoImage(preview_copy)
        self.canvas_res.config(image=tk_photo, text="")
        self.canvas_res.image = tk_photo