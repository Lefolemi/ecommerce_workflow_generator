E-Commerce Workflow Generator
Sistem Otomatisasi Pengolahan Citra Digital untuk Standardisasi Thumbnail Produk UMKM

- DESKRIPSI PROYEK -
E-Commerce Workflow Generator (Studio EcoImage) adalah sistem otomasi teknis berbasis Python yang dirancang untuk melakukan standardisasi visual produk pada marketplace digital. Proyek ini dikembangkan sebagai solusi atas fakta bahwa 70,2% pelaku UMKM masih menghadapi hambatan besar dalam pemasaran digital akibat kendala teknis dan biaya operasional yang tinggi. Dengan mengotomatisasi proses restorasi pencahayaan adaptif, penghapusan latar belakang, penyesuaian ukuran, dan pemusatan objek, aplikasi ini menghasilkan aset visual berbentuk "packshot" yang secara langsung mampu memengaruhi 78,7% keputusan pembelian konsumen yang didasarkan pada kualitas foto produk. Dokumentasi ini mencakup seluruh instruksi pengaturan serta logika operasional yang menggerakkan sistem tersebut.

- PERSYARATAN SYSTEM -
Aplikasi ini dirancang untuk berjalan pada lingkungan Python versi 3.10 atau yang lebih tinggi. Fungsionalitas utama sistem sangat bergantung pada pustaka OpenCV untuk melakukan transformasi spasial, Pillow untuk manajemen kanvas gambar, serta Rembg untuk proses segmentasi objek berbasis kecerdasan buatan. Untuk memastikan performa tetap optimal, sistem menggunakan ONNX Runtime dalam mengeksekusi model deep learning U2-Net yang memiliki konsumsi memori sangat efisien, yakni sekitar 4,7 MB. Koneksi internet aktif hanya diperlukan pada saat eksekusi pertama kali untuk mengunduh otomatis berkas bobot arsitektur U2-Net dari server pustaka.

- INSTALASI DAN PENGATURAN -
Buka terminal pada perangkat Anda dan jalankan perintah berikut untuk menginstal seluruh dependensi yang diperlukan oleh sistem:
pip install -r requirements.py

Pastikan struktur folder proyek telah mencakup direktori core/ untuk menyimpan logika pemrosesan (termasuk sub-direktori engines/, models/, training/, dan folder pengujian evaluation/) serta direktori gui/ untuk komponen antarmuka pengguna sebelum Anda menjalankan skrip utama aplikasi.

- ALUR KERJA OPERASIONAL -
Sistem beroperasi melalui urutan otomasi linear guna memastikan konsistensi hasil pada setiap gambar yang diproses melalui antarmuka berbasis Tkinter yang tersedia:
1. Akuisisi Citra & Guardrail Otomatis: Pengguna memasukkan foto produk mentah melalui tombol ambil file atau fitur Drag & Drop. Sistem secara otomatis memicu algoritma pra-proses untuk mendeteksi kandungan objek. Jika gambar terdeteksi sebagai latar belakang murni (tanpa objek kontras), sistem akan memicu indikator gagal (❌) dan menghapus berkas dari antrean secara otomatis dalam waktu 2 detik.

2. Restorasi Pencahayaan Adaptif: Citra yang lolos validasi akan dihitung tingkat luminans histogramnya secara otomatis. Jika gambar terdeteksi redup/gelap, arsitektur kecerdasan buatan SimpleEnhanceUNet akan menyuntikkan cahaya menggunakan metode Linear Alpha Blending untuk memunculkan detail produk.

3. Isolasi Objek & Penskalaan Geometri: Citra kemudian diproses oleh mesin segmentasi berbasis U2-Net untuk memisahkan objek dari latar belakang bawaannya. Setelah objek terisolasi, OpenCV akan mengekstrak bounding box dan menghitung pusat massa sebaran piksel menggunakan koordinat Image Moments agar produk ditempatkan seimbang di tengah kanvas kustom.

4. Overlay Studio & Atribut Komersial: Pengguna dapat mengubah suasana latar belakang menjadi kanvas solid berbasis dialog Color Picker ("Bersih Studio") atau menggunakan latar ruangan luar ("Kustom Gambar Latar..."). Lapisan akhir diakhiri dengan pencetakan label stiker promo komersial serta penempelan teks watermark toko pelindung hak cipta.

5. Manajemen Ekspor Arsip: Hasil akhir dapat disimpan secara tunggal dalam format JPEG berkualitas tinggi 95% murni, atau dikompresi secara massal ke dalam satu file dokumen .zip langsung melalui buffer memori RAM komputer.

- LANDASAN TEKNIS DAN EVALUASI (UAS REQUIREMENTS) -
Mesin inti aplikasi ini memanfaatkan arsitektur Nested U-Structure (U2-Net) yang memungkinkan proses ekstraksi fitur multi-skala dilakukan tanpa mengorbankan resolusi gambar asli, yang dikombinasikan dengan arsitektur SimpleEnhanceUNet dengan forward pass terinterpolasi bilinear otomatis untuk penanganan dimensi piksel ganjil. Pendekatan arsitektur ini terbukti jauh lebih efisien dibandingkan metode klasifikasi tradisional, sehingga memungkinkan aplikasi untuk memproses citra dengan kecepatan antara 30 hingga 40 FPS pada perangkat keras standar.

Untuk pemenuhan standardisasi penilaian tugas besar berbasis OBE, proyek ini menyediakan modul evaluasi kuantitatif terpisah yang dapat dijalankan secara mandiri melalui perintah berikut:

- Pengujian Nilai Batas Error Model AI: python -m core.evaluation.evaluate_model (Menghitung nilai MAE / L1 Loss pada data uji eval15).

- Pengujian Ketepatan Validasi Objek: python -m core.evaluation.evaluate_validation (Menghitung simulasi skenario pengujian unit deteksi).

Dengan melakukan standardisasi setiap gambar ke dalam format packshot yang profesional, alat ini diproyeksikan dapat mengurangi biaya promosi UMKM hingga 40% sekaligus membantu menjembatani kesenjangan literasi digital bagi para pemilik usaha kecil.

- REFERENSI -
Proyek ini mengintegrasikan temuan riset dari Wulan Dari (2024) mengenai minat konsumen pada platform Shopee, Qin et al. (2020) mengenai arsitektur U2-Net, serta Nikmatus Sholikha et al. (2025) mengenai transformasi digital pada sektor UMKM. Standar visual tambahan yang diterapkan dalam sistem ini merujuk pada penelitian Szulc dan Musielak (2022) serta prinsip pengolahan citra digital dari Chaojian Li (2024).