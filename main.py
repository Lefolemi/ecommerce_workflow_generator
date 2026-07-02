# main.py
import tkinter as tk
import os
import threading
import gc
import zipfile
import io
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD

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
        
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join("assets", "logo", "logo.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                self.app_icon = ImageTk.PhotoImage(icon_img)
                self.root.wm_iconphoto(True, self.app_icon)
            else:
                print(f"Peringatan Log: Berkas ikon fisik tidak ditemukan di jalur: {icon_path}")
        except Exception as e:
            print(f"Gagal memuat sistem ikon aplikasi utama: {e}")
        
        # Registrasi Alur Kerja Antarmuka Workspace Terpadu dengan callback delete & custom bg
        self.gui = UnifiedWorkspace(
            self.root, 
            upload_cb=self.handle_add_to_queue, 
            process_single_cb=self.execute_single_row_pipeline, 
            run_queue_cb=self.start_queue_processing_thread, 
            save_all_cb=self.handle_save_all, 
            save_single_cb=self.handle_save_single,
            drop_cb=self.handle_add_to_queue,
            preview_item_cb=self.handle_switch_preview_target,
            help_cb=MenuHelpHandler.show_instructions,
            delete_cb=self.handle_delete_item
        )
        
        self.queue_registry = {}
        self.active_preview_id = None
        
        self.out_dir = "output"
        self.bg_dir = os.path.join("assets", "backgrounds")
        os.makedirs(self.bg_dir, exist_ok=True)
        os.makedirs(self.out_dir, exist_ok=True)
        
        self._scan_and_register_backgrounds()

    def _scan_and_register_backgrounds(self):
        """Mendaftarkan opsi studio bawaan, pemicu kustom gambar, dan aset lokal."""
        self.bg_registry = {
            "Bersih Studio": None,
            "Kustom Gambar Latar...": "CUSTOM_TRIGGER"
        }
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
            
            # FIXED: Mengganti "Putih Bersih Studio" menjadi "Bersih Studio" dan menyertakan state hex
            self.queue_registry[item_id] = {
                "absolute_path": full_path,
                "no_bg_cache": None,
                "final_result": None,
                "status": "Siap",
                "resolution": "1000",
                "ratio": "1:1 (Kotak Tokopedia/Shopee)",
                "background": "Bersih Studio",
                "bg_color_hex": "#ffffff",
                "custom_bg_path": None,
                "centering": True,
                "stickers": [
                    {"text": "", "bg_color": "#000000", "border_color": "#ffffff"},
                    {"text": "", "bg_color": "#000000", "border_color": "#ffffff"},
                    {"text": "", "bg_color": "#000000", "border_color": "#ffffff"}
                ],
                "watermark": ""
            }
            
        self.gui.update_progress(0, 100, f"⏳ Berhasil menambah {len(all_files)} foto.")

    def handle_switch_preview_target(self, selected_row_id):
        """Menyimpan konfigurasi kontrol aktif dan memuat profile dari target baris baru."""
        if self.active_preview_id and self.active_preview_id in self.queue_registry:
            old_data = self.queue_registry[self.active_preview_id]
            old_data["resolution"] = self.gui.res_var.get()
            old_data["ratio"] = self.gui.ratio_var.get()
            old_data["background"] = self.gui.bg_var.get()
            old_data["bg_color_hex"] = self.gui.bg_color_hex.get()
            old_data["centering"] = self.gui.center_var.get()
            old_data["stickers"] = self.gui.get_current_stickers_state()
            old_data["watermark"] = self.gui.watermark_var.get()

        self.active_preview_id = selected_row_id
        item_data = self.queue_registry[selected_row_id]
        
        self.gui.load_image_data_to_editor(item_data)
        self.gui.show_result(item_data["final_result"])

    def handle_delete_item(self, item_id):
        """Menghapus total representasi baris dari UI dan memori registry."""
        if item_id not in self.queue_registry: return
        
        if item_id in self.gui.row_widgets:
            self.gui.row_widgets[item_id]["frame"].destroy()
            del self.gui.row_widgets[item_id]
            
        del self.queue_registry[item_id]
        
        if self.active_preview_id == item_id:
            self.active_preview_id = None
            self.gui.show_result(None)
            self.gui.clear_texts()
            
        has_finished = any(data["status"] == "✨ Selesai" for data in self.queue_registry.values())
        if not has_finished:
            self.gui.btn_save.config(state="disabled")
            
        gc.collect()
        self.gui.status_lbl.config(text="Foto berhasil dihapus dari daftar antrean.")

    def handle_upload_custom_bg(self):
        """Handler pemanggilan dialog berkas eksternal komputer untuk gambar latar kustom."""
        if not self.active_preview_id:
            messagebox.showwarning("Peringatan", "Silakan pilih foto produk di antrean terlebih dahulu!")
            self.gui.bg_var.set("Bersih Studio")
            self.gui._on_bg_style_changed()
            return

        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        item_data = self.queue_registry[self.active_preview_id]
        
        if file_path:
            item_data["custom_bg_path"] = file_path
            item_data["background"] = "Kustom Gambar Latar..."
        else:
            if not item_data.get("custom_bg_path"):
                self.gui.bg_var.set("Bersih Studio")
                self.gui._on_bg_style_changed()

    def execute_single_row_pipeline(self, item_id, silent_refresh=False):
        """Eksekutor pipeline pengolahan citra tunggal berbasis konfigurasi terikat."""
        item_data = self.queue_registry[item_id]
        
        def _worker():
            try:
                if not silent_refresh:
                    self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "⏳ Proses...", "processing"))
                
                if item_data["no_bg_cache"] is None:
                    clean_img = standardize_input(item_data["absolute_path"])
                    clean_img = apply_lol_enhancement(clean_img)
                    item_data["no_bg_cache"] = remove_background(clean_img)
                    del clean_img

                if not silent_refresh:
                    res = int(item_data["resolution"])
                    ratio = item_data["ratio"].split(" ")[0]
                    center = item_data["centering"]
                    stickers_list = item_data["stickers"]
                    watermark_txt = item_data["watermark"]
                    
                    if item_data["background"] == "Kustom Gambar Latar...":
                        bg_path = item_data["custom_bg_path"]
                    else:
                        bg_path = self._get_bg_path_by_choice(item_data["background"])
                    bg_color = item_data.get("bg_color_hex", "#ffffff")
                else:
                    res = int(self.gui.res_var.get())
                    ratio = self.gui.ratio_var.get().split(" ")[0]
                    center = self.gui.center_var.get()
                    stickers_list = self.gui.get_current_stickers_state()
                    watermark_txt = self.gui.watermark_var.get()
                    bg_color = self.gui.bg_color_hex.get()
                    
                    if self.gui.bg_var.get() == "Kustom Gambar Latar...":
                        bg_path = item_data["custom_bg_path"]
                    else:
                        bg_path = self._get_bg_path_by_choice(self.gui.bg_var.get())
                    
                    item_data["resolution"] = str(res)
                    item_data["ratio"] = self.gui.ratio_var.get()
                    item_data["background"] = self.gui.bg_var.get()
                    item_data["bg_color_hex"] = bg_color
                    item_data["centering"] = center
                    item_data["stickers"] = stickers_list
                    item_data["watermark"] = watermark_txt
                
                final_result = process_to_packshot(
                    item_data["no_bg_cache"], res, ratio, center, 
                    bg_template_path=bg_path, 
                    stickers_list=stickers_list, 
                    watermark_text=watermark_txt,
                    custom_bg_color=bg_color
                )
                item_data["final_result"] = final_result
                item_data["status"] = "✨ Selesai"

                self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "✨ Selesai", "completed"))
                
                if self.active_preview_id == item_id or self.active_preview_id is None:
                    self.active_preview_id = item_id
                    self.root.after(0, lambda img=final_result: self.gui.show_result(img))
                
                self.root.after(0, lambda: self.gui.btn_save.config(state="normal"))
                gc.collect()

            except ValueError as ve:
                error_msg = str(ve)
                print(f"Object validation failed: {error_msg}")
                self.root.after(0, lambda msg=error_msg: self.gui.update_item_row_state(item_id, f"❌ {msg}", "failed"))
                self.root.after(2000, lambda uid=item_id: self.handle_delete_item(uid))

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
        if not item_data["final_result"] or item_data["status"] != "✨ Selesai": return

        orig_name = os.path.basename(item_data["absolute_path"])
        default_name = f"PRO_{os.path.splitext(orig_name)[0]}.jpg"

        save_path = filedialog.asksaveasfilename(
            initialfile=default_name, defaultextension=".jpg",
            filetypes=[("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            title="Pilih Lokasi untuk Ekspor Foto Produk"
        )

        if save_path:
            try:
                item_data["final_result"].convert("RGB").save(save_path, "JPEG", quality=95, optimize=True)
                messagebox.showinfo("Sukses Ekspor", f"Berhasil menyimpan file:\n{os.path.basename(save_path)}")
            except Exception as e:
                messagebox.showerror("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan file:\n{e}")

    def handle_save_all(self):
        finished_items = [data for data in self.queue_registry.values() if data["final_result"] and data["status"] == "✨ Selesai"]
        if not finished_items:
            messagebox.showwarning("Ekspor Gagal", "Belum ada foto produk yang selesai diproses!")
            return

        save_path = filedialog.asksaveasfilename(
            initialfile="Katalog_Produk_UMKM.zip", defaultextension=".zip",
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
                messagebox.showinfo("Sukses Paket Ekspor", f"Berhasil mengekspor {len(finished_items)} foto ke dalam arsip:\n{os.path.basename(save_path)}")
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