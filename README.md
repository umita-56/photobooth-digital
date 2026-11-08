# Cute Photobooth — Flask + MySQL

Website photobooth sederhana untuk demo/tugas. Pengguna mendaftar dan login, lalu mengunggah foto, mengisi nama dan caption, memilih frame pastel, membuat photostrip 2x2, dan menyimpan riwayatnya ke MySQL.

## Fitur
- Register akun dan login/logout. Password disimpan menggunakan hash Werkzeug.
- Halaman photobooth dan galeri dilindungi login.
- Upload foto JPG/JPEG, PNG, atau WEBP (maksimal 10 MB).
- Tiga tema pastel: Strawberry Milk (pink), Lavender Dream, dan Mint Choco.
- Membuat photostrip 2x2 otomatis dari foto yang diunggah.
- Halaman hasil dengan tombol unduh.
- Galeri riwayat photostrip tersimpan di database.
- Validasi format gambar dan tampilan responsif.

## Kebutuhan
- Python 3.10 atau lebih baru
- MySQL melalui XAMPP (MySQL saja cukup) atau MySQL Server
- Browser modern

## Cara menjalankan (Windows + XAMPP)
1. Ekstrak `cute_photobooth.zip`.
2. Buka XAMPP Control Panel, klik **Start** pada MySQL.
3. Buka `http://localhost/phpmyadmin`.
4. Pilih tab **Import**, pilih file `database.sql`, lalu klik **Import/Go**. Jika database lama sudah ada, impor ulang file ini agar tabel `users` ikut dibuat (tabel `sessions` yang lama tidak dihapus).
5. Buka folder project lewat Command Prompt/Terminal.
6. Buat virtual environment (opsional tetapi disarankan):
   ```bash
   py -m venv .venv
   .venv\\Scripts\\activate
   ```
7. Pasang library:
   ```bash
   pip install -r requirements.txt
   ```
8. Jalankan:
   ```bash
   py app.py
   ```
9. Buka `http://127.0.0.1:5000`.

## Konfigurasi MySQL
Default aplikasi memakai:
- host: `localhost`
- user: `root`
- password: kosong
- database: `cute_photobooth`

Ini cocok untuk instalasi XAMPP standar. Jika MySQL memakai password, atur environment variable sebelum menjalankan aplikasi:
```bat
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=password_mysql_kamu
set DB_NAME=cute_photobooth
py app.py
```

## Alur demo singkat
1. Buka `http://127.0.0.1:5000/register` untuk membuat akun.
2. Login melalui halaman login.
3. Masukkan nama dan caption.
4. Pilih tema warna.
5. Upload foto JPG/PNG.
6. Klik **Buat photostrip**.
7. Tunjukkan hasil, unduh gambar, lalu buka menu **Galeri** untuk menunjukkan riwayat dari MySQL.
8. Klik Logout untuk keluar.

## Struktur folder
```text
cute_photobooth/
├── app.py
├── database.sql
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── result.html
│   └── gallery.html
└── static/
    ├── css/style.css
    ├── uploads/   # foto asli yang diunggah
    └── hasil/     # photostrip yang dihasilkan
```

Catatan: file foto disimpan di folder `static/uploads` dan `static/hasil`; metadata sesi disimpan di tabel MySQL `sessions`. Untuk tugas lokal, folder ini sengaja dibuat sederhana agar mudah dipahami dan didemokan.
