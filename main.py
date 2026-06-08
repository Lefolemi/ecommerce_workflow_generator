# main.py
import tkinter as tk
import os
import threading
import gc
import zipfile
import io
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD

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
            item_id = os.urandom(4).hex() # Secure isolated ID keys
            
            # Spawn web row elements dynamically inside the canvas frame
            self.gui.add_item_row(item_id, filename)
            
            self.queue_registry[item_id] = {
                "absolute_path": full_path,
                "no_bg_cache": None,
                "final_result": None,
                "status": "Siap"
            }
            
        self.gui.update_progress(0, 100, f"⏳ Berhasil menambah {len(all_files)} foto.")

    def execute_single_row_pipeline(self, item_id, silent_refresh=False):
        """Processes a single file. Maps 'Proses' to 'Re-Bake' and activates individual 'Export' on success."""
        item_data = self.queue_registry[item_id]
        
        def _worker():
            try:
                if not silent_refresh:
                    self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "⏳ Proses...", "processing"))
                
                # Check background cache to avoid repeating segmentation processing steps
                if item_data["no_bg_cache"] is None:
                    clean_img = standardize_input(item_data["absolute_path"])
                    item_data["no_bg_cache"] = remove_background(clean_img)
                    del clean_img

                res = int(self.gui.res_var.get())
                ratio = self.gui.ratio_var.get().split(" ")[0]
                center = self.gui.center_var.get()
                bg_path = self._get_bg_path_by_choice(self.gui.bg_var.get())
                sticker_txt = self.gui.sticker_var.get()
                watermark_txt = self.gui.watermark_var.get()
                
                final_result = process_to_packshot(
                    item_data["no_bg_cache"], res, ratio, center, 
                    bg_template_path=bg_path, sticker_text=sticker_txt, watermark_text=watermark_txt
                )
                item_data["final_result"] = final_result
                item_data["status"] = "✨ Selesai"

                # UI Inline buttons swap swap state rules
                self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "✨ Selesai", "completed"))
                
                # Instantly draw output frame if active selection matches this row sequence
                if self.active_preview_id == item_id or self.active_preview_id is None:
                    self.active_preview_id = item_id
                    self.root.after(0, lambda img=final_result: self.gui.show_result(img))
                
                self.root.after(0, lambda: self.gui.btn_save.config(state="normal"))
                gc.collect()
            except Exception as e:
                print(f"Row workflow failed: {e}")
                self.root.after(0, lambda: self.gui.update_item_row_state(item_id, "❌ Gagal", "failed"))

        if silent_refresh:
            _worker() # Immediate evaluation context for slider configuration write trace callbacks
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

    def handle_switch_preview_target(self, selected_row_id):
        """Highlights row container profile and presents the processed data context onto monitor panel."""
        self.active_preview_id = selected_row_id
        item_data = self.queue_registry[selected_row_id]
        
        # Enforce dynamic container border background visual feedback context modifications here if desired
        self.gui.show_result(item_data["final_result"])

    def handle_save_single(self, item_id):
        """
        Membuka jendela dialog penyimpanan interaktif agar pengguna bisa 
        memilih sendiri direktori folder tujuan dan nama file ekspor hasil.
        """
        item_data = self.queue_registry[item_id]
        if not item_data["final_result"] or item_data["status"] != "✨ Selesai":
            return

        orig_name = os.path.basename(item_data["absolute_path"])
        default_name = f"PRO_{os.path.splitext(orig_name)[0]}.jpg"

        # Membuka Windows/Mac native file dialog untuk menanyakan lokasi penyimpanan
        save_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".jpg",
            filetypes=[("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            title="Pilih Lokasi untuk Ekspor Foto Produk"
        )

        # Jika pengguna tidak membatalkan proses (menekan Cancel)
        if save_path:
            try:
                # Ekspor dengan kompresi kualitas 95% murni ke jalur yang dipilih pengguna
                item_data["final_result"].convert("RGB").save(save_path, "JPEG", quality=95, optimize=True)
                
                # Ambil hanya nama file akhir untuk kebutuhan notifikasi pop-up yang ringkas
                just_filename = os.path.basename(save_path)
                messagebox.showinfo("Sukses Ekspor", f"Berhasil menyimpan file:\n{just_filename}")
            except Exception as e:
                messagebox.showerror("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan file:\n{e}")

    def handle_save_all(self):
        """
        Mengompresi seluruh matriks gambar yang berstatus selesai menjadi 
        satu file ZIP tunggal melalui dialog penyimpanan interaktif.
        """
        # Saring antrean untuk memastikan ada data yang siap diekspor
        finished_items = [data for data in self.queue_registry.values() if data["final_result"] and data["status"] == "✨ Selesai"]
        
        if not finished_items:
            messagebox.showwarning("Ekspor Gagal", "Belum ada foto produk yang selesai diproses!")
            return

        # Buka dialog untuk menentukan nama dan lokasi penyimpanan file ZIP
        save_path = filedialog.asksaveasfilename(
            initialfile="Katalog_Produk_UMKM.zip",
            defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")],
            title="Pilih Lokasi untuk Menyimpan Paket ZIP Ekspor"
        )

        if save_path:
            try:
                # Sediakan buffer memori RAM sementara untuk menulis data ZIP
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for data in finished_items:
                        orig_name = os.path.basename(data["absolute_path"])
                        output_name = f"PRO_{os.path.splitext(orig_name)[0]}.jpg"
                        
                        # Konversi PIL Image ke format biner JPEG di dalam memori
                        img_buffer = io.BytesIO()
                        data["final_result"].convert("RGB").save(img_buffer, "JPEG", quality=95, optimize=True)
                        img_buffer.seek(0)
                        
                        # Masukkan file JPEG biner tersebut ke dalam arsip ZIP
                        zip_file.writestr(output_name, img_buffer.read())
                        img_buffer.close()

                # Tulis isi buffer ZIP dari RAM murni ke dalam file fisik di disk
                with open(save_path, "wb") as f:
                    f.write(zip_buffer.getvalue())
                
                zip_buffer.close()
                gc.collect()

                just_zipname = os.path.basename(save_path)
                messagebox.showinfo("Sukses Paket Ekspor", f"Berhasil mengekspor {len(finished_items)} foto ke dalam arsip:\n{just_zipname}")
                
            except Exception as e:
                messagebox.showerror("Gagal Membuat ZIP", f"Terjadi kesalahan kompresi arsip:\n{e}")

    def run(self):
        """Memulai siklus hidup loop utama window Tkinter dengan kondisi maximized."""
        try:
            # Untuk Windows OS, perintah ini akan memaksimalkan jendela secara penuh
            self.root.state('zoomed')
        except tk.TclError:
            # Fallback untuk Linux / macOS jika perintah 'zoomed' tidak dikenali sistem
            self.root.attributes('-zoomed', True)
            
        self.root.mainloop()

if __name__ == "__main__":
    WorkflowController().run()