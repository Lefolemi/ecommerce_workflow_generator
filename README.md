- E-Commerce Workflow Generator -
Sistem Otomatisasi Pengolahan Citra Digital untuk Standardisasi Thumbnail Produk UMKM

- DESKRIPSI PROYEK -
E-Commerce Workflow Generator adalah sistem otomasi teknis berbasis Python yang dirancang untuk melakukan standardisasi visual produk pada marketplace digital. Proyek ini dikembangkan sebagai solusi atas fakta bahwa 70,2% pelaku UMKM masih menghadapi hambatan besar dalam pemasaran digital akibat kendala teknis dan biaya operasional yang tinggi. Dengan mengotomatisasi proses penghapusan latar belakang, penyesuaian ukuran, dan pemusatan objek, aplikasi ini menghasilkan aset visual berbentuk "packshot" yang secara langsung mampu memengaruhi 78,7% keputusan pembelian konsumen yang didasarkan pada kualitas foto produk. Dokumentasi ini mencakup seluruh instruksi pengaturan serta logika operasional yang menggerakkan sistem tersebut.

- PERSYARATAN SYSTEM -
Aplikasi ini dirancang untuk berjalan pada lingkungan Python versi 3.10 atau yang lebih tinggi. Fungsionalitas utama sistem sangat bergantung pada pustaka OpenCV untuk melakukan transformasi spasial, Pillow untuk manajemen kanvas gambar, serta Rembg untuk proses segmentasi objek berbasis kecerdasan buatan. Untuk memastikan performa tetap optimal, sistem menggunakan ONNX Runtime dalam mengeksekusi model deep learning U2-Net yang memiliki konsumsi memori sangat efisien, yakni sekitar 4,7 MB.

- INSTALASI DAN PENGATURAN -
Buka terminal pada perangkat Anda dan jalankan perintah berikut untuk menginstal seluruh dependensi yang diperlukan oleh sistem:

pip install opencv-python pillow rembg onnxruntime

Pastikan struktur folder proyek telah mencakup direktori core/ untuk menyimpan logika pemrosesan dan direktori gui/ untuk komponen antarmuka pengguna sebelum Anda menjalankan skrip utama aplikasi.

- ALUR KERJA OPERASIONAL -
Sistem beroperasi melalui urutan otomasi linear guna memastikan konsistensi hasil pada setiap gambar yang diproses. Tahap pertama dimulai saat pengguna memilih foto produk mentah melalui antarmuka berbasis Tkinter yang tersedia. Sistem kemudian secara otomatis memicu algoritma U2-Net untuk melakukan Salient Object Detection yang memisahkan objek produk dari latar belakang aslinya dengan tingkat presisi yang tinggi. Setelah objek berhasil terisolasi, OpenCV akan menghitung bounding box objek untuk menentukan koordinat spasial yang akurat. Sistem kemudian melakukan penskalaan otomatis agar objek sesuai dengan kanvas rasio 1:1 dan menempatkannya tepat di titik tengah guna memastikan produk menjadi fokus utama bagi calon pembeli. Hasil akhir pemrosesan akan diekspor ke folder output dalam format JPEG berkualitas tinggi yang sudah siap untuk diunggah ke platform e-commerce seperti Shopee atau Tokopedia.

- LANDASAN TEKNIS -
Mesin inti aplikasi ini memanfaatkan arsitektur Nested U-Structure (U2-Net) yang memungkinkan proses ekstraksi fitur multi-skala dilakukan tanpa mengorbankan resolusi gambar asli. Pendekatan arsitektur ini terbukti jauh lebih efisien dibandingkan metode klasifikasi tradisional, sehingga memungkinkan aplikasi untuk memproses citra dengan kecepatan antara 30 hingga 40 FPS pada perangkat keras standar. Dengan melakukan standardisasi setiap gambar ke dalam format packshot yang profesional, alat ini diproyeksikan dapat mengurangi biaya promosi UMKM hingga 40% sekaligus membantu menjembatani kesenjangan literasi digital bagi para pemilik usaha kecil.

- REFERENSI -
Proyek ini mengintegrasikan temuan riset dari Wulan Dari (2024) mengenai minat konsumen pada platform Shopee, Qin et al. (2020) mengenai arsitektur U2-Net, serta Nikmatus Sholikha et al. (2025) mengenai transformasi digital pada sektor UMKM. Standar visual tambahan yang diterapkan dalam sistem ini merujuk pada penelitian Szulc dan Musielak (2022) serta prinsip pengolahan citra digital dari Chaojian Li (2024).