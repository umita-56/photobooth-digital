# Black Box Testing - Fitur Pencarian dan Filter Galeri

## Deskripsi fitur
Fitur tambahan pada halaman Galeri memungkinkan pengguna mencari photostrip berdasarkan nama atau caption, memfilter berdasarkan tema frame, menggabungkan pencarian dan filter, serta mengembalikan tampilan ke seluruh data melalui tombol Reset Filter.

## Aturan input
- Kata kunci pencarian: maksimal 60 karakter.
- Kata kunci kosong: dianggap tidak menggunakan pencarian.
- Tema frame yang diterima: `pink`, `lavender`, `mint`, atau kosong (semua tema).
- Pencarian tidak membedakan huruf besar dan kecil sesuai perilaku pencocokan database MySQL yang digunakan.

## Rancangan test case

| ID | Teknik | Skenario / Data Input | Hasil yang Diharapkan |
|---|---|---|---|
| TC01 | Equivalence Partitioning | Kata kunci nama yang terdapat di galeri | Hanya memory dengan nama yang cocok ditampilkan |
| TC02 | Equivalence Partitioning | Kata kunci caption yang terdapat di galeri | Memory dengan caption yang cocok ditampilkan |
| TC03 | Equivalence Partitioning | Kata kunci yang tidak terdapat di galeri | Pesan “Memory tidak ditemukan” ditampilkan |
| TC04 | Equivalence Partitioning | Kata kunci dikosongkan dan tema “Semua tema” dipilih | Seluruh memory ditampilkan |
| TC05 | Equivalence Partitioning | Tema `pink`, `lavender`, atau `mint` dipilih | Hanya memory dengan tema terpilih ditampilkan |
| TC06 | Boundary Value Analysis | Kata kunci sepanjang 59 karakter | Sistem memproses kata kunci tanpa error |
| TC07 | Boundary Value Analysis | Kata kunci sepanjang 60 karakter | Sistem memproses kata kunci sampai batas maksimal |
| TC08 | Boundary Value Analysis | Kata kunci sepanjang 61 karakter dikirim melalui URL secara manual | Sistem membatasi kata kunci yang diproses menjadi 60 karakter |
| TC09 | Decision Table | Kata kunci cocok, tema cocok | Memory yang memenuhi kedua kondisi ditampilkan |
| TC10 | Decision Table | Kata kunci cocok, tema tidak cocok | Tidak ada memory yang ditampilkan |
| TC11 | Decision Table | Kata kunci tidak cocok, tema cocok | Tidak ada memory yang ditampilkan |
| TC12 | Decision Table | Kata kunci kosong, tema kosong | Seluruh memory ditampilkan |
| TC13 | Use Case Testing | Pengguna memasukkan nama, memilih tema, lalu menekan Cari Memory | Hasil galeri sesuai nama dan tema yang dipilih |
| TC14 | Use Case Testing | Pengguna menekan Reset Filter setelah pencarian | Kolom pencarian dan tema kembali kosong, seluruh memory ditampilkan |
| TC15 | Use Case Testing | Pengguna membuka hasil pencarian lalu kembali ke Galeri | Halaman hasil photostrip terbuka dan navigasi galeri tetap berfungsi |

## Kolom hasil pengujian aktual
Saat pengujian langsung, isi kolom berikut berdasarkan hasil yang benar-benar terlihat pada aplikasi.

| ID | Hasil Aktual | Status (Pass/Fail) | Catatan |
|---|---|---|---|
| TC01-TC15 | Diisi setelah pengujian | Diisi setelah pengujian | Catat jika ada perbedaan |

## Catatan
Test case di atas merupakan rancangan pengujian. Status Pass/Fail belum ditentukan karena pengujian harus dijalankan pada aplikasi yang terhubung ke database MySQL dan berisi data galeri.
