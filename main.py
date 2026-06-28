# main.py
import tkinter as tk
import os
import threading
import gc
import zipfile
import io
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD

# FIXED: Menghapus is_low_light karena blending sekarang diatur otomatis secara internal
from core.engines.enhance import apply_lol_enhancement
from gui.interface import UnifiedWorkspace
from core.engines.preprocess import standardize_input
from core.engines.segmentor import remove_background
from core.transform import process_to_packshot
from gui.handlers.help_handler import MenuHelpHandler

class WorkflowController:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.wf_controller = self
        
        # SIKLUS HIDUP UTAMA: Memuat berkas logo eksternal untuk dijadikan ikon aplikasi OS
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join("assets", "logo", "logo.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                # Konversi instans PIL ke format PhotoImage Tkinter
                self.app_icon = ImageTk.PhotoImage(icon_img)
                self.root.wm_iconphoto(True, self.app_icon)
            else:
                print(f"Peringatan Log: Berkas ikon fisik tidak ditemukan di jalur: {icon_path}")
        except Exception as e:
            print(f"Gagal memuat sistem ikon aplikasi utama: {e}")
        
        # Registrasi Alur Kerja Antarmuka Workspace Terpadu
        self.gui = UnifiedWorkspace(
            self.root, 
            upload_cb=self.handle_add_to_queue, 
            process_single_cb=self.execute_single_row_pipeline, 
            run_queue_cb=self.start_queue_processing_thread, 
            save_all_cb=self.handle_save_all, 
            save_single_cb=self.handle_save_single,
            drop_cb=self.handle_add_to_queue,
            preview_item_cb=self.handle_switch_preview_target,
            help_cb=MenuHelpHandler.show_instructions
        )
        
        self.queue_registry = {}
        self.active_preview_id = None
        
        self.out_dir = "output"
        self.bg_dir = os.path.join("assets", "backgrounds")
        os.makedirs(self.bg_dir, exist_ok=True)
        os.makedirs(self.out_dir, exist_ok=True)
        
        self._scan_and_register_backgrounds()

    def _scan_and_register_backgrounds(self):
        self.bg_registry = {"Putih Bersih Studio": None}
        if os.path.exists(self.bg_dir):
            for f in os.listdir(self.bg_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    base_name = os.path.splitext(f)[0]
                    friendly_name = base_name.replace('_', ' ').replace('-', ' ').title()
                    self.bg_registry[friendly_name] = os.path.join(self.bg_dir, f)
                    
        available_options = list(self.bg_registry.keys())
        self.gui.bg_opt.config(values=available_options)

    def _get_bg_path_by_choice(self, choice_str):
        return self.bg_registry.get(choice_str, None)

    def handle_add_to_queue(self, target_paths):
        all_files = []
        if isinstance(target_paths, str): target_paths = [target_paths]

        for path in target_paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                            all_files.append(os.path.join(root, f))
            elif os.path.isfile(path) and path.lower().endswith(('.jpg', '.jpeg', '.png')):
                all_files.append(path)

        for full_path in all_files:
            if any(data["absolute_path"] == full_path for data in self.queue_registry.values()):
                continue
                
            filename = os.path.basename(full_path)
            item_id = os.urandom(4).hex()
            
            self.gui.add_item_row(item_id, filename)
            
            # FIXED: Added default background canvas variables uniquely to each image profile
            self.queue_registry[item_id] = {
                "absolute_path": full_path,
                "no_bg_cache": None,
                "final_result": None,
                "status": "Siap",
                "resolution": "1000",
                "ratio": "1:1 (Kotak Tokopedia/Shopee)",
                "background": "Putih Bersih Studio",
                "centering": True,
                "stickers": [
                    {"text": "100%\nORI", "bg_color": "#000000", "border_color": "#ffffff"},
                    {"text": "FREE\nONGKIR", "bg_color": "#ee4d2d", "border_color": "#ffffff"},
                    {"text": "", "bg_color": "#2ecc71", "border_color": "#ffffff"}
                ],
                "watermark": ""
            }
            
        self.gui.update_progress(0, 100, f"⏳ Berhasil menambah {len(all_files)} foto.")

    def handle_switch_preview_target(self, selected_row_id):
        """Saves current canvas settings/stickers data and paints the incoming target configuration profiles."""
        if self.active_preview_id and self.active_preview_id in self.queue_registry:
            old_data = self.queue_registry[self.active_preview_id]
            old_data["resolution"] = self.gui.res_var.get()
            old_data["ratio"] = self.gui.ratio_var.get()
            old_data["background"] = self.gui.bg_var.get()
            old_data["centering"] = self.gui.center_var.get()
            old_data["stickers"] = self.gui.get_current_stickers_state()
            old_data["watermark"] = self.gui.watermark_var.get()

        self.active_preview_id = selected_row_id
        item_data = self.queue_registry[selected_row_id]
        
        self.gui.load_image_data_to_editor(item_data)
        self.gui.show_result(item_data["final_result"])

    def execute_single_row_pipeline(self, item_id, silent_refresh=False):
        """Processes a single file using its own dedicated workspace configuration metrics."""
        item_data = self.queue_registry[item_id]
        
        def _worker():
            try:
                if not silent_refresh:
                    self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "⏳ Proses...", "processing"))
                
                if item_data["no_bg_cache"] is None:
                    # 1. Jalankan pra-proses pembersihan format & ukuran dasar
                    clean_img = standardize_input(item_data["absolute_path"])
                    
                    # FIXED: Penyesuaian pencahayaan adaptif otomatis dipanggil di sini tanpa if-statement biner
                    clean_img = apply_lol_enhancement(clean_img)
                        
                    # 3. Masukkan gambar yang sudah optimal secara pencahayaan ke Segmentor AI
                    item_data["no_bg_cache"] = remove_background(clean_img)
                    del clean_img

                if not silent_refresh:
                    res = int(item_data["resolution"])
                    ratio = item_data["ratio"].split(" ")[0]
                    center = item_data["centering"]
                    bg_path = self._get_bg_path_by_choice(item_data["background"])
                    stickers_list = item_data["stickers"]
                    watermark_txt = item_data["watermark"]
                else:
                    res = int(self.gui.res_var.get())
                    ratio = self.gui.ratio_var.get().split(" ")[0]
                    center = self.gui.center_var.get()
                    bg_path = self._get_bg_path_by_choice(self.gui.bg_var.get())
                    stickers_list = self.gui.get_current_stickers_state()
                    watermark_txt = self.gui.watermark_var.get()
                    
                    item_data["resolution"] = str(res)
                    item_data["ratio"] = self.gui.ratio_var.get()
                    item_data["background"] = self.gui.bg_var.get()
                    item_data["centering"] = center
                    item_data["stickers"] = stickers_list
                    item_data["watermark"] = watermark_txt
                
                final_result = process_to_packshot(
                    item_data["no_bg_cache"], res, ratio, center, 
                    bg_template_path=bg_path, 
                    stickers_list=stickers_list, 
                    watermark_text=watermark_txt
                )
                item_data["final_result"] = final_result
                item_data["status"] = "✨ Selesai"

                self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "✨ Selesai", "completed"))
                
                if self.active_preview_id == item_id or self.active_preview_id is None:
                    self.active_preview_id = item_id
                    self.root.after(0, lambda img=final_result: self.gui.show_result(img))
                
                self.root.after(0, lambda: self.gui.btn_save.config(state="normal"))
                gc.collect()
            except Exception as e:
                print(f"Row workflow failed: {e}")
                self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "❌ Gagal", "failed"))

        if silent_refresh:
            _worker()
        else:
            threading.Thread(target=_worker, daemon=True).start()

    def start_queue_processing_thread(self):
        if not self.queue_registry: return
        
        def _batch_worker():
            total = len(self.queue_registry)
            for idx, item_id in enumerate(self.queue_registry.keys(), 1):
                self.root.after(0, lambda i=idx, t=total: self.gui.update_progress(i, t, f"🔄 Memproses ({i}/{t})"))
                self.execute_single_row_pipeline(item_id, silent_refresh=True)
            self.root.after(0, lambda: messagebox.showinfo("Selesai", "Batch conversion process done!"))
            
        threading.Thread(target=_batch_worker, daemon=True).start()

    def handle_save_single(self, item_id):
        item_data = self.queue_registry[item_id]
        if not item_data["final_result"] or item_data["status"] != "✨ Selesai":
            return

        orig_name = os.path.basename(item_data["absolute_path"])
        default_name = f"PRO_{os.path.splitext(orig_name)[0]}.jpg"

        save_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".jpg",
            filetypes=[("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            title="Pilih Lokasi untuk Ekspor Foto Produk"
        )

        if save_path:
            try:
                item_data["final_result"].convert("RGB").save(save_path, "JPEG", quality=95, optimize=True)
                just_filename = os.path.basename(save_path)
                messagebox.showinfo("Sukses Ekspor", f"Berhasil menyimpan file:\n{just_filename}")
            except Exception as e:
                messagebox.showerror("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan file:\n{e}")

    def handle_save_all(self):
        finished_items = [data for data in self.queue_registry.values() if data["final_result"] and data["status"] == "✨ Selesai"]
        
        if not finished_items:
            messagebox.showwarning("Ekspor Gagal", "Belum ada foto produk yang selesai diproses!")
            return

        save_path = filedialog.asksaveasfilename(
            initialfile="Katalog_Produk_UMKM.zip",
            defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")],
            title="Pilih Lokasi untuk Menyimpan Paket ZIP Ekspor"
        )

        if save_path:
            try:
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for data in finished_items:
                        orig_name = os.path.basename(data["absolute_path"])
                        output_name = f"PRO_{os.path.splitext(orig_name)[0]}.jpg"
                        
                        img_buffer = io.BytesIO()
                        data["final_result"].convert("RGB").save(img_buffer, "JPEG", quality=95, optimize=True)
                        img_buffer.seek(0)
                        
                        zip_file.writestr(output_name, img_buffer.read())
                        img_buffer.close()

                with open(save_path, "wb") as f:
                    f.write(zip_buffer.getvalue())
                
                zip_buffer.close()
                gc.collect()

                just_zipname = os.path.basename(save_path)
                messagebox.showinfo("Sukses Paket Ekspor", f"Berhasil mengekspor {len(finished_items)} foto ke dalam arsip:\n{just_zipname}")
                
            except Exception as e:
                messagebox.showerror("Gagal Membuat ZIP", f"Terjadi kesalahan kompresi arsip:\n{e}")

    def run(self):
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.attributes('-zoomed', True)
            
        self.root.mainloop()

if __name__ == "__main__":
    WorkflowController().run()